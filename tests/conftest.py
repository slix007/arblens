from __future__ import annotations

import sys
from pathlib import Path

# Ensure src-layout package is importable in tests without installing.
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
