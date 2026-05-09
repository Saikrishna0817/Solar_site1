"""GEE authentication & retry helper."""
import sys
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable

_project_root = Path(__file__).parent.parent.absolute()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
from config.settings import GEE_PROJECT_ID  # noqa: E402


def init_gee(project: str = None, max_attempts: int = 3) -> bool:
    """Initialise Google Earth Engine with project ID (env-aware)."""
    try:
        import ee
        proj = project or GEE_PROJECT_ID
        ee.Initialize(project=proj)
        print(f"GEE initialised for project={proj}")
        return True
    except Exception as exc:
        print(f"GEE init failed: {exc}")
        return False


def gee_retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator that retries a GEE function on EarthEngineException."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    print(f"[attempt {attempt}/{max_attempts}] {func.__name__} raised: {exc}")
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay * attempt)
            return None
        return wrapper
    return decorator
