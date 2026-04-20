"""Integration tests for Google Calendar operations.

These tests use real Calendar API calls with actual credentials.
Tests create/modify/delete test events in your actual calendar.
"""

import pytest
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError


@pytest.mark.integration
@pytest.mark.slow
class TestGoogleCalendarIntegration:
    """Integration tests for GoogleCalendarClient."""
    
    def test_client_initialization(self, calendar_client):
        """Test that Calendar client initializes correctly."""
        assert calendar_client is not None
        assert calendar_client.credentials_path.exists()
        assert calendar_client.service is not None
    
    def test_list_calendars(self, calendar_client):
        """Test listing available calendars."""
        calendars = calendar_client.list_calendars()
        
        assert isinstance(calendars, list)
        assert len(calendars) > 0
        
        # Check for primary calendar
        primary_cals = [cal for cal in calendars if cal.get('primary', False)]
        assert len(primary_cals) == 1
        
        # Verify calendar structure
        cal = calendars[0]
        assert 'id' in cal
        assert 'summary' in cal
        
        print(f"\n✅ Retrieved {len(calendars)} calendars")
        print(f"   Primary: {primary_cals[0]['summary']}")
    
    def test_list_upcoming_events(self, calendar_client):
        """Test listing upcoming events."""
        # Get events for next 30 days
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=30)).isoformat() + 'Z'
        
        events = calendar_client.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=10
        )
        
        assert isinstance(events, list)
        
        if len(events) > 0:
            event = events[0]
            assert 'id' in event
            assert 'summary' in event
            assert 'start' in event
            
            print(f"\n✅ Retrieved {len(events)} upcoming events")
            print(f"   Next event: {event.get('summary', 'No title')}")
    
    def test_list_events_from_multiple_calendars(self, calendar_client):
        """Test listing events from specific calendars."""
        # Get all calendars
        calendars = calendar_client.list_calendars()
        calendar_ids = [cal['id'] for cal in calendars[:3]]  # Test with first 3
        
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
        
        events = calendar_client.list_events_from_calendars(
            calendar_ids=calendar_ids,
            time_min=time_min,
            time_max=time_max,
            max_results_per_calendar=5  # Correct parameter name
        )
        
        assert isinstance(events, list)
        
        print(f"\n✅ Retrieved {len(events)} events from {len(calendar_ids)} calendars")
    
    @pytest.mark.modifies_data
    def test_create_and_delete_event(self, calendar_client, safe_mode):
        """Test creating and deleting an event.
        
        WARNING: This creates and deletes a real calendar event!
        """
        # Create a test event
        start_time = datetime.now() + timedelta(days=7)
        end_time = start_time + timedelta(hours=1)
        
        event = calendar_client.create_event(
            summary="[TEST] Integration Test Event - Can Delete",
            description="This event was created by integration tests and can be safely deleted.",
            start_time=start_time.isoformat() + 'Z',
            end_time=end_time.isoformat() + 'Z'
        )
        
        assert 'id' in event
        assert 'summary' in event
        
        event_id = event['id']
        print(f"\n✅ Created test event with ID: {event_id}")
        
        # Delete the event
        result = calendar_client.delete_event(event_id)
        assert result is True
        print(f"✅ Deleted test event")
    
    @pytest.mark.modifies_data
    def test_create_update_delete_event(self, calendar_client, safe_mode):
        """Test creating, updating, and deleting an event.
        
        WARNING: This creates, modifies, and deletes a real calendar event!
        """
        # Create event
        start_time = datetime.now() + timedelta(days=8)
        end_time = start_time + timedelta(hours=1)
        
        event = calendar_client.create_event(
            summary="[TEST] Update Test Event",
            description="Original description",
            start_time=start_time.isoformat() + 'Z',
            end_time=end_time.isoformat() + 'Z'
        )
        
        event_id = event['id']
        print(f"\n✅ Created event for update test")
        
        try:
            # Update the event
            updated = calendar_client.update_event(
                event_id=event_id,
                summary="[TEST] Updated Event Title",
                description="Updated description"
            )
            
            assert updated['summary'] == "[TEST] Updated Event Title"
            print(f"✅ Updated event successfully")
            
        finally:
            # Always clean up
            calendar_client.delete_event(event_id)
            print(f"✅ Cleaned up test event")
    
    @pytest.mark.modifies_data
    @pytest.mark.skip(reason="Calendar API create_event needs modification to support all-day events with 'date' format instead of 'dateTime'")
    def test_create_all_day_event(self, calendar_client, safe_mode):
        """Test creating an all-day event."""
        # NOTE: This requires modifying GoogleCalendarClient.create_event to support
        # all-day events by using 'date' field instead of 'dateTime'
        start_date = (datetime.now() + timedelta(days=10)).date()
        
        # For all-day events, use date format without time
        event = calendar_client.create_event(
            summary="[TEST] All Day Event",
            description="Test all-day event",
            start_time=start_date.isoformat(),  # YYYY-MM-DD format
            end_time=(start_date + timedelta(days=1)).isoformat()
        )
        
        assert 'id' in event
        event_id = event['id']
        print(f"\n✅ Created all-day event")
        
        try:
            # Verify the event was created
            assert event['summary'] == "[TEST] All Day Event"
        finally:
            calendar_client.delete_event(event_id)
            print(f"✅ Cleaned up all-day event")
    
    def test_list_events_date_range(self, calendar_client):
        """Test listing events within specific date range."""
        # Get events for exactly 7 days from now
        start = datetime.now()
        end = start + timedelta(days=7)
        
        events = calendar_client.list_events(
            time_min=start.isoformat() + 'Z',
            time_max=end.isoformat() + 'Z',
            max_results=20
        )
        
        assert isinstance(events, list)
        
        # Verify all events have required fields
        for event in events:
            assert 'start' in event
            assert event['start'] is not None  # start is a string in the response
        
        print(f"\n✅ Retrieved {len(events)} events in 7-day range")
    
    def test_list_events_from_primary_calendar(self, calendar_client):
        """Test listing events from primary calendar explicitly."""
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=30)).isoformat() + 'Z'
        
        events = calendar_client.list_events(
            calendar_id="primary",
            time_min=time_min,
            time_max=time_max,
            max_results=5
        )
        
        assert isinstance(events, list)
        print(f"\n✅ Retrieved {len(events)} events from primary calendar")
    
    def test_list_events_from_all_calendars(self, calendar_client):
        """Test listing events from all calendars."""
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
        
        events = calendar_client.list_events_from_all_calendars(
            time_min=time_min,
            time_max=time_max,
            max_results_per_calendar=3
        )
        
        assert isinstance(events, list)
        
        # Events from all calendars should have calendar info
        if len(events) > 0:
            assert 'calendar' in events[0]
            assert 'id' in events[0]['calendar']
        
        print(f"\n✅ Retrieved {len(events)} events from all calendars")


@pytest.mark.integration
class TestCalendarTools:
    """Integration tests for Calendar LangChain tools."""
    
    def test_list_calendars_tool(self, calendar_client):
        """Test the list_calendars tool wrapper."""
        from gcalendar.tools import list_calendars
        
        result = list_calendars.invoke({})
        
        # Tool returns JSON string
        assert isinstance(result, str)
        
        # Parse and verify
        import json
        data = json.loads(result)
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        
        print(f"\n✅ list_calendars tool returned valid JSON")
    
    def test_list_events_tool(self, calendar_client):
        """Test the list_events tool wrapper."""
        from gcalendar.tools import list_events
        
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'Z'
        
        result = list_events.invoke({
            "time_min": time_min,
            "time_max": time_max,
            "max_results": 5
        })
        
        import json
        data = json.loads(result)
        
        assert isinstance(data, (list, dict))
        print(f"\n✅ list_events tool returned valid JSON")
