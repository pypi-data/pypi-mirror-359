import torch
from torch import nn


class LearnableTokens(nn.Module):
    def __init__(self, dim: int, num_tokens: int = 1):
        super().__init__()
        self.dim = dim
        self.num_tokens = num_tokens
        # 1d to automatically exclude from weight decay
        self.tokens = nn.Parameter(torch.randn(num_tokens * dim) * 0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != 3:
            raise RuntimeError(f"expecting {type(self).__name__} input to have ndim=3 (got {x.ndim})")
        if x.size(-1) != self.dim:
            raise RuntimeError(f"expecting {type(self).__name__} input to have dim={self.dim} (got {x.size(-1)})")
        x = torch.concat([self.tokens.view(1, self.num_tokens, self.dim).expand(len(x), -1, -1), x], dim=1)
        return x