from typing import Self

from ksuit.utils.epoch_update_sample import EpochUpdateSample


class TrainingProgressProvider:
    def __init__(self, updates_per_epoch: int, global_batch_size: int):
        self.updates_per_epoch = updates_per_epoch
        self.global_batch_size = global_batch_size
        # delayed initialization to pass TrainingProgressProvider already to tracker initialization
        # without actually having details about the training duration/state (which is set in trainer)
        self.__start_eus: EpochUpdateSample | None = None
        self.__start_eus_minspec: EpochUpdateSample | None = None
        self.__end_eus: EpochUpdateSample | None = None
        self.__cur_eus: EpochUpdateSample | None = None

    @property
    def is_initialized(self) -> bool:
        return self.__start_eus is not None

    @property
    def start_eus(self) -> EpochUpdateSample:
        if self.__start_eus is None:
            raise RuntimeError(f"call {type(self).__name__}.initialize before usage")
        return self.__start_eus

    @property
    def start_eus_minspec(self) -> EpochUpdateSample:
        if self.__start_eus_minspec is None:
            raise RuntimeError(f"call {type(self).__name__}.initialize before usage")
        return self.__start_eus_minspec

    @property
    def end_eus(self) -> EpochUpdateSample:
        if self.__end_eus is None:
            raise RuntimeError(f"call {type(self).__name__}.initialize before usage")
        return self.__end_eus

    @property
    def cur_eus(self) -> EpochUpdateSample:
        if self.__cur_eus is None:
            raise RuntimeError(f"call {type(self).__name__}.initialize before usage")
        return self.__cur_eus

    def initialize(
        self,
        start_eus: EpochUpdateSample,
        end_eus: EpochUpdateSample,
    ) -> Self:
        if self.is_initialized:
            raise RuntimeError(f"{type(self).__name__} was already initialized")

        # start_eus should be minimally specified to derive other initial values from updates_per_epoch and
        # global_batch_size. This is relevant if a run is resumed with different global_batch_size or
        # updates_per_epoch (i.e., train dataset size) and makes epoch/update/samples consistent with the
        # current run instead of the previous run
        assert start_eus.is_minimally_specified
        self.__start_eus_minspec = start_eus
        self.__start_eus = start_eus.to_fully_specified(
            updates_per_epoch=self.updates_per_epoch,
            global_batch_size=self.global_batch_size,
        )
        # fully specify end_eus
        assert end_eus.is_minimally_specified
        self.__end_eus = end_eus.to_fully_specified(
            updates_per_epoch=self.updates_per_epoch,
            global_batch_size=self.global_batch_size,
        )
        # initialize cur_eus
        self.__cur_eus = EpochUpdateSample(
            epoch=self.start_eus.epoch,
            update=self.start_eus.update,
            sample=self.start_eus.sample,
        )
        return self

    @property
    def is_full_epoch(self) -> bool:
        assert self.cur_eus.is_fully_specified
        return self.update % self.updates_per_epoch == 0

    @property
    def epoch(self) -> int:
        return self.cur_eus.epoch

    @property
    def update(self) -> int:
        return self.cur_eus.update

    @property
    def sample(self) -> int:
        return self.cur_eus.sample

    @property
    def is_finished(self) -> bool:
        return self.cur_eus == self.end_eus

    def increase_progress(self) -> None:
        self.cur_eus.update += 1
        self.cur_eus.sample += self.global_batch_size
        if self.cur_eus.update % self.updates_per_epoch == 0:
            self.cur_eus.epoch += 1
