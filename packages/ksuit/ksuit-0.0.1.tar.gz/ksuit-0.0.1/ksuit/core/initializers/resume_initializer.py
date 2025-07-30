import os
from typing import Any

import torch
from torch import nn

from ksuit.core.checkpoint_converters import CheckpointConverter
from ksuit.core.factories import Factory
from ksuit.core.initializers import Initializer
from ksuit.core.trainers import TrainingContext
from ksuit.utils.epoch_update_sample import EpochUpdateSample


class ResumeInitializer(Initializer):
    def __init__(self, run_id: str, checkpoint: str | EpochUpdateSample = "latest", **kwargs):
        super().__init__(**kwargs)
        self.run_id = run_id
        self.checkpoint = Factory.create_object(checkpoint)
        if isinstance(self.checkpoint, EpochUpdateSample):
            assert self.checkpoint.is_minimally_specified

    def __call__(self, ctx: TrainingContext) -> None:
        checkpoint_uri = self.path_provider.get_checkpoint_uri(self.run_id)
        weight_fnames = [fname for fname in os.listdir(checkpoint_uri) if fname.endswith("model.th")]

        if isinstance(self.checkpoint, str):
            valid_weight_fnames = [fname for fname in weight_fnames if f" cp={self.checkpoint} " in fname]
            if len(valid_weight_fnames) != 1:
                raise RuntimeError(
                    f"Model state for checkpoint {self.checkpoint} not found in {checkpoint_uri.as_posix()}. "
                    f"Did you mean one of {weight_fnames}?"
                )
            valid_weight_fname = valid_weight_fnames[0]
        elif isinstance(self.checkpoint, EpochUpdateSample):
            # find matching filename
            valid_weight_fname = None
            for fname in weight_fnames:
                # check if it contains E1_U2_S8-like string
                if not EpochUpdateSample.contains_eus_string(fname):
                    continue
                # extract EpochUpdateSample from potential fnames
                eus_from_fname = EpochUpdateSample.from_eus_containing_string(fname)
                # remove unnecesary properties for comparison
                # (e.g. EpochUpdateSample(epoch=5, update=12, samples=123) --> EpochUpdateSample(epoch=5))
                eus_from_fname_minspec = eus_from_fname.to_target_specification(self.checkpoint)
                # check if fname is the desired checkpoint
                if eus_from_fname_minspec == self.checkpoint:
                    if valid_weight_fname is None:
                        valid_weight_fname = fname
                    else:
                        raise RuntimeError(
                            f"multiple valid checkpoint for {self.checkpoint} found "
                            f"({valid_weight_fname} is valid and {fname} is valid)"
                        )
            if valid_weight_fname is None:
                raise RuntimeError(f"no valid checkpoint for {self.checkpoint} found ({weight_fnames})")
        else:
            raise NotImplementedError
        # load model
        model_checkpoint = torch.load(checkpoint_uri / valid_weight_fname, map_location="cpu", weights_only=True)
        ctx.model.load_state_dict(model_checkpoint["state_dict"])

        # load optim + grad_scaler
        if ctx.optimizer is not None:
            valid_optim_fname = valid_weight_fname[:-len("model.th")] + "optim.th"
            if not (checkpoint_uri / valid_optim_fname).exists():
                raise RuntimeError(
                    f"{checkpoint_uri} contains valid weight checkpoint ({valid_weight_fname}) "
                    f"but no valid optim checkpoint ({valid_optim_fname})"
                )
            optim_checkpoint = torch.load(checkpoint_uri / valid_optim_fname, map_location="cpu", weights_only=True)
            ctx.optimizer.load_state_dict(optim_checkpoint["optimizer"])
            # load gradscaler if it was used
            # (e.g., when switching from fp32 to fp16 on resume, grad_scaler will have a new state)
            grad_scaler_state_dict = optim_checkpoint["grad_scaler"]
            if len(grad_scaler_state_dict) > 0:
                ctx.trainer.grad_scaler.load_state_dict(grad_scaler_state_dict)

        # TODO end_eus should include update/sample based end_checkpoints once they are implemented in trainer
        # set trainer checkpoint
        train_dataset = ctx.trainer.data_provider.datasets[ctx.trainer.dataset_key]

        ctx.trainer.training_progress_provider.initialize(
            start_eus=EpochUpdateSample(**model_checkpoint["eus_minspec"]),
            end_eus=EpochUpdateSample(epoch=ctx.trainer.end_epoch),
            global_batch_size=ctx.trainer.global_batch_size,
            updates_per_epoch=len(train_dataset) // ctx.trainer.global_batch_size,
        )

        # initialize callbacks
        for callback in ctx.callbacks:
            callback.on_resume(ctx=ctx, resume_initializer=self)