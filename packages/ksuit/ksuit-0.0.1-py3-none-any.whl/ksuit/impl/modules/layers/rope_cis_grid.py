from typing import Sequence

import einops
import torch
from torch import nn

from .rope_cis import RopeCis


class RopeCisGrid(nn.Module):
    def __init__(
        self,
        head_dim: int,
        ndim: int,
        seqlens: Sequence[int],
        num_prefix_tokens: int = 0,
        rope_dim: int | None = None,
        max_wavelength: int = 10000.0,
    ):
        super().__init__()
        self.seqlens = seqlens
        self.num_prefix_tokens = num_prefix_tokens
        # precompute cis
        rope_cis = RopeCis(
            head_dim=head_dim,
            ndim=ndim,
            rope_dim=rope_dim,
            max_wavelength=max_wavelength,
        )
        grids = [torch.arange(seqlen, dtype=torch.double) for seqlen in seqlens]
        grid = torch.stack(torch.meshgrid(*grids, indexing="ij"), dim=-1)
        freqs = rope_cis(grid)
        freqs = einops.rearrange(freqs, "... dim -> 1 (...) dim")
        if num_prefix_tokens > 0:
            freqs = torch.concat(
                [
                    torch.ones(size=(1, num_prefix_tokens, freqs.size(-1)), dtype=torch.complex64),
                    freqs,
                ],
                dim=1,
            )
        self.register_buffer("freqs", freqs)

    def forward(self, seqlens: Sequence[int]) -> torch.Tensor:
        if seqlens == self.seqlens:
            return self.freqs
        raise NotImplementedError("interpolation not supported")