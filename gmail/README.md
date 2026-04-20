# Gmail API Client and Tools

A clean, Python-based interface for interacting with the Gmail API, featuring both direct client usage and LangChain tool integration.

## Features

### Core Client Features (`GmailClient`)

- **Message Management**: List, read, search, and filter messages
- **Sending**: Send new emails with CC/BCC support, both plain text and HTML
- **Replies**: Reply to messages maintaining thread context
- **Drafts**: Create and send draft messages
- **Labels**: List, add, and remove labels from messages
- **Organization**: Mark messages as read/unread, trash/untrash
- **Search**: Full Gmail query syntax support

### LangChain Tools Integration

14 ready-to-use LangChain tools for agent-based email automation:
- `list_messages` - List messages with filtering
- `read_message` - Read full message content
- `send_email` - Send new emails
- `reply_to_email` - Reply to messages
- `search_emails` - Search with Gmail queries
- `mark_as_read` / `mark_as_unread` - Manage read status
- `trash_email` / `untrash_email` - Manage trash
- `list_gmail_labels` - List available labels
- `add_labels_to_message` / `remove_labels_from_message` - Manage labels
- `create_draft` / `send_draft` - Draft management

## Setup

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Go to [APIs & Credentials](https://console.cloud.google.com/apis/credentials)
5. Create OAuth 2.0 credentials (Desktop app)
6. Download the credentials file as `credentials.json`

### 2. Place Credentials

The Gmail client supports flexible credential discovery. Choose any of these options:

#### Option A: Project Root (Traditional)
```
tools/
├── credentials.json  ← Place here
├── gmail/
└── ...
```

#### Option B: Parent Directory (When cloned into another project)
```
my-agent-project/
├── credentials.json      ← Can be found here
└── common_tools/         ← This repo cloned
    ├── gmail/
    └── ...
```

#### Option C: Environment Variable (Production)
```bash
export GOOGLE_CREDENTIALS_PATH="/secure/location/credentials.json"
```

#### Option D: Explicit Path in Code
```python
from gmail import GmailClient
client = GmailClient(credentials_path="/custom/path/credentials.json")
```

**Credential Search Order:**
1. Explicit `credentials_path` parameter (if provided)
2. `GOOGLE_CREDENTIALS_PATH` environment variable
3. Current working directory
4. Parent directories (up to 5 levels)

This flexible approach allows the repository to be cloned into any project structure!

### 3. First Run

On first run, the client will:
1. Open a browser for OAuth authentication
2. Create `token.json` in the same directory as `credentials.json`
3. Use this token for future requests (auto-refreshes)

**Note**: The Gmail client shares authentication with the Calendar client. If you've already authenticated for Calendar, the same `credentials.json` and `token.json` will work for Gmail (with combined scopes).

## Usage

### Direct Client Usage

```python
from gmail import GmailClient

# Initialize client
client = GmailClient()

# List recent messages
messages = client.list_messages(max_results=10)
for msg in messages:
    print(f"Message ID: {msg['id']}")

# Search for unread messages
unread = client.search_messages(query="is:unread", max_results=5)
for msg in unread:
    print(f"From: {msg['from']}")
    print(f"Subject: {msg['subject']}")

# Read a specific message
message = client.get_message(message_id="abc123")
print(f"Body: {message['body']['plain']}")

# Send an email
result = client.send_message(
    to="recipient@example.com",
    subject="Hello from Gmail API",
    body="This is a test email!"
)
print(f"Sent! Message ID: {result['id']}")

# Reply to a message
reply = client.reply_to_message(
    message_id="abc123",
    body="Thanks for your email!"
)

# Manage labels
client.mark_as_read(message_id="abc123")
client.add_labels(message_id="abc123", label_ids=["IMPORTANT"])
client.trash_message(message_id="abc123")
```

### LangChain Agent Integration

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from gmail import GMAIL_TOOLS

# Create model
model = ChatOpenAI(model="gpt-4")

# Create agent with Gmail tools
agent = create_react_agent(model, GMAIL_TOOLS)

# Use natural language to interact with Gmail
response = agent.invoke({
    "messages": [("user", "Search my inbox for emails from john@example.com")]
})

response = agent.invoke({
    "messages": [("user", "Mark all unread messages from last week as read")]
})

response = agent.invoke({
    "messages": [("user", "Send an email to sarah@example.com with subject 'Meeting Tomorrow'")]
})
```

### Combining with Calendar Tools

```python
from gmail import GMAIL_TOOLS
from calendar.tools import CALENDAR_TOOLS
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Combine Gmail and Calendar tools
all_tools = GMAIL_TOOLS + CALENDAR_TOOLS

model = ChatOpenAI(model="gpt-4")
agent = create_react_agent(model, all_tools)

# Agent can now access both Gmail and Calendar
response = agent.invoke({
    "messages": [("user", "Check my calendar for tomorrow and send an email to my team about the first meeting")]
})
```

## API Reference

### GmailClient Methods

#### `list_messages(query=None, label_ids=None, max_results=10, include_spam_trash=False)`
List messages with optional filtering.

**Parameters:**
- `query` (str, optional): Gmail search query (e.g., "is:unread", "from:user@example.com")
- `label_ids` (List[str], optional): Filter by label IDs (e.g., ["INBOX", "UNREAD"])
- `max_results` (int): Maximum messages to return (default: 10)
- `include_spam_trash` (bool): Include spam and trash (default: False)

**Returns:** List of message dictionaries with id and threadId

#### `get_message(message_id, format='full')`
Get full message details by ID.

**Parameters:**
- `message_id` (str): The message ID to retrieve
- `format` (str): Message format - 'full', 'metadata', 'minimal', or 'raw' (default: 'full')

**Returns:** Dictionary with message details including headers and body

#### `send_message(to, subject, body, cc=None, bcc=None, html=False)`
Send a new email message.

**Parameters:**
- `to` (str): Recipient email (comma-separated for multiple)
- `subject` (str): Email subject
- `body` (str): Email body content
- `cc` (str, optional): CC recipients
- `bcc` (str, optional): BCC recipients
- `html` (bool): Send as HTML email (default: False)

**Returns:** Dictionary with sent message details (id, threadId)

#### `reply_to_message(message_id, body, html=False)`
Reply to an existing message.

**Parameters:**
- `message_id` (str): ID of message to reply to
- `body` (str): Reply body content
- `html` (bool): Send as HTML (default: False)

**Returns:** Dictionary with sent reply details

#### `search_messages(query, max_results=10, include_spam_trash=False)`
Search messages using Gmail query syntax.

**Parameters:**
- `query` (str): Gmail search query
- `max_results` (int): Maximum results (default: 10)
- `include_spam_trash` (bool): Include spam/trash (default: False)

**Returns:** List of full message details matching the query

#### `mark_as_read(message_id)` / `mark_as_unread(message_id)`
Update message read status.

**Returns:** Dictionary with updated message details

#### `trash_message(message_id)` / `untrash_message(message_id)`
Move message to/from trash.

**Returns:** Boolean indicating success

#### `list_labels()`
List all available Gmail labels.

**Returns:** List of label dictionaries with id, name, type, etc.

#### `modify_labels(message_id, add_labels=None, remove_labels=None)`
Modify labels on a message.

**Parameters:**
- `message_id` (str): Message ID to modify
- `add_labels` (List[str], optional): Label IDs to add
- `remove_labels` (List[str], optional): Label IDs to remove

**Returns:** Dictionary with updated message details

## Gmail Query Syntax

The `search_messages` and `list_messages` methods support full Gmail query syntax:

- `is:unread` - Unread messages
- `is:starred` - Starred messages
- `from:user@example.com` - Messages from specific sender
- `to:user@example.com` - Messages to specific recipient
- `subject:meeting` - Messages with "meeting" in subject
- `has:attachment` - Messages with attachments
- `after:2024/01/01` - Messages after date
- `before:2024/12/31` - Messages before date
- `newer_than:7d` - Messages newer than 7 days
- `older_than:1m` - Messages older than 1 month
- `in:inbox` - Messages in inbox
- `label:work` - Messages with "work" label

Combine queries with AND/OR:
- `from:john@example.com subject:project` - Both conditions
- `from:john@example.com OR from:jane@example.com` - Either condition

## Security & Permissions

### OAuth Scopes

The client uses `gmail.modify` scope, which allows:
- ✅ Reading messages
- ✅ Sending messages  
- ✅ Modifying labels
- ✅ Moving to trash (recoverable)
- ❌ Permanent deletion (safer!)

### Best Practices

1. **Keep credentials.json secure** - Never commit to version control
2. **token.json is sensitive** - Contains access tokens, keep private
3. **Test with drafts first** - Use `create_draft()` before `send_message()`
4. **Use trash, not delete** - Messages can be recovered from trash
5. **Verify recipients** - Always double-check email addresses before sending

## Examples

See `examples/gmail_example.py` for comprehensive usage examples:

```bash
python examples/gmail_example.py
```

## Error Handling

All methods raise `HttpError` from `googleapiclient.errors` on API failures. LangChain tools return JSON error messages instead:

```python
from googleapiclient.errors import HttpError

try:
    message = client.get_message("invalid_id")
except HttpError as e:
    print(f"API Error: {e}")
```

## Troubleshooting

### "credentials.json not found"
**Problem:** Client can't locate your credentials file

**Solutions:**
1. Place `credentials.json` in your project root or current working directory
2. Set environment variable: `export GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json`
3. Pass explicit path: `GmailClient(credentials_path="/path/to/credentials.json")`
4. Check that the file actually exists at the expected location

The client searches multiple locations automatically. If it can't find the file anywhere, you'll see a detailed error message showing all locations searched.

### "invalid_grant" error
- Delete `token.json` and re-authenticate
- Ensure OAuth consent screen is configured correctly
- Check that your credentials haven't expired in Google Cloud Console

### "insufficient permissions" error  
- Enable Gmail API in Google Cloud Console
- Verify correct scopes in credentials
- Delete `token.json` to force re-authentication with new scopes

### Rate limits
- Gmail API has quotas (250 quota units per user per second)
- Implement exponential backoff for high-volume operations

### Using in cloned repositories
If you clone this repo into another project:
```
your-project/
├── credentials.json      ← Place here
└── common_tools/         ← Cloned repo
    └── gmail/
```

The client will automatically find `credentials.json` by walking up the directory tree. No code changes needed!

## License

See main project LICENSE file.
