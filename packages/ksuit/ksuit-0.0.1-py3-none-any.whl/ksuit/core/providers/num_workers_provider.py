import logging
import os
import sys


class NumWorkersProvider:
    def __init__(
        self,
        num_cpus_per_device: int | None = None,
        num_devices_per_node: int | None = None,
        num_cpus_per_node: int | None = None,
    ):
        self.logger = logging.getLogger(type(self).__name__)
        self._num_cpus_per_device = num_cpus_per_device
        self._num_devices_per_node = num_devices_per_node
        self._num_cpus_per_node = num_cpus_per_node

    @property
    def num_cpus_per_device(self):
        if self._num_cpus_per_device is not None:
            return self._num_cpus_per_device
        self.logger.info("no num_cpus_per_device defined -> trying to infer it")

        # use SLURM definitions if available
        if "SLURM_PROCID" in os.environ and os.environ.get("SLURM_JOB_NAME", None) != "interactive":
            # slurm already divides cpus among tasks
            if "SLURM_CPUS_PER_TASK" in os.environ:
                num_cpus_per_device = int(os.environ["SLURM_CPUS_PER_TASK"])
                self._num_cpus_per_device = num_cpus_per_device
                self.logger.info(f"inferred {num_cpus_per_device=} from SLURM")
                return num_cpus_per_device
        # divide cpus among devices
        num_cpus_per_device = int(self.num_cpus_per_node / max(1, self.num_devices_per_node))
        self.logger.info(f"inferred {num_cpus_per_device=} from system")
        self._num_cpus_per_device = num_cpus_per_device
        return num_cpus_per_device

    @property
    def num_devices_per_node(self) -> int:
        if self._num_devices_per_node is not None:
            return self._num_devices_per_node
        self.logger.info("no num_devices_per_node defined -> trying to infer it with nvidia-smi")
        # number of devices per node (srun nvidia-smi shows all devices not only the ones assigned for the srun task)
        # GPU 0: NVIDIA A100-PCIE-40GB (UUID: GPU-...)
        # GPU 1: NVIDIA A100-PCIE-40GB (UUID: GPU-...)
        nvidia_smi_lines = os.popen("nvidia-smi -L").read().strip().split("\n")
        num_devices_per_node = 0
        for i, line in enumerate(nvidia_smi_lines):
            if "MIG" in line:
                raise NotImplementedError("MIG devices not supported")
            if "GPU" in line:
                num_devices_per_node += 1
        self.logger.info(f"inferred {num_devices_per_node=}")
        self._num_devices_per_node = num_devices_per_node
        return num_devices_per_node

    @property
    def num_cpus_per_node(self):
        if self._num_cpus_per_node is not None:
            return self._num_cpus_per_node
        self.logger.info("no num_cpus_per_node defined -> try to infer it")
        if os.name == "nt":
            # windows
            num_cpus_per_node = os.cpu_count()
        elif sys.platform == "darwin":
            # macos
            num_cpus_per_node = os.cpu_count()
        elif sys.platform.startswith("linux"):
            # linux supports restricting CPUs to processes
            # this assumes that also the number of GPUs will be restricted by e.g., SLURM
            num_cpus_per_node = len(os.sched_getaffinity(0))
        else:
            raise NotImplementedError(f"Unknown or unsupported system {sys.platform}")
        self.logger.info(f"inferred {num_cpus_per_node=}")
        self._num_cpus_per_node = num_cpus_per_node
        return num_cpus_per_node
