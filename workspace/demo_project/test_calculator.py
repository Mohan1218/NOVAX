from calculator import calculate_discount


def test_percentage_discount():
    result = calculate_discount(1000, 10)
    assert result == 900
