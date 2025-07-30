from typing import Literal

import einops
import torch
from torch import nn


class RopeCis(nn.Module):
    def __init__(
        self,
        head_dim: int,
        ndim: int,
        rope_dim: int | None = None,
        max_wavelength: int = 10000.0,
    ):
        super().__init__()
        self.head_dim = head_dim
        self.rope_dim = rope_dim
        self.max_wavelength = max_wavelength
        self.ndim = ndim
        # partial rope can pass rope_dim to only use a subset for rope
        if rope_dim is None:
            rope_dim = head_dim
        else:
            if rope_dim > head_dim:
                raise ValueError(f"{rope_dim=} > {head_dim=}")
        # if dim is not cleanly divisible -> cut away trailing dimensions
        ndim_padding = rope_dim % ndim
        dim_per_ndim = (rope_dim - ndim_padding) // ndim
        sincos_padding = dim_per_ndim % 2
        padding = ndim_padding + sincos_padding * ndim
        # effective dimension per wave (excludes padding dimensions)
        eff_dim_per_wave = (rope_dim - padding) // ndim
        assert eff_dim_per_wave > 0
        self.register_buffer(
            "omega",
            1.0 / max_wavelength ** (torch.arange(0, eff_dim_per_wave, 2, dtype=torch.float) / eff_dim_per_wave),
            persistent=False,
        )
        # pad also dimensions not used for partial rope
        self.padding = padding + (head_dim - rope_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        with torch.autocast(device_type=x.device.type, enabled=False):
            coordinate_ndim = x.shape[-1]
            assert self.ndim == coordinate_ndim
            out = x.float().unsqueeze(-1) @ self.omega.unsqueeze(0)
        out = einops.rearrange(out, "... ndim dim -> ... (ndim dim)")
        # add padding
        assert self.padding % 2 == 0
        out = torch.concat([out, torch.zeros(*out.shape[:-1], self.padding // 2, device=x.device)], dim=-1)
        return torch.polar(torch.ones_like(out), out)
