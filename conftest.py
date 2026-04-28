"""Root conftest.py to handle Windows compatibility."""

# This must be the FIRST thing that runs to mock fcntl for Windows
import sys
from unittest.mock import MagicMock

# Mock fcntl module (Unix-only, not available on Windows)
if "fcntl" not in sys.modules:
    sys.modules["fcntl"] = MagicMock()
