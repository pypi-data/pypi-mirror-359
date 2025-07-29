from ..quantizer import Quantizer, registered_quantizer
from ..quantized_linear import QuantizedLinear
import torch.nn as nn
import torch.nn.functional as F


@registered_quantizer
class NF4Quantizer(Quantizer):
    @staticmethod
    def name():
        return "nf4"

    @staticmethod
    def quantize(weight, bias, block_size=64) -> "QuantizedLinear":
        from bitsandbytes.nn import Linear4bit

        out_features, in_features = weight.shape

        bnb_quantized = Linear4bit(
            in_features,
            out_features,
            quant_type='nf4',
            compress_statistics=False,
            bias=False,
        )

        state_dict = {
            'weight': weight,
        }

        bnb_quantized.load_state_dict(state_dict)
        bnb_quantized.cuda()
        quantized_state_dict = bnb_quantized.state_dict()

        output = nn.ParameterDict({
            'weight-original': nn.Parameter(weight, requires_grad=False),
            'weight': nn.Parameter(quantized_state_dict['weight'], requires_grad=False),
            'weight-absmax': nn.Parameter(quantized_state_dict['weight.absmax'], requires_grad=False)
        })


        return QuantizedLinear.from_weights(
            output,
            bias,
            {'quantization_method': NF4Quantizer.name()},
        )

    @staticmethod
    def forward(linear, input_):
        return F.linear(
            input_, linear.weights_dict['weight-original'], linear.weights_dict['bias']
        )
