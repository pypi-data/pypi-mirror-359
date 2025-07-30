import os
from typing import Literal

from torch import distributed

from ksuit.core.providers import DistributedProvider


class DistributedProviderProcessGroup(DistributedProvider):
    def __init__(self, parallelism: Literal["data", "sequence", "tensor"] = "data"):
        super().__init__()
        self.parallelism = parallelism

    def _initialize(self) -> None:
        if self.world_size == 1:
            return
        distributed.init_process_group(
            backend=self.backend,
            init_method="env://",
            world_size=self.world_size_from_env,
            rank=self.global_rank_from_env,
        )

    @property
    def device_mesh(self) -> distributed.DeviceMesh:
        raise RuntimeError(f"{self.__class__.__name__} does not implement device_mesh")

    @property
    def backend(self) -> str | None:
        if os.name == "nt":
            # windows doesn't support nccl
            return "gloo"
        # TODO cpu runs should also use gloo
        return "nccl"

    @property
    def data_parallel_rank(self) -> int | None:
        if self.parallelism == "data":
            return self.global_rank
        return None

    @property
    def tensor_parallel_rank(self) -> int | None:
        if self.parallelism == "tensor":
            return self.global_rank
        return None

    @property
    def sequence_parallel_rank(self) -> int | None:
        if self.parallelism == "sequence":
            return self.global_rank
        return None

    @property
    def data_parallel_size(self) -> int:
        if self.parallelism == "data":
            return self.world_size
        return 1

    @property
    def tensor_parallel_size(self):
        if self.parallelism == "tensor":
            return self.world_size
        return 1

    @property
    def sequence_parallel_size(self):
        if self.parallelism == "sequence":
            return self.world_size
        return 1

    def _get_group(self, mesh_dim_name: str) -> distributed.ProcessGroup | None:
        if mesh_dim_name == self.parallelism:
            return None
        raise RuntimeError(
            f"Trying to retrieve '{mesh_dim_name}' process group but this type of parallelism is not used. "
            f"{type(self).__name__} only supports 1D parallel where the parallelism type was set to {self.parallelism}."
        )
