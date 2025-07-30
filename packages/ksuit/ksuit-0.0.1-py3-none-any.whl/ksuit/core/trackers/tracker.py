from __future__ import annotations

import logging
import os
import platform
from typing import TYPE_CHECKING, Any, Literal, Self, Sequence, final

import numpy as np
import torch
import yaml

from ksuit.utils import config_utils, formatting_utils

if TYPE_CHECKING:
    from ksuit.core.providers import DistributedProvider, PathProvider, TrainingProgressProvider


class Tracker:
    def __init_subclass__(cls):
        if cls.initialize != Tracker.initialize:
            raise TypeError(f"{cls.__name__} must not override initialize, override _initialize instead.")
        if cls.flush != Tracker.flush:
            raise TypeError(f"{cls.__name__} must not override flush, override _flush instead.")

    def __init__(
        self,
        distributed_provider: DistributedProvider,
        path_provider: PathProvider,
        training_progress_provider: TrainingProgressProvider | None = None,
    ):
        self.logger = logging.getLogger(type(self).__name__)
        self.distributed_provider = distributed_provider
        self.path_provider = path_provider
        self.training_progress_provider = training_progress_provider

        self._summary = {}
        self._history = []
        self._cache = None
        self.key_to_summary = {}

    @final
    def initialize(
        self,
        config: dict[str, Any],
        run_id: str,
        run_name: str | None,
        device_type: str | None = None,
    ) -> Self:
        if not self.distributed_provider.is_rank0:
            return
        config = config_utils.replace_lists_with_dicts(config)
        config = dict(
            run_id=run_id,
            config=config,
        )
        if run_name is not None:
            config["name"] = run_name
        # add GPU-type
        if device_type is not None:
            if device_type == "cpu":
                config["device"] = "cpu"
            elif device_type == "cuda":
                config["device"] = torch.cuda.get_device_name(0)
            else:
                self.logger.warning(f"could not derive descriptive device name (e.g., GPU name) for {device_type=}")
        # add distributed setup
        config["dist/world_size"] = self.distributed_provider.world_size
        config["dist/data_parallel_size"] = self.distributed_provider.data_parallel_size
        config["dist/tensor_parallel_size"] = self.distributed_provider.tensor_parallel_size
        config["dist/sequence_parallel_size"] = self.distributed_provider.sequence_parallel_size
        # add hostname/jobid
        config["dist/hostname"] = platform.uname().node
        if "SLURM_JOB_ID" in os.environ:
            config["dist/jobid"] = os.environ["SLURM_JOB_ID"]
        # initialize tracker
        self._initialize(config=config, run_id=run_id)
        return self

    def _initialize(self, config: dict[str, Any], run_id: str) -> None:
        self.path_provider.tracker_output_uri.mkdir()
        with open(self.path_provider.tracker_output_uri / "config.yaml", "w") as f:
            yaml.safe_dump(config, f)

    def add_scalar(
        self,
        key: str,
        value: torch.Tensor | np.generic | int | float,
        logger: logging.Logger | None = None,
        format_str: str | None = "auto",
        summary: Literal["min", "max"] | None = None,
    ) -> None:
        # convert to primitive types
        if torch.is_tensor(value):
            if value.numel() != 1:
                raise ValueError(f"non-scalar tensor found {value.shape=}")
            value = value.item()
        if isinstance(value, np.generic):
            if not np.isscalar(value):
                raise ValueError(f"non-scalar numpy array found {value.shape=}")
            value = value.item()
        if not isinstance(value, int | float):
            raise TypeError("scalars should be int or float (either as primitive type or as tensor)")
        # log
        self._log(key, value, logger=logger, format_str=format_str)
        # track how to summarize
        if summary is not None:
            if key in self.key_to_summary:
                if self.key_to_summary[key] != summary:
                    raise ValueError(
                        f"scalar '{key}' should be summarized via '{summary}' but was previously "
                        f"registered to be summarized via '{self.key_to_summary[key]}'"
                    )
            else:
                self.key_to_summary[key] = summary

    def get_history_of_scalar(self, key: str) -> Sequence[int | float]:
        return [history_entry[key] for history_entry in self._history if key in history_entry]

    def _log(
        self,
        key: str,
        value: int | float,
        logger: logging.Logger | None = None,
        format_str: str | None = "auto",
    ):
        # check if training progressed
        if self._cache is not None:
            if self.training_progress_provider is None:
                raise RuntimeError(f"set training_progress_provider of tracker before logging stuff")
            if self.training_progress_provider.cur_eus.update != self._cache["update"]:
                self.flush()
        # populate epoch/update/sample on new update
        if self._cache is None:
            self._cache = dict(self.training_progress_provider.cur_eus)
        if key in self._cache:
            raise RuntimeError(f"can't log {key=} twice")
        self._cache[key] = value
        if logger is not None:
            if format_str == "auto":
                if isinstance(value, int):
                    value = str(value)
                elif isinstance(value, float):
                    value = formatting_utils.float_to_scientific_notation(
                        value=value,
                        max_precision=4,
                    )
                else:
                    value = str(value)
            elif format_str is not None:
                value = f"{value:{format_str}}"
            logger.info(f"{key}: {value}")

    @final
    def flush(self) -> None:
        if self._cache is None:
            return
        # check that every log is fully cached (i.e. no update is logged twice)
        if len(self._history) > 0:
            assert self._cache["update"] > self._history[-1]["update"]
        if self.distributed_provider.is_rank0:
            self._flush()
        # add to history
        self._history.append(self._cache)
        self._cache = None

    def _flush(self) -> None:
        """Tracker by default only logs to disk after training -> nothing to do in flush"""

    def set_summary(self, key: str, value: int | float) -> None:
        if not self.distributed_provider.is_rank0:
            return
        self._set_summary(key=key, value=value)

    def _set_summary(self, key: str, value: int | float) -> None:
        self._summary[key] = value

    def summarize(self):
        self.flush()
        for key, summary in self.key_to_summary.items():
            values = [history_item[key] for history_item in self._history if key in history_item]
            if summary == "min":
                self.set_summary(key=f"{key}/min", value=min(values))
            elif summary == "max":
                self.set_summary(key=f"{key}/max", value=max(values))
            else:
                raise NotImplementedError(f"invalid summary {summary}")

    def cleanup(self) -> None:
        if not self.distributed_provider.is_rank0:
            return
        self.flush()
        self._cleanup()

    def _cleanup(self) -> None:
        pass
