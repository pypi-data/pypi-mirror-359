from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from ksuit.core.callbacks import PeriodicCallback
from ksuit.utils import formatting_utils, param_checking

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class LogProgressCallback(PeriodicCallback):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_time = None
        self._last_log_time = None
        self._last_log_samples = 0

    def _on_fit_start(self, ctx: TrainingContext) -> None:
        self._start_time = self._last_log_time = datetime.now()

    def _invoke(self, ctx: TrainingContext) -> None:
        tpp = ctx.trainer.training_progress_provider
        if tpp.end_eus.epoch is not None:
            total_updates = tpp.end_eus.epoch * tpp.updates_per_epoch
        elif tpp.end_eus.update is not None:
            total_updates = tpp.end_eus.update
        elif tpp.end_eus.sample is not None:
            total_updates = tpp.cur_eus.sample // tpp.global_batch_size
        else:
            raise NotImplementedError

        param_checking.exactly_one_non_none(self.every_n_epochs, self.every_n_updates, self.every_n_samples)
        self.logger.info("------------------")
        if self.every_n_epochs is not None:
            self.logger.info(
                f"Epoch {tpp.cur_eus.epoch}/{tpp.end_eus.epoch} "
                f"({tpp.cur_eus})"
            )
        if self.every_n_updates is not None:
            self.logger.info(
                f"Update {tpp.cur_eus.update}/{total_updates} "
                f"({tpp.cur_eus})"
            )
        if self.every_n_samples is not None:
            self.logger.info(
                f"Sample {tpp.cur_eus.sample}/{tpp.end_eus.sample} "
                f"({tpp.cur_eus})"
            )

        now = datetime.now()
        seconds_since_last_log = (now - self._last_log_time).total_seconds()
        samples_since_last_log = tpp.cur_eus.sample - self._last_log_samples
        updates_since_last_log = samples_since_last_log // tpp.global_batch_size
        if self._last_log_samples == 0:
            progress = tpp.cur_eus.update / total_updates
        else:
            # subtract first interval to give better estimate
            total_updates -= updates_since_last_log
            cur_update = tpp.cur_eus.update - updates_since_last_log
            progress = cur_update / total_updates
        estimated_duration = (now - self._start_time) / progress
        time_per_update = formatting_utils.seconds_to_duration(
            seconds=seconds_since_last_log / updates_since_last_log,
            largest_unit="hour",
            remove_zeros_until_unit="minute",
        )
        self.logger.info(
            f"ETA: {(self._start_time + estimated_duration).strftime('%m.%d %H.%M.%S')} "
            f"estimated_duration: {formatting_utils.seconds_to_duration(estimated_duration.total_seconds())} "
            f"time_since_last_log: {formatting_utils.seconds_to_duration(seconds_since_last_log)} "
            f"time_per_update: {time_per_update}"
        )
        self._last_log_time = now
        self._last_log_samples = tpp.cur_eus.sample
