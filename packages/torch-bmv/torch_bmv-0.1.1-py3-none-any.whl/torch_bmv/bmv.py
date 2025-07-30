from torch import Tensor


def bmv(A: Tensor, x: Tensor, naive: bool = False) -> Tensor:
    """
    Optimized batched matrix-vector multiplication.

    Args:
        A: Tensor with shape (*, m, n).
        x: Tensor with shape (*, n).
        naive: If True, use the naive implementation instead of the optimized one.

    Returns:
        Tensor: Tensor with shape (*, m).
    """
    if A.ndim < 2 or x.ndim < 1:
        raise ValueError(
            "A must have at least 2 dimensions and x must have at least 1 dimension."
        )

    if naive:
        # Don't optimize, just do the multiplication.
        return (A @ x.unsqueeze(-1)).squeeze(-1)

    nbatchdim = max(A.ndim - 2, x.ndim - 1)
    A = A[(None,) * (nbatchdim - A.ndim + 2)]
    x = x[(None,) * (nbatchdim - x.ndim + 1)]
    bshape_A = A.shape[:-2]
    bshape_x = x.shape[:-1]
    assert len(bshape_A) == len(bshape_x), "Batch dimensions must match."

    dims = [d for d, (i, j) in enumerate(zip(bshape_A, bshape_x)) if i == 1 and j > 1]
    if len(dims) == 0:
        # No optimization possible, just do the multiplication.
        return (A @ x.unsqueeze(-1)).squeeze(-1)

    new_dims = tuple(range(-len(dims), 0))
    A = A.squeeze(dims)
    x = x.movedim(dims, new_dims)
    shape = x.shape[-len(dims) :]
    x = x.reshape(*x.shape[: -len(dims)], -1)
    out = A @ x
    out = out.reshape(*out.shape[:-1], *shape)
    out = out.movedim(new_dims, dims)

    return out
