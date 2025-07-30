from pathlib import Path
from typing import Any

import torch
import yaml
from torch import distributed
from torch.distributed.tensor.parallel import parallelize_module
from wandb.util import generate_id

from ksuit.core.callbacks import Callback
from ksuit.core.collators import Collator
from ksuit.core.datasets import Dataset
from ksuit.core.factories import Factory, OptimizerFactory
from ksuit.core.initializers import Initializer
from ksuit.core.models import Model
from ksuit.core.providers import (
    DataProvider,
    DistributedProvider,
    NumWorkersProvider,
    PathProvider,
    TrainingProgressProvider,
)
from ksuit.core.runners import Runner
from ksuit.core.trackers import Tracker
from ksuit.core.trainers import Trainer
from ksuit.impl.callbacks.generic import (
    DatasetStatsCallback,
    LogProgressCallback,
    LogUtilizationCallback,
    ModelInitializationCallback,
    ModelParameterCountCallback,
    OptimizerMetricsCallback,
    OptimizerScheduleCallback,
    PrintUpdateProgressCallback,
    UnusedModelParametersCallback,
)
from ksuit.impl.callbacks.loss import OnlineLossCallback
from ksuit.impl.providers import DistributedProviderProcessGroup
from ksuit.utils import config_utils, device_utils, logging_utils, reflection_utils, seed_utils, system_utils
from ksuit.core.initializers import ResumeInitializer


