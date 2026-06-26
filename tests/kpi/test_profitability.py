import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.ratios import (
    net_profit_margin,
    return_on_equity,
    operating_profit_margin,
)


def test_net_profit_margin():
    assert net_profit_margin(100, 500) == 20.0


def test_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_negative_equity():
    assert return_on_equity(100, -50, -100) is None


def test_operating_profit_margin():
    assert operating_profit_margin(250, 1000) == 25.0