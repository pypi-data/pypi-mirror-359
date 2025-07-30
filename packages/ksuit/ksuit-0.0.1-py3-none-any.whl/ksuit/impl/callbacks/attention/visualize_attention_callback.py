import numpy as np
import math
from typing import Any, Sequence

import einops
import torch
from ksuit.core.callbacks import PeriodicCallback, ForwardFnResult, IterateOverDatasetResult, MetricCallback
from ksuit.core.trainers import TrainingContext
from ksuit.utils.forward_hook import ForwardHook
from ksuit.utils.config_utils import get_by_path
import matplotlib.pyplot as plt
from ksuit.impl.collators.sample_processors import TransformSampleProcessor
from ksuit.impl.transforms.images import ImageMomentNorm

class VisualizeAttentionCallback(PeriodicCallback):
    def __init__(
        self,
        attention_paths: list[str],
        dataset_key: str,
        collator_key: str | None = None,
        image_key: str = "x",
        seqlens_path: str = "patch_embed.seqlens",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dataset_key = dataset_key
        self.collator_key = collator_key
        self.image_key = image_key
        self.attention_paths = attention_paths
        self.seqlens_path = seqlens_path
        self.hooks: list[ForwardHook] = []
        self.seqlens: Sequence[int] = []
        self.output_uri = self.path_provider.run_output_uri / f"attention_maps"
        self.output_uri.mkdir()
        self.added_index = False

    def _on_fit_start(self, ctx: TrainingContext) -> None:
        self.seqlens = get_by_path(ctx.model, path=self.seqlens_path)
        assert len(self.seqlens) == 2
        for path in self.attention_paths:
            attn_module = get_by_path(ctx.model, path=path)
            hook = ForwardHook(track_inputs=True)
            attn_module.register_forward_hook(hook)
            self.hooks.append(hook)

    def _register_interleaved_sampler_configs(self, ctx: TrainingContext) -> None:
        items = ctx.trainer.get_dataset_items()
        if "index" in items:
            self.added_index = False
        else:
            items = items | {"index"}
            self.added_index = True
        self._register_interleaved_sampler_config_with_key(
            dataset_key=self.dataset_key,
            items=items,
            collator_key=self.collator_key,
        )

    def _forward(self, batch: dict[str, Any], ctx: TrainingContext) -> torch.Tensor:
        if self.added_index:
            index = batch.pop("index")
        else:
            index = batch["index"]
        # prepare image
        images = batch[self.image_key]
        collator = self.data_provider.collators[self.collator_key]
        processor: TransformSampleProcessor = collator.get_processor(lambda p: isinstance(p, TransformSampleProcessor))
        if isinstance(processor.transform, ImageMomentNorm):
            images = [processor.transform.denormalize(img) for img in images]
        else:
            self.logger.warning("no denormalization pipeline implemented -> assuming no normalization")
        images = [einops.rearrange(img * 255, "c h w -> h w c").numpy().astype(np.uint8) for img in images]

        batch = ctx.trainer.move_batch_to_device(batch=batch, ctx=ctx)
        _ = ctx.trainer.batch_to_loss(batch=batch, ctx=ctx)
        # CLS token to patch attention
        seqlen_h, seqlen_w = self.seqlens
        attn_maps = {}
        for path, hook in zip(self.attention_paths, self.hooks, strict=True):
            q, k, _ = hook.inputs
            hook.clear()
            cls = q[:, :, :1]
            patches = k[:, :, 1:]

            scale = 1 / math.sqrt(cls.size(-1))
            attn_weight = (cls * scale) @ patches.transpose(-2, -1)
            attn_weight = attn_weight.softmax(dim=-1)
            attn_maps[path] = einops.rearrange(
                attn_weight,
                "batch_size num_heads 1 (seqlen_h seqlen_w) -> batch_size num_heads seqlen_h seqlen_w",
                seqlen_h=seqlen_h,
                seqlen_w=seqlen_w,
            )

        batch_size, num_heads, _, _ = attn_maps[self.attention_paths[0]].shape
        num_blocks = len(attn_maps)
        for i in range(batch_size):
            num_rows = num_blocks + 1
            fig, axes = plt.subplots(num_rows, num_heads, figsize=(2 * num_heads, 2 * num_rows))
            # ensure axes is 2D
            if num_heads == 1:
                axes = np.expand_dims(axes, 1)
            # original image
            for j in range(num_heads):
                ax = axes[0, j]
                ax.imshow(images[i])
                ax.axis("off")
            # attention maps
            for j in range(num_blocks):
                for k in range(num_heads):
                    ax = axes[j + 1, k]
                    key = self.attention_paths[j]
                    ax.imshow(attn_maps[key][i, k].cpu(), cmap="inferno", interpolation="nearest")
                    ax.set_title(f"{key} head={k}")
                    ax.axis("off")
            plt.tight_layout()
            plt.savefig(self.output_uri / f"{index[i].item()}.png")
            plt.close()

    def _invoke(self, ctx: TrainingContext):
        for hook in self.hooks:
            hook.enable()
        self._iterate_over_dataset(forward_fn=self._forward, ctx=ctx)
        for hook in self.hooks:
            hook.disable()
