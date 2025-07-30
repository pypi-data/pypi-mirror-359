from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ksuit.core.callbacks import Callback
from ksuit.utils import module_utils, naming_utils

if TYPE_CHECKING:
    from torch import nn

    from ksuit.core.trainers import TrainingContext


class ModelParameterCountCallback(Callback):
    @staticmethod
    def _get_param_counts(model: nn.Module) -> list[tuple[str, int, int]]:
        return [
            (
                naming_utils.alphanumeric_to_snake_case(type(model).__name__),
                module_utils.get_num_trainable_parameters(model),
                module_utils.get_num_frozen_parameters(model),
            )
        ]

    def _on_fit_start(self, ctx: TrainingContext) -> None:
        # TODO somehow integrate "interesting" splits, like encoder/decoder or backbone
        param_counts = self._get_param_counts(ctx.model)

        _, total_trainable, total_frozen = param_counts[0]
        max_trainable_digits = int(np.log10(total_trainable)) + 1 if total_trainable > 0 else 1
        max_frozen_digits = int(np.log10(total_frozen)) + 1 if total_frozen > 0 else 1
        # add space for thousand seperators
        max_trainable_digits += int(max_trainable_digits / 3)
        max_frozen_digits += int(max_frozen_digits / 3)
        # generate format strings
        tformat = f">{max_trainable_digits},"
        fformat = f">{max_frozen_digits},"

        self.logger.info("------------------")
        self.logger.info("parameter counts (trainable | frozen)")
        self.logger.info("------------------")
        for name, tcount, fcount in param_counts:
            self.logger.info(f"- {format(tcount, tformat)} | {format(fcount, fformat)} | {name}")
            self.tracker.set_summary(key=f"param_count/{name}/trainable", value=tcount)
            self.tracker.set_summary(key=f"param_count/{name}/frozen", value=fcount)
