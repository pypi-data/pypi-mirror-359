from __future__ import annotations

import logging
from abc import ABC
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Self

import torch
from torch import nn
from torch.amp import GradScaler
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import RandomSampler

from ksuit.core.callbacks import Callback, PeriodicCallback
from ksuit.core.factories import Factory, ScheduleFactory
from ksuit.core.loss_wrappers import LossWrapper
from ksuit.core.providers import TrainingProgressProvider
from ksuit.core.samplers import InterleavedSampler
from ksuit.utils import amp_utils, module_utils, param_checking
from ksuit.utils.distributed_sampler import DistributedSampler
from ksuit.utils.epoch_update_sample import EpochUpdateSample

from .training_context import TrainingContext

if TYPE_CHECKING:
    from ksuit.core.initializers import Initializer
    from ksuit.core.models import Model
    from ksuit.core.optim import Optimizer
    from ksuit.core.providers import DataProvider, DistributedProvider, NumWorkersProvider
    from ksuit.core.samplers import SamplerLikeType
    from ksuit.core.schedules import Schedule
    from ksuit.core.trackers import Tracker

class Trainer(ABC):
    @classmethod
    def get_testrun_trainer(cls, config: dict[str, Any], **kwargs) -> Self:
        config = dict(config)
        config["global_batch_size"] = min(config["global_batch_size"], 4)
        return Factory.create_object(config, expected_base_type=Trainer, **kwargs)

    def __init_subclass__(cls):
        if cls.fit != Trainer.fit:
            raise TypeError(f"{cls.__name__} must not override {cls.fit.__name__}, override _process instead.")

    def __init__(
        self,
        device: torch.device,
        end_epoch: int,
        global_batch_size: int,
        # providers
        data_provider: DataProvider,
        distributed_provider: DistributedProvider,
        #
        dataset_key: str = "train",
        precision: torch.dtype | str | int = "float32",
        batch_size_schedule: Schedule | None = None,
        # intervals
        log_every_n_epochs: int | None = None,
        log_every_n_updates: int | None = None,
        log_every_n_samples: int | None = None,
        track_every_n_epochs: int | None = None,
        track_every_n_updates: int | None = None,
        track_every_n_samples: int | None = None,
        # optional
        collator_key: str | None = None,
        num_workers: int | None = None,
        backup_precision: torch.dtype | str | int | None = None,
        num_workers_provider: NumWorkersProvider | None = None,
        training_progress_provider: TrainingProgressProvider | None = None,
        tracker: Tracker | None = None,
    ):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.device = device
        self.dataset_key = dataset_key
        self.end_epoch = end_epoch
        self.global_batch_size = global_batch_size
        self.data_provider = data_provider
        self.distributed_provider = distributed_provider
        # by default track every 50 updates
        if param_checking.all_none(track_every_n_epochs, track_every_n_updates, track_every_n_samples):
            track_every_n_updates = 50
        self.track_every_n_epochs = track_every_n_epochs
        self.track_every_n_updates = track_every_n_updates
        self.track_every_n_samples = track_every_n_samples

        self.collator_key = collator_key
        self.num_workers = num_workers
        self.num_workers_provider = num_workers_provider
        self.tracker = tracker

        # decide log interval
        if not param_checking.at_most_one_non_none(log_every_n_epochs, log_every_n_updates, log_every_n_samples):
            raise ValueError(
                f"multiple log intervals defined {log_every_n_epochs=} {log_every_n_updates=} {log_every_n_samples=}"
            )
        # if not defined -> default to every epoch
        if param_checking.all_none(log_every_n_epochs, log_every_n_updates, log_every_n_samples):
            log_every_n_epochs = 1
        self.log_every_n_epochs = log_every_n_epochs
        self.log_every_n_updates = log_every_n_updates
        self.log_every_n_samples = log_every_n_samples

        # check that train dataset is large enough to at least fit one update with the global_batch_size
        train_dataset = self.data_provider.datasets[dataset_key]
        if len(train_dataset) < self.global_batch_size:
            raise ValueError(f"{len(train_dataset)=} < global_batch_size={self.global_batch_size}")

        # initialize training_progress_provider
        self.training_progress_provider = training_progress_provider or TrainingProgressProvider(
            global_batch_size=self.global_batch_size,
            updates_per_epoch=len(train_dataset) // self.global_batch_size,
        )

        # local_batch_size
        if distributed_provider.has_data_parallel:
            data_parallel_size = distributed_provider.data_parallel_size
            if global_batch_size % data_parallel_size != 0:
                raise ValueError(
                    f"global_batch_size ({global_batch_size}) is not "
                    f"divisible by data_parallel_size ({data_parallel_size})"
                )
            self.local_batch_size = global_batch_size // data_parallel_size
        else:
            self.local_batch_size = global_batch_size
        self.logger.info(f"local_batch_size: {self.local_batch_size}")

        # derive precision
        precision = amp_utils.get_supported_precision(
            desired_precision=precision,
            device=self.device,
            backup_precision=backup_precision,
        )
        self.precision = precision
        # instantiate automatic mixed precision utilities
        self.autocast_context = amp_utils.get_autocast_context(precision=precision, device=self.device)
        self.grad_scaler = amp_utils.get_grad_scaler(precision=precision, device=self.device)

        # batch_size_schedule
        # (can't use training_progress_provider based scheduling because samplers operate asynchronous)
        self.batch_size_schedule = ScheduleFactory.create_object(
            batch_size_schedule,
            max_value=self.local_batch_size,
            updates_per_epoch=len(train_dataset) // self.global_batch_size,
            global_batch_size=self.global_batch_size,
        )

    @property
    def is_eval_run(self) -> bool:
        # TODO add other items
        return self.end_epoch == 0

    def get_dataset_items(self) -> set[str] | None:
        return None

    def get_trainer_callbacks(self) -> Sequence[Callback]:
        return []

    def apply_loss_wrapper(self, model: Model) -> nn.Module:
        return LossWrapper(model)

    # TODO FSDP/FSDP2 + check param layout of FSDP/FSDP2 does not interfer with exclude_from_wd
    # TODO check how FSDP interfers with clip_grad_norm
    def apply_dp_wrapper(self, model: nn.Module) -> nn.Module:
        # check for batchnorm
        if self.distributed_provider.has_data_parallel:
            if any(isinstance(m, nn.BatchNorm1d | nn.BatchNorm2d | nn.BatchNorm3d) for m in model.modules()):
                raise NotImplementedError("handling BatchNorm in data parallel not implemented")
        if self.distributed_provider.has_tensor_parallel:
            if any(isinstance(m, nn.BatchNorm1d | nn.BatchNorm2d | nn.BatchNorm3d) for m in model.modules()):
                raise NotImplementedError("handling BatchNorm in tensor parallel not implemented")
        if self.distributed_provider.has_sequence_parallel:
            if any(isinstance(m, nn.BatchNorm1d | nn.BatchNorm2d | nn.BatchNorm3d) for m in model.modules()):
                raise NotImplementedError("handling BatchNorm in sequence parallel not implemented")
        # wrap DDP
        if self.distributed_provider.has_data_parallel:
            # TODO maybe its better to force same initialization by using the same seed and then only later changing
            #   it for different ddp ranks; not sure how FSDP handles it; ddp can disable it with init_sync=False
            group = self.distributed_provider.get_group(mesh_dim_name="data")
            if module_utils.get_num_trainable_parameters(model) > 0:
                model = DistributedDataParallel(model, process_group=group)
            else:
                # DDP broadcasts weights from rank0 to other ranks but raises an error if no param requires grad
                # workaround: temporarily unfreeze one parameter if all parameters are frozen to broadcast weights
                self.logger.info("not wrapping into DDP (no trainable parameters) -> only broadcast parameters")
                first_param = next(model.parameters())
                first_param.requires_grad = True
                DistributedDataParallel(model, process_group=group)
                first_param.requires_grad = False
        return model

    def get_model_ctor_kwargs(self) -> dict[str, Any]:
        return {}

    def fit(
        self,
        model: Model,
        optimizer: Optimizer | torch.optim.Optimizer | None = None,
        initializers: Sequence[Initializer] | None = None,
        runner_callbacks: Sequence[Callback] | None = None,
        config_callbacks: Sequence[Callback] | None = None,
    ) -> None:
        # compose callbacks
        # - runner callbacks (e.g., DatasetStatsCallback to log sizes of datasets)
        # - trainer specific callbacks (e.g., OnlineAccuracyCallback for a classification task)
        # - callbacks defined in the model (e.g., UpdateOutputCallback with some internal state of the model)
        # - callbacks defined in the config (e.g., OfflineLossCallback)
        # - callbacks passed to Trainer.fit
        callbacks = (
            (list(runner_callbacks or []))
            + list(self.get_trainer_callbacks())
            + (list(config_callbacks or []))
        )
        self.logger.info("-----------------")
        self.logger.info("callbacks")
        for callback in callbacks:
            self.logger.info(f"- {callback}")
        # instantiate ctx 
        # (avoids having to pass many things around in methods or to other componens like callbacks)
        ctx = TrainingContext(
            trainer=self,
            model=model,
            loss_wrapped_model=model,
            dp_wrapped_model=model,
            optimizer=optimizer,
            callbacks=callbacks,
            local_batch_size=self.local_batch_size,
            global_batch_size=self.global_batch_size,
            state={},
        )

        # TODO not sure how initializing works with distributed tensors from FSDP
        for initializer in (initializers or []):
            initializer(ctx)

        # TODO initializers need to be applied before wrapping (e.g., because DDP syncs randomly initialized parameters
        #  on instantiation, not sure about FSDP or other DDP backends), so this is a bit of a hacky workaround
        model = model.to(self.device)
        loss_wrapped_model = self.apply_loss_wrapper(model)
        loss_wrapped_model = loss_wrapped_model.to(self.device)
        dp_wrapped_model = self.apply_dp_wrapper(loss_wrapped_model)
        ctx.loss_wrapped_model = loss_wrapped_model
        ctx.dp_wrapped_model = dp_wrapped_model

        # resume initializer already initializes training_progress_provider
        if not self.training_progress_provider.is_initialized:
            self.training_progress_provider.initialize(
                start_eus=EpochUpdateSample(epoch=0),
                end_eus=EpochUpdateSample(epoch=self.end_epoch),
            )

        # freeze model if no optimizer
        if optimizer is None:
            self.logger.info("no optimizer provided -> freezing model parameters")
            module_utils.freeze(loss_wrapped_model)

        # on_fit_start
        self._call_hook(hook_name="on_fit_start", ctx=ctx, log_hook_header=True)

        # self._fit
        model.train()
        self.logger.info("------------------")
        self.logger.info("Trainer._fit")
        self._fit(ctx)

        # on_fit_end
        model.eval()  # always put into eval to have consistent output state
        self._call_hook(hook_name="on_fit_end", ctx=ctx, log_hook_header=True)

    def _create_train_sampler(self) -> SamplerLikeType:
        train_dataset_items = self.get_dataset_items()
        train_dataset = self.data_provider.get_dataset(key=self.dataset_key, items=train_dataset_items)
        if self.distributed_provider.has_data_parallel:
            # ---
            # set seed such that varying the main seed via config also changes data sampling
            # if this would not be used the dataset would be shuffled always with seed=0
            # this makes it consistent with the non distributed setting where the global seed
            # influences the order of a RandomSampler
            # ---
            # using the same seed on all ranks is recommended but the generated seed will be
            # different per device because seed is set to seed + data_parallel_rank to avoid patterns
            # in stochatic processes during training (e.g., masking, dropout, stochastic depth, ...)
            seed = int(torch.empty((), dtype=torch.int64).random_().item())
            seed = self.distributed_provider.all_gather_nograd(seed)[0].item()
            return DistributedSampler(
                train_dataset,
                seed=seed,
                shuffle=True,
                drop_last=True,
            )
        return RandomSampler(train_dataset)

    def _fit(self, ctx: TrainingContext) -> None:
        train_collator = self.data_provider.get_collator(self.collator_key)
        interleaved_sampler_configs = PeriodicCallback.compose_interleaved_sampler_configs(ctx.callbacks, ctx=ctx)

        sampler = InterleavedSampler(
            main_sampler=self._create_train_sampler(),
            batch_size=self.local_batch_size,
            configs=interleaved_sampler_configs,
            main_collator=train_collator,
            end_epoch=self.end_epoch,
            batch_size_schedule=self.batch_size_schedule,
            # on resuming, one of these will be != 0
            start_epoch=self.training_progress_provider.start_eus_minspec.epoch,
            start_update=self.training_progress_provider.start_eus_minspec.update,
            start_sample=self.training_progress_provider.start_eus_minspec.sample,
        )
        # infere num_workers
        if self.num_workers is None:
            num_workers = self.num_workers_provider.num_cpus_per_device
        else:
            num_workers = self.num_workers
        interleaved_dataloader = sampler.get_data_loader(num_workers=num_workers)
        self.logger.info(f"initializing dataloader workers ({num_workers=})")
        interleaved_data_iter = iter(interleaved_dataloader)
        self.logger.info("initialized dataloader workers")
        ctx.interleaved_dataloader_iter = interleaved_data_iter

        while not self.training_progress_provider.is_finished:
            batch = next(interleaved_data_iter)
            self._call_hook(hook_name="on_update_start", ctx=ctx)
            batch = self.move_batch_to_device(batch=batch, ctx=ctx)
            loss = self.batch_to_loss(batch=batch, ctx=ctx)
            ctx.state["loss"] = loss
            # TODO check if model is frozen
            if ctx.optimizer is not None:
                self.grad_scaler.scale(loss).backward()
            self._call_hook(hook_name="on_after_backward", ctx=ctx)
            # TODO gradient accumulation
            self._call_hook(hook_name="on_before_optimizer_step", ctx=ctx)
            if ctx.optimizer is not None:
                ctx.optimizer.step(self.grad_scaler)
            self._call_hook(hook_name="on_before_zero_grad", ctx=ctx)
            if ctx.optimizer is not None:
                ctx.optimizer.zero_grad()

            # update progress
            self.training_progress_provider.increase_progress()
            self._call_hook(hook_name="on_update_end", ctx=ctx)

            # after progress update hooks
            if self.training_progress_provider.is_full_epoch:
                # on epoch end
                self._call_hook(hook_name="on_epoch_end", ctx=ctx)
            # remove state
            ctx.state = {}
        try:
            next(interleaved_data_iter)
            raise RuntimeError("data_iter (iterator of InterleavedSampler dataloading) was not fully consumed")
        except StopIteration:
            pass

    def batch_to_loss(self, batch: dict[str, Any], ctx: TrainingContext) -> torch.Tensor:
        with self.autocast_context:
            loss = ctx.dp_wrapped_model(batch=batch, ctx=ctx)
        return loss

    def _call_hook(self, hook_name: str, ctx: TrainingContext, log_hook_header: bool = False):
        if log_hook_header:
            if Callback.at_least_one_override_for_hook(callbacks=ctx.callbacks, hook_name=hook_name):
                self.logger.info("------------------")
                self.logger.info(f"Callback.{hook_name}")
        ctx.model.eval()
        getattr(ctx.model, hook_name)(ctx=ctx)
        for callback in ctx.callbacks:
            getattr(callback, hook_name)(ctx=ctx)
        ctx.model.train()

    @staticmethod
    def _item_to_device(value: Any, ctx: TrainingContext) -> Any:
        """Moves a `value` to the device of the model (`ctx.model`). By default the following data structures are
        supported:
        - torch.Tensor: tensor is moved to the device
        - list[torch.Tensor]: all tensors are moved to the device
        - dict[Any, torch.Tensor]: All values are moved to the device, keys are untouched.
        - Any: kept as-is
        """
        # tensors
        if torch.is_tensor(value):
            return value.to(ctx.model.device, non_blocking=True)
        # list[torch.Tensor]
        if isinstance(value, list) and all(torch.is_tensor(item) for item in value):
            return [item.to(ctx.model.device, non_blocking=True) for item in value]
        # dict[Any, torch.Tensor]
        if isinstance(value, dict) and all(torch.is_tensor(item) for item in value.values()):
            return {key: item.to(ctx.model.device, non_blocking=True) for key, item in value.values()}
        return value

    def move_batch_to_device(self, batch: dict[str, Any], ctx: TrainingContext) -> dict[str, Any]:
        """Moves a full batch to the device of the model using `Trainer._item_to_device`."""
        return {key: self._item_to_device(value=value, ctx=ctx) for key, value in batch.items()}

    def state_dict(self) -> dict[str, Any]:
        state_dict = dict(
            epoch=self.training_progress_provider.cur_eus.epoch,
            update=self.training_progress_provider.cur_eus.update,
            sample=self.training_progress_provider.cur_eus.sample,
        )
        if isinstance(self.grad_scaler, GradScaler):
            state_dict["grad_scaler"] = self.grad_scaler.state_dict()
        return state_dict

    def load_state_dict(self, state_dict: dict[str, Any]) -> None:
        # load grad_scaler
        grad_scaler_state_dict = state_dict.get("grad_scaler", None)
        if isinstance(self.grad_scaler, GradScaler):
            if grad_scaler_state_dict is None:
                self.logger.warning(
                    f"trainer checkpoint has no grad_scaler but current trainer uses {self.precision} precision "
                    f"-> no grad_scaler state is loaded"
                )
            else:
                self.grad_scaler.load_state_dict(grad_scaler_state_dict)
