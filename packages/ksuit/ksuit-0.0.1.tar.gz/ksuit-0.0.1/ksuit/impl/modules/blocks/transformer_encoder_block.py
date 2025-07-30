from typing import Any

import torch
from torch import nn

from ksuit.impl.modules.attention import SelfAttention
from ksuit.impl.modules.layers import DropPath, LayerScale
from ksuit.impl.modules.mlp import TransformerMLP


class TransformerEncoderBlock(nn.Module):
    def __init__(
        self,
        dim: int,
        num_heads: int,
        mlp_hidden_dim: int | None = None,
        drop_path_rate: float = 0.0,
        fast_drop_path: bool = False,
        layerscale: float | None = None,
        norm_ctor: type[nn.Module] = nn.LayerNorm,
        attn_ctor: type[nn.Module] = SelfAttention,
        mlp_ctor: type[nn.Module] = TransformerMLP,
        eps: float = 1e-6,
    ):
        super().__init__()
        mlp_hidden_dim = mlp_hidden_dim or dim * 4
        # attention block
        self.norm1 = norm_ctor(dim, eps=eps)
        self.attn = attn_ctor(dim=dim, num_heads=num_heads)
        self.ls1 = nn.Identity() if layerscale is None else LayerScale(dim, init_scale=layerscale)
        self.drop_path1 = DropPath(drop_prob=drop_path_rate, fast=fast_drop_path)
        # mlp block
        self.norm2 = norm_ctor(dim, eps=eps)
        self.mlp = mlp_ctor(input_dim=dim, hidden_dim=mlp_hidden_dim)
        self.ls2 = nn.Identity() if layerscale is None else LayerScale(dim, init_scale=layerscale)
        self.drop_path2 = DropPath(drop_prob=drop_path_rate, fast=fast_drop_path)

    def _attn_residual_fn(self, x: torch.Tensor, attn_kwargs: dict[str, Any] | None) -> torch.Tensor:
        return self.ls1(self.attn(self.norm1(x), **(attn_kwargs or {})))

    def _mlp_residual_fn(self, x: torch.Tensor) -> torch.Tensor:
        return self.ls2(self.mlp(self.norm2(x)))

    def forward(self, x: torch.Tensor, attn_kwargs: dict[str, Any] | None = None) -> torch.Tensor:
        x = self.drop_path1(x, residual_fn=self._attn_residual_fn, attn_kwargs=attn_kwargs)
        x = self.drop_path2(x, residual_fn=self._mlp_residual_fn)
        return x
