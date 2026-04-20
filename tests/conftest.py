"""Pytest configuration and fixtures for all tests."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env
load_dotenv()


@pytest.fixture(scope="session")
def credentials_path() -> Path:
    """Get the path to Google API credentials.
    
    Returns:
        Path to credentials.json file
        
    Raises:
        pytest.skip: If credentials are not configured
    """
    creds_path_str = os.getenv('GOOGLE_CREDENTIALS_PATH')
    
    if not creds_path_str:
        pytest.skip("GOOGLE_CREDENTIALS_PATH not set in environment")
    
    creds_path = Path(creds_path_str)
    
    if not creds_path.exists():
        pytest.skip(f"Credentials file not found at: {creds_path}")
    
    return creds_path


@pytest.fixture(scope="session")
def gmail_client():
    """Create a Gmail client for integration tests.
    
    Returns:
        GmailClient instance
        
    Raises:
        pytest.skip: If Gmail client cannot be initialized
    """
    try:
        from gmail.gmail_client import GmailClient
        client = GmailClient()
        return client
    except Exception as e:
        pytest.skip(f"Failed to initialize Gmail client: {e}")


@pytest.fixture(scope="session")
def calendar_client():
    """Create a Google Calendar client for integration tests.
    
    Returns:
        GoogleCalendarClient instance
        
    Raises:
        pytest.skip: If Calendar client cannot be initialized
    """
    try:
        from gcalendar.google_cal import GoogleCalendarClient
        client = GoogleCalendarClient()
        return client
    except Exception as e:
        pytest.skip(f"Failed to initialize Calendar client: {e}")


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for filesystem tests.
    
    Yields:
        Path to temporary directory
        
    Cleanup:
        Removes the temporary directory after test completes
    """
    with tempfile.TemporaryDirectory(prefix="common_tools_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def filesystem_client(temp_test_dir):
    """Create a FileSystemClient with temp directory as base.
    
    Args:
        temp_test_dir: Temporary directory fixture
        
    Returns:
        FileSystemClient instance
    """
    from filesystem.filesystem_client import FileSystemClient
    return FileSystemClient(base_path=temp_test_dir)


@pytest.fixture(scope="session")
def safe_mode() -> bool:
    """Check if tests should run in safe mode.
    
    In safe mode, tests that modify real data (send emails, delete events)
    are skipped or use mock operations.
    
    Returns:
        True if safe mode is enabled (default: True)
    """
    # Default to safe mode unless explicitly disabled
    return os.getenv('TEST_SAFE_MODE', 'true').lower() != 'false'


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires API credentials)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "modifies_data: mark test as modifying real user data"
    )
