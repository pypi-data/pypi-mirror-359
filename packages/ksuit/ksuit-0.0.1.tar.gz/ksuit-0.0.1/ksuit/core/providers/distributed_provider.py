import logging
import os
from abc import ABC, abstractmethod
from typing import Self, final

import einops
import torch
from torch import distributed

from ksuit.utils import gather_utils


class DistributedProvider(ABC):
    def __init_subclass__(cls):
        if cls.initialize != DistributedProvider.initialize:
            raise TypeError(f"{cls.__name__} must not override initialize, override _initialize instead.")
        if cls.get_group != DistributedProvider.get_group:
            raise TypeError(f"{cls.__name__} must not override get_group, override _get_group instead.")

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self._initialized = False

    @property
    def is_initialized(self):
        return self._initialized

    @final
    def initialize(self) -> Self:
        if self._initialized:
            return self
        self._check_world_size_consistency()
        self._initialize()
        self._initialized = True
        self.barrier()
        return self

    @abstractmethod
    def _initialize(self) -> None:
        pass

    @property
    @abstractmethod
    def device_mesh(self) -> distributed.DeviceMesh:
        pass

    def _check_world_size_consistency(self) -> None:
        data_parallel_size = self.data_parallel_size
        tensor_parallel_size = self.tensor_parallel_size
        sequence_parallel_size = self.sequence_parallel_size
        expected_world_size = data_parallel_size * tensor_parallel_size * sequence_parallel_size
        if expected_world_size != self.world_size:
            raise RuntimeError(
                f"world_size does not match specified distributed config "
                f"(world_size={self.world_size} != {data_parallel_size=} "
                f"* {tensor_parallel_size=} * {sequence_parallel_size=} == {expected_world_size=})"
            )

    @property
    @abstractmethod
    def data_parallel_rank(self) -> int | None:
        pass

    @property
    @abstractmethod
    def tensor_parallel_rank(self) -> int | None:
        pass

    @property
    @abstractmethod
    def sequence_parallel_rank(self) -> int | None:
        pass

    @property
    @abstractmethod
    def data_parallel_size(self) -> int:
        pass

    @property
    def has_data_parallel(self) -> bool:
        return self.data_parallel_size > 1

    @property
    @abstractmethod
    def tensor_parallel_size(self):
        pass

    @property
    def has_tensor_parallel(self) -> bool:
        return self.tensor_parallel_size > 1

    @property
    @abstractmethod
    def sequence_parallel_size(self):
        pass

    @property
    def has_sequence_parallel(self) -> bool:
        return self.sequence_parallel_size > 1

    @property
    def world_size_from_env(self) -> int:
        if "WORLD_SIZE" in os.environ:
            world_size = int(os.environ["WORLD_SIZE"])
        elif "SLURM_JOB_NUM_NODES" in os.environ and "SLURM_NTASKS_PER_NODE" in os.environ:
            world_size = int(os.environ["SLURM_JOB_NUM_NODES"]) * int(os.environ["SLURM_NTASKS_PER_NODE"])
        else:
            world_size = 1
        return world_size

    @property
    def global_rank_from_env(self) -> int:
        if self.world_size == 1:
            return 0
        if "RANK" in os.environ:
            return int(os.environ["RANK"])
        if "GLOBAL_RANK" in os.environ:
            return int(os.environ["GLOBAL_RANK"])
        if "SLURM_PROCID" in os.environ:
            return int(os.environ["SLURM_PROCID"])
        raise NotImplementedError(
            "Could not infer 'global_rank' from environment variables. "
            "Set 'RANK' or 'GLOBAL_RANK' or 'SLURM_PROCID' environment variables."
        )

    @property
    def local_rank_from_env(self) -> int:
        if "LOCAL_RANK" in os.environ:
            return int(os.environ["LOCAL_RANK"])
        # interactive single node run (can have multiple GPUs)
        if os.environ.get("SLURM_JOB_NAME") == "interactive":
            return self.global_rank_from_env
        if "SLURM_LOCALID" in os.environ:
            return int(os.environ["SLURM_LOCALID"])
        raise NotImplementedError(
            "Could not infer 'local_rank' from environment variables."
            "Set 'LOCAL_RANK' or 'SLURM_LOCALID' environment variables."
        )

    @property
    def local_rank(self) -> int:
        if self.world_size_from_env == 1:
            return 0
        return self.local_rank_from_env

    @property
    def is_distributed(self) -> bool:
        if not self._initialized:
            raise RuntimeError(f"{type(self).__name__}.is_distributed called before {type(self).__name__}.initialize")
        return distributed.is_available() and distributed.is_initialized()

    @property
    def is_interactive(self) -> bool:
        if "SLURM_JOB_ID" not in os.environ:
            return True
        if os.environ.get("SLURM_JOB_NAME") == "interactive":
            return True
        if "TORCHELASTIC_RUN_ID" in os.environ:
            return True
        return False

    @property
    def global_rank(self) -> int:
        return self.get_rank()

    def get_rank(self, mesh_dim_name: str | None = None) -> int:
        if self.world_size == 1:
            return 0
        if not self._initialized:
            return self.global_rank_from_env
        if mesh_dim_name is None:
            torch_rank = distributed.get_rank()
            if torch_rank != self.global_rank_from_env:
                raise RuntimeError(
                    f"inconsistent global_rank definition (torch.distributed.get_rank={torch_rank} != "
                    f"global_rank_from_env={self.global_rank_from_env})"
                )
            return torch_rank
        if mesh_dim_name == "data":
            if not self.has_data_parallel:
                raise RuntimeError("called get_rank('data') but no data parallel is used")
            return self.data_parallel_rank
        if mesh_dim_name == "tensor":
            if not self.has_tensor_parallel:
                raise RuntimeError("called get_rank('tensor') but no tensor parallel is used")
            return self.tensor_parallel_rank
        if mesh_dim_name == "sequence":
            if not self.has_sequence_parallel:
                raise RuntimeError("called get_rank('sequence') but no sequence parallel is used")
            return self.sequence_parallel_rank
        raise NotImplementedError(f"invalid mesh_dim_name '{mesh_dim_name}'")

    @property
    def world_size(self) -> int:
        return self.get_world_size()

    def get_world_size(self, mesh_dim_name: str | None = None) -> int:
        if not distributed.is_initialized():
            return self.world_size_from_env
        if mesh_dim_name is None:
            torch_world_size = distributed.get_world_size()
            if torch_world_size != self.world_size_from_env:
                raise RuntimeError(
                    f"inconsistent world_size definition (torch.distributed.get_world_size={torch_world_size} != "
                    f"world_size_from_env={self.world_size_from_env})"
                )
            return torch_world_size
        if mesh_dim_name == "data":
            return self.data_parallel_size
        if mesh_dim_name == "tensor":
            return self.tensor_parallel_size
        if mesh_dim_name == "sequence":
            return self.sequence_parallel_size
        raise NotImplementedError(f"invalid mesh_dim_name '{mesh_dim_name}'")

    @property
    def is_rank0(self) -> bool:
        return self.get_rank() == 0

    @property
    def is_global_rank0(self) -> bool:
        return self.is_rank0

    @property
    def is_local_rank0(self) -> bool:
        return self.get_local_rank() == 0

    @property
    def store_on_rank(self) -> bool:
        # could do something more sophisticated with tensor parallel + another
        # parallelism where different nodes store checkpoints on their local disk
        # (e.g., tp=8, dp=8 -> dp0 stores tp0 weights, dp1 stores tp1 weights, ...)
        # this heavily depends on the distributed config and should be implemented
        # by overriding this property within a derived class
        return self.get_rank("data") == 0 and self.get_rank("sequence") == 0

    def barrier(self) -> None:
        if self.is_distributed:
            distributed.barrier()

    @property
    def backend(self) -> str | None:
        if self.is_distributed:
            return distributed.get_backend()
        return None

    def log(self) -> None:
        self.logger.info("------------------")
        self.logger.info("DISTRIBUTED CONFIG")
        self.logger.info(f"world_size: {self.world_size}")
        if self.is_distributed:
            self.logger.info(f"backend: {self.backend}")
            if self.has_data_parallel:
                self.logger.info(f"data_parallel_size: {self.data_parallel_size}")
            if self.has_tensor_parallel:
                self.logger.info(f"tensor_parallel_size: {self.tensor_parallel_size}")
            if self.has_sequence_parallel:
                self.logger.info(f"sequence_parallel_size: {self.sequence_parallel_size}")
        if "SLURM_JOB_ID" in os.environ:
            self.logger.info(f"slurm_job_id: {os.environ['SLURM_JOB_ID']}")
        if "ALL_HOST_NAMES" in os.environ:
            self.logger.info(f"hostnames: {os.environ['ALL_HOST_NAMES']}")

    def cleanup(self) -> None:
        if self.is_distributed:
            distributed.destroy_process_group()

    def get_group(self, mesh_dim_name: str | None) -> distributed.ProcessGroup | None:
        if mesh_dim_name is None:
            return None
        return self._get_group(mesh_dim_name=mesh_dim_name)

    @abstractmethod
    def _get_group(self, mesh_dim_name: str) -> distributed.ProcessGroup | None:
        pass

    @torch.no_grad()
    def all_gather_nograd(self, x: torch.Tensor, mesh_dim_name: str | None = None) -> torch.Tensor:
        x, og_device, og_dtype = gather_utils.prepare_tensor_for_communication(x, backend=self.backend)
        group_world_size = self.get_world_size(mesh_dim_name)
        if group_world_size > 1:
            result = [torch.zeros_like(x) for _ in range(group_world_size)]
            group = self.get_group(mesh_dim_name)
            distributed.all_gather(result, x, group=group)
            if result[0].ndim == 0:
                # scalars can't be concatenated
                result = torch.tensor(result, device=og_device)
            else:
                result = torch.concat(result).to(og_device)
        else:
            result = gather_utils.all_gather_non_distributed(x, og_device=og_device).detach()
        result = gather_utils.postprocess_tensor(result, og_dtype=og_dtype)
        return result

    def all_gather_grad(self, x: torch.Tensor, mesh_dim_name: str | None = None, dim: int = 0) -> torch.Tensor:
        x, og_device, og_dtype = gather_utils.prepare_tensor_for_communication(x, backend=self.backend)
        group_world_size = self.get_world_size(mesh_dim_name)
        if group_world_size > 1:
            group = self.get_group(mesh_dim_name)
            rank_in_group = self.get_rank(mesh_dim_name)
            # autograd functions require arg (not kwargs)
            result = gather_utils.AllGatherGradAutograd.apply(x, group, rank_in_group, group_world_size)
            if result[0].ndim == 0:
                # scalars can't be concatenated
                result = [r.unsqueeze(0) for r in result]
            result = torch.concat(result, dim=dim).to(og_device)
        else:
            result = gather_utils.all_gather_non_distributed(x, og_device=og_device)
        result = gather_utils.postprocess_tensor(result, og_dtype=og_dtype)
        return result

    def all_reduce_sum_grad(self, x: torch.Tensor, mesh_dim_name: str | None = None) -> torch.Tensor:
        x, og_device, og_dtype = gather_utils.prepare_tensor_for_communication(x, backend=self.backend)
        group_world_size = self.get_world_size(mesh_dim_name)
        if group_world_size > 1:
            group = self.get_group(mesh_dim_name)
            # all_reduce is differentiable https://github.com/pytorch/pytorch/issues/58005
            distributed.all_reduce(x, op=distributed.ReduceOp.SUM, group=group)
        x = gather_utils.postprocess_tensor(x, og_device=og_device, og_dtype=og_dtype)
        return x

    @torch.no_grad()
    def all_reduce_sum_nograd(self, x: torch.Tensor, mesh_dim_name: str | None = None) -> torch.Tensor:
        return self.all_reduce_sum_grad(x, mesh_dim_name=mesh_dim_name).detach()

    def all_reduce_mean_grad(self, x: torch.Tensor, mesh_dim_name: str | None = None) -> torch.Tensor:
        group_world_size = self.get_world_size(mesh_dim_name)
        x = self.all_reduce_sum_grad(x, mesh_dim_name=mesh_dim_name)
        if group_world_size > 1:
            x = x / group_world_size
        return x

    @torch.no_grad()
    def all_reduce_mean_nograd(self, x: torch.Tensor, mesh_dim_name: str | None = None) -> torch.Tensor:
        return self.all_reduce_mean_grad(x, mesh_dim_name=mesh_dim_name).detach()

    def all_gather_distributed_eval(self, x: torch.Tensor, max_length: int) -> torch.Tensor:
        result = self.all_gather_nograd(x, mesh_dim_name="data")
        if self.data_parallel_size == 1:
            return result
        # gathering changes the order of the samples -> correct them
        # most of the time this is not needed (e.g. for metrics) as the order is not important
        # for things like predictions it does matter
        # 1 GPU: [0, 1, 2, 3, 4, 5, 6, 7]
        # 2 GPU: [0, 2, 4, 6] + [1, 3, 5, 7]
        # 4 GPU: [0, 4] + [1, 5] + [2, 6] + [3, 7]
        if len(result) % self.data_parallel_size != 0:
            raise RuntimeError(
                f"Called all_gather_distributed_eval where gathered batch dimension is not divisible by "
                f"data_parallel_size ({len(result)} % {self.data_parallel_size} != 0). This is necessary to "
                f"remove the padding added by DistributedSampler."
            )
        result = einops.rearrange(
            result,
            "(data_world_size len_per_data_rank) ... -> (len_per_data_rank data_world_size) ...",
            data_world_size=self.data_parallel_size,
        )
        # DistributedSampler pads the dataset to give every GPU the same amount of samples
        return result[:max_length]
