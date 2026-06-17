"""Tests IBKR connection via ib_insync. Requires TWS/IB Gateway running on port 7497."""
import pytest
from ib_insync import IB


@pytest.mark.integration
def test_ibkr_connection():
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
    assert ib.isConnected(), "IBKR connection failed"
    ib.disconnect()
