import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sds_batch import process_sds_batch

@pytest.mark.parametrize("run_id", [1, 2])
def test_process_sds_batch_missing_gcp_creds(run_id, monkeypatch):
    """
    Test that process_sds_batch handles missing GCP credentials
    by expecting the appropriate exception, with no mocking.
    """
    monkeypatch.delenv("GCP_CREDENTIALS", raising=False)
    with pytest.raises(ValueError, match="GCP_CREDENTIALS environment variable missing"):
        process_sds_batch()
