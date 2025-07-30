import math
from collections import defaultdict
from functools import reduce
from itertools import product
from numbers import Number
from operator import mul

import numpy as np
from dask.array.core import (
    _get_axis,
)
from dask._task_spec import List, Task, TaskRef
from dask.array import Array
from dask.array.core import keyname, interleave_none
from dask.array.slicing import replace_ellipsis
from dask.base import (
    tokenize,
)
from dask.highlevelgraph import HighLevelGraph
from dask.utils import (
    cached_cumsum,
    cached_max,
)

def _vindex(x, *indexes):
    """Point wise indexing with broadcasting.

    >>> x = np.arange(56).reshape((7, 8))
    >>> x
    array([[ 0,  1,  2,  3,  4,  5,  6,  7],
           [ 8,  9, 10, 11, 12, 13, 14, 15],
           [16, 17, 18, 19, 20, 21, 22, 23],
           [24, 25, 26, 27, 28, 29, 30, 31],
           [32, 33, 34, 35, 36, 37, 38, 39],
           [40, 41, 42, 43, 44, 45, 46, 47],
           [48, 49, 50, 51, 52, 53, 54, 55]])

    >>> d = from_array(x, chunks=(3, 4))
    >>> result = _vindex(d, [0, 1, 6, 0], [0, 1, 0, 7])
    >>> result.compute()
    array([ 0,  9, 48,  7])
    """
    
    indexes = replace_ellipsis(x.ndim, indexes)

    nonfancy_indexes = []
    reduced_indexes = []
    for ind in indexes:
        if isinstance(ind, Number):
            nonfancy_indexes.append(ind)
        elif isinstance(ind, slice):
            nonfancy_indexes.append(ind)
            reduced_indexes.append(slice(None))
        else:
            nonfancy_indexes.append(slice(None))
            reduced_indexes.append(ind)

    nonfancy_indexes = tuple(nonfancy_indexes)
    reduced_indexes = tuple(reduced_indexes)

    x = x[nonfancy_indexes]

    array_indexes = {}
    for i, (ind, size) in enumerate(zip(reduced_indexes, x.shape)):
        if not isinstance(ind, slice):
            ind = np.array(ind, copy=True)
            if ind.dtype.kind == "b":
                raise IndexError("vindex does not support indexing with boolean arrays")
            if ((ind >= size) | (ind < -size)).any():
                raise IndexError(
                    "vindex key has entries out of bounds for "
                    "indexing along axis %s of size %s: %r" % (i, size, ind)
                )
            ind %= size
            array_indexes[i] = ind

    if array_indexes:
        x = _vindex_array(x, array_indexes)

    return x

