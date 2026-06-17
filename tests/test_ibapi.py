"""Tests IBKR connection via ibapi (low-level). Requires TWS/IB Gateway running on port 7497."""
import threading
import time
import pytest
from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class _IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False

    def nextValidId(self, orderId):
        self.connected = True
        self.disconnect()


@pytest.mark.integration
def test_ibkr_connection_low_level():
    app = _IBApp()
    app.connect('127.0.0.1', 7497, clientId=2)
    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()
    thread.join(timeout=10)
    assert app.connected, "IBKR low-level connection failed (nextValidId not received)"
