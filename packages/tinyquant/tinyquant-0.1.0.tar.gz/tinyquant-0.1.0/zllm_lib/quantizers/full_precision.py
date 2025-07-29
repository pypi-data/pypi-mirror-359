from ..quantizer import Quantizer, registered_quantizer
from ..quantized_linear import QuantizedLinear
import torch.nn as nn
import torch.nn.functional as F


@registered_quantizer
class FullPrecisionQuantizer(Quantizer):
    @staticmethod
    def name():
        return "full_precision"

    @staticmethod
    def quantize(weight, bias) -> "QuantizedLinear":
        return QuantizedLinear.from_weights(nn.ParameterDict({
            'weight': weight,
        }), bias, {'quantization_method': FullPrecisionQuantizer.name()})

    @staticmethod
    def forward(linear, input_):
        return F.linear(
            input_, linear.weights_dict['weight'], linear.weights_dict['bias']
        )
