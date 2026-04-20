"""Example usage of Gmail client and tools.

This example demonstrates how to use the Gmail client directly
or integrate it with LangChain agents.
"""
from gmail import GmailClient, GMAIL_TOOLS


def direct_client_example():
    """Example of using the GmailClient directly."""
    print("=" * 60)
    print("Gmail Client Direct Usage Example")
    print("=" * 60)
    
    # Initialize the client
    client = GmailClient()
    
    # List recent messages
    print("\n1. Listing recent messages...")
    messages = client.list_messages(max_results=5)
    print(f"Found {len(messages)} messages")
    for msg in messages:
        print(f"  - Message ID: {msg['id']}")
    
    # Search for unread messages
    print("\n2. Searching for unread messages...")
    unread = client.search_messages(query="is:unread", max_results=3)
    print(f"Found {len(unread)} unread messages")
    for msg in unread:
        print(f"  - From: {msg.get('from', 'Unknown')}")
        print(f"    Subject: {msg.get('subject', 'No subject')}")
        print(f"    Snippet: {msg.get('snippet', '')[:50]}...")
    
    # List available labels
    print("\n3. Listing Gmail labels...")
    labels = client.list_labels()
    print(f"Found {len(labels)} labels:")
    for label in labels[:10]:  # Show first 10
        print(f"  - {label['name']} (ID: {label['id']})")
    
    # Example: Read a specific message (if messages exist)
    if messages:
        print(f"\n4. Reading first message in detail...")
        message_id = messages[0]['id']
        full_message = client.get_message(message_id)
        print(f"  From: {full_message.get('from', 'Unknown')}")
        print(f"  To: {full_message.get('to', 'Unknown')}")
        print(f"  Subject: {full_message.get('subject', 'No subject')}")
        print(f"  Date: {full_message.get('date', 'Unknown')}")
        body = full_message.get('body', {})
        plain_text = body.get('plain', '')
        if plain_text:
            print(f"  Body preview: {plain_text[:100]}...")
    
    print("\n" + "=" * 60)
    print("Direct client example completed!")
    print("=" * 60)


def langchain_tools_example():
    """Example of using Gmail tools with LangChain.
    
    Note: This requires additional setup with a language model.
    """
    print("\n" + "=" * 60)
    print("Gmail LangChain Tools Example")
    print("=" * 60)
    
    print("\nAvailable Gmail tools:")
    for i, tool in enumerate(GMAIL_TOOLS, 1):
        print(f"{i:2d}. {tool.name}: {tool.description}")
    
    print("\n" + "=" * 60)
    print("These tools can be used with LangChain agents like:")
    print("=" * 60)
    print("""
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    from gmail import GMAIL_TOOLS
    
    # Create a model
    model = ChatOpenAI(model="gpt-4")
    
    # Create an agent with Gmail tools
    agent = create_react_agent(model, GMAIL_TOOLS)
    
    # Use the agent
    response = agent.invoke({
        "messages": [("user", "Search my inbox for emails about project updates")]
    })
    """)


def send_email_example():
    """Example of sending an email.
    
    WARNING: This will actually send an email if executed!
    Uncomment the code below to test sending.
    """
    print("\n" + "=" * 60)
    print("Send Email Example (Commented Out)")
    print("=" * 60)
    
    print("\nTo send an email, use:")
    print("""
    client = GmailClient()
    
    result = client.send_message(
        to="recipient@example.com",
        subject="Test Email from Gmail Client",
        body="This is a test email sent via the Gmail API client."
    )
    
    print(f"Email sent! Message ID: {result['id']}")
    """)
    
    # Uncomment to actually send (replace with real email):
    # client = GmailClient()
    # result = client.send_message(
    #     to="your-email@example.com",
    #     subject="Test Email",
    #     body="Hello from the Gmail client!"
    # )
    # print(f"Email sent! Message ID: {result['id']}")


def draft_example():
    """Example of creating and managing drafts."""
    print("\n" + "=" * 60)
    print("Draft Management Example (Commented Out)")
    print("=" * 60)
    
    print("\nTo create and send a draft:")
    print("""
    client = GmailClient()
    
    # Create a draft
    draft = client.create_draft(
        to="recipient@example.com",
        subject="Draft Email",
        body="This is a draft that can be edited before sending."
    )
    print(f"Draft created! Draft ID: {draft['id']}")
    
    # Later, send the draft
    result = client.send_draft(draft['id'])
    print(f"Draft sent! Message ID: {result['id']}")
    """)


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Gmail API Client - Example Usage".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    
    try:
        # Run the direct client example
        direct_client_example()
        
        # Show LangChain tools
        langchain_tools_example()
        
        # Show sending examples (commented out for safety)
        send_email_example()
        draft_example()
        
    except AssertionError as e:
        print("\n" + "!" * 60)
        print("ERROR: Credentials not found!")
        print("!" * 60)
        print(str(e))
        print("\nTo use the Gmail client, you need to:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 credentials")
        print("3. Download the credentials.json file")
        print("4. Place it in the project root directory")
        print("\nMake sure to enable the Gmail API in your Google Cloud project!")
        
    except Exception as e:
        print(f"\n! Error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")
