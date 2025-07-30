from __future__ import annotations

import bisect
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

from torch.utils.data import ConcatDataset, DataLoader, Dataset

from ksuit.core.collators import Collator
from ksuit.utils import param_checking

if TYPE_CHECKING:
    from ksuit.core.schedules import Schedule


class SamplerLikeType(Protocol):
    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[int]: ...


@dataclass
class InterleavedSamplerConfig:
    sampler: SamplerLikeType
    every_n_epochs: int | None = None
    every_n_updates: int | None = None
    every_n_samples: int | None = None
    collator: Collator | None = None
    batch_size: int | None = None

    def __str__(self) -> str:
        strs = []
        if self.every_n_epochs is not None:
            strs.append(f"every_n_epochs={self.every_n_epochs}")
        if self.every_n_updates is not None:
            strs.append(f"every_n_updates={self.every_n_updates}")
        if self.every_n_samples is not None:
            strs.append(f"every_n_samples={self.every_n_samples}")
        if self.collator is not None:
            strs.append(f"collator={type(self.collator).__name__}")
        if self.batch_size is not None:
            strs.append(f"batch_size={self.batch_size}")
        return f"{type(self).__name__}({','.join(strs)})"


# can't be a local class as it is required to be pickleable
# AttributeError: Can't pickle local object 'InterleavedSampler.__init__.<locals>._InterleavedConcatDataset'
class _InterleavedConcatDataset(ConcatDataset):
    """`torch.utils.data.ConcatDataset` but it additionally returns the dataset index."""

    def __getitem__(self, idx: int) -> Any:
        if idx < 0:
            if -idx > len(self):
                raise ValueError("absolute value of index should not exceed dataset length")
            idx = len(self) + idx
        dataset_idx = bisect.bisect_right(self.cumulative_sizes, idx)
        if dataset_idx == 0:
            sample_idx = idx
        else:
            sample_idx = idx - self.cumulative_sizes[dataset_idx - 1]
        return dataset_idx, self.datasets[dataset_idx][sample_idx]


# can't be a local class as it is required to be pickleable
# AttributeError: Can't pickle local object 'InterleavedSampler.__init__.<locals>._InterleavedCollator'
class _InterleavedCollator:
    def __init__(self, collators: list[Collator], datasets: list[Dataset]):
        self.collators = collators
        self.datasets = datasets

    def __call__(self, samples_with_dataset_idx: list[tuple[int, dict[str, Any]]]) -> dict[str, Any]:
        dataset_idxs, samples = zip(*samples_with_dataset_idx)
        assert all(dataset_idxs[0] == idx for idx in dataset_idxs)
        return self.collators[dataset_idxs[0]](samples, dataset=self.datasets[dataset_idxs[0]])


