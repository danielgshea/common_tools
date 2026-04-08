"""Google Calendar tools wrapper for LangChain."""
import json
from typing import List, Optional
from langchain_core.tools import tool
from googleapiclient.errors import HttpError
from calendar.google_cal import GoogleCalendarClient

# Initialize the calendar client (will be created on first use)
_calendar_client = None


def get_calendar_client() -> GoogleCalendarClient:
    """Get or create the GoogleCalendarClient instance."""
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient()
    return _calendar_client


@tool
def list_calendars() -> str:
    """List all available Google calendars.
    
    Returns:
        JSON string containing list of calendars with their IDs and names.
    """
    try:
        client = get_calendar_client()
        calendars = client.list_calendars()
        
        if not calendars:
            return json.dumps({"message": "No calendars found."})
        
        return json.dumps(calendars, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def list_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 10
) -> str:
    """List events from a Google Calendar.
    
    Args:
        calendar_id: The calendar ID (default: "primary" for main calendar)
        time_min: Start time in RFC3339 format (e.g., "2024-01-01T00:00:00Z")
        time_max: End time in RFC3339 format (e.g., "2024-12-31T23:59:59Z")
        max_results: Maximum number of events to return (default: 10)
        
    Returns:
        JSON string containing list of events with details.
    """
    try:
        client = get_calendar_client()
        events = client.list_events(
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=max_results
        )
        
        if not events:
            return json.dumps({"message": "No upcoming events found."})
        
        return json.dumps(events, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None
) -> str:
    """Create a new event in Google Calendar.
    
    Args:
        summary: The title/summary of the event
        start_time: Start time in RFC3339 format (e.g., "2024-01-01T10:00:00Z")
        end_time: End time in RFC3339 format (e.g., "2024-01-01T11:00:00Z")
        calendar_id: The calendar ID (default: "primary")
        description: Optional event description
        location: Optional event location
        attendees: Optional list of attendee email addresses
        
    Returns:
        JSON string with created event details including event ID.
    """
    try:
        client = get_calendar_client()
        event = client.create_event(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            calendar_id=calendar_id,
            description=description,
            location=location,
            attendees=attendees
        )
        
        result = {**event, 'message': 'Event created successfully'}
        return json.dumps(result, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def update_event(
    event_id: str,
    calendar_id: str = "primary",
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """Update an existing event in Google Calendar.
    
    Args:
        event_id: The ID of the event to update
        calendar_id: The calendar ID (default: "primary")
        summary: New event title/summary
        start_time: New start time in RFC3339 format
        end_time: New end time in RFC3339 format
        description: New event description
        location: New event location
        
    Returns:
        JSON string with updated event details.
    """
    try:
        client = get_calendar_client()
        event = client.update_event(
            event_id=event_id,
            calendar_id=calendar_id,
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location
        )
        
        result = {**event, 'message': 'Event updated successfully'}
        return json.dumps(result, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def delete_event(
    event_id: str,
    calendar_id: str = "primary"
) -> str:
    """Delete an event from Google Calendar.
    
    Args:
        event_id: The ID of the event to delete
        calendar_id: The calendar ID (default: "primary")
        
    Returns:
        Confirmation message.
    """
    try:
        client = get_calendar_client()
        client.delete_event(event_id=event_id, calendar_id=calendar_id)
        
        return json.dumps({
            'message': f'Event {event_id} deleted successfully'
        }, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def list_events_from_multiple_calendars(
    calendar_ids: List[str],
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results_per_calendar: int = 10
) -> str:
    """List events from multiple specified calendars.
    
    Args:
        calendar_ids: List of calendar IDs to query (e.g., ["primary", "user@example.com"])
        time_min: Start time in RFC3339 format (e.g., "2024-01-01T00:00:00Z")
        time_max: End time in RFC3339 format
        max_results_per_calendar: Maximum events per calendar (default: 10)
        
    Returns:
        JSON string with combined events from all specified calendars, sorted by start time.
        Each event includes a 'calendar' field showing which calendar it came from.
    """
    try:
        client = get_calendar_client()
        events = client.list_events_from_calendars(
            calendar_ids=calendar_ids,
            time_min=time_min,
            time_max=time_max,
            max_results_per_calendar=max_results_per_calendar
        )
        
        if not events:
            return json.dumps({"message": "No events found in the specified calendars."})
        
        return json.dumps(events, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


@tool
def list_events_from_all_calendars(
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results_per_calendar: int = 10
) -> str:
    """List events from ALL accessible calendars.
    
    Args:
        time_min: Start time in RFC3339 format (defaults to midnight today)
        time_max: End time in RFC3339 format
        max_results_per_calendar: Maximum events per calendar (default: 10)
        
    Returns:
        JSON string with combined events from all calendars, sorted by start time.
        Each event includes a 'calendar' field with calendar name and ID.
    """
    try:
        client = get_calendar_client()
        events = client.list_events_from_all_calendars(
            time_min=time_min,
            time_max=time_max,
            max_results_per_calendar=max_results_per_calendar
        )
        
        if not events:
            return json.dumps({"message": "No events found across all calendars."})
        
        return json.dumps(events, indent=2)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})


# Export all tools
CALENDAR_TOOLS = [
    list_calendars,
    list_events,
    list_events_from_multiple_calendars,
    list_events_from_all_calendars,
    create_event,
    update_event,
    delete_event
]
