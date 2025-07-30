from typing import Literal

from torch import distributed

from ksuit.core.providers import DistributedProvider
from ksuit.utils import param_checking


class DistributedProviderDeviceMesh(DistributedProvider):
    def __init__(
        self,
        data_parallel_size: int | None = None,
        tensor_parallel_size: int | None = None,
        sequence_parallel_size: int | None = None,
        default_parallelism: Literal["data", "sequence", "tensor"] = "data",
        mesh_dim_names: list[str] | None = None,
    ):
        super().__init__()
        if default_parallelism not in {"data", "sequence", "tensor"}:
            raise ValueError(f"invalid default_parallelism {default_parallelism} (use 'data', 'sequence' or 'tensor')")
        self._data_parallel_size = data_parallel_size
        self._tensor_parallel_size = tensor_parallel_size
        self._sequence_parallel_size = sequence_parallel_size
        self._default_parallelism = default_parallelism
        self.mesh_dim_names = mesh_dim_names
        self._device_mesh = None

    def _initialize(self) -> None:
        if self.world_size == 1:
            return

        mesh_shape = []
        if self.mesh_dim_names is None:
            # default order: model -> sequence -> data
            mesh_dim_names = []
            if self.has_tensor_parallel:
                mesh_shape.append(self.tensor_parallel_size)
                mesh_dim_names.append("tensor")
            if self.has_sequence_parallel:
                mesh_shape.append(self.sequence_parallel_size)
                mesh_dim_names.append("sequence")
            if self.has_data_parallel:
                mesh_shape.append(self.data_parallel_size)
                mesh_dim_names.append("data")
        else:
            # make sure user specified order is consistent with the specified parallel sizes
            for i in range(len(self.mesh_dim_names)):
                name = self.mesh_dim_names[i]
                if name == "data":
                    if self.data_parallel_size == 1:
                        raise ValueError("passed 'data' in mesh_dim_names but no data parallelism is used")
                    mesh_shape.append(self.data_parallel_size)
                if name == "tensor":
                    if self.tensor_parallel_size == 1:
                        raise ValueError("passed 'tensor' in mesh_dim_names but no tensor parallelism is used")
                    mesh_shape.append(self.tensor_parallel_size)
                if name == "sequence":
                    if self.sequence_parallel_size == 1:
                        raise ValueError("passed 'sequence' in mesh_dim_names but no sequence parallelism is used")
                    mesh_shape.append(self.sequence_parallel_size)
            mesh_dim_names = self.mesh_dim_names
        self._device_mesh = distributed.device_mesh.init_device_mesh(
            device_type="cuda",
            mesh_shape=tuple(mesh_shape),
            mesh_dim_names=tuple(mesh_dim_names),
        )

    @property
    def device_mesh(self) -> distributed.DeviceMesh:
        return self._device_mesh

    @property
    def backend(self) -> str | None:
        # initializing device mesh defaults to "undefined"
        return "nccl"

    @property
    def data_parallel_rank(self) -> int | None:
        if self.has_data_parallel:
            return self.device_mesh.get_local_rank(self.device_mesh.mesh_dim_names.index("data"))
        return None

    @property
    def tensor_parallel_rank(self) -> int | None:
        if self.has_tensor_parallel:
            return self.device_mesh.get_local_rank(self.device_mesh.mesh_dim_names.index("tensor"))
        return None

    @property
    def sequence_parallel_rank(self) -> int | None:
        if self.has_sequence_parallel:
            return self.device_mesh.get_local_rank(self.device_mesh.mesh_dim_names.index("sequence"))
        return None

    def _get_parallel_size(self, name: Literal["data", "sequence", "tensor"], parallel_size: int | None) -> int:
        if param_checking.all_none(self._data_parallel_size, self._sequence_parallel_size, self._tensor_parallel_size):
            if self._default_parallelism == name:
                # data/sequence/model parallel only
                return self.world_size
            # the specified parallelism (via name) is not used
            return 1
        if parallel_size is None:
            # the specified parallelism (via name) is not used
            return 1
        # the specified parallelism (via name) is used in conjunction with other parallelisms
        return parallel_size

    @property
    def data_parallel_size(self) -> int:
        return self._get_parallel_size(name="data", parallel_size=self._data_parallel_size)

    @property
    def tensor_parallel_size(self):
        return self._get_parallel_size(name="tensor", parallel_size=self._tensor_parallel_size)

    @property
    def sequence_parallel_size(self):
        return self._get_parallel_size(name="sequence", parallel_size=self._sequence_parallel_size)

    def _get_group(self, mesh_dim_name: str) -> distributed.ProcessGroup | None:
        return self.device_mesh[mesh_dim_name].get_group()
