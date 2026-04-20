"""Credential path discovery utilities.

This module provides flexible credential path discovery for Google API clients,
supporting multiple deployment scenarios and project structures.
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logger for credential discovery
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def find_credentials_path(
    explicit_path: Optional[Path] = None,
    filename: str = "credentials.json",
    env_var: str = "GOOGLE_CREDENTIALS_PATH",
    max_depth: int = 5,
    verbose: bool = True
) -> Path:
    """Find credentials file using multiple strategies with logging.
    
    This function searches for credentials in the following order:
    1. Explicit path parameter (if provided and exists)
    2. Environment variable (if set and file exists)
    3. Current working directory
    4. Walk up directory tree (max depth levels)
    
    This flexible approach allows the repository to be cloned into any
    project structure and still locate credentials properly.
    
    Args:
        explicit_path: Directly provided path to credentials file
        filename: Name of the credentials file to find (default: "credentials.json")
        env_var: Environment variable name to check (default: "GOOGLE_CREDENTIALS_PATH")
        max_depth: Maximum number of parent directories to search (default: 5)
        verbose: Enable detailed logging of search process (default: True)
        
    Returns:
        Path to credentials file
        
    Raises:
        FileNotFoundError: If credentials file is not found in any location
        ValueError: If credentials file is found but invalid
        
    Examples:
        >>> # Use default search
        >>> path = find_credentials_path()
        
        >>> # Provide explicit path
        >>> path = find_credentials_path(explicit_path=Path("/secure/creds.json"))
        
        >>> # Use environment variable
        >>> os.environ['GOOGLE_CREDENTIALS_PATH'] = '/path/to/creds.json'
        >>> path = find_credentials_path()
        
        >>> # Custom filename
        >>> path = find_credentials_path(filename="my_credentials.json")
    """
    if verbose:
        logger.info(f"🔍 Searching for {filename}...")
    
    search_log = []
    
    # Strategy 1: Explicit path (highest priority)
    if explicit_path is not None:
        explicit_path = Path(explicit_path)
        search_log.append(f"  1. Explicit path: {explicit_path}")
        if explicit_path.exists():
            if verbose:
                logger.info(f"✅ Found credentials via explicit path: {explicit_path}")
            _validate_credentials_file(explicit_path, verbose=verbose)
            return explicit_path.resolve()
        else:
            if verbose:
                logger.warning(f"❌ Explicit path does not exist: {explicit_path}")
    else:
        search_log.append(f"  1. Explicit path: (not provided)")
    
    # Strategy 2: Environment variable
    env_path_str = os.getenv(env_var)
    if env_path_str:
        env_path = Path(env_path_str)
        search_log.append(f"  2. Environment variable {env_var}: {env_path}")
        if env_path.exists():
            if verbose:
                logger.info(f"✅ Found credentials via environment variable: {env_path}")
            _validate_credentials_file(env_path, verbose=verbose)
            return env_path.resolve()
        else:
            if verbose:
                logger.warning(f"❌ Environment variable path does not exist: {env_path}")
    else:
        search_log.append(f"  2. Environment variable {env_var}: (not set)")
        if verbose:
            logger.debug(f"💡 Tip: You can set {env_var}=/path/to/{filename}")
    
    # Strategy 3: Current working directory
    cwd_path = Path.cwd() / filename
    search_log.append(f"  3. Current working directory: {Path.cwd()}")
    if cwd_path.exists():
        if verbose:
            logger.info(f"✅ Found credentials in current directory: {cwd_path}")
        _validate_credentials_file(cwd_path, verbose=verbose)
        return cwd_path.resolve()
    else:
        if verbose:
            logger.debug(f"   Not found in: {cwd_path}")
    
    # Strategy 4: Walk up directory tree
    if verbose:
        logger.debug(f"  4. Searching parent directories (up to {max_depth} levels)...")
    
    current = Path.cwd()
    for level in range(max_depth):
        candidate = current / filename
        if verbose:
            logger.debug(f"     Checking: {candidate}")
        
        if candidate.exists():
            if verbose:
                logger.info(f"✅ Found credentials {level + 1} level(s) up: {candidate}")
            _validate_credentials_file(candidate, verbose=verbose)
            return candidate.resolve()
        
        # Check if we've reached the filesystem root
        parent = current.parent
        if parent == current:
            if verbose:
                logger.debug(f"     Reached filesystem root")
            break
        current = parent
    
    search_log.append(f"  4. Parent directories: (searched up to {max_depth} levels)")
    
    # Credentials not found - raise detailed error with helpful instructions
    error_msg = _build_credentials_not_found_error(
        filename=filename,
        env_var=env_var,
        search_log=search_log,
        explicit_path=explicit_path,
        env_path_str=env_path_str
    )
    
    logger.error("❌ Credentials not found!")
    raise FileNotFoundError(error_msg)


def _validate_credentials_file(path: Path, verbose: bool = True) -> None:
    """Validate that a credentials file is properly formatted.
    
    Args:
        path: Path to credentials file to validate
        verbose: Enable logging
        
    Raises:
        ValueError: If credentials file is invalid
    """
    try:
        with open(path, 'r') as f:
            creds_data = json.load(f)
        
        # Check for required fields based on credential type
        if 'installed' in creds_data or 'web' in creds_data:
            # OAuth2 credentials
            credential_type = 'installed' if 'installed' in creds_data else 'web'
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            
            cred_section = creds_data.get(credential_type, {})
            missing_fields = [f for f in required_fields if f not in cred_section]
            
            if missing_fields:
                raise ValueError(
                    f"Credentials file is missing required fields: {', '.join(missing_fields)}\n"
                    f"Please download a valid credentials file from Google Cloud Console."
                )
            
            if verbose:
                logger.info(f"✓ Credentials file is valid OAuth2 format ({credential_type})")
        else:
            # Unknown format
            if verbose:
                logger.warning(
                    "⚠️  Credentials file format not recognized. "
                    "Expected 'installed' or 'web' OAuth2 format."
                )
    
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Credentials file is not valid JSON: {e}\n"
            f"Please ensure you downloaded the correct file from Google Cloud Console."
        )
    except Exception as e:
        if verbose:
            logger.warning(f"⚠️  Could not fully validate credentials: {e}")


def _build_credentials_not_found_error(
    filename: str,
    env_var: str,
    search_log: list,
    explicit_path: Optional[Path],
    env_path_str: Optional[str]
) -> str:
    """Build a detailed, helpful error message for missing credentials.
    
    Args:
        filename: Name of credentials file
        env_var: Environment variable name
        search_log: List of searched locations
        explicit_path: Explicit path provided (if any)
        env_path_str: Environment variable value (if set)
        
    Returns:
        Formatted error message with instructions
    """
    error_parts = [
        f"\n{'='*70}",
        f"❌ CREDENTIALS NOT FOUND: {filename}",
        f"{'='*70}\n",
        "Searched locations:",
        *search_log,
        "",
        "="*70,
        "📋 HOW TO FIX THIS:",
        "="*70,
        "",
        "Option 1: Place credentials in your project directory",
        f"  • Download from: https://console.cloud.google.com/apis/credentials",
        f"  • Save as: {filename}",
        f"  • Put in: {Path.cwd()}",
        "",
        "Option 2: Use environment variable (recommended for production)",
        f"  • export {env_var}=/path/to/{filename}",
        "  • Or add to your .env file or shell profile",
        "",
        "Option 3: Pass path explicitly in code",
        "  • client = GmailClient(credentials_path='/path/to/credentials.json')",
        "",
        "="*70,
        "🔧 SETUP INSTRUCTIONS:",
        "="*70,
        "",
        "1. Go to https://console.cloud.google.com/",
        "2. Create or select a project",
        "3. Enable Gmail API and/or Calendar API",
        "4. Go to 'APIs & Services' > 'Credentials'",
        "5. Click 'Create Credentials' > 'OAuth client ID'",
        "6. Choose 'Desktop app'",
        "7. Download the JSON file",
        f"8. Rename it to '{filename}'",
        "9. Place it in one of the locations above",
        "",
        "="*70,
        "📚 For more help, see: CREDENTIALS_SETUP.md",
        "="*70,
    ]
    
    return "\n".join(error_parts)


def find_token_path(
    credentials_path: Path,
    explicit_token_path: Optional[Path] = None,
    token_filename: str = "token.json"
) -> Path:
    """Determine token file path based on credentials location.
    
    By default, the token file is placed in the same directory as credentials.
    This keeps authentication files together and works regardless of project structure.
    
    Args:
        credentials_path: Path where credentials.json was found
        explicit_token_path: Optional explicit path for token file
        token_filename: Name of the token file (default: "token.json")
        
    Returns:
        Path where token file should be stored
        
    Examples:
        >>> creds = Path("/project/credentials.json")
        >>> token = find_token_path(creds)
        >>> # Returns: Path("/project/token.json")
        
        >>> token = find_token_path(creds, explicit_token_path=Path("/custom/token.json"))
        >>> # Returns: Path("/custom/token.json")
    """
    if explicit_token_path is not None:
        return Path(explicit_token_path).resolve()
    
    # Place token in same directory as credentials
    return (credentials_path.parent / token_filename).resolve()
