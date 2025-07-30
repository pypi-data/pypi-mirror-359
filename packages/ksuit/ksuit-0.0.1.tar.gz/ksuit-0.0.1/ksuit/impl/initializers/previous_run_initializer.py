import os
from typing import Any

import torch
from torch import nn

from ksuit.core.checkpoint_converters import CheckpointConverter
from ksuit.core.factories import Factory
from ksuit.core.initializers import Initializer
from ksuit.core.trainers import TrainingContext
from ksuit.utils.epoch_update_sample import EpochUpdateSample


class PreviousRunInitializer(Initializer):
    def __init__(
        self,
        run_id: str,
        checkpoint: EpochUpdateSample | str,
        checkpoint_converter: str | CheckpointConverter | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.run_id = run_id
        self.checkpoint = Factory.create_object(checkpoint)
        self.checkpoint_converter = Factory.create_object(checkpoint_converter)
        if isinstance(self.checkpoint, EpochUpdateSample):
            assert self.checkpoint.is_minimally_specified or self.checkpoint.is_fully_specified

    def _load_checkpoint(self) -> dict[str, Any]:
        checkpoint_uri = self.path_provider.get_checkpoint_uri(self.run_id)
        checkpoint_fnames = [fname for fname in os.listdir(checkpoint_uri) if fname.endswith("model.th")]
        if len(checkpoint_fnames) == 1:
            checkpiont_fname = checkpoint_fnames[0]
        else:
            # TODO
            raise NotImplementedError
        model_checkpoint_uri = checkpoint_uri / checkpiont_fname
        checkpoint = torch.load(model_checkpoint_uri, map_location="cpu", weights_only=True)
        return checkpoint

    def get_initializer_context(self) -> dict[str, Any]:
        checkpoint = self._load_checkpoint()
        # dont put tensors into initializer_context
        checkpoint = {key: value for key, value in checkpoint.items() if key != "state_dict"}
        return checkpoint

    def __call__(self, ctx: TrainingContext) -> None:
        checkpoint = self._load_checkpoint()
        state_dict = checkpoint["state_dict"]
        if self.checkpoint_converter is None:
            pass
        elif isinstance(self.checkpoint_converter, CheckpointConverter):
            state_dict = self.checkpoint_converter(state_dict)
        elif isinstance(self.checkpoint_converter, str):
            checkpoint_converters = checkpoint["checkpoint_converters"]
            if self.checkpoint_converter not in checkpoint_converters:
                raise KeyError(
                    f"Checkpoint does not define a checkpoint_converter for key '{self.checkpoint_converter}'. "
                    f"Use one of the checkpoint converters stored in the checkpoint "
                    f"({list(checkpoint_converters.keys())}) or define a custom one."
                )
            checkpoint_converter = Factory.create_object(
                checkpoint_converters[self.checkpoint_converter],
                expected_base_type=CheckpointConverter,
            )
            state_dict = checkpoint_converter(state_dict)
        else:
            raise NotImplementedError
        ctx.model.load_state_dict(state_dict)
