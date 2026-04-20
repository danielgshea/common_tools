# Quick Start Guide

Get up and running with Gmail and Calendar tools in 5 minutes!

## Step 1: Get Credentials (2 minutes)

1. Visit: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download as `credentials.json`

## Step 2: Place Credentials (1 minute)

Choose one option:

```bash
# Option A: In your project root
cp ~/Downloads/credentials.json ./credentials.json

# Option B: Use environment variable
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"

# Option C: In parent directory (if repo is cloned)
cp ~/Downloads/credentials.json ../credentials.json
```

## Step 3: Enable APIs (1 minute)

- Gmail: https://console.cloud.google.com/apis/library/gmail.googleapis.com
- Calendar: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com

Click "ENABLE" for each API you need.

## Step 4: Verify Setup (30 seconds)

```bash
python -m utils.verify_credentials
```

Look for ✅ green checkmarks. If you see ❌, follow the instructions shown.

## Step 5: Use the Tools! (30 seconds)

### Gmail Example

```python
from gmail import GmailClient

client = GmailClient()

# List unread emails
unread = client.search_messages(query="is:unread", max_results=5)
for msg in unread:
    print(f"{msg['from']}: {msg['subject']}")

# Send an email
client.send_message(
    to="friend@example.com",
    subject="Hello!",
    body="Just testing my new Gmail client!"
)
```

### Calendar Example

```python
from calendar import GoogleCalendarClient

cal = GoogleCalendarClient()

# List today's events
events = cal.list_events(max_results=10)
for event in events:
    print(f"{event['start']}: {event['summary']}")

# Create an event
cal.create_event(
    summary="Quick Meeting",
    start_time="2024-01-15T14:00:00Z",
    end_time="2024-01-15T14:30:00Z"
)
```

### LangChain Agent Example

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from gmail import GMAIL_TOOLS
from calendar.tools import CALENDAR_TOOLS

model = ChatOpenAI(model="gpt-4")
agent = create_react_agent(model, GMAIL_TOOLS + CALENDAR_TOOLS)

# Use natural language!
agent.invoke({
    "messages": [("user", "What meetings do I have today?")]
})

agent.invoke({
    "messages": [("user", "Send an email to john@example.com about tomorrow's meeting")]
})
```

## Common Issues

### ❌ "credentials.json not found"
→ Run: `python -m utils.verify_credentials --guide`

### ❌ "API not enabled"
→ Enable APIs at the links in Step 3 above

### ❌ "invalid_grant"
→ Delete `token.json` and try again

### ❌ "Access denied"
→ Click "Allow" when browser opens for authentication

## Need More Help?

- **Detailed setup**: See `CREDENTIALS_SETUP.md`
- **Gmail docs**: See `gmail/README.md`
- **Examples**: Check `examples/` directory
- **Verification**: Run `python -m utils.verify_credentials`

## TL;DR - Absolute Minimum

```bash
# 1. Get credentials from Google Cloud Console
# 2. Save as credentials.json in project root
# 3. Enable Gmail/Calendar APIs
# 4. Run your code

python examples/gmail_example.py
```

The client will open a browser for first-time auth. That's it! 🚀
