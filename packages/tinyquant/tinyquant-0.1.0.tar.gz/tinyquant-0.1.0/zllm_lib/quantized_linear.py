import torch
import torch.nn as nn
from functools import cached_property
import json
from .quantizer import get_quantizer


def quantize_meta(meta):
    assert isinstance(meta, dict)
    meta = json.dumps(meta)
    meta_bytes = meta.encode('utf-8')
    meta_tensor = torch.tensor(list(meta_bytes), dtype=torch.uint8)
    return meta_tensor


def dequantize_meta(meta_tensor):
    meta_bytes = meta_tensor.tolist()
    meta = bytes(meta_bytes).decode('utf-8')
    meta = json.loads(meta)
    assert isinstance(meta, dict)
    return meta


class QuantizedLinear(nn.Module):
    def __init__(self):
        super().__init__()
        self.weights_dict = nn.ParameterDict()

    @classmethod
    def from_weights(cls, weights_dict, bias, meta) -> "QuantizedLinear":
        output = cls()
        assert 'quantization_method' in meta

        assert 'meta' not in weights_dict
        assert isinstance(weights_dict, nn.ParameterDict)
        weights_dict['meta'] = nn.Parameter(
            quantize_meta(meta), requires_grad=False
        )

        assert 'bias' not in weights_dict
        if bias is not None:
            assert isinstance(bias, torch.Tensor)
            weights_dict['bias'] = nn.Parameter(
                bias, requires_grad=False
            )

        output.weights_dict = weights_dict
        return output

    def forward(self, x):
        return get_quantizer(self.quantization_method).forward(self, x)

    @cached_property
    def quantization_method(self):
        return self.meta['quantization_method']

    @cached_property
    def meta(self):
        if len(self.weights_dict) == 0:
            raise RuntimeError("QuantizedLinear is not initialized")

        return dequantize_meta(self.weights_dict['meta'])

    def load_state_dict(self, state_dict, strict=True):
        assert len(self.weights_dict) == 0

        prefix = 'weights_dict.'
        for key, value_tensor in state_dict.items():
            assert key.startswith(prefix)
            param_name = key[len(prefix):]
            self.weights_dict[param_name] = nn.Parameter(
                torch.empty_like(value_tensor),
                requires_grad=False,
            )

        return super().load_state_dict(state_dict, strict=strict)
