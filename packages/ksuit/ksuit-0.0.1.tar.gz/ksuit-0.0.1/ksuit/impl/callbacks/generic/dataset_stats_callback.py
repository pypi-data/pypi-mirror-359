from __future__ import annotations

from typing import TYPE_CHECKING

from ksuit.core.callbacks import Callback

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class DatasetStatsCallback(Callback):
    def _on_fit_start(self, ctx: TrainingContext) -> None:
        self.logger.info("------------------")
        self.logger.info("dataset statistics")
        self.logger.info("------------------")
        for key, dataset in self.data_provider.datasets.items():
            self.tracker.set_summary(key=f"ds_stats/{key}/len", value=len(dataset))
            self.logger.info(f"- {key}: len={len(dataset)} items={dataset.items}")
