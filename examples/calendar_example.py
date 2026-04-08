"""Example usage of the Google Calendar client.

This script demonstrates how to use the GoogleCalendarClient to interact
with Google Calendar API.

Prerequisites:
    - Place credentials.json in the project root directory
    - Install dependencies: pip install -r requirements.txt
"""

from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path to import tools package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import GoogleCalendarClient


def main():
    """Demonstrate Google Calendar client functionality."""
    
    # Initialize the client
    # This will check for credentials.json in your project root
    print("Initializing Google Calendar client...")
    try:
        calendar = GoogleCalendarClient()
        print("✓ Client initialized successfully!\n")
    except AssertionError as e:
        print(f"✗ Error: {e}")
        return
    
    # List all calendars
    print("=" * 60)
    print("LISTING ALL CALENDARS")
    print("=" * 60)
    calendars = calendar.list_calendars()
    for cal in calendars:
        primary = " (PRIMARY)" if cal['primary'] else ""
        print(f"• {cal['summary']}{primary}")
        print(f"  ID: {cal['id']}")
        print(f"  Timezone: {cal['timeZone']}\n")
    
    # List upcoming events from primary calendar
    print("=" * 60)
    print("LISTING UPCOMING EVENTS FROM PRIMARY CALENDAR")
    print("=" * 60)
    events = calendar.list_events(calendar_id="primary", max_results=5)
    
    if not events:
        print("No upcoming events found.\n")
    else:
        for event in events:
            print(f"• {event['summary']}")
            print(f"  Start: {event['start']}")
            print(f"  End: {event['end']}")
            if event['location']:
                print(f"  Location: {event['location']}")
            print()
    
    # List events from all calendars
    print("=" * 60)
    print("LISTING EVENTS FROM ALL CALENDARS")
    print("=" * 60)
    all_events = calendar.list_events_from_all_calendars(max_results_per_calendar=3)
    
    if not all_events:
        print("No events found across all calendars.\n")
    else:
        for event in all_events:
            print(f"• {event['summary']}")
            print(f"  Calendar: {event['calendar']['summary']}")
            print(f"  Start: {event['start']}")
            print()
    
    # Example: Create a new event (commented out by default)
    # Uncomment to test event creation
    """
    print("=" * 60)
    print("CREATING A NEW EVENT")
    print("=" * 60)
    
    # Calculate times for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    new_event = calendar.create_event(
        summary="Test Event from Python",
        start_time=start_time.isoformat() + "Z",
        end_time=end_time.isoformat() + "Z",
        description="This is a test event created using the GoogleCalendarClient",
        location="Virtual",
    )
    
    print(f"✓ Event created successfully!")
    print(f"  Event ID: {new_event['id']}")
    print(f"  Link: {new_event['htmlLink']}\n")
    """
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
