import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.ratios import *


def test_net_profit_margin():
    assert net_profit_margin(100, 500) == 20.0


def test_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_negative_equity():
    assert return_on_equity(100, -50, -100) is None


def test_operating_profit_margin():
    assert operating_profit_margin(250, 1000) == 25.0


def test_return_on_equity():
    assert return_on_equity(100, 200, 300) == 20.0


def test_return_on_assets():
    assert return_on_assets(50, 500) == 10.0


def test_roa_zero_assets():
    assert return_on_assets(50, 0) is None


def test_opm_cross_check():
    assert opm_cross_check(20.5, 18.0) is True