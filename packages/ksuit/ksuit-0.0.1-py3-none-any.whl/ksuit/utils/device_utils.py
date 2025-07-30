import logging
import os

import torch

_logger = logging.getLogger(__name__)


def check_single_device_visible(device_type: str) -> None:
    if device_type == "cpu":
        # nothing to check
        return
    elif device_type == "cuda":
        # torchrun sets CUDA_VISIBLE_DEVICES to all devices
        if "TORCHELASTIC_RUN_ID" in os.environ:
            if "CUDA_VISIBLE_DEVICES" not in os.environ:
                raise RuntimeError("CUDA_VISIBLE_DEVICES should be set to all visible GPUs when starting with torchrun")
            local_rank = int(os.environ["LOCAL_RANK"])
            os.environ["CUDA_VISIBLE_DEVICES"] = os.environ["CUDA_VISIBLE_DEVICES"].split(",")[local_rank]

        # check
        if "CUDA_VISIBLE_DEVICES" in os.environ:
            if len(os.environ["CUDA_VISIBLE_DEVICES"].split(",")) != 1:
                raise RuntimeError(
                    f"CUDA_VISIBLE_DEVICES is expected to contain a single device but it is "
                    f"'{os.environ['CUDA_VISIBLE_DEVICES']}'"
                )
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA not available set device_type to 'cpu' in config to run on cpu")
            # if "torch.cuda" is called before "CUDA_VISIBLE_DEVICES" is set, torch will see all devices
            visible_device_count = torch.cuda.device_count()
            if visible_device_count > 1:
                raise RuntimeError(
                    f"Set CUDA_VISIBLE_DEVICES before the first call to torch.cuda "
                    f"CUDA_VISIBLE_DEVICES='{os.environ['CUDA_VISIBLE_DEVICES']}' "
                    f"torch.cuda.device_count={visible_device_count}. You most likely"
                    f"called torch.cuda before ksuit could setup the runtime."
                )
    else:
        raise NotImplementedError(f"unsupported {device_type=}")


def device_type_to_backend(device_type: str) -> str:
    if device_type == "cpu":
        # gloo is recommended for cpu multiprocessing
        # https://pytorch.org/docs/stable/distributed.html#which-backend-to-use
        return "gloo"
    if os.name == "nt":
        # windows doesn't support nccl
        return "gloo"
    # nccl is recommended for gpu multiprocessing
    # https://pytorch.org/docs/stable/distributed.html#which-backend-to-use
    return "nccl"


def log_device_info(device: torch.device) -> None:
    _logger.info("------------------")
    _logger.info("DEVICE INFOS")
    _logger.info(f"device_type: {device.type}")
    if device.type == "cuda":
        _logger.info(f"device_name: {torch.cuda.get_device_name()}")
        _logger.info(f"device_capability: {torch.cuda.get_device_capability()}")
        _logger.info(f"cuda_memory: {torch.cuda.get_device_properties(device).total_memory / 1024 / 1024 / 1024:.1f}GB")
        _logger.info(f"multi_processor_count: {torch.cuda.get_device_properties(device).multi_processor_count}")
