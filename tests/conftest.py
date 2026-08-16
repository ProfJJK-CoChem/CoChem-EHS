import os
import pytest

@pytest.fixture(autouse=True)
def setup_cochem_env():
    # Set the data directory to the actual data directory in the repo
    repo_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
    os.environ["COCHEM_DATA_DIR"] = repo_data_dir
    os.environ["ARTIFACTS_DIR"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../artifacts'))