class DefaultRunner(Runner):
    def __init__(self, config: dict[str, Any], apply_config_overwrites: bool = True):
        super().__init__()
        self.config = config
        self.apply_config_overwrites = apply_config_overwrites

    def run(self) -> Tracker:
        config = dict(self.config)

        # remove vars (utility to structure configs)
        config.pop("vars", None)
        config_without_overwrites = dict(config)

        # add cli overrides to name (e.g., for wandb run name)
        if "config_overrides" in config:
            config_override_name = "--"
            for config_override in config["config_overrides"]:
                if "=" in config_override:
                    config_override_name += config_override.replace("+", "")
                elif "~" in config_override:
                    config_override_name += config_override
                else:
                    self.logger.warning(
                        f"override {config_override} has logic for appending to name -> not included into name",
                    )
            if len(config_override_name) > 2:
                config["name"] += config_override_name

        # overwrite parts of config
        if self.apply_config_overwrites:
            config_overwrites_uri = Path("config_overwrites.yaml")
            if config_overwrites_uri.exists():
                with open(config_overwrites_uri) as f:
                    config_overwrites = yaml.safe_load(f)
                # fully delete keys (e.g., tracker for debugging)
                for key in config_overwrites.pop("keys_to_delete", []):
                    if config_utils.has_path(config=config, path=key):
                        config_utils.delete_by_path(config=config, path=key)
                force_overwrite = config_overwrites.pop("force_overwrite", {})
                # check that force_overwrite keys match the actually specified keys
                for key in force_overwrite.keys():
                    if key not in config_overwrites:
                        raise ValueError(
                            f"specified key '{key}' in force_overwrites of config_overwrites.yaml without "
                            f"corresponding key (specified keys={set(config_overwrites.keys())})"
                        )
                for key, value in config_overwrites.items():
                    if not config_utils.has_path(config=config, path=key):
                        # add missing keys
                        if key not in config:
                            config_utils.set_by_path(config=config, path=key, value=config_overwrites[key])
                    # if key is present in config -> overwrite if force_overwrite is defined for this key
                    if force_overwrite.get(key, False):
                        config_utils.set_by_path(config=config, path=key, value=config_overwrites[key])
        config_with_overwrites = dict(config)

        # resume alias
        resume = config.pop("resume", None)
        if resume is not None:
            resume_run_id = resume.pop("id")
            resume_initializer = dict(
                _target_=f"{ResumeInitializer.__module__}.{ResumeInitializer.__qualname__}",
                run_id=resume_run_id,
                **resume,
            )
            if "initializers" in config:
                config["initializers"] = [resume_initializer] + config["initializers"]
            else:
                config["initializers"] = [resume_initializer]


        # initialize device
        device_type = config.pop("device_type", "cuda")
        device_utils.check_single_device_visible(device_type)
        device = torch.device(device_type)

        # initialize distributed config
        if "distributed" in config:
            distributed_provider = Factory.create_object(
                config.pop("distributed"),
                expected_base_type=DistributedProvider,
            )
        else:
            distributed_provider = DistributedProviderProcessGroup()
        distributed_provider.initialize()

        # initialize output_uri
        if "output_uri" not in config:
            self.logger.info("no output_uri specified -> using ./outputs")
            output_uri = Path("./outputs")
            # outputs typically exists anyways because hydra creates it but simply create it for tests
            output_uri.mkdir(exist_ok=True)
        else:
            output_uri = Path(config.pop("output_uri")).expanduser()
        if not output_uri.exists():
            raise ValueError(f"output_uri '{output_uri.as_posix()}' does not exist")
        if not output_uri.is_dir():
            raise ValueError(f"output_uri '{output_uri.as_posix()}' does not a directory")

        # generate run_id and sync across devices (run_id can be defined in yaml)
        if "run_id" in config:
            # check defined run_id
            run_id = config.pop("run_id")
            if len(run_id) != 8:
                raise ValueError(f"expecting run_id with 8 characters, got '{run_id}'")
            if any(not (c.islower() or c.isdigit()) for c in run_id):
                raise ValueError(f"expecting run_id to contain only lowercase letters or digits, got '{run_id}'")
            if (output_uri / run_id).exists():
                raise ValueError(f"{(output_uri / run_id).as_posix()} already exists")
        else:
            # generate run_id, technically there can be an overlap although it is extremely rare
            if distributed_provider.is_rank0:
                while True:
                    run_id = generate_id()
                    if not (output_uri / run_id).exists():
                        break
            else:
                run_id = None
            # sync rank0 run_id with other ranks
            if distributed_provider.is_distributed:
                object_list = [run_id]
                distributed.broadcast_object_list(object_list)
                run_id = object_list[0]

        # create run_output folder and path_provider
        path_provider = PathProvider(output_uri=output_uri, run_id=run_id)
        run_output_uri = path_provider.run_output_uri
        if distributed_provider.is_rank0:
            run_output_uri.mkdir()

        # initialize logging, dump resolved config and copy hydra files
        message_counter = logging_utils.initialize(
            is_rank0=distributed_provider.is_rank0,
            log_file_uri=(run_output_uri / "log.txt").as_posix(),
        )

        # store unresolved configs
        if distributed_provider.is_rank0:
            if "config_unresolved" in config:
                with open(run_output_uri / "config_unresolved.yaml", "w") as f:
                    yaml.safe_dump(data=config.pop("config_unresolved"), stream=f, sort_keys=False)
            if "config_overrides" in config:
                with open(run_output_uri / "config_overrides.yaml", "w") as f:
                    yaml.safe_dump(data=config.pop("config_overrides"), stream=f, sort_keys=False)

        # initializers
        self.logger.info("------------------")
        self.logger.info("INITIALIZING INITIALIZERS")
        initializers = []
        initializer_contexts = []
        for initializer_config in config.pop("initializers", []):
            initializer = Factory.create_object(
                initializer_config,
                path_provider=path_provider,
                expected_base_type=Initializer,
            )
            initializers.append(initializer)
            initializer_contexts.append(initializer.get_initializer_context())
        # populate _from_initializer_
        config = config_utils.populate_from_initializer_contexts(
            config=config,
            initializer_contexts=initializer_contexts,
        )

        # store resolved config
        if distributed_provider.is_rank0:
            with open(run_output_uri / "config_resolved.yaml", "w") as f:
                yaml.safe_dump(data=config_without_overwrites, stream=f, sort_keys=False)

        # log distributed config
        distributed_provider.log()
        device_utils.log_device_info(device)
        system_utils.log_system_info()
        # TODO log versions
        # safe_dump appends a trailing newline
        self.logger.info(f"\n{yaml.safe_dump(config)[:-1]}")

        # seed
        seed = config.pop("seed", None)
        if seed is None:
            seed = 0
            self.logger.info(f"no seed specified -> using {seed=}")
        if distributed_provider.has_data_parallel:
            # using a different seed for every rank to ensure that stochastic processes are different across ranks
            # for large batch_sizes this shouldn't matter too much
            # this is relevant for:
            # - augmentations (augmentation parameters of sample0 of rank0 == augparams of sample0 of rank1 == ...)
            # - stochastic processes in the forward pass (e.g., masks of a MAE are the same for every rank)
            # NOTE: DDP syncs the parameters in its __init__ method -> same initial parameters independent of seed
            # only data parallel varies seed such that sequence/model/... parallelisms load the exact same sample
            seed += distributed_provider.data_parallel_rank
            self.logger.info("using different seeds per data parallel process (seed + data_parallel rank)")
        seed_utils.set_seed(seed)
        self.logger.info(f"set seed to {seed}")

        # testrun
        testrun = config.pop("testrun", False)

        # init datasets
        self.logger.info("------------------")
        self.logger.info("INITIALIZING DATASETS")
        datasets = {}
        for key, dataset in config.pop("datasets").items():
            self.logger.info(f"initializing dataset '{key}'")
            if testrun:
                dataset_type = reflection_utils.type_from_fully_qualified_name_typed(
                    fqn=dataset.pop("_target_"),
                    expected_base_type=Dataset,
                )
                datasets[key] = dataset_type.get_testrun_dataset(dataset)
            else:
                datasets[key] = Factory.create_object(dataset, expected_base_type=Dataset)
        collators = {}
        for key, collator in config.pop("collators", {}).items():
            collators[key] = Factory.create_object(collator, expected_base_type=Collator)
        data_provider = DataProvider(datasets=datasets, collators=collators)

        # init tracker
        self.logger.info("------------------")
        self.logger.info("INITIALIZING TRACKER")
        if "tracker" in config:
            tracker = Factory.create_object(
                config.pop("tracker"),
                expected_base_type=Tracker,
                distributed_provider=distributed_provider,
                path_provider=path_provider,
            )
        else:
            # no special tracker defined -> store only to disk
            tracker = Tracker(
                distributed_provider=distributed_provider,
                path_provider=path_provider,
            )
        # TODO is this the fully resolved config?? probably not
        tracker.initialize(
            config=config_with_overwrites,
            run_id=run_id,
            run_name=config.pop("name", None),
            device_type=device.type,
        )

        # init trainer
        self.logger.info("------------------")
        self.logger.info("INITIALIZING TRAINER")
        trainer_config = config.pop("trainer")
        if testrun:
            trainer_type = reflection_utils.type_from_fully_qualified_name_typed(
                fqn=trainer_config["_target_"],
                expected_base_type=Trainer,
            )
            trainer = trainer_type.get_testrun_trainer(
                trainer_config,
                device=device,
                data_provider=data_provider,
                distributed_provider=distributed_provider,
                num_workers_provider=NumWorkersProvider(),
                tracker=tracker,
            )
        else:
            trainer = Factory.create_object(
                trainer_config,
                expected_base_type=Trainer,
                device=device,
                data_provider=data_provider,
                distributed_provider=distributed_provider,
                num_workers_provider=NumWorkersProvider(),
                tracker=tracker,
            )

        # patch training_progress_provider into tracker
        training_progress_provider = trainer.training_progress_provider
        tracker.training_progress_provider = training_progress_provider

        # init model
        self.logger.info("------------------")
        self.logger.info("INITIALIZING MODEL")
        model_ctor_kwargs_from_trainer = trainer.get_model_ctor_kwargs()
        self.logger.info(
            f"additional model_ctor kwargs from trainer:\n"
            f"{yaml.safe_dump(model_ctor_kwargs_from_trainer, sort_keys=False)[:-1]}"
        )
        model_config = config.pop("model")
        if testrun:
            model_type = reflection_utils.type_from_fully_qualified_name_typed(
                fqn=model_config["_target_"],
                expected_base_type=Model,
            )
            model = model_type.get_testrun_model(
                model_config,
                distributed_provider=distributed_provider,
                ctor_kwargs_from_trainer=model_ctor_kwargs_from_trainer,
                **model_ctor_kwargs_from_trainer,
            )
        else:
            model = Factory.create_object(
                model_config,
                expected_base_type=Model,
                run_config=config_with_overwrites,
                ctor_kwargs_from_trainer=model_ctor_kwargs_from_trainer,
                distributed_provider=distributed_provider,
                **model_ctor_kwargs_from_trainer,
            )
        self.logger.info(f"model:\n{model}")

        # initialize tensor parallel
        if distributed_provider.has_tensor_parallel:
            plan = model.get_tensor_parallel_plan()
            self.logger.info("applying tensor parallelization plan")
            for key, value in plan.items():
                self.logger.info(f"- {key}: {type(value).__name__}")
            parallelize_module(model, device_mesh=distributed_provider.device_mesh["tensor"], parallelize_plan=plan)

        # init optim
        if "optimizer" in config:
            self.logger.info("------------------")
            self.logger.info("INITIALIZING OPTIM")
            optimizer = OptimizerFactory.create_object(
                config.pop("optimizer"),
                model=model,
                training_progress_provider=training_progress_provider,
                fused=not distributed_provider.has_tensor_parallel,
            )
        else:
            optimizer = None

        # init runner callbacks
        default_kwargs = dict(
            data_provider=data_provider,
            distributed_provider=distributed_provider,
            path_provider=path_provider,
            tracker=tracker,
        )
        log_interval_kwargs = dict(
            every_n_epochs=trainer.log_every_n_epochs,
            every_n_updates=trainer.log_every_n_updates,
            every_n_samples=trainer.log_every_n_samples,
        )
        runner_callbacks = [
            UnusedModelParametersCallback(**default_kwargs),
            ModelInitializationCallback(**default_kwargs),
            DatasetStatsCallback(**default_kwargs),
            ModelParameterCountCallback(**default_kwargs),
        ]
        # add default training loggers (not needed for eval runs)
        if not trainer.is_eval_run:
            runner_callbacks += [
                LogProgressCallback(**log_interval_kwargs, **default_kwargs),
                LogUtilizationCallback(**log_interval_kwargs, **default_kwargs),
                OptimizerScheduleCallback(**log_interval_kwargs, **default_kwargs),
                OnlineLossCallback(**log_interval_kwargs, **default_kwargs, verbose=True),
            ]
            # PrintUpdateProgressCallback is mainly useful for interactive runs (e.g., debug runs)
            if distributed_provider.is_interactive and distributed_provider.is_rank0:
                runner_callbacks += [PrintUpdateProgressCallback(**log_interval_kwargs, **default_kwargs)]
            track_interval_kwargs = dict(
                every_n_epochs=trainer.track_every_n_epochs,
                every_n_updates=trainer.track_every_n_updates,
                every_n_samples=trainer.track_every_n_samples,
            )
            runner_callbacks += [
                OptimizerMetricsCallback(**track_interval_kwargs, **default_kwargs),
                OnlineLossCallback(**track_interval_kwargs, **default_kwargs, verbose=False),
            ]

        # init config callbacks
        if "callbacks" in config:
            self.logger.info("------------------")
            self.logger.info("INITIALIZING CALLBACKS")
            config_callbacks = Factory.create_list(
                config.pop("callbacks"),
                tracker=tracker,
                data_provider=data_provider,
                distributed_provider=distributed_provider,
                path_provider=path_provider,
                expected_base_type=Callback,
            )
        else:
            config_callbacks = None

        # start training
        trainer.fit(
            model=model,
            optimizer=optimizer,
            initializers=initializers,
            runner_callbacks=runner_callbacks,
            config_callbacks=config_callbacks,
        )

        # summarize
        self.logger.info("------------------")
        self.logger.info("SUMARIZE")
        tracker.summarize()

        # cleanup
        self.logger.info("------------------")
        self.logger.info("CLEANUP")
        # check that all config parts were used
        if len(config) > 0:
            self.logger.error(f"found unused config parts {config}")
        tracker.cleanup()
        # log number of warnings/errors
        message_counter.log()
        distributed_provider.cleanup()
        return tracker