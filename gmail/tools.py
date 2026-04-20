"""Gmail tools wrapper for LangChain."""
import json
from typing import List, Optional
from langchain_core.tools import tool
from googleapiclient.errors import HttpError
from .gmail_client import GmailClient

# Initialize the Gmail client (will be created on first use)
_gmail_client = None


def get_gmail_client() -> GmailClient:
    """Get or create the GmailClient instance."""
    global _gmail_client
    if _gmail_client is None:
        _gmail_client = GmailClient()
    return _gmail_client


@tool
def list_messages(
    query: Optional[str] = None,
    label_ids: Optional[List[str]] = None,
    max_results: int = 10,
    include_spam_trash: bool = False
) -> str:
    """List messages from Gmail inbox.
    
    Args:
        query: Gmail search query (e.g., "is:unread", "from:user@example.com")
        label_ids: List of label IDs to filter by (e.g., ["INBOX", "UNREAD"])
        max_results: Maximum number of messages to return (default: 10)
        include_spam_trash: Include spam and trash in results (default: False)
        
    Returns:
        JSON string containing list of messages with basic info.
    """
    try:
        client = get_gmail_client()
        messages = client.list_messages(
            query=query,
            label_ids=label_ids,
            max_results=max_results,
            include_spam_trash=include_spam_trash
        )
        
        if not messages:
            return json.dumps({"message": "No messages found."})
        
        return json.dumps(messages, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def read_message(message_id: str) -> str:
    """Read the full content of a specific email message.
    
    Args:
        message_id: The ID of the message to read
        
    Returns:
        JSON string with complete message details including headers and body.
    """
    try:
        client = get_gmail_client()
        message = client.get_message(message_id)
        
        return json.dumps(message, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html: bool = False
) -> str:
    """Send a new email message.
    
    Args:
        to: Recipient email address (can be comma-separated for multiple)
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional, comma-separated)
        bcc: BCC recipients (optional, comma-separated)
        html: If True, send as HTML email (default: False for plain text)
        
    Returns:
        JSON string with sent message details.
    """
    try:
        client = get_gmail_client()
        result = client.send_message(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            html=html
        )
        
        response = {**result, 'message': 'Email sent successfully'}
        return json.dumps(response, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def reply_to_email(message_id: str, body: str, html: bool = False) -> str:
    """Reply to an existing email message.
    
    Args:
        message_id: The ID of the message to reply to
        body: Reply body content
        html: If True, send as HTML email (default: False)
        
    Returns:
        JSON string with sent reply details.
    """
    try:
        client = get_gmail_client()
        result = client.reply_to_message(
            message_id=message_id,
            body=body,
            html=html
        )
        
        response = {**result, 'message': 'Reply sent successfully'}
        return json.dumps(response, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def search_emails(
    query: str,
    max_results: int = 10,
    include_spam_trash: bool = False
) -> str:
    """Search emails using Gmail query syntax.
    
    Args:
        query: Gmail search query (e.g., "from:user@example.com subject:important")
        max_results: Maximum number of results (default: 10)
        include_spam_trash: Include spam and trash (default: False)
        
    Returns:
        JSON string with matching messages and their full details.
    """
    try:
        client = get_gmail_client()
        messages = client.search_messages(
            query=query,
            max_results=max_results,
            include_spam_trash=include_spam_trash
        )
        
        if not messages:
            return json.dumps({"message": "No messages found matching the query."})
        
        return json.dumps(messages, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def mark_as_read(message_id: str) -> str:
    """Mark an email message as read.
    
    Args:
        message_id: The ID of the message to mark as read
        
    Returns:
        Confirmation message.
    """
    try:
        client = get_gmail_client()
        result = client.mark_as_read(message_id)
        
        return json.dumps({
            'message': f'Message {message_id} marked as read',
            'labelIds': result.get('labelIds', [])
        }, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def mark_as_unread(message_id: str) -> str:
    """Mark an email message as unread.
    
    Args:
        message_id: The ID of the message to mark as unread
        
    Returns:
        Confirmation message.
    """
    try:
        client = get_gmail_client()
        result = client.mark_as_unread(message_id)
        
        return json.dumps({
            'message': f'Message {message_id} marked as unread',
            'labelIds': result.get('labelIds', [])
        }, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def trash_email(message_id: str) -> str:
    """Move an email message to trash.
    
    Args:
        message_id: The ID of the message to trash
        
    Returns:
        Confirmation message.
    """
    try:
        client = get_gmail_client()
        client.trash_message(message_id)
        
        return json.dumps({
            'message': f'Message {message_id} moved to trash successfully'
        }, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def untrash_email(message_id: str) -> str:
    """Restore an email message from trash.
    
    Args:
        message_id: The ID of the message to restore
        
    Returns:
        Confirmation message.
    """
    try:
        client = get_gmail_client()
        client.untrash_message(message_id)
        
        return json.dumps({
            'message': f'Message {message_id} restored from trash successfully'
        }, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def list_gmail_labels() -> str:
    """List all available Gmail labels.
    
    Returns:
        JSON string containing list of labels with their details.
    """
    try:
        client = get_gmail_client()
        labels = client.list_labels()
        
        if not labels:
            return json.dumps({"message": "No labels found."})
        
        return json.dumps(labels, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def add_labels_to_message(message_id: str, label_ids: List[str]) -> str:
    """Add labels to an email message.
    
    Args:
        message_id: The ID of the message to modify
        label_ids: List of label IDs to add (e.g., ["IMPORTANT", "STARRED"])
        
    Returns:
        JSON string with updated message details.
    """
    try:
        client = get_gmail_client()
        result = client.modify_labels(message_id, add_labels=label_ids)
        
        return json.dumps({
            'message': f'Labels added to message {message_id}',
            'labelIds': result.get('labelIds', [])
        }, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def remove_labels_from_message(message_id: str, label_ids: List[str]) -> str:
    """Remove labels from an email message.
    
    Args:
        message_id: The ID of the message to modify
        label_ids: List of label IDs to remove (e.g., ["IMPORTANT", "STARRED"])
        
    Returns:
        JSON string with updated message details.
    """
    try:
        client = get_gmail_client()
        result = client.modify_labels(message_id, remove_labels=label_ids)
        
        return json.dumps({
            'message': f'Labels removed from message {message_id}',
            'labelIds': result.get('labelIds', [])
        }, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def create_draft(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html: bool = False
) -> str:
    """Create a draft email message.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html: If True, create as HTML email (default: False)
        
    Returns:
        JSON string with draft details.
    """
    try:
        client = get_gmail_client()
        result = client.create_draft(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            html=html
        )
        
        response = {**result, 'message': 'Draft created successfully'}
        return json.dumps(response, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def send_draft(draft_id: str) -> str:
    """Send an existing draft email.
    
    Args:
        draft_id: The ID of the draft to send
        
    Returns:
        JSON string with sent message details.
    """
    try:
        client = get_gmail_client()
        result = client.send_draft(draft_id)
        
        response = {**result, 'message': 'Draft sent successfully'}
        return json.dumps(response, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


# Export all tools
GMAIL_TOOLS = [
    list_messages,
    read_message,
    send_email,
    reply_to_email,
    search_emails,
    mark_as_read,
    mark_as_unread,
    trash_email,
    untrash_email,
    list_gmail_labels,
    add_labels_to_message,
    remove_labels_from_message,
    create_draft,
    send_draft
]
