from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Self


class EpochUpdateSample:
    def __init__(self, epoch: int | None = None, update: int | None = None, sample: int | None = None):
        self.epoch = epoch
        self.update = update
        self.sample = sample

    @property
    def specified_properties_count(self) -> int:
        return sum([self.epoch is not None, self.update is not None, self.sample is not None])

    @property
    def is_fully_specified(self) -> bool:
        return self.specified_properties_count == 3

    @property
    def is_minimally_specified(self) -> bool:
        return self.specified_properties_count == 1

    def to_fully_specified(self, updates_per_epoch: int, global_batch_size: int) -> Self:
        if self.is_fully_specified:
            return EpochUpdateSample(self.epoch, self.update, self.sample)
        assert self.is_minimally_specified
        if self.update is not None:
            total_updates = self.update
        elif self.epoch is not None:
            total_updates = updates_per_epoch * self.epoch
        else:
            total_updates = int(self.sample / global_batch_size)
        return EpochUpdateSample(
            epoch=int(total_updates / updates_per_epoch),
            update=total_updates,
            sample=total_updates * global_batch_size,
        )

    def has_same_specified_properties(self, other: Self) -> bool:
        if (self.epoch is None) != (other.epoch is None):
            return False
        if (self.update is None) != (other.update is None):
            return False
        if (self.sample is None) != (other.sample is None):
            return False
        return True

    def __eq__(self, other: Self) -> bool:
        return self.epoch == other.epoch and self.update == other.update and self.sample == other.sample

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self.is_minimally_specified:
            if self.epoch is not None:
                return f"Epoch {self.epoch}"
            if self.update is not None:
                return f"Update {self.update}"
            if self.sample is not None:
                return f"Sample {self.sample}"
        return f"E{self.epoch}_U{self.update}_S{self.sample}"

    @staticmethod
    def from_eus_containing_string(eus_string: str) -> EpochUpdateSample:
        matches = re.findall("E(\\d*)_U(\\d*)_S(\\d*)", eus_string)
        assert len(matches) == 1
        epoch_str, update_str, sample_str = matches[0]
        return EpochUpdateSample(epoch=int(epoch_str), update=int(update_str), sample=int(sample_str))

    @staticmethod
    def contains_eus_string(source: str) -> bool:
        matches = re.findall("E\\d*_U\\d*_S\\d*", source)
        return len(matches) > 0


    def to_target_specification(self, target: EpochUpdateSample) -> Self:
        assert target.specified_properties_count <= self.specified_properties_count
        kwargs = {}
        if target.epoch is not None:
            kwargs["epoch"] = self.epoch
        if target.update is not None:
            kwargs["update"] = self.update
        if target.sample is not None:
            kwargs["sample"] = self.sample
        return EpochUpdateSample(**kwargs)

    def __iter__(self) -> Iterator[str | int]:
        # proxy for casting to dict
        # https://stackoverflow.com/questions/35282222/in-python-how-do-i-cast-a-class-object-to-a-dict
        if self.epoch is not None:
            yield "epoch", self.epoch
        if self.update is not None:
            yield "update", self.update
        if self.sample is not None:
            yield "sample", self.sample
