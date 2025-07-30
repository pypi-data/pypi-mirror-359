import torch
import pytest

from torch_bmv import bmv


@pytest.mark.parametrize(
    "bshape_A, bshape_B",
    [
        ((2, 3, 4), (2, 3, 4)),
        ((2, 3, 4), (3, 4)),
        ((2, 3, 4), (4,)),
        ((3, 4), (2, 3, 4)),
        ((4,), (2, 3, 4)),
        ((2, 1, 4), (2, 3, 4)),
        ((2, 1, 1), (2, 3, 4)),
        ((2, 3, 4), (2, 1, 4)),
        ((2, 3, 4), (2, 1, 1)),
        ((2, 3, 1), (1, 3, 4)),
        ((2, 1, 1), (1, 3, 4)),
    ],
)
@pytest.mark.parametrize(
    "m, n",
    [
        (5, 5),
        (5, 6),
        (6, 5),
    ],
)
@pytest.mark.parametrize("device", pytest.devices)
def test_bmv(bshape_A, bshape_B, m, n, device):
    A = torch.randn(*bshape_A, m, n, device=device)
    x = torch.randn(*bshape_B, n, device=device)

    out = bmv(A, x)
    expected = bmv(A, x, naive=True)

    torch.testing.assert_close(out, expected)
