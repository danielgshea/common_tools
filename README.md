# Agentic Tools

Common tooling for agentic applications. This repository provides easy-to-use utilities for integrating various services into your AI agent applications.

## Features

### Google Calendar Integration
- ✅ List calendars and events
- ✅ Create, update, and delete events
- ✅ Query events from multiple calendars
- ✅ Full Google Calendar API support

## Installation

### Prerequisites

1. **Python 3.7+** is required
2. **Google Cloud Project** with Calendar API enabled
3. **OAuth 2.0 credentials** from Google Cloud Console

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
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
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

# Update an event
calendar.update_event(
    event_id=new_event['id'],
    summary="Updated Team Meeting",
    location="Conference Room B"
)

# Delete an event
calendar.delete_event(event_id=new_event['id'])

# List events from all calendars
all_events = calendar.list_events_from_all_calendars(max_results_per_calendar=5)
for event in all_events:
    print(f"{event['calendar']['summary']}: {event['summary']}")
```

### Authentication Flow

The first time you run the client, it will:
1. Check for `credentials.json` in your project root (required)
2. Open a browser window for Google OAuth authentication
3. Save the authentication token to `token.json` for future use
4. Subsequent runs will use the saved token automatically

**Important:** Both `credentials.json` and `token.json` contain sensitive information and are automatically excluded from version control via `.gitignore`.

## Project Structure

```
tools/
├── __init__.py           # Root module for easy imports
├── calendar/
│   ├── __init__.py       # Calendar package
│   └── google_cal.py     # Google Calendar client implementation
├── .gitignore            # Excludes credentials and sensitive files
└── README.md             # This file
```

## Security Notes

⚠️ **Never commit `credentials.json` or `token.json` to version control!**

These files contain sensitive authentication data. They are automatically excluded via `.gitignore`, but always double-check before pushing to a public repository.

## Contributing

Contributions are welcome! This repository is designed to grow with additional tooling for agentic applications.

### Adding New Tools

When adding new tools:
1. Create a new package directory (e.g., `email/`, `slack/`, etc.)
2. Implement your client with clear documentation
3. Add exports to both the package `__init__.py` and root `__init__.py`
4. Update this README with usage examples
5. Update `.gitignore` if new credentials are needed

## License

[Add your license here]

## Support

For issues, questions, or contributions, please open an issue on GitHub.
