# Agentic Tools

Common tooling for agentic applications. This repository provides easy-to-use utilities for integrating various services into your AI agent applications.

## Features

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
2. **Google Cloud Project** with Calendar API enabled (for calendar tools)
3. **OAuth 2.0 credentials** from Google Cloud Console (for calendar tools)
4. **OpenAI API Key** (for LangChain agent examples)

### Setup Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials file
5. **Rename the downloaded file to `credentials.json`**
6. **Place `credentials.json` in your project root directory**

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

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

# Initialize the client
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
├── calendar/
│   ├── __init__.py          # Exports GoogleCalendarClient
│   └── google_cal.py        # Google Calendar implementation
├── filesystem/
│   ├── __init__.py          # Exports FileSystemClient
│   ├── filesystem_client.py # Filesystem operations implementation
│   └── tools.py             # LangChain tool wrappers
├── examples/
│   ├── calendar_example.py          # Calendar usage examples
│   └── filesystem_hitl_example.py   # HITL demo with filesystem
├── .gitignore               # Excludes credentials and sensitive files
├── requirements.txt         # Dependencies
├── LICENSE                  # MIT License
└── README.md                # This file
```

## Security Notes

⚠️ **Never commit `credentials.json` or `token.json` to version control!**

These files contain sensitive authentication data. They are automatically excluded via `.gitignore`, but always double-check before pushing to a public repository.

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

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.
