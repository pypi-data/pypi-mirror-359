from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import torch
from torch import nn
from torch.amp import GradScaler

from ksuit.core.factories import Factory
from ksuit.utils import formatting_utils
from ksuit.utils.amp_utils import NoopGradScaler
from ksuit.utils.injective_dict import InjectiveDict

from .lr_schedule import LrSchedule
from .param_group_modifier import ParamGroupModifier

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any

    from ksuit.core.providers import TrainingProgressProvider


class Optimizer:
    def __init__(
        self,
        model: nn.Module,
        torch_optim_ctor: Callable[[Iterable[dict[str, Any]]], torch.optim.Optimizer],
        lr_schedule: dict[str, Any] | None = None,
        clip_grad_value: float | None = None,
        clip_grad_norm: float | None = None,
        param_group_modifiers: list | None = None,
        exclude_bias_from_weight_decay: bool = True,
        exclude_scalar_params_from_weight_decay: bool = True,
        exclude_vector_params_from_weight_decay: bool = True,
        # providers
        training_progress_provider: TrainingProgressProvider | None = None,
    ):
        self.logger = logging.getLogger(type(self).__name__)
        self.model = model
        self.clip_grad_value = clip_grad_value
        self.clip_grad_norm = clip_grad_norm

        # checks
        if self.clip_grad_value is not None and self.clip_grad_value < 0:
            raise ValueError(f"invalid clip_grad_value {self.clip_grad_value}")
        if self.clip_grad_norm is not None and self.clip_grad_norm < 0:
            raise ValueError(f"invalid clip_grad_norm {self.clip_grad_norm}")

        # create lr_schedule modifier
        # (used as first param_group_modifiers but it is a separate flage because its such a common use-case)
        param_group_defaults = torch_optim_ctor([nn.Parameter(torch.ones((1,)))]).defaults
        if lr_schedule is None:
            self.param_group_modifiers = []
        else:
            self.param_group_modifiers = [
                LrSchedule(
                    schedule=lr_schedule,
                    training_progress_provider=training_progress_provider,
                    param_group_defaults=param_group_defaults,
                ),
            ]
        # create param_group_modifiers
        self.param_group_modifiers += Factory.create_list(
            param_group_modifiers,
            expected_base_type=ParamGroupModifier,
            training_progress_provider=training_progress_provider,
            param_group_defaults=param_group_defaults,
        )
        parameter_properties = []
        self.logger.info(f"{exclude_bias_from_weight_decay=}")
        self.logger.info(f"{exclude_scalar_params_from_weight_decay=}")
        self.logger.info(f"{exclude_vector_params_from_weight_decay=}")
        self.logger.info(f"param_group_modifiers={self.param_group_modifiers}")
        # create a parameter group per parameter and apply exclude from weight decay
        for name, param in model.named_parameters():
            properties = dict(
                name=name,
                params=[param],
            )
            # excluding norm and bias params is very common for all models -> support with simple flag
            # bias has ndim == 1, so it needs to be checked before
            # the bias of norm layers is considered a bias, not a norm parameter
            exclude_from_wd = False
            if exclude_bias_from_weight_decay and name.endswith(".bias"):
                exclude_from_wd = True
            elif exclude_scalar_params_from_weight_decay and param.ndim == 0:
                exclude_from_wd = True
            # this excludes e.g., weights of norms or scalar parameters
            elif exclude_vector_params_from_weight_decay and param.ndim == 1:
                exclude_from_wd = True
            if exclude_from_wd:
                properties["weight_decay"] = 0.0
            parameter_properties.append(properties)

        # extract param_group defaults
        for param_group_modifier in self.param_group_modifiers:
            param_group_modifier.populate_parameter_properties(parameter_properties, model=model)

        # merge same groups with same parameters (useful for logging)
        merged_groups = []
        merged_groups_properties = []
        merged_groups_paramnames = []
        for param_group in parameter_properties:
            param_name = param_group.pop("name")
            properties = {k: v for k, v in param_group.items() if k != "params"}
            matching_group_idx = None
            for i, merged_group_properties in enumerate(merged_groups_properties):
                if properties == merged_group_properties:
                    matching_group_idx = i
                    break
            if matching_group_idx is None:
                merged_groups.append(param_group)
                merged_groups_properties.append(properties)
                merged_groups_paramnames.append([param_name])
            else:
                merged_groups[matching_group_idx]["params"] += param_group["params"]
                merged_groups_paramnames[matching_group_idx].append(param_name)

        # add name to param_groups
        for param_group in merged_groups:
            names = []
            for key, value in param_group.items():
                if key == "params":
                    continue
                if isinstance(value, float):
                    value_str = formatting_utils.float_to_scientific_notation(value, max_precision=1, remove_plus=True)
                elif isinstance(value, int):
                    value_str = str(value)
                else:
                    raise NotImplementedError
                names.append(f"{key}={value_str}")
            if len(names) == 0:
                param_group["name"] = "default"
            else:
                param_group["name"] = "&".join(names)

        # log param groups
        self.logger.info(f"using {len(merged_groups)} param groups:")
        for i in range(len(merged_groups)):
            self.logger.info(
                " ".join(
                    [f"{key}={value}" for key, value in merged_groups[i].items() if key not in ["params", "name"]]
                    + [f"len(params)={len(merged_groups[i]['params'])}"]
                )
            )
            for param_name in merged_groups_paramnames[i]:
                self.logger.info(f"- {param_name}")

        # torch optimizer organizes parameters by enumerating them (not by name)
        # so for loading an arbitrary optim state_dict an association from param_name to param_idx has to be stored
        param_idx_to_name = {}
        for group_paramnames in merged_groups_paramnames:
            for param_name in group_paramnames:
                idx = len(param_idx_to_name)
                param_idx_to_name[idx] = param_name
        self.param_idx_to_name = InjectiveDict(param_idx_to_name)

        # initialize torch optim
        self.torch_optim = torch_optim_ctor(merged_groups)

        # for grad clipping all parameters of the optimizer are required
        self.all_parameters = None
        if self.clip_grad_value is not None or self.clip_grad_norm is not None:
            self.all_parameters = list(model.parameters())

    def _has_param_with_grad(self) -> bool:
        for param_group in self.torch_optim.param_groups:
            for p in param_group["params"]:
                if p.grad is not None:
                    return True
        return False

    def step(
        self,
        grad_scaler: GradScaler | NoopGradScaler | None = None,
        step: int | None = None,
        total_steps: int | None = None,
    ) -> None:
        # grad_scaler doesnt support update without gradient (e.g. GAN setting)
        # Error: AssertionError: No inf checks were recorded for this optimizer
        if isinstance(grad_scaler, GradScaler):
            if not self._has_param_with_grad():
                return
        # grad scaler is not strictly required
        # (e.g. if Optimizer is only used as wrapper for excluding bias/norm parameters from weight decay)
        if grad_scaler is None:
            grad_scaler = NoopGradScaler()

        # apply param_group_modifiers (e.g., lr schedule)
        for param_group_modifier in self.param_group_modifiers:
            param_group_modifier.on_before_optimizer_step(
                self.torch_optim.param_groups,
                step=step,
                total_steps=total_steps,
            )

        # NOTE: closure is not supported
        if self.clip_grad_value is not None or self.clip_grad_norm is not None:
            grad_scaler.unscale_(self.torch_optim)
        # clip gradients
        if self.clip_grad_value is not None:
            torch.nn.utils.clip_grad_value_(self.all_parameters, self.clip_grad_value)
        if self.clip_grad_norm is not None:
            torch.nn.utils.clip_grad_norm_(self.all_parameters, self.clip_grad_norm)
        # torch optim step with grad scaler
        grad_scaler.step(self.torch_optim)
        grad_scaler.update()

    def zero_grad(self, set_to_none: bool = True) -> None:
        self.torch_optim.zero_grad(set_to_none=set_to_none)

    def state_dict(self) -> dict[str, Any]:
        sd = self.torch_optim.state_dict()
        sd["param_idx_to_name"] = self.param_idx_to_name.to_dict(key_type=int)
        return sd

    def load_state_dict(self, state_dict_to_load: dict[str, Any]) -> None:
        # torch optim state_dict stores param_groups and the states of each parameter
        # if a torch optim state_dict is loaded it would overwrite all param_groups from the checkpoint
        # this results in unexpected behavior when loading an optimizer (e.g. for resuming a run from a checkpoint)
        # - add new parameters (e.g. unfreeze something)
        # - change weight_decay or other param_group properties: the load_state_dict would overwrite the actual
        #   weight_decay with the weight_decay from the checkpoint
        if "param_idx_to_name" in state_dict_to_load:
            # torch optim stores:
            # - a list of param_idxs in each param_group
            # - a dict from param_idxs to state for the state of the param
            # -> match the param_idxs and overwrite the state
            loaded_param_idx_to_name = InjectiveDict(state_dict_to_load["param_idx_to_name"])
            loaded_states = state_dict_to_load["state"]
            cur_state_dict = self.torch_optim.state_dict()
            cur_states = cur_state_dict["state"]
            cur_param_groups = cur_state_dict["param_groups"]
            for cur_param_group in cur_param_groups:
                for cur_param_idx in cur_param_group["params"]:
                    param_name = self.param_idx_to_name[cur_param_idx]
                    loaded_param_idx = loaded_param_idx_to_name[param_name]
                    if loaded_param_idx not in loaded_states:
                        # if no optim step was done no state exists -> dont load the state
                        cur_states.pop(loaded_param_idx, None)
                    else:
                        # overwrite state with loaded state
                        cur_states[cur_param_idx] = loaded_states[loaded_param_idx]
            state_dict_to_load = dict(state=cur_states, param_groups=cur_param_groups)
        self.torch_optim.load_state_dict(state_dict_to_load)
