from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np

from ksuit.core.callbacks import PeriodicCallback
from ksuit.utils import formatting_utils

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class PrintUpdateProgressCallback(PeriodicCallback):
    class LoggerWasCalledHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.was_called = False

        def emit(self, _):
            self.was_called = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_since_last_log = 0.
        self.handler = self.LoggerWasCalledHandler()
        self.epoch_format = None
        self.update_format = None
        self._start_time = None

    def _on_fit_start(self, ctx: TrainingContext) -> None:
        if self.distributed_provider is not None and not self.distributed_provider.is_rank0:
            raise RuntimeError(f"{type(self).__name__} should only be running on rank0 process")
        train_progress_provider = ctx.trainer.training_progress_provider
        self.epoch_format = f"{int(np.log10(max(1, train_progress_provider.end_eus.epoch))) + 1}d"
        self.update_format = f"{int(np.log10(train_progress_provider.end_eus.update)) + 1}d"
        self.every_n_epochs_format = f"{int(np.log10(self.every_n_epochs)) + 1}d" if self.every_n_epochs else None
        self.every_n_updates_format = f"{int(np.log10(self.every_n_updates)) + 1}d" if self.every_n_updates else None

        if self.every_n_epochs:
            self.updates_per_log_interval_format = f"{int(np.log10(train_progress_provider.updates_per_epoch)) + 1}d"
        elif self.every_n_updates:
            self.updates_per_log_interval_format = self.every_n_updates_format
        elif self.every_n_samples:
            self.updates_per_every_n_samples = np.ceil(self.every_n_samples / self.trainer.global_batch_size)
            self.updates_per_log_interval_format = f"{int(np.log10(self.updates_per_every_n_samples)) + 1}d"
        else:
            self.updates_per_log_interval_format = None
        self._start_time = datetime.now()

    def _on_update_end(self, ctx: TrainingContext) -> None:
        tpp = ctx.trainer.training_progress_provider
        cur_epoch = tpp.cur_eus.epoch
        cur_update = tpp.cur_eus.update
        cur_sample = tpp.cur_eus.sample

        # reset time_since_last_log on new log interval
        if self._should_invoke_after_epoch(tpp.cur_eus.epoch) and tpp.is_full_epoch:
            self.time_since_last_log = 0.
        if self._should_invoke_after_update(tpp.cur_eus.update):
            self.time_since_last_log = 0.
        if self._should_invoke_after_sample(tpp.cur_eus.sample, tpp.global_batch_size):
            self.time_since_last_log = 0.

        if self.every_n_epochs:
            last_epoch = self.every_n_epochs * (cur_epoch // self.every_n_epochs)
            updates_at_last_log = last_epoch * tpp.updates_per_epoch
            updates_since_last_log = cur_update - updates_at_last_log
            updates_per_log_interval = self.every_n_epochs * tpp.updates_per_epoch
        elif self.every_n_updates:
            updates_since_last_log = cur_update % self.every_n_updates
            updates_per_log_interval = self.every_n_updates
        elif self.every_n_samples:
            samples_since_last_log = cur_sample % self.every_n_samples
            samples_at_last_log = cur_sample - samples_since_last_log
            updates_at_last_log = samples_at_last_log // tpp.effective_batch_size
            superflous_samples_at_last_log = samples_at_last_log % tpp.effective_batch_size
            updates_since_last_log = cur_update - updates_at_last_log
            samples_for_cur_log_interval = self.every_n_samples - superflous_samples_at_last_log
            updates_per_log_interval = int(
                np.ceil(samples_for_cur_log_interval / tpp.effective_batch_size)
            )
        else:
            updates_since_last_log = None
            updates_per_log_interval = None

        logstr = (
            f"E {format(cur_epoch, self.epoch_format)}/{tpp.end_eus.epoch} "
            f"U {format(cur_update, self.update_format)}/{tpp.end_eus.update} "
            f"S {formatting_utils.int_to_si_string(cur_sample):>6}/"
            f"{formatting_utils.int_to_si_string(tpp.end_eus.sample)} | "
        )
        # log interval ETA
        if self.updates_per_log_interval_format is not None:
            logstr += (
                f"next_log {format(updates_since_last_log, self.updates_per_log_interval_format)}/"
                f"{format(updates_per_log_interval, self.updates_per_log_interval_format)}"
            )
        if self.handler.was_called:
            print(logstr)
            self.handler.was_called = False
        else:
            print(logstr, end="\r")

    def _invoke(self, ctx: TrainingContext) -> None:
        print()

    def _on_fit_end(self, ctx: TrainingContext) -> None:
        logging.getLogger().removeHandler(self.handler)
