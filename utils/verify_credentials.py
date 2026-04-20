"""Credential verification utility for Google API clients.

This script helps diagnose credential and authentication issues.
Run this before using Gmail or Calendar clients to ensure proper setup.
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

from ..utils.credentials import find_credentials_path

# Configure colorful logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def verify_credentials_setup(verbose: bool = True) -> Dict[str, Any]:
    """Verify that Google API credentials are properly set up.
    
    Args:
        verbose: Print detailed information during verification
        
    Returns:
        Dictionary with verification results
    """
    results = {
        'success': False,
        'credentials_found': False,
        'credentials_valid': False,
        'credentials_path': None,
        'token_exists': False,
        'token_path': None,
        'issues': [],
        'warnings': []
    }
    
    if verbose:
        print("\n" + "="*70)
        print("🔐 GOOGLE API CREDENTIALS VERIFICATION")
        print("="*70 + "\n")
    
    # Step 1: Find credentials file
    if verbose:
        print("Step 1: Locating credentials.json...")
        print("-" * 70)
    
    try:
        creds_path = find_credentials_path(verbose=verbose)
        results['credentials_found'] = True
        results['credentials_path'] = str(creds_path)
        
        if verbose:
            print()
    
    except FileNotFoundError as e:
        results['issues'].append("Credentials file not found")
        if verbose:
            print(f"\n{e}\n")
        return results
    
    # Step 2: Validate credentials file
    if verbose:
        print("\nStep 2: Validating credentials file...")
        print("-" * 70)
    
    try:
        validation_result = _validate_credentials_detailed(creds_path, verbose=verbose)
        results['credentials_valid'] = validation_result['valid']
        results['issues'].extend(validation_result.get('errors', []))
        results['warnings'].extend(validation_result.get('warnings', []))
        
    except Exception as e:
        results['issues'].append(f"Error validating credentials: {e}")
        if verbose:
            print(f"❌ Error: {e}\n")
        return results
    
    # Step 3: Check for token file
    if verbose:
        print("\nStep 3: Checking for existing auth token...")
        print("-" * 70)
    
    token_path = creds_path.parent / "token.json"
    results['token_path'] = str(token_path)
    
    if token_path.exists():
        results['token_exists'] = True
        if verbose:
            print(f"✅ Token file found: {token_path}")
            print("   You are already authenticated!")
        
        # Validate token if it exists
        try:
            _validate_token_file(token_path, verbose=verbose)
        except Exception as e:
            results['warnings'].append(f"Token validation warning: {e}")
    else:
        if verbose:
            print(f"ℹ️  No token file found at: {token_path}")
            print("   This is normal for first-time setup.")
            print("   A token will be created when you first use the client.")
    
    # Step 4: Check API enablement (cannot verify without attempting auth)
    if verbose:
        print("\nStep 4: API Configuration Check...")
        print("-" * 70)
        print("⚠️  Cannot verify API enablement without authentication attempt.")
        print("   Please ensure you have enabled the required APIs:")
        print("   • Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com")
        print("   • Calendar API: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com")
    
    # Summary
    if verbose:
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        print(f"Credentials found: {'✅ Yes' if results['credentials_found'] else '❌ No'}")
        print(f"Credentials valid: {'✅ Yes' if results['credentials_valid'] else '❌ No'}")
        print(f"Token exists: {'✅ Yes' if results['token_exists'] else 'ℹ️  No (will be created on first use)'}")
        
        if results['issues']:
            print(f"\n❌ Issues found: {len(results['issues'])}")
            for issue in results['issues']:
                print(f"   • {issue}")
        
        if results['warnings']:
            print(f"\n⚠️  Warnings: {len(results['warnings'])}")
            for warning in results['warnings']:
                print(f"   • {warning}")
        
        if results['credentials_found'] and results['credentials_valid'] and not results['issues']:
            print("\n✅ Setup looks good! You should be able to use the Gmail/Calendar clients.")
            results['success'] = True
        else:
            print("\n❌ Setup incomplete. Please address the issues above.")
        
        print("="*70 + "\n")
    
    return results


def _validate_credentials_detailed(path: Path, verbose: bool = True) -> Dict[str, Any]:
    """Perform detailed validation of credentials file.
    
    Args:
        path: Path to credentials file
        verbose: Print details
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'credential_type': None,
        'project_id': None,
        'client_id': None
    }
    
    try:
        with open(path, 'r') as f:
            creds_data = json.load(f)
        
        # Determine credential type
        if 'installed' in creds_data:
            result['credential_type'] = 'installed (Desktop app)'
            cred_section = creds_data['installed']
        elif 'web' in creds_data:
            result['credential_type'] = 'web'
            cred_section = creds_data['web']
        else:
            result['errors'].append(
                "Invalid credentials format. Expected 'installed' or 'web' OAuth2 credentials."
            )
            if verbose:
                print("❌ Invalid format: Missing 'installed' or 'web' section")
            return result
        
        # Check required fields
        required_fields = {
            'client_id': 'OAuth2 Client ID',
            'client_secret': 'OAuth2 Client Secret',
            'auth_uri': 'Authorization URI',
            'token_uri': 'Token URI',
            'redirect_uris': 'Redirect URIs'
        }
        
        missing = []
        for field, description in required_fields.items():
            if field not in cred_section:
                missing.append(description)
        
        if missing:
            result['errors'].append(f"Missing required fields: {', '.join(missing)}")
            if verbose:
                print(f"❌ Missing fields: {', '.join(missing)}")
            return result
        
        # Extract useful info
        result['client_id'] = cred_section.get('client_id', '')
        result['project_id'] = cred_section.get('project_id', 'Unknown')
        
        if verbose:
            print(f"✅ Valid OAuth2 format: {result['credential_type']}")
            print(f"   Project ID: {result['project_id']}")
            print(f"   Client ID: {result['client_id'][:20]}...{result['client_id'][-10:]}")
        
        # Check if it's a test/localhost setup
        redirect_uris = cred_section.get('redirect_uris', [])
        if any('localhost' in uri or '127.0.0.1' in uri for uri in redirect_uris):
            if verbose:
                print("   ✓ Configured for local development")
        
        result['valid'] = True
        
    except json.JSONDecodeError as e:
        result['errors'].append(f"Invalid JSON format: {e}")
        if verbose:
            print(f"❌ Invalid JSON: {e}")
    except Exception as e:
        result['errors'].append(f"Unexpected error: {e}")
        if verbose:
            print(f"❌ Error: {e}")
    
    return result


