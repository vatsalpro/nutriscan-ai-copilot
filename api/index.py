import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
BACKEND_API_DIR = BACKEND_DIR / "api"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if "api" in sys.modules:
    _api_pkg = sys.modules["api"]
    if hasattr(_api_pkg, "__path__") and str(BACKEND_API_DIR) not in _api_pkg.__path__:
        _api_pkg.__path__.insert(0, str(BACKEND_API_DIR))

from main import app
