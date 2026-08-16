import os
from pathlib import Path

def get_artifacts_dir() -> Path:
    """Get the configurable artifacts directory."""
    artifacts_dir = Path(os.environ.get("ARTIFACTS_DIR", Path.home() / "cochem_artifacts"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir

def get_data_dir() -> Path:
    """Get the configurable data directory."""
    data_dir = Path(os.environ.get("COCHEM_DATA_DIR", Path.home() / "cochem_data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
