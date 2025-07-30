import fnmatch
from typing import Any

import torch

from ksuit.core.parameter_renamers import ParameterRenamer


class IdentityParameterRenamer(ParameterRenamer):
    def __init__(self, pattern: str):
        super().__init__()
        self.pattern = pattern

    def __call__(self, state_dict: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        new_state_dict = {}
        for key, value in state_dict.items():
            if fnmatch.fnmatch(key, pat=self.pattern):
                new_state_dict[key] = value
        return new_state_dict