def _vindex_array(x, dict_indexes):
    """Fancy indexing with only NumPy Arrays."""
    
    token = tokenize(x, dict_indexes)
    try:
        broadcast_shape = np.broadcast_shapes(
            *(arr.shape for arr in dict_indexes.values())
        )

    except ValueError as e:
        # note: error message exactly matches numpy
        shapes_str = " ".join(str(a.shape) for a in dict_indexes.values())
        raise IndexError(
            "shape mismatch: indexing arrays could not be "
            "broadcast together with shapes " + shapes_str
        ) from e
    npoints = math.prod(broadcast_shape)
    axes = [i for i in range(x.ndim) if i in dict_indexes]

    def _subset_to_indexed_axes(iterable):
        for i, elem in enumerate(iterable):
            if i in axes:
                yield elem
    
    bounds2 = tuple(
        np.array(cached_cumsum(c, initial_zero=True))
        for c in _subset_to_indexed_axes(x.chunks)
    )
    axis = _get_axis(tuple(i if i in axes else None for i in range(x.ndim)))
    out_name = "vindex-merge-" + token

    # Now compute indices of each output element within each input block
    # The index is relative to the block, not the array.
    block_idxs = tuple(
        np.searchsorted(b, ind, side="right") - 1
        for b, ind in zip(bounds2, dict_indexes.values())
    )
    starts = (b[i] for i, b in zip(block_idxs, bounds2))
    inblock_idxs = []
    for idx, start in zip(dict_indexes.values(), starts):
        a = idx - start
        if len(a) > 0:
            dtype = np.min_scalar_type(np.max(a, axis=None))
            inblock_idxs.append(a.astype(dtype, copy=False))
        else:
            inblock_idxs.append(a)
    
    chunks = [c for i, c in enumerate(x.chunks) if i not in axes]

    # determine number of points in one single output block.
    # Use the input chunk size to determine this.
    max_chunk_point_dimensions = reduce(
        mul, map(cached_max, _subset_to_indexed_axes(x.chunks))
    )

    n_chunks, remainder = divmod(npoints, max_chunk_point_dimensions)
    chunks.insert(
        0,
        (
            (max_chunk_point_dimensions,) * n_chunks
            + ((remainder,) if remainder > 0 else ())
            if npoints > 0
            else (0,)
        ),
    )
    chunks = tuple(chunks)


    unis = []
    for block_idxs_dim in block_idxs:
        N = block_idxs_dim.shape[0]
        arr = block_idxs_dim.reshape(N, -1)
        uni = [np.unique(arr[i]) for i in range(N)]
        unis.append(uni)

    def cartesian_product_linewise(line):
        return np.array(tuple(product(*line)))  
    
    # Represents for each observation, which chunk should be opened
    chunk_idxs = [cartesian_product_linewise(row) for row in zip(*unis)]
    
    in_blocks = [] # List of each part, and more specifically the chunk to be opened for that part.
    in_indices = [] # List of each part, and for each part, which section of the chunk to extract.
    out_indices = [] # List of each part, and for each part, in which section of the final chunk the part should be written.
    obs_indices = [] # For each part, which observation index that part corresponds to.
    
    # For each observation
    for i, (blocks, inblocks, chunks) in enumerate(zip(zip(*block_idxs), zip(*inblock_idxs), chunk_idxs)):

        # For each chunk
        for chunk in chunks:
            chunk = tuple(chunk)
            sub_in_indices = []
            sub_out_indices = []
            obs_indices.append(i)
            
            # For each dimension
            for dim, coord in enumerate(chunk):
                reshp = [1]*len(chunk)
    
                # Extraction of the inblock corresponding to the chunk
                seq = blocks[dim] == coord
                res = inblocks[dim][seq]
    
                # Extraction of the outblock corresponding to the chunk
                size = blocks[dim].size
                dtype = np.min_scalar_type(size)
                outblocks = np.arange(size, dtype=dtype).reshape(blocks[dim].shape)
                resout = outblocks[seq]
                
                reshp[dim] = len(res)
                sub_in_indices.append(res.reshape(reshp))
                sub_out_indices.append(resout.reshape(reshp))
            in_blocks.append(tuple(int(x) for x in chunk))
            in_indices.append(tuple(sub_in_indices))
            out_indices.append(tuple(sub_out_indices))

    name = "vindex-slice-" + token
    vindex_merge_name = "vindex-merge-" + token

    dsk = {}
    
    out_blk = (0,) * len(broadcast_shape)
    merge_inputs = defaultdict(list)
    merge_indexer = defaultdict(list)
    merge_obs_indices = defaultdict(list)

    # SLICE
    for i, (in_blk, in_indice, out_indice, obs_indice) in enumerate(zip(in_blocks, in_indices, out_indices, obs_indices)):
        k = (name, i)

        dsk[k] = Task(
            k,
            _vindex_slice,
            TaskRef((x.name,) + in_blk), # block
            in_indice, # index
        )

        merge_inputs[out_blk].append(TaskRef(k))
        merge_indexer[out_blk].append(out_indice)
        merge_obs_indices[out_blk].append(obs_indice)

    # MERGE
    for i in merge_inputs.keys():
        k = (vindex_merge_name,) + i

        dsk[k] = Task(
            k,
            _vindex_merge,
            broadcast_shape,
            merge_indexer[i],
            List(merge_inputs[i]),
            List(merge_obs_indices[i]),
        )

    array = Array(
        HighLevelGraph.from_collections(out_name, dsk, dependencies=[x]),
        out_name,
        chunks=tuple((i,) for i in broadcast_shape),
        dtype=x.dtype,
        meta=x._meta,
    )
    return array

def _vindex_slice(block, index):
    """Slice a block using a given index."""
    block = block[index]
    return block

def _vindex_merge(shape, locations, values, obs_indices):
    """Merge multiple slices into a single array based on locations and sub-blocks."""
    values = list(values)
    dtype = values[0].dtype
    y = np.empty(shape, dtype=dtype)
    for loc, val, idx in zip(locations, values, obs_indices):
        y[idx][loc] = val
    return y