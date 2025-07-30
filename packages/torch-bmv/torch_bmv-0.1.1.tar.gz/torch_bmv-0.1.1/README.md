# torch-bmv
![tests workflow status](https://github.com/hchau630/torch-bmv/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/hchau630/torch-bmv/graph/badge.svg?token=I7Y08Z80S4)](https://codecov.io/gh/hchau630/torch-bmv)

Batched matrix-vector multiplication in PyTorch which intelligently rearranges tensor shapes for efficient computation.

# Install
`pip install torch-bmv`

# Example
```
import torch
from torch_bmv import bmv

A = torch.randn(1, 4, 5)
x = torch.randn(10, 5)
out = bmv(A, x)
assert out.shape == (10, 4)
```

# Benchmarks
Benchmark results can be viewed at https://hchau630.github.io/torch-bmv.
