import einops
import torch


def apply_rope(x: torch.Tensor, freqs: torch.Tensor) -> torch.Tensor:
    """RoPE (https://arxiv.org/abs/2104.09864) via complex multiplication."""
    # adapted from https://github.com/meta-llama/llama3/blob/main/llama/model.py#L65
    if x.ndim != 4:
        raise ValueError(f"expected {x.shape=} to be (batch_size, num_heads, seqlen, head_dim)")
    if not torch.is_tensor(freqs):
        raise RuntimeError(f"freqs is not tensor ({type(freqs)=})")
    if not torch.is_complex(freqs):
        raise RuntimeError(f"freqs is not complex ({freqs.dtype=})")
    if freqs.ndim != 3:
        raise RuntimeError(f"expected {freqs.shape=} to be (batch_size, seqlen, head_dim // 2)")
    head_dim = x.size(-1)
    if head_dim % 2 != 0:
        raise RuntimeError(f"{head_dim=} needs to be multiple of two")
    # check if dim (full hidden dim) was used to create frequencies instead of head_dim
    rope_dim = freqs.size(-1)
    if rope_dim != (head_dim // 2):
        num_heads = x.size(1)
        dim = num_heads * head_dim
        if rope_dim == dim:
            raise RuntimeError(
                "Frequencies should have dimension of head_dim // 2, but found dim. You probably forgot to "
                f"divide the model dimension by num_heads when creating the RoPE frequencies. Got: {dim=} "
                f"{num_heads=} {head_dim=} {rope_dim=} (rope_dim should be equal to head_dim)."
            )
        raise RuntimeError(f"{freqs.size(-1)=} should have dimension {head_dim // 2=}")

    # apply rope
    x_complex = torch.view_as_complex(x.float().reshape(*x.shape[:-1], -1, 2))
    # add head dimension (same rotation for all heads)
    freqs = einops.rearrange(freqs, "batch_size seqlen head_dim -> batch_size 1 seqlen head_dim")
    x_rotated = torch.view_as_real(x_complex * freqs).flatten(start_dim=3)
    return x_rotated.type_as(x)
