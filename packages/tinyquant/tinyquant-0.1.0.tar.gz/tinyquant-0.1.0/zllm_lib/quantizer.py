from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .quantized_linear import QuantizedLinear

_QUANTIZER_BY_NAME = {}


def register_quantizer(quantizer):
    _QUANTIZER_BY_NAME[quantizer.name()] = quantizer


def registered_quantizer(quantizer_cls):
    """A decorator to register a quantizer."""
    register_quantizer(quantizer_cls)
    return quantizer_cls


def get_quantizer(name):
    return _QUANTIZER_BY_NAME[name]


def quantize(name, weight, bias, *args, **kwargs):
    quantizer = get_quantizer(name)
    return quantizer.quantize(weight, bias, *args, **kwargs)


class Quantizer(ABC):
    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def quantize(weight, bias, *args, **kwargs) -> "QuantizedLinear":
        pass

    @staticmethod
    @abstractmethod
    def forward(linear, input_):
        pass
