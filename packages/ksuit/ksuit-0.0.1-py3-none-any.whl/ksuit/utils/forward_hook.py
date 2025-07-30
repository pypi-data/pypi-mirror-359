import uuid

import torch
from typing import Any, Self
from ksuit.utils import param_checking

class ForwardHook:
    class StopForwardException(Exception):
        pass

    def __init__(self, track_inputs: bool = False, track_outputs: bool = False, raise_exception: bool = False):
        assert param_checking.at_least_one_true(track_inputs, track_outputs)
        self.track_inputs = track_inputs
        self.track_outputs = track_outputs
        self.raise_exception = raise_exception
        self.enabled = False
        self.inputs = None
        self.outputs = None

    def enable(self) -> Self:
        self.enabled = True
        return self

    def disable(self) -> Self:
        self.enabled = False
        return self

    def clear(self) -> None:
        self.inputs = None
        self.outputs = None

    def __call__(self, _, inputs, outputs: Any) -> None:
        if not self.enabled:
            return
        if self.track_inputs:
            if self.inputs is not None:
                raise RuntimeError(
                    f"{type(self).__name__} already stored inputs. "
                    f"Call clear() between forward passes to avoid memory leaks."
                )
            self.inputs = inputs
        if self.track_outputs:
            if self.outputs is not None:
                raise RuntimeError(
                    f"{type(self).__name__} already stored outputs. "
                    f"Call clear() between forward passes to avoid memory leaks."
                )
            self.outputs = outputs
        if self.raise_exception:
            raise StopForwardException
