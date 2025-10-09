"""
Pytest configuration and fixtures.
"""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def mock_env_variables():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "GROQ_API_KEY": "test-api-key-mock"
    }):
        yield


@pytest.fixture
def sample_pass_document():
    """Load the sample passing document."""
    doc_path = Path(__file__).parent.parent / "data" / "sample_document_pass.txt"
    try:
        with open(doc_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        Policy Number: HM-2025-10-A4B
        Vessel: MV Neptune
        Start Date: 2025-11-01
        End Date: 2026-10-31
        Insured Value: $5,000,000
        """


@pytest.fixture
def sample_fail_document():
    """Load the sample failing document."""
    doc_path = Path(__file__).parent.parent / "data" / "sample_document_fail.txt"
    try:
        with open(doc_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        Vessel: The Wanderer
        Start Date: 2026-01-01
        End Date: 2025-12-31
        Insured Value: -$500
        """


@pytest.fixture
def valid_vessels():
    """Return a list of valid vessel names."""
    return ["MV Neptune", "Oceanic Voyager", "Starlight Carrier", "The Sea Serpent", "Ironclad Freighter"]
