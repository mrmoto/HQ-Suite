"""
Pytest configuration and shared fixtures for DigiDoc tests.

This file is automatically discovered by pytest and provides:
- Shared fixtures for all tests
- Test configuration
- Common test utilities
"""

import pytest
import sys
from pathlib import Path

# Add ocr_service to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test utilities
from ocr_service.config import get_config, reload_config


@pytest.fixture(scope="session")
def config():
    """Load and return DigiDoc configuration."""
    return reload_config()


@pytest.fixture(scope="function")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
def sample_image_path(test_data_dir):
    """Return path to a sample test image."""
    # TODO: Add actual test image
    sample_path = test_data_dir / "sample_receipt.jpg"
    if not sample_path.exists():
        pytest.skip(f"Test image not found: {sample_path}")
    return sample_path


@pytest.fixture(scope="function")
def temp_queue_dir(tmp_path):
    """Create a temporary queue directory for testing."""
    queue_dir = tmp_path / "queue"
    queue_dir.mkdir()
    return queue_dir

