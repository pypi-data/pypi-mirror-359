import torch
from torch import distributed


class AllGatherGradAutograd(torch.autograd.Function):
    """
    Gathers tensors from all process and supports backward propagation
    for the gradients across processes.
    """

    # noinspection PyMethodOverriding
    @staticmethod
    def forward(
        ctx,
        x: torch.Tensor,
        group: distributed.ProcessGroup | None,
        rank_in_group: int,
        group_world_size: int,
    ) -> tuple[torch.Tensor, ...]:
        output = [torch.zeros_like(x) for _ in range(group_world_size)]
        distributed.all_gather(output, x, group=group)
        ctx.group = group
        ctx.rank_in_group = rank_in_group
        # without the tuple call here, the gradient is not propagated for some reason
        # (therefore the backward is then not called)
        return tuple(output)

    @staticmethod
    def backward(ctx, *grads):
        all_gradients = torch.stack(grads)
        distributed.all_reduce(all_gradients, op=distributed.ReduceOp.SUM, group=ctx.group)
        grad_out = all_gradients[ctx.rank_in_group]
        # there needs to be an output for all arguments that were passed to forward
        # None is used for constants
        return grad_out, None, None, None


def get_communication_device(backend: str | None) -> torch.device | None:
    # gloo cpu -> okay
    # gloo cuda -> okay (although https://pytorch.org/docs/stable/distributed.html says it isn't supported)
    # nccl cpu -> fail (should use gloo anyways for cpu communication)
    # nccl cuda -> okay
    if backend is None:
        return None
    if backend == "nccl":
        return torch.device("cuda")
    if backend == "gloo":
        return torch.device("cpu")
    raise NotImplementedError(f"unsupported communication backend '{backend}'")


def is_bfloat16_supported(backend: str | None) -> bool:
    if backend is None:
        return True
    if backend == "nccl":
        return True
    if backend == "gloo":
        return False
    raise NotImplementedError(f"unsupported communication backend '{backend}'")


def is_bool_gather_supported(backend: str | None) -> bool:
    if backend is None:
        return True
    if backend == "nccl":
        return True
    if backend == "gloo":
        return False
    raise NotImplementedError


def convert_to_supported_dtype(x: torch.Tensor, backend: str | None) -> tuple[torch.Tensor, torch.dtype | None]:
    # bfloat16 gather is not supported in some settings
    if x.dtype == torch.bfloat16 and not is_bfloat16_supported(backend):
        return x.type(torch.float32), torch.bfloat16
    # bool gather is not supported in some settings
    if x.dtype == torch.bool and not is_bool_gather_supported(backend):
        return x.type(torch.float32), torch.bool
    return x, None


def prepare_tensor_for_communication(
    x: torch.Tensor,
    backend: str | None,
) -> tuple[torch.Tensor, torch.device, torch.dtype]:
    """
    prepare for distributed communication
    - wrap primitive types into tensors
    - push tensor onto supported device
    - convert bool to float if bool gathering is not supported
    - call .contiguous if x is not in a contiguous memory block
    """
    device = get_communication_device(backend)
    # convert primitive types to tensor
    if isinstance(x, (bool, float, int)):
        if device is None:
            x = torch.tensor(x)
        else:
            x = torch.tensor(x, device=device)
        og_device = torch.device("cpu")
    else:
        og_device = x.device
    if not torch.is_tensor(x):
        raise NotImplementedError(
            f"Invalid input type '{type(x).__name__}' for distributed communication. "
            f"Expecting torch.Tensor or primitive value type (bool, float or int)."
        )
    x, og_dtype = convert_to_supported_dtype(x, backend=backend)
    if not x.is_contiguous():
        x = x.contiguous()
    if device is not None:
        x = x.to(device)
    return x, og_device, og_dtype


def postprocess_tensor(
    x: torch.Tensor,
    og_dtype: torch.dtype | None,
    og_device: torch.device | None = None,
) -> torch.Tensor:
    if og_dtype is not None:
        x = x.to(og_dtype)
    if og_device is not None:
        x = x.to(og_device)
    return x

def all_gather_non_distributed(x: torch.Tensor, og_device: torch.device) -> torch.Tensor:
    if x.ndim == 0:
        # distributed gather adds a dimension to scalars
        x = x.unsqueeze(0)
    return x.to(og_device)
