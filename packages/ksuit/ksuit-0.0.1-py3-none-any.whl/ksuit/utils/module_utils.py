import copy
from dataclasses import dataclass

import torch

from ksuit.utils import formatting_utils, param_checking


def get_device(module: torch.nn.Module) -> torch.device | None:
    """Returns the device of the module. Returns none if device could not be inferred."""
    try:
        param = next(module.parameters())
        return param.device
    except StopIteration:
        try:
            buffer = next(module.buffers())
            return buffer.device
        except StopIteration:
            return None


def get_num_parameters(module: torch.nn.Module) -> int:
    """Returns the total number of parameters of the module."""
    return sum(p.numel() for p in module.parameters())


def get_num_trainable_parameters(module: torch.nn.Module) -> int:
    """Returns the total number of trainable (requires_grad=True) parameters of the module."""
    return sum(p.numel() for p in module.parameters() if p.requires_grad)


def get_num_frozen_parameters(module: torch.nn.Module) -> int:
    """Returns the total number of frozen (requires_grad=False) parameters of the module."""
    return sum(p.numel() for p in module.parameters() if not p.requires_grad)


def freeze(module: torch.nn.Module) -> bool:
    """Freezes all parameters in a module by setting p.requires_grad=False."""
    for p in module.parameters():
        p.requires_grad = False


def unfreeze(module: torch.nn.Module) -> bool:
    """Unfreezes all parameters in a module by setting p.requires_grad=True."""
    for p in module.parameters():
        p.requires_grad = True


@dataclass
class ModelInitializationGroup:
    group_name: str
    initialization: str
    parameter_names: list[str]

    def __len__(self) -> int:
        return len(self.parameter_names)

    def __str__(self) -> str:
        return f"{self.group_name}: {self.initialization} ({len(self)} params)"


@dataclass
class MergedModelInitializationGroups:
    weight_groups: list[ModelInitializationGroup]
    bias_groups: list[ModelInitializationGroup]
    parameter_groups: list[ModelInitializationGroup]


def get_model_initialization_groups(module: torch.nn.Module) -> list[ModelInitializationGroup]:
    groups = []
    for name, p in module.named_parameters():
        mean = p.mean().item()
        mean_str = formatting_utils.float_to_scientific_notation(mean, max_precision=1)
        # TODO this threshold could be parameter size dependent
        if mean < 1e-3:
            mean = 0.0
        std = p.std().item()
        std_str = formatting_utils.float_to_scientific_notation(std, max_precision=1)
        # check for common initializations
        if 0.019 < std < 0.021:
            std = 0.02
        if std == 0:
            if mean == 0:
                initialization = "zeros"
            elif mean == 1:
                initialization = "ones"
            else:
                initialization = f"constant={mean_str}"
        elif mean == 0:
            initialization = f"std={std_str}"
        else:
            initialization = f"mean={mean_str} std={std_str}"

        group = ModelInitializationGroup(
            group_name=name,
            initialization=initialization,
            parameter_names=[name],
        )
        groups.append(group)
    return groups


def get_grouped_model_initialization_groups(
    module: torch.nn.Module,
    merge_depth: int = 1,
) -> MergedModelInitializationGroups:
    groups = get_model_initialization_groups(module)

    # group into weights/biases/parameters
    weight_groups = []
    bias_groups = []
    parameter_groups = []
    for group in groups:
        if len(group) != 1:
            raise RuntimeError("get_model_initialization_groups did not produce ungrouped ModelInitializationGroups")
        if group.group_name.endswith(".bias"):
            bias_groups.append(
                ModelInitializationGroup(
                    group_name=group.group_name[:-len(".bias")],
                    initialization=group.initialization,
                    parameter_names=[group.group_name[:-len(".bias")]],
                ),
            )
        elif group.group_name.endswith(".weight"):
            weight_groups.append(
                ModelInitializationGroup(
                    group_name=group.group_name[:-len(".weight")],
                    initialization=group.initialization,
                    parameter_names=[group.group_name[:-len(".weight")]],
                ),
            )
        else:
            parameter_groups.append(copy.deepcopy(group))

    # merge groups
    for _ in range(merge_depth):
        weight_groups = _merge_groups(weight_groups)
        bias_groups = _merge_groups(bias_groups)
        parameter_groups = _merge_groups(parameter_groups)

    # readd .weights/.bias
    for weight_group in weight_groups:
        weight_group.group_name += ".weight"
        for parameter_name in weight_group.parameter_names:
            parameter_name += ".weight"
    for bias_group in bias_groups:
        bias_group.group_name += ".bias"
        for parameter_name in bias_group.parameter_names:
            parameter_name += ".bias"

    return MergedModelInitializationGroups(
        weight_groups=weight_groups,
        bias_groups=bias_groups,
        parameter_groups=parameter_groups,
    )


def _merge_groups(groups: list[ModelInitializationGroup]) -> list[ModelInitializationGroup]:
    groups = copy.deepcopy(groups)

    merged_groups = {}
    i = 0
    while i < len(groups):
        name_i_tokens = groups[i].group_name.split(".")
        is_part_of_group = False
        j = i + 1
        while j < len(groups):
            name_j_tokens = groups[j].group_name.split(".")
            if len(name_i_tokens) != len(name_j_tokens):
                j += 1
                continue
            num_different_tokens = sum(a != b for a, b in zip(name_i_tokens, name_j_tokens, strict=True))
            if num_different_tokens == 1 and groups[i].initialization == groups[j].initialization:
                different_token = [a for a, b in zip(name_i_tokens, name_j_tokens, strict=True) if a != b]
                if len(different_token) != 1:
                    raise RuntimeError
                # keep initial token unmerged
                if different_token[0] == name_i_tokens[0]:
                    j += 1
                    continue
                # merge int tokens before string tokens by disallowing merges if a int token is present
                # (i.e., merge blocks.*.norm1.weight and not blocks.0.*.weight)
                has_int_token_i = any(param_checking.string_is_int(token) for token in name_i_tokens)
                has_int_token_j = any(param_checking.string_is_int(token) for token in name_j_tokens)
                if has_int_token_i and has_int_token_j and not different_token[0].isnumeric():
                    j += 1
                    continue
                # prevent overmerging (e.g., blocks.*.norm1 + blocks.*.norm2 -> blocks.*.*)
                num_unmerged_tokens_i = sum(token != "*" for token in name_i_tokens)
                num_unmerged_tokens_j = sum(token != "*" for token in name_j_tokens)
                if num_unmerged_tokens_i <= 2 or num_unmerged_tokens_j <= 2:
                    j += 1
                    continue

                merged_group_tokens = [
                    a
                    if a == b else "*"
                    for a, b in zip(name_i_tokens, name_j_tokens, strict=True)
                ]
                merged_group_name = ".".join(merged_group_tokens)
                if merged_group_name in merged_groups:
                    merged_groups[merged_group_name].parameter_names.append(groups[j].group_name)
                else:
                    is_part_of_group = True
                    merged_groups[merged_group_name] = ModelInitializationGroup(
                        group_name=merged_group_name,
                        initialization=groups[i].initialization,
                        parameter_names=[groups[i].group_name, groups[j].group_name],
                    )
                groups.pop(j)
            else:
                j += 1
        if not is_part_of_group:
            if groups[i].group_name in merged_groups:
                raise KeyError
            merged_groups[groups[i].group_name] = groups[i]
        i += 1
    return list(merged_groups.values())
