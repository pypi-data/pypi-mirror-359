# Copyright (c) Ye Liu. Licensed under the MIT License.

import torch
import torch.nn.functional as F
from torch.utils.data.dataloader import default_collate

import nncore
from .container import DataContainer


def collate(batch, samples_per_gpu=-1):
    """
    A collate function for :obj:`DataLoader` with :obj:`DataContainer` support.

    Args:
        batch (any): The batch of data to be collated.
        samples_per_gpu (int, optional): Number of samples per GPU. ``-1``
            means moving all the data to a single GPU. Default: ``-1``.
    """
    if isinstance(batch[0], DataContainer):
        stacked = []
        if samples_per_gpu < 0:
            samples_per_gpu = len(batch)
        if batch[0].stack:
            for i in range(0, len(batch), samples_per_gpu):
                assert torch.is_tensor(batch[i].data)
                if batch[i].pad_dims is None:
                    stacked.append(
                        default_collate([
                            sample.data
                            for sample in batch[i:i + samples_per_gpu]
                        ]))
                else:
                    ndim = batch[i].dim()
                    max_shape = [0] * batch[i].pad_dims
                    for dim in range(1, batch[i].pad_dims + 1):
                        max_shape[dim - 1] = batch[i].size(-dim)
                    for sample in batch[i:i + samples_per_gpu]:
                        for dim in range(0, ndim - batch[i].pad_dims):
                            assert batch[i].size(dim) == sample.size(dim)
                        for dim in range(1, batch[i].pad_dims + 1):
                            max_shape[dim - 1] = max(max_shape[dim - 1],
                                                     sample.size(-dim))
                    padded = []
                    for sample in batch[i:i + samples_per_gpu]:
                        pad = [0] * batch[i].pad_dims * 2
                        for dim in range(1, batch[i].pad_dims + 1):
                            pad[2 * dim -
                                1] = max_shape[dim - 1] - sample.size(-dim)
                        padded.append(
                            F.pad(sample.data, pad, value=sample.pad_value))
                    stacked.append(default_collate(padded))
        else:
            for i in range(0, len(batch), samples_per_gpu):
                stacked.append(
                    [sample.data for sample in batch[i:i + samples_per_gpu]])
        return DataContainer(
            stacked,
            stack=batch[0].stack,
            pad_value=batch[0].pad_value,
            pad_dims=batch[0].pad_dims,
            cpu_only=batch[0].cpu_only)
    elif isinstance(batch[0], list):
        return collate(nncore.concat(batch), samples_per_gpu)
    elif isinstance(batch[0], tuple):
        transposed = zip(*batch)
        return [collate(samples, samples_per_gpu) for samples in transposed]
    elif isinstance(batch[0], dict):
        return {
            k: collate([d[k] for d in batch], samples_per_gpu)
            for k in batch[0]
        }
    else:
        return default_collate(batch)
