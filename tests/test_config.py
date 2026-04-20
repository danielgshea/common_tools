"""Test configuration and utilities."""

import os
from pathlib import Path
from typing import Optional


class TestConfig:
    """Configuration for integration tests."""
    
    def __init__(self):
        """Initialize test configuration from environment."""
        self.credentials_path: Optional[str] = os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.safe_mode: bool = os.getenv('TEST_SAFE_MODE', 'true').lower() != 'false'
        self.verbose: bool = os.getenv('TEST_VERBOSE', 'false').lower() == 'true'
        
    def has_credentials(self) -> bool:
        """Check if credentials are configured and exist."""
        if not self.credentials_path:
            return False
        return Path(self.credentials_path).exists()
    
    def __repr__(self) -> str:
        return (
            f"TestConfig(credentials={'configured' if self.has_credentials() else 'missing'}, "
            f"safe_mode={self.safe_mode}, verbose={self.verbose})"
        )


# Global config instance
config = TestConfig()
