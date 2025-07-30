# Copyright (c) Ye Liu. Licensed under the MIT License.

from ..builder import HOOKS
from .base import Hook


@HOOKS.register()
class SamplerSeedHook(Hook):
    """
    Update sampler seeds every epoch. This hook is normally used in
    distributed training.
    """

    def before_epoch(self, engine):
        engine.data_loader.sampler.set_epoch(engine.epoch)
