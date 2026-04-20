"""Common tooling for agentic applications.

This package provides utilities for integrating various services
into agentic applications.

Available modules:
    - gmail: Gmail API client for managing email
    - gcalendar: Google Calendar API client for managing calendar events (renamed from 'calendar' to avoid stdlib conflicts)
    - filesystem: File system operations with LangChain tool support
    
Import these modules directly when needed:
    from gmail import GmailClient, GMAIL_TOOLS
    from gcalendar import GoogleCalendarClient, CALENDAR_TOOLS
    from filesystem import FileSystemClient
"""

# Note: Wildcard imports are commented out to avoid circular import issues
# with the requests library. Import modules directly as needed.
# from .gmail import *
# from .calendar import *
# from .filesystem import *

__version__ = "0.1.0"
