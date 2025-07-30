import logging
from contextlib import nullcontext
from typing import Any, ContextManager

import torch
from torch.amp import GradScaler

FLOAT32_ALIASES = [torch.float32, "float32", "fp32", 32, "single"]
FLOAT16_ALIASES = [torch.float16, "float16", "fp16", 16, "half"]
BFLOAT16_ALIASES = [torch.bfloat16, "bfloat16", "bf16"]
VALID_PRECISIONS = FLOAT32_ALIASES + FLOAT16_ALIASES + BFLOAT16_ALIASES

_logger = logging.getLogger(__name__)


def get_supported_precision(
    desired_precision: torch.dtype | str | int,
    device: torch.device,
    backup_precision: torch.dtype | str | int | None = None,
) -> torch.dtype:
    assert desired_precision in VALID_PRECISIONS, \
        f"invalid desired_precision ({desired_precision}), use one of {VALID_PRECISIONS}"
    if backup_precision is not None:
        assert backup_precision in VALID_PRECISIONS, \
            f"invalid backup_precision ({backup_precision}), use one of {VALID_PRECISIONS}"
    if desired_precision in FLOAT32_ALIASES:
        return torch.float32
    if desired_precision in FLOAT16_ALIASES:
        desired_precision = "float16"
    if desired_precision in BFLOAT16_ALIASES:
        desired_precision = "bfloat16"

    if desired_precision == "bfloat16":
        if _is_bfloat16_compatible(device):
            return torch.bfloat16
        else:
            # use float16 if it is defined via backup_precision
            if backup_precision is not None and backup_precision in FLOAT16_ALIASES:
                if _is_float16_compatible(device):
                    _logger.info("bfloat16 not supported -> using float16")
                    return torch.float16
                else:
                    _logger.info("bfloat16/float16 not supported -> using float32")
                    return torch.float32
            # use float32 as default (float16 can lead to under-/overflows)
            _logger.info("bfloat16 not supported -> using float32")
            return torch.float32

    if desired_precision == "float16":
        if _is_float16_compatible(device):
            return torch.float16
        else:
            # currently cpu only supports bfloat16
            if _is_bfloat16_compatible(device):
                _logger.info("float16 not supported -> using bfloat16")
                return torch.bfloat16

    _logger.info("float16/bfloat16 not supported -> using float32")
    return torch.float32


def device_to_autocast_device_type(device: torch.device) -> str:
    """Converts torch.device("cuda:0") to "cuda"."""
    return str(device).split(":")[0]


def _is_compatible(device: torch.device, dtype: torch.dtype) -> bool:
    try:
        with torch.autocast(device_type=device_to_autocast_device_type(device), dtype=dtype):
            pass
    except RuntimeError:
        return False
    return True


def _is_bfloat16_compatible(device: torch.device):
    return _is_compatible(device, torch.bfloat16)


def _is_float16_compatible(device: torch.device):
    return _is_compatible(device, torch.float16)


class NoopGradScaler:
    @staticmethod
    def scale(loss: Any) -> Any:
        return loss

    @staticmethod
    def unscale_(optimizer: torch.optim.Optimizer) -> None:
        pass

    @staticmethod
    def step(optimizer: torch.optim.Optimizer, *args, **kwargs) -> float | None:
        optimizer.step(*args, **kwargs)

    @staticmethod
    def update(new_scale: torch.Tensor | float | None = None) -> None:
        pass

    @staticmethod
    def state_dict() -> dict[str, Any]:
        return {}

    @staticmethod
    def load_state_dict(state_dict: dict[str, Any]) -> None:
        pass


def get_grad_scaler(precision: torch.dtype, device: torch.device) -> GradScaler | NoopGradScaler:
    if precision == torch.float16:
        if str(device) == "cpu":
            # GradScaler is not supported on CPU
            return NoopGradScaler()
        return GradScaler()
    # float32/bfloat16 dont need GradScaler (https://github.com/pytorch/pytorch/issues/36169)
    return NoopGradScaler()


def get_autocast_context(precision: torch.dtype, device: torch.device) -> ContextManager:
    if precision == torch.float32:
        return nullcontext()
    if device.type == "cpu" and precision == torch.float16:
        # fp32 instead of fp16 on cpu runs because grad_scaler is not supported on cpu
        _logger.warning("GradScaler not supported on cpu -> switching to fp32")
        return nullcontext()
    return torch.autocast(device_to_autocast_device_type(device), dtype=precision)
