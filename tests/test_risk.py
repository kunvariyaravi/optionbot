"""Risk engine tests: limits gate every order, kill switch halts all."""
import pytest

from optionbot.execution.paper import PaperPortfolio
from optionbot.risk.kill_switch import KillSwitch
from optionbot.risk.limits import RiskConfig, check_order, position_qty


def test_position_qty_fractional():
    assert position_qty(100000, 1.0, 20.0) == 50
    with pytest.raises(ValueError):
        position_qty(100000, 1.0, 0)


def test_qty_limit_blocks():
    cfg = RiskConfig(max_position_qty=100)
    assert check_order(50, 0, False, cfg)[0] is True
    assert check_order(101, 0, False, cfg)[0] is False


def test_daily_loss_blocks():
    cfg = RiskConfig(max_daily_loss=5000)
    assert check_order(10, -6000, False, cfg)[0] is False


def test_kill_switch_blocks_and_portfolio_enforces():
    kill = KillSwitch()
    kill.engage("test")
    pf = PaperPortfolio(kill=kill)
    with pytest.raises(RuntimeError, match="kill switch"):
        pf.buy("NIFTY", 25000, "CE", 50, 100.0)


def test_paper_buy_reduces_capital():
    pf = PaperPortfolio(capital=100000)
    pf.buy("NIFTY", 25000, "CE", 50, 100.0)
    assert pf.capital == pytest.approx(95000.0)
    assert pf.summary()["open_positions"] == 1
