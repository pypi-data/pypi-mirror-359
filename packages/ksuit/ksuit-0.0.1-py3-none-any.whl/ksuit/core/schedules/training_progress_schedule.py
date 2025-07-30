from __future__ import annotations

from typing import TYPE_CHECKING

from .schedule import Schedule

if TYPE_CHECKING:
    from ksuit.core.providers import TrainingProgressProvider


class TrainingProgressSchedule(Schedule):
    def __init__(
        self,
        schedule: Schedule,
        training_progress_provider: TrainingProgressProvider,
        raise_on_reuse: bool = True,
    ):
        super().__init__()
        self.schedule = schedule
        self.training_progress_provider = training_progress_provider
        self.raise_on_reuse = raise_on_reuse
        self._prev_step = -1

    def evaluate(self, step: int | None = None, total_steps: int | None = None) -> float:
        """Evaluates a schedule based on the current training progress as provided by `training_progress_provider`.
        If `step` or `total_steps` are passed, they need to match the `training_progress_provider` state.
        """
        if step is not None:
            assert step == self.training_progress_provider.cur_eus.update
        if total_steps is not None:
            assert total_steps == self.training_progress_provider.end_eus.update

        # check if evaluate was called twice with the same step and raise an error to make
        # sure the user did not mistakenly forget to the training_progress_provider
        if self.raise_on_reuse:
            if self._prev_step >= self.training_progress_provider.cur_eus.update:
                raise RuntimeError(
                    f"{type(self).__name__} was previously called with step={self._prev_step} and is now called with "
                    f"{self.training_progress_provider.cur_eus.update}. If this is expected, set raise_on_reuse to "
                    f"False. If this is not expected, you probably forgot to update the state of the "
                    f"training_progress_provider or are updating the wrong {TrainingProgressProvider.__name__} object."
                )

        # evaluate
        return super().evaluate(
            step=self.training_progress_provider.cur_eus.update,
            total_steps=self.training_progress_provider.end_eus.update,
        )

    def _evaluate(self, step: int, total_steps: int | None) -> float:
        return self.schedule.evaluate(step=step, total_steps=total_steps)
