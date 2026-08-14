"""Pytest path setup for the repo's package layout.

This ensures both the repository root and the `backend` folder are importable
when running tests from the project root without requiring a custom shell
environment.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"

for path in (str(ROOT), str(BACKEND)):
    if path not in sys.path:
        sys.path.insert(0, path)
