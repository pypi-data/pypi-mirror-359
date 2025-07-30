from __future__ import annotations

from typing import TYPE_CHECKING

import torch.cuda

from ksuit.core.callbacks import PeriodicCallback

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class LogUtilizationCallback(PeriodicCallback):
    def _invoke(self, ctx: TrainingContext) -> None:
        if ctx.model.device.type == "cpu":
            return
        logstr = ""
        # utilization requires 'pip install pynvml'
        try:
            logstr += f"utilization={torch.cuda.utilization()}% "
        except ModuleNotFoundError:
            pass
        logstr += f"max_memory_allocated={torch.cuda.max_memory_allocated() / 1024 / 1024 / 1024:.1f}GB"
        self.logger.info(logstr)
        torch.cuda.reset_peak_memory_stats()
