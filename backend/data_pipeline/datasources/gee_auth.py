"""Google Earth Engine authentication helper."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
from config.settings import GEE_PROJECT_ID  # noqa: E402


def authenticate(project: str = None) -> None:
    """Authenticate to GEE using the configured project ID."""
    try:
        import ee
        proj = project or GEE_PROJECT_ID
        ee.Authenticate()
        ee.Initialize(project=proj)
        print("GEE authenticated successfully.")
    except Exception as e:
        print(f"GEE authentication failed: {e}")
        raise


if __name__ == "__main__":
    authenticate()
