import einops
import torch
from torch import nn


class ContinuousSincosEmbed(nn.Module):
    def __init__(self, dim, ndim, max_wavelength: int = 10000, dtype=torch.float32):
        super().__init__()
        self.ndim = ndim
        # if dim is not cleanly divisible -> cut away trailing dimensions
        ndim_padding = dim % ndim
        dim_per_ndim = (dim - ndim_padding) // ndim
        sincos_padding = dim_per_ndim % 2
        self.padding = ndim_padding + sincos_padding * ndim
        effective_dim_per_wave = (dim - self.padding) // ndim
        if effective_dim_per_wave <= 0:
            raise ValueError(f"{effective_dim_per_wave=} <= 0 ({dim=} {ndim=})")
        self.register_buffer(
            "omega",
            1. / max_wavelength ** (torch.arange(0, effective_dim_per_wave, 2, dtype=dtype) / effective_dim_per_wave),
            persistent=False,
        )

    def forward(self, x: torch.Tensor):
        x = x.float()
        with torch.autocast(device_type=x.device.type, enabled=False):
            if self.ndim != x.shape[-1]:
                raise RuntimeError(f"invalid input shape {x.shape=}, expecting last dim to match {self.ndim=}")
            out = x.unsqueeze(-1) @ self.omega.unsqueeze(0)
            x = torch.concat([torch.sin(out), torch.cos(out)], dim=-1)
            x = einops.rearrange(x, "... ndim dim -> ... (ndim dim)")
        if self.padding > 0:
            padding = torch.zeros(*x.shape[:-1], self.padding, device=x.device, dtype=x.dtype)
            x = torch.concat([x, padding], dim=-1)
        return x
