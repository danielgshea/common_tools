"""Example of filesystem tools with Human-in-the-Loop controls.

This example demonstrates how to use the filesystem tools with LangChain's
HumanInTheLoopMiddleware for approval workflows. Destructive operations like
creating, writing, and deleting files require human approval before execution.

Prerequisites:
    - Install LangChain dependencies: pip install -r requirements.txt
    - Set your OpenAI API key: export OPENAI_API_KEY=your_key_here
"""

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from filesystem.tools import (
    create_file_tool,
    read_file_tool,
    write_file_tool,
    delete_file_tool,
    file_exists_tool,
    list_files_tool
)


def create_filesystem_agent():
    """Create an agent with filesystem tools and HITL middleware."""
    
    agent = create_agent(
        model="gpt-4o-mini",  # or "gpt-4"
        tools=[
            create_file_tool,
            read_file_tool,
            write_file_tool,
            delete_file_tool,
            file_exists_tool,
            list_files_tool
        ],
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    # Require approval for destructive operations
                    "create_file_tool": {
                        "allowed_decisions": ["approve", "edit", "reject"],
                        "description": "File creation requires approval"
                    },
                    "write_file_tool": {
                        "allowed_decisions": ["approve", "edit", "reject"],
                        "description": "File modification requires approval"
                    },
                    "delete_file_tool": {
                        "allowed_decisions": ["approve", "reject"],  # No editing delete
                        "description": "File deletion requires approval"
                    },
                    # Auto-approve safe read operations
                    "read_file_tool": False,
                    "file_exists_tool": False,
                    "list_files_tool": False,
                },
                description_prefix="⚠️  Action requires approval",
            ),
        ],
        # Human-in-the-loop requires checkpointing
        checkpointer=InMemorySaver(),
    )
    
    return agent


def handle_interrupts(result, config):
    """Process interrupts and get human decisions.
    
    Args:
        result: GraphOutput with interrupts
        config: Thread configuration
        
    Returns:
        List of decisions for each interrupted action
    """
    if not result.interrupts:
        return None
    
    interrupt = result.interrupts[0]
    action_requests = interrupt.value.get('action_requests', [])
    review_configs = interrupt.value.get('review_configs', [])
    
    print("\n" + "="*70)
    print("🛑 HUMAN APPROVAL REQUIRED")
    print("="*70)
    
    decisions = []
    
    for i, (action, review_config) in enumerate(zip(action_requests, review_configs)):
        print(f"\n📋 Action #{i+1}:")
        print(f"   Tool: {action['name']}")
        print(f"   Arguments: {action.get('arguments', {})}")
        print(f"   Description: {action.get('description', 'N/A')}")
        print(f"   Allowed decisions: {review_config['allowed_decisions']}")
        
        # Get human decision
        while True:
            decision_type = input(f"\n   Your decision [approve/edit/reject]: ").strip().lower()
            
            if decision_type not in review_config['allowed_decisions']:
                print(f"   ❌ Invalid decision. Allowed: {review_config['allowed_decisions']}")
                continue
            
            if decision_type == "approve":
                decisions.append({"type": "approve"})
                print("   ✅ Approved")
                break
            
            elif decision_type == "edit":
                print("   ✏️  Edit mode - modify arguments")
                # For simplicity, just collect new arguments as JSON
                import json
                new_args_str = input("   Enter new arguments as JSON: ").strip()
                try:
                    new_args = json.loads(new_args_str)
                    decisions.append({
                        "type": "edit",
                        "edited_action": {
                            "name": action['name'],
                            "args": new_args
                        }
                    })
                    print("   ✅ Edited and approved")
                    break
                except json.JSONDecodeError:
                    print("   ❌ Invalid JSON, try again")
            
            elif decision_type == "reject":
                reason = input("   Reason for rejection: ").strip()
                decisions.append({
                    "type": "reject",
                    "message": reason or "Action rejected by user"
                })
                print("   ❌ Rejected")
                break
    
    print("\n" + "="*70)
    
    return decisions


def main():
    """Run the filesystem agent with HITL demo."""
    
    print("="*70)
    print("FILESYSTEM TOOLS WITH HUMAN-IN-THE-LOOP DEMO")
    print("="*70)
    print("\nThis demo shows how filesystem operations require human approval.")
    print("Safe operations (read, list) are auto-approved.")
    print("Destructive operations (create, write, delete) need your permission.\n")
    
    # Create the agent
    agent = create_filesystem_agent()
    
    # Configuration with thread ID for persistence
    config = {"configurable": {"thread_id": "demo_thread_001"}}
    
    # Example task requiring approval
    task = """
    Please help me with the following tasks:
    1. List all .py files in the current directory
    2. Create a new file called 'test_output.txt' with the content 'Hello from HITL demo!'
    3. Read the content of the file you just created
    """.strip()
    
    print(f"Task: {task}\n")
    print("-" * 70)
    
    # Run the agent
    print("\n🤖 Agent is working...\n")
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": task}]},
        config=config,
        version="v2"
    )
    
    # Handle interrupts if any
    while result.interrupts:
        decisions = handle_interrupts(result, config)
        
        if decisions:
            # Resume with decisions
            print("\n🤖 Resuming agent with your decisions...\n")
            result = agent.invoke(
                Command(resume={"decisions": decisions}),
                config=config,
                version="v2"
            )
        else:
            break
    
    # Show final result
    print("\n" + "="*70)
    print("✅ TASK COMPLETE")
    print("="*70)
    
    if hasattr(result, 'value') and result.value:
        messages = result.value.get('messages', [])
        if messages:
            final_message = messages[-1]
            print(f"\nAgent's final response:\n{final_message.get('content', 'No content')}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
