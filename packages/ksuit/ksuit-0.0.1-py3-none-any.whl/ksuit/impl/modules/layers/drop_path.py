from typing import Protocol

import torch
from torch import nn


class DropPathResidualFunctionProtocol(Protocol):
    def __call__(self, x: torch.Tensor, **kwargs) -> torch.Tensor: ...


class DropPath(nn.Module):
    def __init__(
        self,
        drop_prob: float = 0.,
        scale_by_keep: bool = True,
        fast: bool = False,
    ):
        super().__init__()
        assert 0. <= drop_prob < 1.
        self._drop_prob = drop_prob
        self.scale_by_keep = scale_by_keep
        self.fast = fast

    @property
    def drop_prob(self):
        return self._drop_prob

    @drop_prob.setter
    def drop_prob(self, value):
        assert 0. <= value < 1.
        self._drop_prob = value

    @property
    def keep_prob(self):
        return 1. - self.drop_prob

    def forward(self, x, residual_fn: DropPathResidualFunctionProtocol, **kwargs):
        if self.drop_prob == 0. or not self.training:
            return x + residual_fn(x, **kwargs)

        # slow implementation (computes everything -> randomly zero out)
        if not self.fast:
            # same as timm; enable any shape
            og_x = x
            x = residual_fn(x, **kwargs)
            shape = (x.shape[0],) + (1,) * (x.ndim - 1)
            random_tensor = x.new_empty(shape).bernoulli_(self.keep_prob)
            if self.scale_by_keep:
                if self.keep_prob == 0.0:
                    raise ValueError("can't scale_by_keep if keep_prob is 0")
                random_tensor.div_(self.keep_prob)
            x = x * random_tensor
            return og_x + x

        # kwargs also need to be subsampled for fast implementation
        for key, value in kwargs.items():
            if value is None:
                continue
            raise NotImplementedError(
                f"Invalid value passed to DropPath as **kwargs ({key=} type(value)={type(value).__name__}). "
                f"Use fast=False or implement subsampling for fast DropPath implementation."
            )

        # fast implementation where computations are completely skipped
        # this implementation is faster but also slightly different from the slow version
        # - each layer propagates a fixed number of samples through (in the slow version, this number is stochastic)
        # - the drop probability changes slightly depending on drop probability and batch size
        bs = len(x)
        keep_count_float = bs * self.keep_prob
        keep_count_round = round(keep_count_float)
        if keep_count_round == 0 or keep_count_round == bs:
            raise ValueError(
                f"Fast DropPath implementation with drop probability {self.drop_prob} and batch_size={bs} would keep "
                f"{keep_count_round}/{bs} samples, which is unintended behavior. Increase batch_size, adjust drop "
                f"probability or disable fast implementation."
            )
        perm = torch.randperm(bs, device=x.device)[:keep_count_round]

        # propagate
        if self.scale_by_keep:
            alpha = bs / len(perm)
        else:
            alpha = 1.
        residual = residual_fn(x[perm], **kwargs)
        return torch.index_add(
            x.flatten(start_dim=1),
            dim=0,
            index=perm,
            source=residual.to(x.dtype).flatten(start_dim=1),
            alpha=alpha,
        ).view_as(x)

    def extra_repr(self) -> str:
        return f"drop_prob={round(self.drop_prob, 3):0.3f} scale_by_keep={self.scale_by_keep} fast={self.fast}"
