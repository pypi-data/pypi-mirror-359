import einops
import torch
from torch import nn

from ksuit.core.providers import DistributedProvider
from ksuit.impl.functional import ScaledDotProductAttentionFunction, AttentionMask
from ksuit.impl.functional.rope import apply_rope


class SelfAttention(nn.Module):
    def __init__(
        self,
        dim: int,
        num_heads: int,
        attn_ctor: type[nn.Module] = ScaledDotProductAttentionFunction,
        distributed_provider: DistributedProvider | None = None,
    ):
        super().__init__()
        if dim % num_heads != 0:
            raise ValueError(f"{dim=} % {num_heads=} != 0")

        self.dim = dim
        self.num_heads = num_heads
        self.distributed_provider = distributed_provider

        self.qkv = nn.Linear(dim, dim * 3)
        self.attn = attn_ctor()
        self.proj = nn.Linear(dim, dim)
        self.reset_weights()

        # tensor parallel
        if distributed_provider is not None and distributed_provider.has_tensor_parallel:
            tensor_parallel_size = distributed_provider.tensor_parallel_size
            if num_heads % tensor_parallel_size != 0:
                raise ValueError(f"{num_heads=} % {tensor_parallel_size=} != 0")
            self.local_num_heads = num_heads // tensor_parallel_size
        else:
            self.local_num_heads = num_heads

    def reset_weights(self) -> None:
        nn.init.normal_(self.qkv.weight, std=0.02)
        nn.init.zeros_(self.qkv.bias)
        nn.init.normal_(self.proj.weight, std=0.02)
        nn.init.zeros_(self.proj.bias)

    def forward(
        self,
        x: torch.Tensor,
        attn_mask: AttentionMask | torch.Tensor | None = None,
        rope_frequencies: torch.Tensor | None = None,
    ) -> torch.Tensor:
        # qkv + reshape
        q, k, v = einops.rearrange(
            self.qkv(x),
            "bs seqlen (three_num_heads head_dim) -> bs three_num_heads seqlen head_dim",
            three_num_heads=self.local_num_heads * 3,
        ).chunk(chunks=3, dim=1)

        # apply rotary embedding
        if rope_frequencies is not None:
            q = apply_rope(q, freqs=rope_frequencies)
            k = apply_rope(k, freqs=rope_frequencies)

        # simple sequence parallel implementation
        if self.distributed_provider is not None and self.distributed_provider.sequence_parallel_size > 1:
            assert attn_mask is None
            k = self.distributed_provider.all_gather_grad(k, mesh_dim_name="sequence", dim=2)
            v = self.distributed_provider.all_gather_grad(v, mesh_dim_name="sequence", dim=2)

        # attention
        x = self.attn(q, k, v, attn_mask=attn_mask)

        # reshape + out projection
        x = einops.rearrange(x, "bs num_heads seqlen head_dim -> bs seqlen (num_heads head_dim)")
        x = self.proj(x)

        return x
