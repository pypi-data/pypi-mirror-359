from torch.utils.data import DistributedSampler as TorchDistributedSampler


class DistributedSampler(TorchDistributedSampler):
    """torch.utils.data.DistributedSampler that makes sure that set_epoch was called correctly."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_iter_epoch = None

    def __iter__(self):
        if self.shuffle:
            if self._last_iter_epoch is None:
                assert self.epoch == 0
            else:
                assert self._last_iter_epoch + 1 == self.epoch
            self._last_iter_epoch = self.epoch
        return super().__iter__()
