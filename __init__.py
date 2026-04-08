"""Common tooling for agentic applications.

This package provides utilities for integrating various services
into agentic applications.

Available modules:
    - calendar: Google Calendar API client for managing calendar events
    - filesystem: File system operations with LangChain tool support
"""

from .calendar import *
from .filesystem import *

__version__ = "0.1.0"
