from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ksuit.core.schedules import Schedule, TrainingProgressSchedule

from .factory import Factory

if TYPE_CHECKING:
    from ksuit.core.providers import TrainingProgressProvider


class ScheduleFactory(Factory):
    @staticmethod
    def instantiate(
        config: Any | dict[str, Any] | None,
        *args,
        _recursive_: bool = False,
        updates_per_epoch: int | None = None,
        global_batch_size: int | None = None,
        training_progress_provider: TrainingProgressProvider | None = None,
        **kwargs,
    ) -> Any:
        """Converts attributes with suffixes "_epochs", "_updates" and "_samples" into attributes with suffix
        "_steps". This allows configuration of attributes (e.g., warmup_epochs) without exposing the
        epoch/update/samples abstraction to the schedule (Schedules only have "steps" and "total_steps", no epochs or
        samples). This conversion requires training_progress_provider for global_batch_size and updates_per_epoch.
        For example:
        - warmup_epochs will be converted into warmup_steps via updates_per_epoch
        - warmup_updates will be renamed to warmup_steps
        - warmup_samples will be converted into warmup_steps via global_batch_size
        """
        if config is None:
            return None
        # schedule was already instantiated
        if isinstance(config, Schedule):
            return config
        # only dict config is supported
        if not isinstance(config, dict):
            raise ValueError(
                f"{type(ScheduleFactory).__name__} expected dict config for instantiation, "
                f"got '{type(config).__name__}'"
            )

        # convert epoch suffixes
        epoch_kwarg_keys = {key for key in config.keys() if key.endswith("_epochs")}
        for epoch_kwarg_key in epoch_kwarg_keys:
            # setup updates_per_epoch
            if updates_per_epoch is None:
                updates_per_epoch = training_progress_provider.updates_per_epoch
            elif training_progress_provider is not None:
                assert updates_per_epoch == training_progress_provider.updates_per_epoch
            # convert
            value = config.pop(epoch_kwarg_key)
            new_key = f"{epoch_kwarg_key[:-len('_epochs')]}_steps"
            config[new_key] = value * updates_per_epoch

        # convert update suffixes
        update_kwarg_keys = {key for key in config.keys() if key.endswith("_updates")}
        for update_kwarg_key in update_kwarg_keys:
            value = config.pop(update_kwarg_key)
            new_key = f"{update_kwarg_key[:-len('_updates')]}_steps"
            config[new_key] = value

        # convert sample suffixes
        samples_kwarg_keys = {key for key in config.keys() if key.endswith("_samples")}
        for samples_kwarg_key in samples_kwarg_keys:
            # setup global_batch_size
            if global_batch_size is None:
                global_batch_size = training_progress_provider.global_batch_size
            elif training_progress_provider is not None:
                assert global_batch_size == training_progress_provider.global_batch_size
            # convert
            value = config.pop(samples_kwarg_key)
            new_key = f"{samples_kwarg_key[:-len('_samples')]}_steps"
            if value % global_batch_size != 0:
                raise ValueError(f"{samples_kwarg_key}={value} should be divisible by {global_batch_size=}")
            config[new_key] = value // global_batch_size

        schedule = Factory.instantiate(config, *args, _recursive_=_recursive_, **kwargs)
        if training_progress_provider is not None:
            schedule = TrainingProgressSchedule(
                schedule=schedule,
                training_progress_provider=training_progress_provider,
            )
        return schedule
