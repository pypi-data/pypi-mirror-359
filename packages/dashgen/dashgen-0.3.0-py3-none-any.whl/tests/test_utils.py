import base64
from dashgen.core.utils import (
    format_currency,
    format_percent,
    calculate_performance,
    image_to_base64,
)


def test_format_currency_basic():
    assert format_currency(500) == "R$ 500"


def test_format_currency_thousands():
    assert format_currency(1250) == "R$ 1,2K"


def test_format_currency_millions():
    assert format_currency(2200000) == "R$ 2,2M"


def test_format_currency_no_currency():
    assert format_currency(1200, currency="") == "1,2K"


def test_image_to_base64_exists(tmp_path):
    img = tmp_path / "test.bin"
    img.write_bytes(b"hello")
    expected = base64.b64encode(b"hello").decode()
    assert image_to_base64(img) == expected


def test_image_to_base64_missing(tmp_path):
    missing = tmp_path / "missing.bin"
    assert image_to_base64(missing) == ""


def test_format_percent_basic():
    assert format_percent(12.3) == "12,3%"


def test_calculate_performance_basic():
    assert calculate_performance(50, 200) == 25


def test_calculate_performance_zero_target():
    assert calculate_performance(10, 0) == 0
