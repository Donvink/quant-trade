#!/usr/bin/env python3
"""Entry point for quant-trade."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "quant_trade"))

from main import main

if __name__ == "__main__":
    main()
