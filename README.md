# Agentic Tools

Common tooling for agentic applications. This repository provides easy-to-use utilities for integrating various services into your AI agent applications.

## Features

### Gmail Integration
- ✅ Read, send, and reply to emails
- ✅ Search messages with Gmail query syntax
- ✅ Manage labels and organize messages
- ✅ Create and send drafts
- ✅ Mark as read/unread, trash/untrash
- ✅ Full Gmail API support with 14 LangChain tools

### Google Calendar Integration
- ✅ List calendars and events
- ✅ Create, update, and delete events
- ✅ Query events from multiple calendars
- ✅ Full Google Calendar API support

### Filesystem Tools
- ✅ Create, read, write, and delete files
- ✅ List files with pattern matching
- ✅ LangChain tool wrappers for AI agents
- ✅ Human-in-the-Loop (HITL) support for safe file operations
- ✅ Built-in error handling and validation

## Installation

### Prerequisites

1. **Python 3.7+** is required
2. **Google Cloud Project** with Gmail/Calendar API enabled (for Google tools)
3. **OAuth 2.0 credentials** from Google Cloud Console (for Google tools)
4. **OpenAI API Key** (for LangChain agent examples)

### Setup Google APIs (Gmail & Calendar)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API and/or Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and "Google Calendar API"
   - Click "Enable" for each API you want to use
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials file
5. **Rename the downloaded file to `credentials.json`**

**Note:** The same `credentials.json` file works for both Gmail and Calendar APIs.

#### Credential Placement Options

The tools support flexible credential discovery. Choose any of these options:

**Option 1: Project Root (Recommended for standalone use)**
```
your-project/
├── credentials.json  ← Place here
└── common_tools/     ← This repo (if cloned)
```

**Option 2: Environment Variable (Recommended for deployments)**
```bash
export GOOGLE_CREDENTIALS_PATH="/secure/location/credentials.json"
```

**Option 3: Parent Directory (Works when cloned into another project)**
```
my-agent-project/
├── credentials.json      ← Can be found here
└── common_tools/         ← Cloned repo
    ├── gmail/
    └── calendar/
```

**Option 4: Explicit Path in Code**
```python
from gmail import GmailClient
client = GmailClient(credentials_path="/custom/path/credentials.json")
```

The tools automatically search for credentials in this order:
1. Explicit `credentials_path` parameter
2. `GOOGLE_CREDENTIALS_PATH` environment variable
3. Current working directory
4. Parent directories (up to 5 levels)

This design allows the repository to be cloned into any project structure!

#### Verify Your Setup

Before using the Gmail or Calendar clients, you can verify your credentials are set up correctly:

```bash
# Run the verification utility
python -m utils.verify_credentials

# Or for just the setup guide
python -m utils.verify_credentials --guide

# Quiet mode (just exit code)
python -m utils.verify_credentials --quiet
```

This will check:
- ✅ Credentials file is found and valid
- ✅ Token file exists (if already authenticated)
- ✅ Credentials have correct OAuth2 format
- ✅ Helpful error messages if issues found

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Gmail Client

```python
from gmail import GmailClient

# Initialize the client (requires credentials.json in project root)
client = GmailClient()

# List recent messages
messages = client.list_messages(max_results=10)
for msg in messages:
    print(f"Message ID: {msg['id']}")

# Search for unread emails
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
```

See `gmail/README.md` for comprehensive documentation and `examples/gmail_example.py` for more examples.

### Google Calendar Client

```python
from tools import GoogleCalendarClient

# Initialize the client (requires credentials.json in project root)
calendar = GoogleCalendarClient()

# List all calendars
calendars = calendar.list_calendars()
for cal in calendars:
    print(f"Calendar: {cal['summary']} (ID: {cal['id']})")

# List upcoming events
events = calendar.list_events(calendar_id="primary", max_results=10)
for event in events:
    print(f"Event: {event['summary']} at {event['start']}")

# Create a new event
new_event = calendar.create_event(
    summary="Team Meeting",
    start_time="2024-01-15T10:00:00Z",
    end_time="2024-01-15T11:00:00Z",
    description="Weekly team sync",
    location="Conference Room A",
    attendees=["colleague@example.com"]
)
print(f"Created event: {new_event['htmlLink']}")
```

### Filesystem Client

