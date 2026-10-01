from decimal import Decimal

import pytest

from app.models import from_cents, to_cents


@pytest.mark.parametrize("dollars, cents", [
    ("0.01", 1), ("1", 100), ("500.25", 50025), ("0.10", 10), ("99999999.99", 9999999999),
])
def test_money_round_trip(dollars, cents):
    assert to_cents(Decimal(dollars)) == cents
    assert from_cents(cents) == Decimal(dollars).quantize(Decimal("0.01"))


def test_from_cents_always_two_places():
    assert str(from_cents(0)) == "0.00"
    assert str(from_cents(5)) == "0.05"
