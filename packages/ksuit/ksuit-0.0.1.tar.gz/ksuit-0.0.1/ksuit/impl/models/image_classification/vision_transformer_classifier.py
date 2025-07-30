from collections.abc import Sequence
from functools import partial
from typing import Any, Literal, Self

import einops
import torch
from torch import nn
from torch.distributed.tensor.parallel import (
    ColwiseParallel,
    ParallelStyle,
    RowwiseParallel,
)

from ksuit.core.factories import Factory
from ksuit.core.initializers import Initializer, SequentialParameterInitializer
from ksuit.core.models import Model
from ksuit.impl.initializers.parameter_initializers import (
    NoopParameterInitializer,
    NormalParameterInitializer,
    ZerosParameterInitializer,
)
from ksuit.impl.modules.attention import SelfAttention
from ksuit.impl.modules.blocks import TransformerEncoderBlock
from ksuit.impl.modules.layers import GridPosEmbed, LearnableTokens, PatchEmbed, RopeCisGrid


class VisionTransformerClassifier(Model):
    @classmethod
    def get_testrun_model(cls, config: dict[str, Any], **kwargs) -> Self:
        config = dict(config)
        config["dim"] = 24
        config["num_heads"] = 2
        return Factory.create_object(config, expected_base_type=VisionTransformerClassifier, **kwargs)

    def __init__(
        self,
        num_classes: int,
        dim: int = 192,
        num_heads: int = 3,
        depth: int = 12,
        patch_size: int | Sequence[int] = (16, 16),
        num_channels: int = 3,
        resolution: int | Sequence[int] = (224, 224),
        drop_path_rate: float = 0.0,
        rope_ratio: float = 0.0,
        pooling: Literal["avg", "cls", "concat"] = "cls",
        use_absolute_position: bool = True,
        patch_embed_ctor: type[nn.Module] = PatchEmbed,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.pooling = pooling
        # embed
        self.patch_embed = Factory.create_object(
            patch_embed_ctor,
            num_channels=num_channels,
            dim=dim,
            resolution=resolution,
            patch_size=patch_size,
            ndim=2,
            implementation="conv",
        )
        if use_absolute_position:
            self.pos_embed = GridPosEmbed(dim=dim, seqlens=self.patch_embed.seqlens)
        else:
            self.pos_embed = nn.Identity()
        self.learnable_tokens = LearnableTokens(dim=dim, num_tokens=1)
        if rope_ratio > 0:
            assert dim % num_heads == 0, f"{dim=} % {num_heads=} != 0"
            head_dim = dim // num_heads
            self.rope = RopeCisGrid(
                head_dim=head_dim,
                rope_dim=int(head_dim * rope_ratio),
                seqlens=self.patch_embed.seqlens,
                num_prefix_tokens=1,
                ndim=2,
            )
        else:
            self.rope = None

        # transformer
        self.blocks = nn.ModuleList(
            [
                TransformerEncoderBlock(
                    dim=dim,
                    num_heads=num_heads,
                    mlp_hidden_dim=dim * 4,
                    drop_path_rate=drop_path_rate,
                    attn_ctor=partial(SelfAttention, distributed_provider=self.distributed_provider),
                )
                for _ in range(depth)
            ],
        )
        # head
        self.norm = nn.LayerNorm(dim, eps=1e-6)
        self.head = nn.Linear(dim * 2 if pooling == "concat" else dim, num_classes)
        self.reset_weights()

    def reset_weights(self) -> None:
        nn.init.normal_(self.head.weight, std=0.02)
        nn.init.zeros_(self.head.bias)

    def _get_tensor_parallel_plan(self) -> dict[str, ParallelStyle]:
        # for full parallelizatioin patch_embed needs to be nn.Linear
        # "patch_embed.embed": ColwiseParallel(output_layouts=Replicate()),
        # "head": ColwiseParallel(output_layouts=Replicate()),
        plan = {}
        for i in range(len(self.blocks)):
            plan[f"blocks.{i}.attn.qkv"] = ColwiseParallel()
            plan[f"blocks.{i}.attn.proj"] = RowwiseParallel()
            plan[f"blocks.{i}.mlp.fc1"] = ColwiseParallel()
            plan[f"blocks.{i}.mlp.fc2"] = RowwiseParallel()
        return plan

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.patch_embed(x)
        x = self.pos_embed(x)
        block_kwargs = {}
        if self.rope is not None:
            block_kwargs["attn_kwargs"] = dict(rope_frequencies=self.rope(tuple(x.shape[1:-1])))
        x = einops.rearrange(x, "bs ... d -> bs (...) d")
        x = self.learnable_tokens(x)
        for block in self.blocks:
            x = block(x, **block_kwargs)
        if self.pooling == "cls":
            x = x[:, 0]
        elif self.pooling == "avg":
            x = x[:, 1:].mean(dim=1)
        elif self.pooling == "concat":
            x = torch.stack([x[:, 0], x[:, 1:].mean(dim=1)], dim=1)
        else:
            raise NotImplementedError
        x = self.norm(x).flatten(start_dim=1)
        x = self.head(x)
        return x
