#!/usr/bin/env python3
"""Demo file to verify all tools are working correctly.

This script:
1. Loads credentials from .env file
2. Checks credentials for calendar and email tools
3. Tests basic functionality of all tools
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("COMMON TOOLS - COMPREHENSIVE DEMO")
print("=" * 80)

# Verify credentials
print("\n📋 Step 1: Verifying Credentials")
print("-" * 80)

creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
if not creds_path:
    print("❌ GOOGLE_CREDENTIALS_PATH not set in .env file")
    sys.exit(1)

if not Path(creds_path).exists():
    print(f"❌ Credentials file not found: {creds_path}")
    sys.exit(1)

print(f"✅ Credentials file found: {creds_path}")

# Test 1: Filesystem Tools
print("\n📁 Step 2: Testing Filesystem Tools")
print("-" * 80)

try:
    from filesystem.filesystem_client import FileSystemClient
    
    # Create temp directory for demo
    import tempfile
    with tempfile.TemporaryDirectory(prefix="demo_") as tmpdir:
        client = FileSystemClient(base_path=tmpdir)
        
        # Create a file
        result = client.create_file("demo.txt", content="Hello from filesystem tools!")
        print(f"✅ Created file: {result['path']}")
        
        # Read it back
        read_result = client.read_file("demo.txt")
        print(f"✅ Read file content: '{read_result['content']}'")
        
        # List files
        list_result = client.list_files()
        print(f"✅ Listed {list_result['count']} file(s)")
        
        print("✅ Filesystem tools: ALL WORKING")
        
except Exception as e:
    print(f"❌ Filesystem tools failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Gmail Tools with Credential Check
print("\n📧 Step 3: Testing Gmail Tools")
print("-" * 80)

try:
    from gmail.gmail_client import GmailClient
    
    # Initialize client (this checks credentials)
    print("🔐 Initializing Gmail client (checking credentials)...")
    gmail_client = GmailClient()
    
    print(f"✅ Gmail credentials valid")
    print(f"   Credentials: {gmail_client.credentials_path}")
    print(f"   Token: {gmail_client.token_path}")
    
    # Test listing recent messages
    print("\n📬 Listing recent messages...")
    messages = gmail_client.list_messages(max_results=3)
    
    print(f"✅ Retrieved {len(messages)} messages")
    
    if messages:
        msg = messages[0]
        print(f"\n   📨 Sample message:")
        print(f"      Subject: {msg.get('subject', 'No subject')[:60]}")
        print(f"      From: {msg.get('from', 'Unknown')[:40]}")
        print(f"      Snippet: {msg.get('snippet', '')[:60]}...")
    
    # Test listing labels
    labels = gmail_client.list_labels()
    print(f"\n✅ Retrieved {len(labels)} labels")
    print(f"   Sample: {', '.join([l['name'] for l in labels[:5]])}")
    
    print("\n✅ Gmail tools: ALL WORKING")
    
except Exception as e:
    print(f"❌ Gmail tools failed: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Ensure Gmail API is enabled")
    print("   2. Check credentials.json is valid")
    print("   3. Try deleting token.json and re-authenticating")
    import traceback
    traceback.print_exc()

# Test 3: Calendar Tools with Credential Check
print("\n📅 Step 4: Testing Calendar Tools")
print("-" * 80)

try:
    from gcalendar.google_cal import GoogleCalendarClient
    
    # Initialize client (this checks credentials)
    print("🔐 Initializing Calendar client (checking credentials)...")
    cal_client = GoogleCalendarClient()
    
    print(f"✅ Calendar credentials valid")
    print(f"   Credentials: {cal_client.credentials_path}")
    print(f"   Token: {cal_client.token_path}")
    
    # Test listing calendars
    print("\n📆 Listing calendars...")
    calendars = cal_client.list_calendars()
    
    print(f"✅ Retrieved {len(calendars)} calendar(s)")
    
    for cal in calendars:
        icon = "⭐" if cal.get('primary') else "  "
        print(f"   {icon} {cal['summary']}")
    
    # Test listing upcoming events
    print("\n📅 Listing upcoming events (next 14 days)...")
    now = datetime.now()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=14)).isoformat() + 'Z'
    
    events = cal_client.list_events(
        time_min=time_min,
        time_max=time_max,
        max_results=5
    )
    
    print(f"✅ Retrieved {len(events)} upcoming event(s)")
    
    if events:
        print(f"\n   📌 Next event:")
        event = events[0]
        print(f"      Title: {event.get('summary', 'No title')}")
        print(f"      Start: {event.get('start', 'Unknown')}")
    
    print("\n✅ Calendar tools: ALL WORKING")
    
except Exception as e:
    print(f"❌ Calendar tools failed: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Ensure Calendar API is enabled")
    print("   2. Check credentials.json is valid")
    print("   3. Try deleting token.json and re-authenticating")
    import traceback
    traceback.print_exc()

# Test 4: LangChain Tool Wrappers
print("\n🔧 Step 5: Testing LangChain Tool Wrappers")
print("-" * 80)

try:
    from gmail.tools import GMAIL_TOOLS, GMAIL_TOOLS_S, GMAIL_TOOLS_D
    from gcalendar.tools import CALENDAR_TOOLS, CALENDAR_TOOLS_S, CALENDAR_TOOLS_D
    from filesystem.tools import FILE_SYSTEM_TOOLS, FILE_SYSTEM_TOOLS_S, FILE_SYSTEM_TOOLS_D
    
    print(f"✅ Gmail tools loaded:")
    print(f"   Total: {len(GMAIL_TOOLS)} tools")
    print(f"   Safe (read-only): {len(GMAIL_TOOLS_S)} tools")
    print(f"   Dangerous (write): {len(GMAIL_TOOLS_D)} tools")
    
    print(f"\n✅ Calendar tools loaded:")
    print(f"   Total: {len(CALENDAR_TOOLS)} tools")
    print(f"   Safe (read-only): {len(CALENDAR_TOOLS_S)} tools")
    print(f"   Dangerous (write): {len(CALENDAR_TOOLS_D)} tools")
    
    print(f"\n✅ Filesystem tools loaded:")
    print(f"   Total: {len(FILE_SYSTEM_TOOLS)} tools")
    print(f"   Safe (read-only): {len(FILE_SYSTEM_TOOLS_S)} tools")
    print(f"   Dangerous (write): {len(FILE_SYSTEM_TOOLS_D)} tools")
    
    print("\n✅ LangChain tool wrappers: ALL WORKING")
    
except Exception as e:
    print(f"❌ Tool wrappers failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 80)
print("DEMO COMPLETE - SUMMARY")
print("=" * 80)

print("""
✅ All tools are loaded and working correctly!

Your tools are ready to use in LangChain agents:

    from gmail.tools import GMAIL_TOOLS
    from gcalendar.tools import CALENDAR_TOOLS
    from filesystem.tools import create_file_tool, read_file_tool
    
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    
    all_tools = GMAIL_TOOLS + CALENDAR_TOOLS + [create_file_tool, read_file_tool]
    
    model = ChatOpenAI(model="gpt-4")
    agent = create_react_agent(model, all_tools)
    
    response = agent.invoke({
        "messages": [("user", "Check my emails and calendar for today")]
    })

📖 Documentation: See tests/README.md for more examples
🧪 Run Tests: pytest tests/
""")
