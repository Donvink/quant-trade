"""Integration tests for the full quant-trade pipeline."""
import sys
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "quant_trade"))


@pytest.mark.integration
def test_imports():
    from core.config import RPS_THRESHOLD, RPS_PERIODS, MAX_BUY, MAX_OWN
    from core.data_manager import DataManager
    from core.stock_pool import get_sp500_symbols
    from analysis.screener import get_candidates_for_date
    from analysis.backtest import backtest
    assert RPS_THRESHOLD > 0
    assert len(RPS_PERIODS) == 3


@pytest.mark.integration
@pytest.mark.slow
def test_data_download():
    from core.data_manager import DataManager
    from core.stock_pool import get_sp500_symbols
    dm = DataManager()
    symbols = get_sp500_symbols()[:3]
    dm.download_full_history(symbols, years_back=1)
    for sym in symbols:
        df = dm.get_data(sym)
        assert not df.empty, f"No data downloaded for {sym}"
    dm.close()


@pytest.mark.integration
def test_dry_run_trade():
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "run.py"), "--step", "trade", "--dry-run"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"dry-run trade failed:\n{result.stderr}"
