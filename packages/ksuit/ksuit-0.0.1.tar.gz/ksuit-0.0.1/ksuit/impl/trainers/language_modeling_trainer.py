from typing import Any

from torch import nn

from ksuit.core.trainers import Trainer
from ksuit.impl.loss_wrappers import LanguageModelingLossWrapper


class LanguageModelingTrainer(Trainer):
    def get_model_ctor_kwargs(self) -> dict[str, Any]:
        dataset = self.data_provider.datasets[self.dataset_key]
        return dict(vocabulary_size=dataset.vocabulary_size)

    def apply_loss_wrapper(self, model: nn.Module) -> nn.Module:
        return LanguageModelingLossWrapper(model)