class InterleavedSampler:
    def __init__(
        self,
        main_sampler: SamplerLikeType,
        batch_size: int,
        configs: list[InterleavedSamplerConfig] | None = None,
        # properties of main sampler
        drop_last: bool = True,
        main_collator: Collator = None,
        # duration of InterleavedSampler
        end_epoch: int | None = None,
        end_update: int | None = None,
        end_sample: int | None = None,
        start_epoch: int | None = None,
        start_update: int | None = None,
        start_sample: int | None = None,
        batch_size_schedule: Schedule | None = None,
    ):
        super().__init__()
        assert isinstance(batch_size, int) and batch_size >= 1
        assert batch_size <= len(main_sampler)
        assert end_epoch is None or (isinstance(end_epoch, int) and 0 <= end_epoch)
        assert end_update is None or (isinstance(end_update, int) and 0 <= end_update)
        assert end_sample is None or (isinstance(end_sample, int) and 0 <= end_sample)
        assert param_checking.exactly_one_non_none(end_epoch, end_update, end_sample)
        configs = configs or []
        for config in configs:
            assert param_checking.at_least_one_non_none(
                config.every_n_epochs,
                config.every_n_updates,
                config.every_n_samples,
            )
            assert config.every_n_epochs is None or 0 < config.every_n_epochs
            assert config.every_n_updates is None or 0 < config.every_n_updates
            assert config.every_n_samples is None or 0 < config.every_n_samples
            assert config.batch_size is None or 0 < config.batch_size

        # infer full start checkpoint from one of epoch/update/sample
        if start_epoch is not None:
            assert isinstance(start_epoch, int) and start_update is None and start_sample is None
            start_update = len(main_sampler) // batch_size * start_epoch
            start_sample = start_update * batch_size
        elif start_update is not None:
            assert start_epoch is None and isinstance(start_update, int) and start_sample is None
            start_epoch = int(start_update / (len(main_sampler) // batch_size))
            start_sample = start_update * batch_size
        elif start_sample is not None:
            assert start_epoch is None and start_update is None and isinstance(start_sample, int)
            assert start_sample % batch_size == 0
            start_update = start_sample // batch_size
            start_epoch = int(start_update / (len(main_sampler) // batch_size))
        else:
            start_epoch = start_update = start_sample = 0

        self.main_sampler = main_sampler
        self.drop_last = drop_last
        self.configs = configs
        self.batch_size = batch_size
        self.epochs = end_epoch
        self.updates = end_update
        self.samples = end_sample
        self.start_epoch = start_epoch
        self.start_update = start_update
        self.start_sample = start_sample

        def _get_data_source(sampler) -> Dataset:
            if hasattr(sampler, "data_source"):
                return sampler.data_source
            if hasattr(sampler, "dataset"):
                return sampler.dataset
            raise NotImplementedError

        self.index_offsets = [len(_get_data_source(self.main_sampler))]
        for config in self.configs[:-1]:
            self.index_offsets.append(self.index_offsets[-1] + len(_get_data_source(config.sampler)))

        datasets = (
            [_get_data_source(self.main_sampler)] +
            [_get_data_source(config.sampler) for config in self.configs]
        )
        collators = (
            [main_collator or Collator()] +
            [config.collator or Collator() for config in self.configs]
        )
        self.dataset = _InterleavedConcatDataset(datasets)
        self.collator = _InterleavedCollator(datasets=datasets, collators=collators)
        if batch_size_schedule is not None:
            # TODO cleaner solution
            assert self.start_epoch == 0
            assert self.start_update == 0
            assert self.start_sample == 0
            assert self.epochs is not None
            assert self.drop_last
            if len(self.main_sampler) < self.batch_size:
                self.batch_size = len(self.main_sampler)
            updates_per_epoch = len(self.main_sampler) // self.batch_size
            total_num_batches = updates_per_epoch * self.epochs
        else:
            total_num_batches = None
        self.batch_sampler = _InterleavedBatchSampler(
            self,
            batch_size_schedule=batch_size_schedule,
            total_num_batches=total_num_batches,
        )

    def get_data_loader(self, num_workers: int = 0, pin_memory: bool = True) -> DataLoader:
        return DataLoader(
            dataset=self.dataset,
            batch_sampler=self.batch_sampler,
            collate_fn=self.collator,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )

    def __iter__(self) -> Iterator[tuple[bool, int]]:
        if self.epochs == 0 or self.updates == 0 or self.samples == 0:
            assert self.start_epoch == 0 and self.start_update == 0 and self.start_sample == 0
            yield from self._eval_loop()
        else:
            yield from self._training_loop()

    def _eval_loop(self) -> Iterator[tuple[bool, int]]:
        for config_idx, config in enumerate(self.configs):
            index_offset = self.index_offsets[config_idx]
            sample_in_interleaved = 0
            interleaved_batch_size = config.batch_size or self.batch_size
            for interleaved_idx in config.sampler:
                sample_in_interleaved += 1
                if (
                    sample_in_interleaved % interleaved_batch_size == 0
                    or sample_in_interleaved == len(config.sampler)
                ):
                    yield True, False, index_offset + interleaved_idx
                else:
                    yield False, False, index_offset + interleaved_idx

    def _training_loop(self) -> Iterator[tuple[bool, int]]:
        if self.drop_last:
            if len(self.main_sampler) < self.batch_size:
                self.batch_size = len(self.main_sampler)
            batch_size = self.batch_size
            samples_per_epoch = len(self.main_sampler) // batch_size * batch_size
        else:
            samples_per_epoch = len(self.main_sampler)

        epoch = self.start_epoch
        update = self.start_update
        sample = self.start_sample
        sample_in_update = 0
        sample_at_last_update = 0
        while True:
            sample_in_epoch = 0
            if hasattr(self.main_sampler, "set_epoch"):
                self.main_sampler.set_epoch(epoch)
            for main_idx in self.main_sampler:
                sample += 1
                sample_in_epoch += 1
                sample_in_update += 1
                if sample_in_update == self.batch_size or sample_in_epoch == samples_per_epoch:
                    yield True, True, main_idx
                else:
                    yield False, True, main_idx
                # check if interleaved dataset has to be iterated (only possible after a update)
                # sample_in_update == self.batch_size -> full batch
                # if not drop_last -> last batch is not full but is also an update
                if sample_in_update == self.batch_size or sample_in_epoch == samples_per_epoch:
                    # keep track of what the sample counter was at the last update for every_n_sample checks
                    sample_in_update = 0
                    # increase counters
                    update += 1
                    if sample_in_epoch == samples_per_epoch:
                        epoch += 1

                    for config_idx, config in enumerate(self.configs):
                        # check if interleaved dataset has to be iterated
                        should_iter = False
                        if config.every_n_epochs is not None:
                            # can only occour at the end of an epoch
                            should_iter = sample_in_epoch == samples_per_epoch and epoch % config.every_n_epochs == 0
                        if config.every_n_updates is not None:
                            should_iter = update % config.every_n_updates == 0
                        if config.every_n_samples is not None:
                            if sample % config.every_n_samples == 0:
                                should_iter = True
                            elif sample_at_last_update // config.every_n_samples < sample // config.every_n_samples:
                                should_iter = True
                        if not should_iter:
                            continue
                        index_offset = self.index_offsets[config_idx]
                        interleaved_batch_size = config.batch_size or self.batch_size
                        sample_in_interleaved = 0
                        for interleaved_idx in config.sampler:
                            sample_in_interleaved += 1
                            if (
                                sample_in_interleaved % interleaved_batch_size == 0
                                or sample_in_interleaved == len(config.sampler)
                            ):
                                yield True, False, index_offset + interleaved_idx
                            else:
                                yield False, False, index_offset + interleaved_idx

                    sample_at_last_update = sample
                    # check if end is reached
                    if (
                        (self.epochs is not None and epoch == self.epochs)
                        or (self.updates is not None and update == self.updates)
                        or (self.samples is not None and sample >= self.samples)
                    ):
                        return
                    # if drop_last -> skip last non-full batch
                    if sample_in_epoch == samples_per_epoch:
                        break


# can't be a local class as it is required to be pickleable
# AttributeError: Can't pickle local object 'InterleavedSampler.__init__.<locals>._InterleavedBatchSampler'
class _InterleavedBatchSampler:
    def __init__(
        self,
        sampler: InterleavedSampler,
        batch_size_schedule: Schedule | None = None,
        total_num_batches: int | None = None,
    ):
        super().__init__()
        self.sampler = sampler
        self.batch_size_schedule = batch_size_schedule
        self.total_num_batches = total_num_batches
        self.counter = 0

    def __iter__(self) -> Iterator[list[int]]:
        idxs = []
        for is_full_batch, is_train_batch, idx in self.sampler:
            idxs.append(idx)
            if is_full_batch:
                if is_train_batch and self.batch_size_schedule is not None:
                    cur_batch_size = self.batch_size_schedule.evaluate(
                        step=self.counter,
                        total_steps=self.total_num_batches,
                    )
                    if not cur_batch_size.is_integer():
                        raise TypeError(
                            f"Batchsize schedule should return integer values (got {cur_batch_size}). "
                            "Use a schedule_postprocessor if necessary."
                        )
                    if cur_batch_size < 1:
                        raise RuntimeError("Batchsize schedule should return values >= 1.")
                    idxs = idxs[:int(cur_batch_size)]
                    self.counter += 1
                yield idxs
                idxs = []
        assert len(idxs) == 0
        if self.batch_size_schedule is not None:
            assert self.counter == self.total_num_batches
