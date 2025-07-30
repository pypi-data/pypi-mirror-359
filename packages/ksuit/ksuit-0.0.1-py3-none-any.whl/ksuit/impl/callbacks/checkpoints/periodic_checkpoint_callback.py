import torch
from torch.nn.parallel import DistributedDataParallel

from ksuit.core.callbacks import PeriodicCallback
from ksuit.core.trainers import TrainingContext


class PeriodicCheckpointCallback(PeriodicCallback):
    def __init__(self, save_weights: bool = True, save_optim: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.save_weights = save_weights
        self.save_optim = save_optim

    def _on_fit_start(self, ctx: TrainingContext) -> None:
        self.path_provider.checkpoint_uri.mkdir(exist_ok=True)

    def _invoke(self, ctx: TrainingContext) -> None:
        if self.distributed_provider.has_tensor_parallel:
            # TODO requires prefix for storing+loading or gathering
            raise NotImplementedError
        if self.distributed_provider.has_data_parallel:
            if not isinstance(ctx.dp_wrapped_model, DistributedDataParallel):
                raise NotImplementedError("FSDP checkpoint storing not handled")
        # TODO this should be something like sequence_rank0 and data_rank0
        if not self.distributed_provider.store_on_rank:
            self.distributed_provider.barrier()
            return

        if self.save_weights:
            model_checkpoint = ctx.model.to_checkpoint(
                checkpoint="latest",
                eus=ctx.trainer.training_progress_provider.cur_eus,
                run_id=self.path_provider.run_id,
                interval_type=self.interval_type,
            )
            model_checkpoint_uri = self.path_provider.checkpoint_uri / f"{type(ctx.model).__name__} cp=latest model.th"
            torch.save(model_checkpoint, model_checkpoint_uri)
            self.logger.info(f"stored weights to {model_checkpoint_uri.as_posix()}")
        if self.save_optim:
            optim_checkpoint_uri = self.path_provider.checkpoint_uri / f"{type(ctx.model).__name__} cp=latest optim.th"
            torch.save(
                dict(
                    optimizer=ctx.optimizer.state_dict(),
                    grad_scaler=ctx.trainer.grad_scaler.state_dict(),
                ),
                optim_checkpoint_uri,
            )
            self.logger.info(f"stored optimizer to {optim_checkpoint_uri.as_posix()}")

        self.distributed_provider.barrier()
