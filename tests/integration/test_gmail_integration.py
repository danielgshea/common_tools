"""Integration tests for Gmail operations.

These tests use real Gmail API calls with actual credentials.
Tests are read-only by default (safe mode).
"""

import pytest
from googleapiclient.errors import HttpError


@pytest.mark.integration
@pytest.mark.slow
class TestGmailIntegration:
    """Integration tests for GmailClient."""
    
    def test_client_initialization(self, gmail_client):
        """Test that Gmail client initializes correctly."""
        assert gmail_client is not None
        assert gmail_client.credentials_path.exists()
        assert gmail_client.service is not None
    
    def test_list_messages(self, gmail_client):
        """Test listing recent messages with full details."""
        messages = gmail_client.list_messages(max_results=5)
        
        assert isinstance(messages, list)
        
        if len(messages) > 0:
            # Check that messages have the expected structure
            msg = messages[0]
            assert 'id' in msg
            assert 'threadId' in msg
            assert 'snippet' in msg
            assert 'from' in msg
            assert 'subject' in msg
            assert 'date' in msg
            
            # Verify these are not empty (the bug we fixed)
            assert msg['id'] != ''
            assert len(msg.get('snippet', '')) > 0 or len(msg.get('subject', '')) > 0
            
            print(f"\n✅ Retrieved {len(messages)} messages")
            print(f"   Sample: {msg['subject'][:50]}... from {msg['from'][:30]}")
    
    def test_get_message_details(self, gmail_client):
        """Test getting full details of a specific message."""
        # First get a message ID
        messages = gmail_client.list_messages(max_results=1)
        
        if len(messages) == 0:
            pytest.skip("No messages available to test")
        
        message_id = messages[0]['id']
        
        # Get full message details
        full_message = gmail_client.get_message(message_id)
        
        assert full_message['id'] == message_id
        assert 'from' in full_message
        assert 'to' in full_message
        assert 'subject' in full_message
        assert 'date' in full_message
        assert 'body' in full_message
        assert 'snippet' in full_message
        
        print(f"\n✅ Retrieved full message details")
        print(f"   Subject: {full_message['subject']}")
        print(f"   From: {full_message['from']}")
        print(f"   Body length: {len(full_message['body'].get('plain', ''))} chars")
    
    def test_list_labels(self, gmail_client):
        """Test listing Gmail labels."""
        labels = gmail_client.list_labels()
        
        assert isinstance(labels, list)
        assert len(labels) > 0
        
        # Check for common labels
        label_names = [label['name'] for label in labels]
        assert 'INBOX' in label_names or any('inbox' in name.lower() for name in label_names)
        
        # Verify label structure
        label = labels[0]
        assert 'id' in label
        assert 'name' in label
        assert 'type' in label
        
        print(f"\n✅ Retrieved {len(labels)} labels")
        print(f"   Sample labels: {', '.join(label_names[:5])}")
    
    def test_search_messages(self, gmail_client):
        """Test searching messages with a query."""
        # Search for messages in INBOX (should always return something)
        messages = gmail_client.search_messages(
            query="in:inbox",
            max_results=3
        )
        
        assert isinstance(messages, list)
        
        if len(messages) > 0:
            msg = messages[0]
            assert 'id' in msg
            assert 'from' in msg
            assert 'subject' in msg
            
            print(f"\n✅ Search returned {len(messages)} messages")
            print(f"   First result: {msg['subject'][:50]}")
    
    def test_list_messages_with_label_filter(self, gmail_client):
        """Test listing messages filtered by label."""
        messages = gmail_client.list_messages(
            label_ids=["INBOX"],
            max_results=3
        )
        
        assert isinstance(messages, list)
        
        if len(messages) > 0:
            # Verify messages have INBOX label
            for msg in messages:
                assert 'INBOX' in msg.get('labelIds', [])
            
            print(f"\n✅ Retrieved {len(messages)} INBOX messages")
    
    def test_list_unread_messages(self, gmail_client):
        """Test listing only unread messages."""
        messages = gmail_client.list_messages(
            query="is:unread",
            max_results=5
        )
        
        assert isinstance(messages, list)
        
        print(f"\n✅ Found {len(messages)} unread messages")
        
        if len(messages) > 0:
            # Verify they have UNREAD label
            for msg in messages:
                assert 'UNREAD' in msg.get('labelIds', [])
    
    @pytest.mark.modifies_data
    def test_mark_as_read_unread(self, gmail_client, safe_mode):
        """Test marking a message as read/unread.
        
        WARNING: This modifies real email data!
        Skipped in safe mode.
        """
        if safe_mode:
            pytest.skip("Skipped in safe mode - would modify email data")
        
        # Get first unread message
        messages = gmail_client.list_messages(query="is:unread", max_results=1)
        
        if len(messages) == 0:
            pytest.skip("No unread messages to test with")
        
        message_id = messages[0]['id']
        
        # Mark as read
        result = gmail_client.mark_as_read(message_id)
        assert 'UNREAD' not in result.get('labelIds', [])
        
        # Mark as unread again
        result = gmail_client.mark_as_unread(message_id)
        assert 'UNREAD' in result.get('labelIds', [])
        
        print("\n✅ Successfully toggled read/unread status")
    
    @pytest.mark.modifies_data
    def test_create_draft(self, gmail_client, safe_mode):
        """Test creating a draft email.
        
        WARNING: This creates a draft in your Gmail!
        Skipped in safe mode.
        """
        if safe_mode:
            pytest.skip("Skipped in safe mode - would create draft")
        
        draft = gmail_client.create_draft(
            to="test@example.com",
            subject="[TEST] Integration Test Draft",
            body="This is a test draft created by integration tests."
        )
        
        assert 'id' in draft
        assert 'message' in draft
        
        print(f"\n✅ Created draft with ID: {draft['id']}")
        print("   NOTE: Please manually delete this draft from Gmail")
    
    def test_error_handling_invalid_message_id(self, gmail_client):
        """Test error handling for invalid message ID."""
        with pytest.raises(HttpError) as exc_info:
            gmail_client.get_message("invalid_message_id_12345")
        
        assert exc_info.value.resp.status in [400, 404]
    
    def test_list_messages_empty_result(self, gmail_client):
        """Test handling of search with no results."""
        # Search for something that shouldn't exist
        messages = gmail_client.search_messages(
            query="from:thisshouldnotexist@invaliddomain12345.com",
            max_results=1
        )
        
        assert isinstance(messages, list)
        assert len(messages) == 0


@pytest.mark.integration
class TestGmailTools:
    """Integration tests for Gmail LangChain tools."""
    
    def test_list_messages_tool(self, gmail_client):
        """Test the list_messages tool wrapper."""
        from gmail.tools import list_messages
        
        result = list_messages.invoke({"max_results": 3})
        
        # Tool returns JSON string
        assert isinstance(result, str)
        
        # Parse and verify
        import json
        data = json.loads(result)
        
        if isinstance(data, list):
            assert len(data) <= 3
            if len(data) > 0:
                assert 'id' in data[0]
                assert 'subject' in data[0]
        
        print(f"\n✅ list_messages tool returned valid JSON")
    
    def test_search_emails_tool(self, gmail_client):
        """Test the search_emails tool wrapper."""
        from gmail.tools import search_emails
        
        result = search_emails.invoke({
            "query": "in:inbox",
            "max_results": 2
        })
        
        import json
        data = json.loads(result)
        
        assert isinstance(data, (list, dict))
        print(f"\n✅ search_emails tool returned valid JSON")
