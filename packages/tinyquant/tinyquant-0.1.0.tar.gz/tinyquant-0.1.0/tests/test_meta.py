from zllm_lib.quantized_linear import quantize_meta, dequantize_meta


def check_quantize_dequantize(meta):
    assert dequantize_meta(quantize_meta(meta)) == meta


def test_meta() -> None:
    check_quantize_dequantize(dict())
    check_quantize_dequantize({'foo': 'bar'})
    check_quantize_dequantize({'foo': 1, 'bar': None})
