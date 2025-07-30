from typing import Any, Sequence

from torch import nn
from torch.utils.data import default_collate

from ksuit.core.callbacks import Callback
from ksuit.core.trackers import Tracker
from ksuit.core.trainers import Trainer
from ksuit.impl.callbacks.classification import OnlineAccuracyCallback
from ksuit.impl.loss_wrappers import ClassificationLossWrapper


class ImageClassificationTrainer(Trainer):
    def get_dataset_items(self) -> set[str] | None:
        return {"x", "y"}

    def get_trainer_callbacks(self) -> Sequence[Callback]:
        return [
            OnlineAccuracyCallback(
                verbose=False,
                every_n_epochs=self.track_every_n_epochs,
                every_n_updates=self.track_every_n_updates,
                every_n_samples=self.track_every_n_samples,
                data_provider=self.data_provider,
                distributed_provider=self.distributed_provider,
                tracker=self.tracker,
            ),
            OnlineAccuracyCallback(
                every_n_epochs=self.log_every_n_epochs,
                every_n_updates=self.log_every_n_updates,
                every_n_samples=self.log_every_n_samples,
                data_provider=self.data_provider,
                distributed_provider=self.distributed_provider,
                tracker=self.tracker,
            ),
        ]

    def get_model_ctor_kwargs(self) -> dict[str, Any]:
        dataset = self.data_provider.datasets[self.dataset_key]
        if not hasattr(dataset, "num_classes"):
            raise RuntimeError(f"{type(self).__name__} requires dataset with num_classes attribute")
        # load a single sample
        select_items_dataset = self.data_provider.get_dataset(key=self.dataset_key, items=self.get_dataset_items())
        samples = [select_items_dataset[0]]
        # collate single sample
        collator = self.data_provider.get_collator(self.collator_key)
        if collator is None:
            batch = default_collate(samples)
        else:
            batch = collator(samples, dataset=dataset)
        _, num_channels, height, width = batch["x"].shape
        return dict(num_channels=num_channels, resolution=(height, width), num_classes=dataset.num_classes)

    def apply_loss_wrapper(self, model: nn.Module) -> nn.Module:
        dataset = self.data_provider.datasets[self.dataset_key]
        return ClassificationLossWrapper(model, num_classes=dataset.num_classes)