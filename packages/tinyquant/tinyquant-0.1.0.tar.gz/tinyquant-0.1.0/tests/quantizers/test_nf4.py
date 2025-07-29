from zllm_lib.quantizer import quantize

import torch
import torch.nn as nn


def test_nf4_quantizer():
    original = nn.Linear(in_features=10, out_features=20).cuda()
    quantized = quantize('nf4', original.weight, original.bias)

    input_ = torch.randn(10, device='cuda')

    torch.testing.assert_close(quantized(input_), original(input_))
