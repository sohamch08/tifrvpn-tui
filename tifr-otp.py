#!/usr/bin/env python3
"""Compatibility launcher; reusable implementation lives in tifrvpn."""
from pathlib import Path
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    # A source checkout uses src; install.sh places the package under lib.
    sys.path.insert(0, str(root / ("src" if (root / "src/tifrvpn").is_dir() else "lib")))
    from tifrvpn.cli import otp_main
    raise SystemExit(otp_main())
