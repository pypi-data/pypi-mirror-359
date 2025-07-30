from collections.abc import Sequence
from typing import Literal

import einops
import numpy as np
import torch
from torch import nn

from ksuit.utils import param_checking, patchify_utils


class PatchEmbed(nn.Module):
    def __init__(
        self,
        dim: int,
        num_channels: int,
        resolution: int | Sequence[int],
        patch_size: int | Sequence[int],
        ndim: int,
        implementation: Literal["conv", "linear"] = "conv",
    ):
        super().__init__()
        self.dim = dim
        self.num_channels = num_channels
        self.ndim = ndim
        self.implementation = implementation
        self.patch_size = param_checking.to_ntuple(patch_size, n=self.ndim)
        self.resolution = param_checking.to_ntuple(resolution, n=self.ndim)
        self.seqlens = tuple([self.resolution[i] // self.patch_size[i] for i in range(self.ndim)])
        if implementation == "conv":
            if self.ndim == 1:
                conv_ctor = nn.Conv1d
            elif self.ndim == 2:
                conv_ctor = nn.Conv2d
            elif self.ndim == 3:
                conv_ctor = nn.Conv3d
            else:
                raise NotImplementedError(
                    "Implementation 'conv' is only supported for 1D, 2D or 3D inputs. "
                    "Use implementation=linear for ND support."
                )
            self.embed = conv_ctor(num_channels, dim, kernel_size=self.patch_size, stride=self.patch_size)
        elif implementation == "linear":
            # can be initialized from checkpoint that used conv via
            # with torch.no_grad():
            #     linear.weight.data.copy_(einops.rearrange(conv.weight, "o i ... -> o (... i)"))
            #     linear.bias.data.copy_(conv.bias)
            self.embed = nn.Linear(num_channels * int(np.prod(self.patch_size)), dim)
        else:
            raise NotImplementedError

    @staticmethod
    def conv_to_linear_weights(weights: torch.Tensor):
        return einops.rearrange(weights, "o i ... -> o (... i)")

    def linear_to_conv_weights(self, weights: torch.Tensor):
        kernel_size_kwargs = {f"ks{i}": self.patch_size[i] for i in range(self.ndim)}
        kernel_size_str = " ".join(kernel_size_kwargs.keys())
        return einops.rearrange(weights, f"o ({kernel_size_str} i) -> o i {kernel_size_str}", **kernel_size_kwargs)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if any(x.size(i + 2) % self.patch_size[i] != 0 for i in range(self.ndim)):
            raise ValueError(f"{x.shape=} incompatible with patch_size={self.patch_size}")
        if self.implementation == "conv":
            x = self.embed(x)
            x = einops.rearrange(x, "b c h w -> b h w c")
        elif self.implementation == "linear":
            x = patchify_utils.patchify(x, patch_size=self.patch_size)
            x = self.embed(x)
        else:
            raise NotImplementedError
        return x