```python
from tools import FileSystemClient

# Initialize the client (defaults to current working directory)
fs = FileSystemClient()

# Or set a base path explicitly
fs = FileSystemClient(base_path="/path/to/project")

# Or use environment variable
# export FILESYSTEM_BASE_PATH=/path/to/project
fs = FileSystemClient()

# Create a file
result = fs.create_file("example.txt", content="Hello, World!")
print(f"Created: {result['path']}")

# Read a file
data = fs.read_file("example.txt")
print(f"Content: {data['content']}")

# Write to a file
fs.write_file("example.txt", content="Updated content")

# List files
files = fs.list_files(pattern="*.txt")
print(f"Found {files['count']} text files")

# Delete a file
fs.delete_file("example.txt")
```

### Filesystem Tools with LangChain & Human-in-the-Loop

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from filesystem.tools import (
    create_file_tool, read_file_tool, write_file_tool,
    delete_file_tool, list_files_tool
)

# Create an agent with HITL middleware
agent = create_agent(
    model="gpt-4o-mini",
    tools=[
        create_file_tool,
        read_file_tool,
        write_file_tool,
        delete_file_tool,
        list_files_tool
    ],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # Require approval for destructive operations
                "create_file_tool": True,
                "write_file_tool": True,
                "delete_file_tool": True,
                # Auto-approve safe operations
                "read_file_tool": False,
                "list_files_tool": False,
            },
        ),
    ],
    checkpointer=InMemorySaver(),
)

# Use the agent - it will pause for approval on file modifications
config = {"configurable": {"thread_id": "my_thread"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Create a file called data.txt"}]},
    config=config,
    version="v2"
)

# Handle interrupts and provide decisions
if result.interrupts:
    # User reviews and approves/rejects/edits the action
    from langgraph.types import Command
    agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
        version="v2"
    )
```

See `examples/filesystem_hitl_example.py` for a complete interactive demo.

## Project Structure

```
tools/
├── __init__.py              # Root module (imports from submodules)
├── gmail/
│   ├── __init__.py          # Exports GmailClient and GMAIL_TOOLS
│   ├── gmail_client.py      # Gmail API implementation
│   ├── tools.py             # LangChain tool wrappers (14 tools)
│   └── README.md            # Detailed Gmail documentation
├── calendar/
│   ├── __init__.py          # Exports GoogleCalendarClient
│   ├── google_cal.py        # Google Calendar implementation
│   └── tools.py             # LangChain tool wrappers
├── filesystem/
│   ├── __init__.py          # Exports FileSystemClient
│   ├── filesystem_client.py # Filesystem operations implementation
│   └── tools.py             # LangChain tool wrappers
├── examples/
│   ├── gmail_example.py             # Gmail usage examples
│   ├── filesystem_example.py        # Filesystem usage demo
│   └── filesystem_hitl_example.py   # HITL demo with filesystem
├── .gitignore               # Excludes credentials and sensitive files
├── requirements.txt         # Dependencies
├── LICENSE                  # MIT License
└── README.md                # This file
```

## Security Notes

⚠️ **Never commit `credentials.json` or `token.json` to version control!**

These files contain sensitive authentication data. They are automatically excluded via `.gitignore`, but always double-check before pushing to a public repository.

### Environment Variables

For production deployments, use environment variables:

```bash
# Google API credentials
export GOOGLE_CREDENTIALS_PATH="/secure/location/credentials.json"

# Filesystem operations base path
export FILESYSTEM_BASE_PATH="/app/data"
```

This keeps sensitive paths out of your code and allows different configurations per environment.

### Human-in-the-Loop Safety

The filesystem tools are designed with safety in mind:
- **Destructive operations** (create, write, delete) can require human approval
- **Safe operations** (read, list, check existence) can be auto-approved
- **Edit capability** lets you modify tool arguments before execution
- **Reject with feedback** helps the agent understand why an action was denied

This is especially important when giving AI agents access to your filesystem!

## Contributing

Contributions are welcome! This repository is designed to grow with additional tooling for agentic applications.

### Adding New Tools

When adding new tools:
1. Create a new package directory (e.g., `email/`, `slack/`, etc.)
2. Implement your client with clear documentation
3. Add LangChain tool wrappers in a `tools.py` file
4. Add exports to both the package `__init__.py` and root `__init__.py`
5. Update this README with usage examples
6. Update `.gitignore` if new credentials are needed
7. Consider adding HITL support for sensitive operations

## Support

For issues, questions, or contributions, please open an issue on GitHub.
