from typing import Sequence
import torch
import numpy as np


def _end_dims(tensor: torch.Tensor, dims: Sequence[int]):
    length = len(tensor.shape)
    dim_length = len(dims)
    all_dims = np.arange(length)
    dims = np.array(dims, copy=False)
    middle_index = length - dim_length
    all_dims[:middle_index] = np.setdiff1d(all_dims, dims)
    all_dims[middle_index:] = dims
    recovering_all_dims = np.empty_like(all_dims)
    recovering_all_dims[dims] = np.nonzero(np.isin(all_dims, dims))[0]
    recovering_all_dims[all_dims[:middle_index]] = np.nonzero(np.isin(all_dims, all_dims[:middle_index]))[0]
    return tuple(all_dims), middle_index, tuple(recovering_all_dims)


def _limited_dim_indexing(using_shape, len_shape, start: int = 0):
    return (torch.arange(dim_size).view((1,) * (i + start) + (dim_size,) + (1,) * (len_shape - (i + start) - 1)) for i, dim_size in enumerate(using_shape))