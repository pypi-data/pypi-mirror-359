from typing import Sequence

import einops
import torch


def patchify(x: torch.Tensor, patch_size: Sequence[int], flatten_spatial_dims: bool = False) -> torch.Tensor:
    if x.ndim - 2 != len(patch_size):
        raise RuntimeError(
            f"{x.shape=} should be (batch_size num_channels ...) where ... are arbitrary many "
            f"spatial dimensions and need to match the spatial dimensions from {patch_size=}"
        )
    ndim = len(patch_size)
    resolution = x.shape[2:]
    if any(resolution[i] % patch_size[i] != 0 for i in range(ndim)):
        raise RuntimeError(f"{resolution=} is not divisible by {patch_size=}")
    seqlens = [resolution[i] // patch_size[i] for i in range(ndim)]
    # generate generic pattern for ndim
    # pattern for 2d is: "bs c (h ph) (w pw) -> bs h w (ph pw c)"
    # pattern for 3d is: "bs c (x px) (y py) (z pz) -> bs x y z (px py pz c)"
    from_pattern = "c " + " ".join([f"(seqlen{i} patchsize{i})" for i in range(ndim)])
    to_pattern1 = " ".join([f"seqlen{i}" for i in range(ndim)])
    to_pattern2 = " ".join([f"patchsize{i}" for i in range(ndim)]) + " c"
    kwargs = {f"seqlen{i}": seqlens[i] for i in range(ndim)}
    if flatten_spatial_dims:
        to_pattern1 = f"({to_pattern1})"
    x = einops.rearrange(x, f"bs {from_pattern} -> bs {to_pattern1} ({to_pattern2})", **kwargs)
    return x
