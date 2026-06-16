#!/usr/bin/env python3
"""Entry point for running quant-trade from the project root."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "skills" / "quant-trade" / "scripts"))

from main import main

if __name__ == "__main__":
    main()
