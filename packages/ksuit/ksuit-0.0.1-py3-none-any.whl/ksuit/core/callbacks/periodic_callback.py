from __future__ import annotations

import math
from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Callable, final

import torch
from torch.utils.data import DistributedSampler, SequentialSampler
from tqdm import tqdm

from ksuit.core.samplers import InterleavedSamplerConfig
from ksuit.utils import param_checking, tqdm_utils

from .callback import Callback

ForwardFnScalarResult = int | float | bool | torch.Tensor
ForwardFnResult = ForwardFnScalarResult | dict[ForwardFnScalarResult] | Sequence[ForwardFnScalarResult] | None
IterateOverDatasetResult = torch.Tensor | dict[torch.Tensor] | Sequence[torch.Tensor] | None

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class PeriodicCallback(Callback):
    def __init_subclass__(cls):
        if (
            cls._register_interleaved_sampler_config_with_key
            != PeriodicCallback._register_interleaved_sampler_config_with_key
        ):
            raise TypeError(
                f"{cls.__name__} must not override _register_interleaved_sampler_config_with_key, "
                f"override _register_interleaved_sampler_configs instead."
            )
        if cls.register_interleaved_sampler_configs != PeriodicCallback.register_interleaved_sampler_configs:
            raise TypeError(
                f"{cls.__name__} must not override register_interleaved_sampler_configs, "
                f"override _register_interleaved_sampler_configs instead."
            )

    def __init__(
        self,
        every_n_epochs: int | None = None,
        every_n_updates: int | None = None,
        every_n_samples: int | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not param_checking.exactly_one_non_none(every_n_epochs, every_n_updates, every_n_samples):
            raise ValueError
        self.every_n_epochs = every_n_epochs
        self.every_n_updates = every_n_updates
        self.every_n_samples = every_n_samples
        self._interleaved_sampler_configs = []
        self.__registered_interleaved_sampler_configs = False

    @staticmethod
    def compose_interleaved_sampler_configs(callbacks: Sequence[Callback], ctx: TrainingContext):
        configs = []
        for callback in callbacks:
            # only PeriodicCallbacks have interleaved sampler config
            if not isinstance(callback, PeriodicCallback):
                continue
            callback.register_interleaved_sampler_configs(ctx=ctx)
            if len(callback._interleaved_sampler_configs) > 1:
                raise NotImplementedError
            configs += callback._interleaved_sampler_configs
        return configs

    @final
    def register_interleaved_sampler_configs(self, ctx: TrainingContext):
        # check that this is the first call to register
        assert not self.__registered_interleaved_sampler_configs
        self._register_interleaved_sampler_configs(ctx=ctx)
        self.__registered_interleaved_sampler_configs = True

    def _register_interleaved_sampler_configs(self, ctx: TrainingContext) -> None:
        pass

    @final
    def _register_interleaved_sampler_config_with_key(
        self,
        dataset_key: str,
        items: set[str] | None = None,
        collator_key: str | None = None,
    ) -> int:
        dataset = self.data_provider.get_dataset(key=dataset_key, items=items)
        collator = self.data_provider.get_collator(key=collator_key)
        if len(dataset) == 0:
            raise RuntimeError(f"dataset is empty type={type(dataset).__name__} dataset={dataset}")
        if self.distributed_provider.has_data_parallel:
            sampler = DistributedSampler(dataset, shuffle=False)
        else:
            sampler = SequentialSampler(dataset)
        if len(self._interleaved_sampler_configs) > 0:
            raise NotImplementedError("registering multiple InterleavedSamplerConfigs not supported")
        self._interleaved_sampler_configs.append(
            InterleavedSamplerConfig(
                sampler=sampler,
                every_n_epochs=self.every_n_epochs,
                every_n_updates=self.every_n_updates,
                every_n_samples=self.every_n_samples,
                collator=collator,
            ),
        )

    def _should_invoke_after_epoch(self, epoch: int) -> bool:
        if self.every_n_epochs is not None:
            return epoch % self.every_n_epochs == 0
        return False

    def _should_invoke_after_update(self, update: int) -> bool:
        if self.every_n_updates is not None:
            return update % self.every_n_updates == 0
        return False

    def _should_invoke_after_sample(self, sample: int, global_batch_size: int) -> bool:
        if self.every_n_samples is not None:
            last_update_samples = sample - global_batch_size
            prev_invoke_step = int(last_update_samples / self.every_n_samples)
            cur_invoke_step = int(sample / self.every_n_samples)
            if cur_invoke_step > prev_invoke_step:
                return True
        return False

    def _on_epoch_end(self, ctx: TrainingContext) -> None:
        if self._should_invoke_after_epoch(ctx.trainer.training_progress_provider.cur_eus.epoch):
            self._invoke(ctx=ctx)

    def _on_update_end(self, ctx: TrainingContext) -> None:
        if self._should_invoke_after_update(ctx.trainer.training_progress_provider.cur_eus.update):
            self._invoke(ctx=ctx)
        if self._should_invoke_after_sample(
            sample=ctx.trainer.training_progress_provider.cur_eus.sample,
            global_batch_size=ctx.trainer.global_batch_size,
        ):
            self._invoke(ctx=ctx)

    @abstractmethod
    def _invoke(self, ctx: TrainingContext) -> None:
        """Hook that is periodically invoked from either `on_epoch_end` or `on_update_end` based on `every_n_epochs`,
        `every_n_updates` or `every_n_samples`.
        """

    @property
    def short_interval_string(self) -> str:
        if self.every_n_epochs is not None:
            return f"E{self.every_n_epochs}"
        if self.every_n_updates is not None:
            return f"U{self.every_n_updates}"
        if self.every_n_samples is not None:
            return f"S{self.every_n_samples}"
        raise RuntimeError

    @property
    def interval_type(self) -> str:
        if self.every_n_epochs is not None:
            return "epoch"
        if self.every_n_updates is not None:
            return "update"
        if self.every_n_samples is not None:
            return "sample"
        raise RuntimeError

    def _iterate_over_dataset(
        self,
        forward_fn: Callable[[dict[str, Any], TrainingContext], ForwardFnResult],
        ctx: TrainingContext,
    ) -> IterateOverDatasetResult:
        # extract config
        if len(self._interleaved_sampler_configs) > 1:
            raise NotImplementedError
        config = self._interleaved_sampler_configs[0]

        # create pbar_ctor
        if self.distributed_provider.is_interactive and self.distributed_provider.is_rank0:
            pbar_ctor = tqdm
        else:
            pbar_ctor = tqdm_utils.NoopTqdm

        # calculate results
        results = []
        local_dataset_len = len(config.sampler)
        num_batches = math.ceil(local_dataset_len / (config.batch_size or ctx.trainer.local_batch_size))
        for _ in pbar_ctor(iterable=range(num_batches)):
            # load data
            batch = next(ctx.interleaved_dataloader_iter)
            # forward
            result = forward_fn(batch, ctx)
            results.append(result)

        # retrieve global dataset length
        sampler = config.sampler
        if self.distributed_provider.has_data_parallel:
            if not isinstance(sampler, DistributedSampler):
                raise NotImplementedError(
                    f"expecting DistributedSampler if data_parallel is used but got {type(sampler).__name__}"
                )
            if sampler.shuffle or sampler.drop_last:
                raise NotImplementedError(
                    f"expecting DistributedSampler(shuffle=False, drop_last=False) but got "
                    f"{type(sampler).__name__}(shuffle={sampler.shuffle}, drop_last={sampler.drop_last})"
                )
            global_dataset_len = len(sampler.dataset)
        else:
            if not isinstance(sampler, SequentialSampler):
                raise NotImplementedError(f"expecting SequentialSampler but got {type(sampler).__name__}")
            global_dataset_len = len(sampler)

        # concatenate results
        results = self._concat_iterate_over_dataset_results(results=results, max_length=global_dataset_len)
        return results

    def _concat_iterate_over_dataset_results(
        self,
        results: list[ForwardFnResult],
        max_length: int,
    ) -> IterateOverDatasetResult:
        # the abstraction into _concat_iterate_over_dataset_results and its _impl method is necessary for
        # MultiMetricCallback such that if _concat_iterate_over_dataset_results is overriden the recursive
        # calls in the _impl method properly call the _impl method directly
        return self._concat_iterate_over_dataset_results_impl(
            results=results,
            max_length=max_length,
            allow_collection_type=True,
        )

    def _concat_iterate_over_dataset_results_impl(
        self,
        results: list[ForwardFnResult],
        max_length: int,
        allow_collection_type: bool,
    ) -> IterateOverDatasetResult:
        if results[0] is None:
            if not all(r is None for r in results):
                raise RuntimeError(f"mixed none and non-none values in iterate_over_dataset return values")
            return None
        # check collections (dict, tuple, lists)
        if isinstance(results[0], dict | Sequence):
            if not allow_collection_type:
                raise TypeError("forward_fn result concatenation is not supported with nested dict/list/tuple")
            if any(type(results[0]) is not type(result) for result in results):
                raise TypeError(
                    f"forward_fn produced variable types ({sorted({type(result).__name__ for result in results})}). "
                    f"Expecting the same type for all results."
                )
        # unpack dict
        if isinstance(results[0], dict):
            # check consistent keys
            if any(results[0].keys() != result.keys() for result in results):
                raise TypeError(
                    "forward_fn produced dict with variable keys. "
                    "Expecting the same keys for all results."
                )
            keys = list(results[0].keys())
            dict_results = {}
            for key in keys:
                key_results = [result[key] for result in results]
                dict_result = self._concat_iterate_over_dataset_results_impl(
                    results=key_results,
                    max_length=max_length,
                    allow_collection_type=False,
                )
                if len(dict_result) > max_length:
                    raise RuntimeError(
                        f"Error when removing padding of SequentialSampler in distributed eval. "
                        f"Concatenated result has len={len(dict_result)} but {max_length=}"
                    )
                dict_results[key] = dict_result
            return dict_results
        # unpack sequence
        if isinstance(results[0], Sequence):
            # check same length
            if any(len(results[0]) != len(result) for result in results):
                raise TypeError(
                    "forward_fn produced sequence with variable length. "
                    "Expecting the same length for all results."
                )
            sequence_results = []
            for i in range(len(results[0])):
                sequence_result = self._concat_iterate_over_dataset_results_impl(
                    results=[result[i] for result in results],
                    max_length=max_length,
                    allow_collection_type=False,
                )
                if len(sequence_result) > max_length:
                    raise RuntimeError(
                        f"Error when removing padding of SequentialSampler in distributed eval. "
                        f"Concatenated result has len={len(sequence_result)} but {max_length=}"
                    )
                sequence_results.append(sequence_result)
            return sequence_results

        # TODO support numpy arrays
        # convert scalars into tensors
        if not isinstance(results[0], int | float | bool | torch.Tensor):
            raise TypeError(
                "Result of forward_fn should be int, float, bool or torch.Tensor. "
                "It can also be a dictionary or tuple of these types."
            )
        if isinstance(results[0], int | float | bool):
            if any(type(results[0]) is not type(result) for result in results):
                raise TypeError(
                    f"forward_fn produced variable types ({sorted({type(result).__name__ for result in results})}). "
                    f"Expecting the same type for all results."
                )
            results = [torch.tensor(result) for result in results]
        # concatenate tensors
        if torch.is_tensor(results[0]):
            if any(results[0].dtype != result.dtype for result in results):
                raise TypeError(
                    f"forward_fn produced variable tensor.dtype ({sorted({result.dtype for result in results})}). "
                    f"Expecting the same dtype for all results."
                )
            if results[0].ndim == 0:
                concatenated = torch.stack(results)
            else:
                concatenated = torch.concat(results)
            gathered = self.distributed_provider.all_gather_distributed_eval(concatenated, max_length=max_length)
            if len(gathered) > max_length:
                raise RuntimeError(
                    f"Error when removing padding of SequentialSampler in distributed eval. "
                    f"Concatenated result has len={len(gathered)} but {max_length=}"
                )
            return gathered
        raise NotImplementedError(
            f"forward_fn of _iterate_over_dataset produced {type(results[0])} which has no defined "
            f"behavior of how to combine results of batches into a single concatenated result"
        )
