import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union, Set

# handle jagged ndarray
def pad_to_dense(M:List[List[int]]) -> np.ndarray:
    maxlen = max(len(r) for r in M)
    Z = np.zeros((len(M), maxlen),dtype=int)-1  # type: ignore
    for enu, row in enumerate(M):
        Z[enu, :len(row)] = row
    return Z

# convert per var variables to per var shapes
def var_to_shape(dim_lengths_np:np.ndarray,
                 variable:np.ndarray) -> np.ndarray:
    return dim_lengths_np[variable]    

# convert per var shapes to per var sizes (# elements)
def shape_to_size(shape:np.ndarray) -> int:
    if np.shape(shape)[1]>1:    # e.g., 1*1 kernel will not cause additional input size
        shape[:,1:][shape[:,1:]>0] -= 1
    return int(np.prod(np.sum(shape,axis=-1)))

# convert dim and var to b,k,m,n for matmul
def dim_var_to_bkmn(dim_lengths:List[int],
                    variables:List[List[List[int]]]) -> Tuple[int,int,int,int]:
    out = np.array(variables[0]).flatten()[-2:]
    inA = np.array(variables[1]).flatten()[-2:]
    inB = np.array(variables[2]).flatten()[-2:]
    kset = np.intersect1d(inA, inB)
    k_idx = np.setdiff1d(kset, out)[0]
    m_idx = np.setdiff1d(inA[-2:], [k_idx])[0]
    n_idx = np.setdiff1d(inB[-2:], [k_idx])[0]
    k = dim_lengths[k_idx]
    m = dim_lengths[m_idx]
    n = dim_lengths[n_idx]
    if n>m:
        m,n = n,m
    if m<=16:
        m,n = n,m
    b = 1
    if len(dim_lengths>3):
        b = np.prod(dim_lengths[:-3])
    return b,k,m,n
