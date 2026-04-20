"""Gmail API client for managing email operations.

This module provides a clean interface to interact with the Gmail API,
handling authentication and common email operations.
"""
import base64
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, List, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logger
logger = logging.getLogger(__name__)


# If modifying these scopes, delete the token.json file.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]


class GmailClient:
    """Client for interacting with Gmail API."""
    
    def __init__(self, credentials_path: Optional[Path] = None, token_path: Optional[Path] = None):
        """Initialize the Gmail client.
        
        Args:
            credentials_path: Path to credentials.json file (optional).
                If not provided, searches in this order:
                1. GOOGLE_CREDENTIALS_PATH environment variable
                2. Current working directory
                3. Parent directories (up to 5 levels)
            token_path: Path to token.json file (optional).
                If not provided, uses same directory as credentials.json
            
        Raises:
            FileNotFoundError: If credentials.json cannot be found.
            
        Environment Variables:
            GOOGLE_CREDENTIALS_PATH: Path to credentials.json file
            
        Examples:
            >>> # Use default search
            >>> client = GmailClient()
            
            >>> # Explicit path
            >>> client = GmailClient(credentials_path=Path("/secure/credentials.json"))
            
            >>> # Via environment variable
            >>> os.environ['GOOGLE_CREDENTIALS_PATH'] = '/path/to/credentials.json'
            >>> client = GmailClient()
        """
        # Robust import that works in all contexts:
        # 1. As subdirectory in parent project (relative import)
        # 2. Standalone/testing (absolute import)
        # 3. Direct execution (sys.path fallback)
        try:
            from ..utils.credentials import find_credentials_path, find_token_path
        except (ImportError, ValueError):
            # Fallback for standalone usage or testing
            try:
                from utils.credentials import find_credentials_path, find_token_path
            except ImportError:
                # Last resort: add parent to path
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from utils.credentials import find_credentials_path, find_token_path
        
        # Find credentials using flexible search strategy
        self.credentials_path = find_credentials_path(
            explicit_path=credentials_path,
            filename="credentials.json",
            env_var="GOOGLE_CREDENTIALS_PATH"
        )
        
        # Determine token path (same directory as credentials by default)
        self.token_path = find_token_path(
            credentials_path=self.credentials_path,
            explicit_token_path=token_path,
            token_filename="token.json"
        )
        
        self._service = None
    
    def _get_credentials(self) -> Credentials:
        """Get valid credentials for Gmail API with enhanced error handling.
        
        Returns:
            Valid credentials object.
            
        Raises:
            FileNotFoundError: If credentials.json is not found.
            ValueError: If credentials are invalid or APIs not enabled.
            RuntimeError: If authentication fails.
        """
        creds = None
        
        # The token.json stores the user's access and refresh tokens
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
                logger.debug(f"Loaded credentials from token: {self.token_path}")
            except Exception as e:
                logger.warning(f"Failed to load token file: {e}")
                logger.info("Will attempt to re-authenticate...")
                # Delete invalid token and force re-auth
                self.token_path.unlink(missing_ok=True)
                creds = None
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                    logger.info("✅ Credentials refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {e}")
                    logger.info("Will attempt to re-authenticate...")
                    # Delete invalid token and force re-auth
                    self.token_path.unlink(missing_ok=True)
                    creds = None
            
            if not creds:
                # Need to authenticate
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"credentials.json not found at {self.credentials_path}. "
                        "Please download it from Google Cloud Console and place it in the project root."
                    )
                
                try:
                    logger.info("🔐 Starting OAuth2 authentication flow...")
                    logger.info("A browser window will open for you to authorize the application.")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                    
                    logger.info("✅ Authentication successful!")
                    
                except Exception as e:
                    error_msg = self._build_auth_error_message(e)
                    logger.error(error_msg)
                    raise RuntimeError(error_msg) from e
            
            # Save the credentials for the next run
            try:
                self.token_path.write_text(creds.to_json())
                logger.debug(f"Saved credentials to: {self.token_path}")
            except Exception as e:
                logger.warning(f"Failed to save token file: {e}")
                logger.warning("Authentication succeeded but token won't persist.")
        
        return creds
    
    def _build_auth_error_message(self, error: Exception) -> str:
        """Build a helpful error message for authentication failures.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Formatted error message with troubleshooting steps
        """
        error_str = str(error).lower()
        
        # Check for common error patterns
        if 'access_denied' in error_str:
            return (
                "\n❌ Authentication Failed: Access Denied\n"
                "\nYou denied the authorization request or the consent screen was not completed.\n"
                "\nTo fix this:\n"
                "  1. Run the authentication flow again\n"
                "  2. Make sure to click 'Allow' when prompted\n"
                "  3. Approve all requested permissions\n"
            )
        
        elif 'invalid_client' in error_str or 'invalid_grant' in error_str:
            return (
                "\n❌ Authentication Failed: Invalid Credentials\n"
                "\nYour credentials.json file may be invalid, expired, or revoked.\n"
                "\nTo fix this:\n"
                "  1. Go to https://console.cloud.google.com/apis/credentials\n"
                "  2. Delete the old OAuth 2.0 Client ID\n"
                "  3. Create a new one (Desktop app type)\n"
                "  4. Download the new credentials.json\n"
                f"  5. Replace the file at: {self.credentials_path}\n"
                f"  6. Delete the token file: {self.token_path}\n"
                "  7. Try again\n"
            )
        
        elif 'redirect_uri_mismatch' in error_str:
            return (
                "\n❌ Authentication Failed: Redirect URI Mismatch\n"
                "\nThe OAuth client is not configured for localhost redirects.\n"
                "\nTo fix this:\n"
                "  1. Go to https://console.cloud.google.com/apis/credentials\n"
                "  2. Edit your OAuth 2.0 Client ID\n"
                "  3. Ensure 'Desktop app' is selected (not Web)\n"
                "  4. Or manually add http://localhost redirects to authorized URIs\n"
                "  5. Download updated credentials.json\n"
            )
        
        elif 'api not enabled' in error_str or '403' in error_str:
            return (
                "\n❌ Authentication Failed: API Not Enabled\n"
                "\nThe Gmail API may not be enabled for your project.\n"
                "\nTo fix this:\n"
                "  1. Go to https://console.cloud.google.com/apis/library/gmail.googleapis.com\n"
                "  2. Click 'Enable' for the Gmail API\n"
                "  3. Wait a few minutes for changes to propagate\n"
                "  4. Try again\n"
                "\nFor Calendar: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com\n"
            )
        
        else:
            return (
                f"\n❌ Authentication Failed: {error}\n"
                "\nTroubleshooting steps:\n"
                "  1. Ensure Gmail API is enabled in Google Cloud Console\n"
                "  2. Check that credentials.json is valid and not expired\n"
                "  3. Try deleting token.json and re-authenticating\n"
                f"  4. Run: python -m utils.verify_credentials\n"
                "\nFor more help, see: CREDENTIALS_SETUP.md\n"
            )
    
    @property
    def service(self):
        """Get or create the Gmail API service instance.
        
        Returns:
            Gmail API service instance.
        """
        if self._service is None:
            creds = self._get_credentials()
            self._service = build('gmail', 'v1', credentials=creds)
        return self._service
    
    def _parse_message_headers(self, headers: List[Dict[str, str]]) -> Dict[str, str]:
        """Parse message headers into a dictionary.
        
        Args:
            headers: List of header dictionaries from Gmail API
            
        Returns:
            Dictionary with common headers (From, To, Subject, Date, etc.)
        """
        header_dict = {}
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            if name in ['from', 'to', 'subject', 'date', 'cc', 'bcc', 'reply-to', 'message-id']:
                header_dict[name] = value
        return header_dict
    
    def _decode_body(self, part: Dict[str, Any]) -> str:
        """Decode message body from base64url encoding.
        
        Args:
            part: Message part containing body data
            
        Returns:
            Decoded body text
        """
        if 'data' in part.get('body', {}):
            data = part['body']['data']
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            return decoded
        return ""
    
    def _get_message_body(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Extract plain text and HTML body from message payload.
        
        Args:
            payload: Message payload from Gmail API
            
        Returns:
            Dictionary with 'plain' and 'html' body content
        """
        body = {'plain': '', 'html': ''}
        
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/plain':
                    body['plain'] += self._decode_body(part)
                elif mime_type == 'text/html':
                    body['html'] += self._decode_body(part)
                elif mime_type.startswith('multipart/'):
                    # Recursively handle multipart messages
                    if 'parts' in part:
                        sub_body = self._get_message_body(part)
                        body['plain'] += sub_body['plain']
                        body['html'] += sub_body['html']
        else:
            # Single part message
            mime_type = payload.get('mimeType', '')
            if mime_type == 'text/plain':
                body['plain'] = self._decode_body(payload)
            elif mime_type == 'text/html':
                body['html'] = self._decode_body(payload)
        
        return body
    
    def list_messages(
        self,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        max_results: int = 10,
        include_spam_trash: bool = False
    ) -> List[Dict[str, Any]]:
        """List messages from Gmail inbox with full details.
        
        Args:
            query: Gmail search query (e.g., "is:unread", "from:user@example.com")
            label_ids: List of label IDs to filter by (e.g., ["INBOX", "UNREAD"])
            max_results: Maximum number of messages to return (default: 10)
            include_spam_trash: Include spam and trash in results (default: False)
            
        Returns:
            List of message dictionaries with details (id, threadId, subject, from, to, date, snippet)
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'includeSpamTrash': include_spam_trash
            }
            
            if query:
                params['q'] = query
            if label_ids:
                params['labelIds'] = label_ids
            
            results = self.service.users().messages().list(**params).execute()
            messages = results.get('messages', [])
            
            # Fetch full details for each message
            message_list = []
            for msg in messages:
                try:
                    # Get message with metadata format (headers but no body)
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'To', 'Subject', 'Date']
                    ).execute()
                    
                    # Parse headers
                    headers = self._parse_message_headers(full_msg.get('payload', {}).get('headers', []))
                    
                    message_list.append({
                        'id': full_msg['id'],
                        'threadId': full_msg['threadId'],
                        'snippet': full_msg.get('snippet', ''),
                        'from': headers.get('from', ''),
                        'to': headers.get('to', ''),
                        'subject': headers.get('subject', ''),
                        'date': headers.get('date', ''),
                        'labelIds': full_msg.get('labelIds', [])
                    })
                except HttpError:
                    # If we can't get details for a message, skip it
                    continue
            
            return message_list
            
        except HttpError as error:
            raise error
    
    def get_message(self, message_id: str, format: str = 'full') -> Dict[str, Any]:
        """Get full message details by ID.
        
        Args:
            message_id: The message ID to retrieve
            format: Message format ('full', 'metadata', 'minimal', 'raw')
            
        Returns:
            Dictionary with complete message details including headers and body
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format=format
            ).execute()
            
            # Parse the message
            parsed = {
                'id': message['id'],
                'threadId': message['threadId'],
                'labelIds': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'internalDate': message.get('internalDate', '')
            }
            
            if format in ['full', 'metadata']:
                payload = message.get('payload', {})
                headers = self._parse_message_headers(payload.get('headers', []))
                parsed['headers'] = headers
                parsed['from'] = headers.get('from', '')
                parsed['to'] = headers.get('to', '')
                parsed['subject'] = headers.get('subject', '')
                parsed['date'] = headers.get('date', '')
                
                if format == 'full':
                    body = self._get_message_body(payload)
                    parsed['body'] = body
            
            return parsed
            
        except HttpError as error:
            raise error
    
    def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """Send a new email message.
        
        Args:
            to: Recipient email address (can be comma-separated for multiple)
            subject: Email subject
            body: Email body content
            cc: CC recipients (optional, comma-separated)
            bcc: BCC recipients (optional, comma-separated)
            html: If True, send as HTML email (default: False for plain text)
            
        Returns:
            Dictionary with sent message details (id, threadId, labelIds)
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            message = MIMEMultipart() if html else MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            if html:
                message.attach(MIMEText(body, 'html'))
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return {
                'id': sent_message['id'],
                'threadId': sent_message['threadId'],
                'labelIds': sent_message.get('labelIds', [])
            }
            
        except HttpError as error:
            raise error
    
    def reply_to_message(
        self,
        message_id: str,
        body: str,
        html: bool = False
    ) -> Dict[str, Any]:
        """Reply to an existing message.
        
        Args:
            message_id: The ID of the message to reply to
            body: Reply body content
            html: If True, send as HTML email (default: False)
            
        Returns:
            Dictionary with sent reply details
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            # Get the original message to extract headers
            original = self.get_message(message_id, format='metadata')
            headers = original['headers']
            
            message = MIMEMultipart() if html else MIMEText(body)
            message['to'] = headers.get('from', '')
            message['subject'] = 'Re: ' + headers.get('subject', '').replace('Re: ', '')
            message['In-Reply-To'] = headers.get('message-id', '')
            message['References'] = headers.get('message-id', '')
            
            if html:
                message.attach(MIMEText(body, 'html'))
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={
                    'raw': raw,
                    'threadId': original['threadId']
                }
            ).execute()
            
            return {
                'id': sent_message['id'],
                'threadId': sent_message['threadId'],
                'labelIds': sent_message.get('labelIds', [])
            }
            
        except HttpError as error:
            raise error
    
    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """Create a draft email message.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html: If True, create as HTML email (default: False)
            
        Returns:
            Dictionary with draft details (id, message)
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            message = MIMEMultipart() if html else MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            if html:
                message.attach(MIMEText(body, 'html'))
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            return {
                'id': draft['id'],
                'message': draft['message']
            }
            
        except HttpError as error:
            raise error
    
    def send_draft(self, draft_id: str) -> Dict[str, Any]:
        """Send an existing draft.
        
        Args:
            draft_id: The ID of the draft to send
            
        Returns:
            Dictionary with sent message details
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            sent_message = self.service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()
            
            return {
                'id': sent_message['id'],
                'threadId': sent_message['threadId'],
                'labelIds': sent_message.get('labelIds', [])
            }
            
        except HttpError as error:
            raise error
    
    def trash_message(self, message_id: str) -> bool:
        """Move a message to trash.
        
        Args:
            message_id: The ID of the message to trash
            
        Returns:
            True if successful
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return True
            
        except HttpError as error:
            raise error
    
    def untrash_message(self, message_id: str) -> bool:
        """Restore a message from trash.
        
        Args:
            message_id: The ID of the message to restore
            
        Returns:
            True if successful
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            self.service.users().messages().untrash(
                userId='me',
                id=message_id
            ).execute()
            return True
            
        except HttpError as error:
            raise error
    
    def modify_labels(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Modify labels on a message.
        
        Args:
            message_id: The ID of the message to modify
            add_labels: List of label IDs to add
            remove_labels: List of label IDs to remove
            
        Returns:
            Dictionary with updated message details
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            message = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            
            return {
                'id': message['id'],
                'labelIds': message.get('labelIds', [])
            }
            
        except HttpError as error:
            raise error
    
    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read.
        
        Args:
            message_id: The ID of the message to mark as read
            
        Returns:
            Dictionary with updated message details
            
        Raises:
            HttpError: If the API request fails.
        """
        return self.modify_labels(message_id, remove_labels=['UNREAD'])
    
    def mark_as_unread(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as unread.
        
        Args:
            message_id: The ID of the message to mark as unread
            
        Returns:
            Dictionary with updated message details
            
        Raises:
            HttpError: If the API request fails.
        """
        return self.modify_labels(message_id, add_labels=['UNREAD'])
    
    def list_labels(self) -> List[Dict[str, Any]]:
        """List all available labels.
        
        Returns:
            List of label dictionaries with id, name, type, etc.
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            label_list = []
            for label in labels:
                label_list.append({
                    'id': label['id'],
                    'name': label['name'],
                    'type': label.get('type', ''),
                    'messageListVisibility': label.get('messageListVisibility', ''),
                    'labelListVisibility': label.get('labelListVisibility', '')
                })
            
            return label_list
            
        except HttpError as error:
            raise error
    
    def search_messages(
        self,
        query: str,
        max_results: int = 10,
        include_spam_trash: bool = False
    ) -> List[Dict[str, Any]]:
        """Search messages using Gmail query syntax.
        
        Args:
            query: Gmail search query (e.g., "from:user@example.com subject:important")
            max_results: Maximum number of results (default: 10)
            include_spam_trash: Include spam and trash (default: False)
            
        Returns:
            List of full message details matching the query
            
        Raises:
            HttpError: If the API request fails.
        """
        try:
            # First get the list of matching message IDs
            message_ids = self.list_messages(
                query=query,
                max_results=max_results,
                include_spam_trash=include_spam_trash
            )
            
            # Then fetch full details for each message
            messages = []
            for msg_info in message_ids:
                try:
                    message = self.get_message(msg_info['id'])
                    messages.append(message)
                except HttpError:
                    # Skip messages that can't be retrieved
                    continue
            
            return messages
            
        except HttpError as error:
            raise error
