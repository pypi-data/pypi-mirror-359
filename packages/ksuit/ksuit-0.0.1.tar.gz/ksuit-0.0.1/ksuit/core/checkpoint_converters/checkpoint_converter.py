import logging
from copy import deepcopy
from typing import Any, Sequence

import torch

from ksuit.core.parameter_renamers import ParameterRenamer


class CheckpointConverter:
    def __init__(self, ctor_kwargs: dict[str, Any], parameter_renamers: Sequence[ParameterRenamer]):
        self.logger = logging.getLogger(type(self).__name__)
        self.ctor_kwargs = ctor_kwargs
        self.parameter_renamers = parameter_renamers

    def __call__(self, state_dict: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        new_state_dict = {}
        for parameter_renamer in self.parameter_renamers:
            new_state_dict_update = parameter_renamer(state_dict)
            for key in new_state_dict_update.keys():
                if key in new_state_dict:
                    raise RuntimeError(
                        f"Parameter '{key}' was already included into converted checkpoint. Make sure to include "
                        f"parameters only once to avoid renaming two different parameters to the same name."
                    )
            new_state_dict.update(new_state_dict_update)
        return new_state_dict