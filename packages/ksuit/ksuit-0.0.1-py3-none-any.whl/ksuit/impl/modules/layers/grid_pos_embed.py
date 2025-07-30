from collections.abc import Sequence
from typing import Literal

import einops
import numpy as np
import torch
from torch import nn

from .continuous_pos_embed import ContinuousSincosEmbed


class GridPosEmbed(nn.Module):
    def __init__(
        self,
        dim: int,
        seqlens: Sequence[int],
        allow_interpolation: bool = False,
        mode: Literal["learnable", "sincos"] = "learnable",
    ):
        super().__init__()
        self.dim = dim
        self.seqlens = seqlens
        self.allow_interpolation = allow_interpolation
        # 1d to automatically exclude from weight decay
        if mode == "learnable":
            self.embed = nn.Parameter(torch.randn(int(np.prod(seqlens)) * dim) * 0.02)
        elif mode == "sincos":
            grids = [torch.arange(seqlen, dtype=torch.double) for seqlen in seqlens]
            grid = torch.stack(torch.meshgrid(*grids, indexing="ij"), dim=-1)
            embed = ContinuousSincosEmbed(dim=dim, ndim=len(seqlens))(grid)
            self.register_buffer("embed", embed.unsqueeze(0))
        else:
            raise NotImplementedError

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != len(self.seqlens) + 2:
            raise RuntimeError(
                f"{x.shape=} should be (batch_size ... dim) where ... are "
                f"spatial dimensions that match seqlens={self.seqlens}"
            )
        if x.shape[-1] != self.dim:
            raise RuntimeError(
                f"{x.shape=} should be (batch_size ... dim) where ... are spatial dimensions. "
                f"Dimension does not match ({x.shape[-1]=} != dim={self.dim})."
            )
        embed = self.embed.view(1, *self.seqlens, self.dim)
        if embed.dtype != torch.float32:
            raise RuntimeError("positional embedding should be done in fp32")
        # interpolate if seqlens dont match
        actual_seqlens = x.shape[1:-1]
        if actual_seqlens != tuple(self.seqlens):
            if not self.allow_interpolation:
                raise RuntimeError(
                    f"Interpolation of positional embedding requested, but allow_interpolation=False. "
                    f"Actual seqlens ({actual_seqlens}) != expected seqlens ({self.seqlens})."
                )
            embed = einops.rearrange(embed, "1 ... dim -> 1 dim ...")
            with torch.autocast(device_type=embed.device.type, enabled=False):
                embed = nn.functional.interpolate(embed, size=actual_seqlens, mode="bicubic", align_corners=False)
            embed = einops.rearrange(embed, "1 dim ... -> 1 ... dim")
        x = x.float() + embed
        return x
