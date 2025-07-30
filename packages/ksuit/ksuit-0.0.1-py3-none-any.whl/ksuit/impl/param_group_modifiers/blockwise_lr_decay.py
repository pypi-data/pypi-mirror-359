from typing import Any

from torch import nn

from ksuit.core.optim import ParamGroupModifier
from ksuit.utils import config_utils


class BlockwiseLrDecay(ParamGroupModifier):
    def __init__(self, decay: float, path_to_blocks: str = "blocks", **kwargs):
        super().__init__(**kwargs)
        self.decay = decay
        self.path_to_blocks = path_to_blocks

    def populate_parameter_properties(
        self,
        parameter_properties: list[dict[str, Any]],
        model: nn.Module | None = None,
    ) -> list[dict[str, Any]]:
        # extract num_blocks
        if model is None:
            raise ValueError(f"{type(BlockwiseLrDecay).__name__} requires model to extract num_blocks")
        if not config_utils.has_path(model, path=self.path_to_blocks):
            raise ValueError(f"model does not have a {self.path_to_blocks} attribute")
        num_blocks = len(config_utils.get_by_path(model, path=self.path_to_blocks))

        # parameter_properties are sorted according to their registration order
        # this order is made use of as follows:
        # - assign everything before the block the lowest lr
        # - assign steadily increasing values as blocks increase
        # - assign the highest lr (unscaled lr) to everything after the last block
        lr_scales = list(self.decay**(num_blocks - i + 1) for i in range(num_blocks + 1))
        i = 0
        for parameter_properties_item in parameter_properties:
            # check if parameter is located before first block
            if i == 0 and not parameter_properties_item["name"].startswith(self.path_to_blocks):
                assert f"{type(self).__name__}.lr_scale" not in parameter_properties_item
                parameter_properties_item[f"{type(self).__name__}.lr_scale"] = lr_scales[i]
                continue
            # if a parameter follows after the last block -> full learning rate (i.e., no scaling)
            if i == num_blocks and not parameter_properties_item["name"].startswith(self.path_to_blocks):
                assert f"{type(self).__name__}.lr_scale" not in parameter_properties_item
                continue
            # increase i if the next block starts
            # (this also means if a parameter is between two blocks, it will have the lr scale of the preceeding block)
            if parameter_properties_item["name"].startswith(self.path_to_blocks):
                name_without_prefix = parameter_properties_item["name"][len(self.path_to_blocks) + 1:]
                block_idx = int(name_without_prefix.split(".")[0])
                i = block_idx + 1

            assert f"{type(self).__name__}.lr_scale" not in parameter_properties_item
            parameter_properties_item[f"{type(self).__name__}.lr_scale"] = lr_scales[i]

    def on_before_optimizer_step(
        self,
        param_groups: list[dict[str, Any]],
        step: int | None = None,
        total_steps: int | None = None
    ) -> None:
        for param_group in param_groups:
            if f"{type(self).__name__}.lr_scale" in param_group:
                param_group["lr"] = param_group["lr"] * param_group[f"{type(self).__name__}.lr_scale"]
