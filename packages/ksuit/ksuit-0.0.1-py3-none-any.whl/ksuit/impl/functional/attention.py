import math
from abc import ABC
from typing import Sequence

import einops
import torch
import torch.nn.functional as F
from torch import nn
from torch.nn.attention import SDPBackend

class AttentionMask(ABC):
    pass


class ChunkedBlockDiagonalMask(AttentionMask):
    def __init__(self, batch_sizes: Sequence[int], sequence_lengths: Sequence[int]):
        if len(batch_sizes) != len(sequence_lengths):
            raise ValueError(
                f"{type(self).__name__} requires same number of batch_sizes "
                f"({len(batch_sizes)}) as sequence_lengths ({len(sequence_lengths)})"
            )
        self.batch_sizes = batch_sizes
        self.sequence_lengths = sequence_lengths

    @property
    def chunk_sizes(self) -> Sequence[int]:
        return [
            batch_size * sequence_length
            for batch_size, sequence_length in zip(self.batch_sizes, self.sequence_lengths, strict=True)
        ]


class ScaledDotProductAttentionFunction(nn.Module):
    """Wraps scaled_dot_product_attention into a nn.Module such that hooks can easily extract inputs."""

    def __init__(self, backend: str | None = None):
        super().__init__()
        self.backend = backend

    @staticmethod
    def convert_backend(model: nn.Module, backend: str):
        for m in model.modules():
            if isinstance(m, ScaledDotProductAttentionFunction):
                m.backend = backend

    def forward(self, *args, **kwargs):
        if self.backend is not None:
            kwargs["backend"] = self.backend
        return scaled_dot_product_attention(*args, **kwargs)


def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attn_mask: AttentionMask | torch.Tensor | None = None,
    is_causal: bool = False,
    backend: str = "auto",
):
    # custom attention masks
    if isinstance(attn_mask, AttentionMask):
        return __scaled_dot_product_attention_custom_mask(
            query=query,
            key=key,
            value=value,
            attn_mask=attn_mask,
            is_causal=is_causal,
            backend=backend,
        )
    # native implementation (useful for counting FLOPS, inspecting attention maps or debugging)
    if backend == "native":
        # https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
        seqlen_q, seqlen_k = query.size(-2), key.size(-2)
        scale = 1 / math.sqrt(query.size(-1))
        if is_causal or attn_mask is not None:
            attn_bias = torch.zeros(seqlen_q, seqlen_k, dtype=query.dtype, device=query.device)
            if is_causal:
                assert attn_mask is None
                temp_mask = torch.ones(seqlen_q, seqlen_k, dtype=torch.bool).tril(diagonal=0)
                attn_bias.masked_fill_(temp_mask.logical_not(), float("-inf"))
                attn_bias.to(query.dtype)
            if attn_mask is not None:
                if attn_mask.dtype == torch.bool:
                    attn_bias.masked_fill_(attn_mask.logical_not(), float("-inf"))
                else:
                    attn_bias = attn_mask + attn_bias
        else:
            attn_bias = None

        attn_weight = (query * scale) @ key.transpose(-2, -1)
        if attn_bias is not None:
            attn_weight = attn_weight + attn_bias
        attn_weight = attn_weight.softmax(dim=-1)
        return attn_weight @ value
    # efficient implementation
    if backend == "auto":
        if len(query) > 60000:
            # FlashAttention doesnt support large batch sizes
            with torch.nn.attention.sdpa_kernel(backends=[SDPBackend.MATH]):
                return F.scaled_dot_product_attention(
                    query=query,
                    key=key,
                    value=value,
                    attn_mask=attn_mask,
                    is_causal=is_causal
                )
        return F.scaled_dot_product_attention(
            query=query,
            key=key,
            value=value,
            attn_mask=attn_mask,
            is_causal=is_causal
        )
    raise NotImplementedError(f"invalid scaled_dot_product_attention backend '{backend}'")


def __scaled_dot_product_attention_custom_mask(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attn_mask: AttentionMask,
    **kwargs,
):
    if isinstance(attn_mask, ChunkedBlockDiagonalMask):
        chunk_sizes = attn_mask.chunk_sizes
        query = query.split(split_size=chunk_sizes, dim=2)
        key = key.split(split_size=chunk_sizes, dim=2)
        value = value.split(split_size=chunk_sizes, dim=2)
        chunk_results = []
        for i in range(len(chunk_sizes)):
            chunk_query = einops.rearrange(
                query[i],
                "1 num_heads (batch_size seqlen) head_dim -> batch_size num_heads seqlen head_dim",
                batch_size=attn_mask.batch_sizes[i],
                seqlen=attn_mask.sequence_lengths[i],
            )
            chunk_key = einops.rearrange(
                key[i],
                "1 num_heads (batch_size seqlen) head_dim -> batch_size num_heads seqlen head_dim",
                batch_size=attn_mask.batch_sizes[i],
                seqlen=attn_mask.sequence_lengths[i],
            )
            chunk_value = einops.rearrange(
                value[i],
                "1 num_heads (batch_size seqlen) head_dim -> batch_size num_heads seqlen head_dim",
                batch_size=attn_mask.batch_sizes[i],
                seqlen=attn_mask.sequence_lengths[i],
            )
            result = scaled_dot_product_attention(
                query=chunk_query,
                key=chunk_key,
                value=chunk_value,
                **kwargs,
            )
            result = einops.rearrange(
                result,
                "batch_size num_heads seqlen head_dim -> 1 num_heads (batch_size seqlen) head_dim",
            )
            chunk_results.append(result)
        return torch.concat(chunk_results, dim=2)
    raise NotImplementedError