def _validate_token_file(path: Path, verbose: bool = True) -> None:
    """Validate token file if it exists.
    
    Args:
        path: Path to token file
        verbose: Print details
    """
    try:
        with open(path, 'r') as f:
            token_data = json.load(f)
        
        required_token_fields = ['token', 'refresh_token', 'token_uri', 'client_id']
        missing = [f for f in required_token_fields if f not in token_data]
        
        if missing:
            if verbose:
                print(f"   ⚠️  Token file may be incomplete (missing: {', '.join(missing)})")
        else:
            if verbose:
                print("   ✓ Token file structure looks valid")
        
        # Check expiry
        if 'expiry' in token_data:
            if verbose:
                print(f"   ✓ Token has expiry information")
        
    except json.JSONDecodeError:
        if verbose:
            print("   ⚠️  Token file is not valid JSON (may need re-authentication)")
    except Exception as e:
        if verbose:
            print(f"   ⚠️  Could not validate token: {e}")


def print_setup_guide():
    """Print a quick setup guide."""
    guide = """
╔══════════════════════════════════════════════════════════════════════╗
║                   QUICK SETUP GUIDE                                  ║
╚══════════════════════════════════════════════════════════════════════╝

1️⃣  GET CREDENTIALS
   → Visit: https://console.cloud.google.com/apis/credentials
   → Create OAuth 2.0 Client ID (Desktop app)
   → Download as credentials.json

2️⃣  ENABLE APIs
   Gmail: https://console.cloud.google.com/apis/library/gmail.googleapis.com
   Calendar: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com

3️⃣  PLACE CREDENTIALS
   Option A: In your project directory
   Option B: Set GOOGLE_CREDENTIALS_PATH environment variable
   Option C: Pass explicit path in code

4️⃣  FIRST RUN
   • The client will open a browser for authentication
   • Approve the requested permissions
   • token.json will be created automatically
   • Subsequent runs will use the saved token

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 For detailed instructions, see: CREDENTIALS_SETUP.md
"""
    print(guide)


if __name__ == "__main__":
    """Run verification when script is executed directly."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify Google API credentials setup for Gmail and Calendar clients"
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress detailed output'
    )
    parser.add_argument(
        '--guide', '-g',
        action='store_true',
        help='Print setup guide'
    )
    
    args = parser.parse_args()
    
    if args.guide:
        print_setup_guide()
        sys.exit(0)
    
    try:
        result = verify_credentials_setup(verbose=not args.quiet)
        sys.exit(0 if result['success'] else 1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
