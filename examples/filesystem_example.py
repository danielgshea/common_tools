"""Example usage of the Filesystem client.

This script demonstrates how to use the FileSystemClient for basic
file operations without LangChain or HITL complexity.

Prerequisites:
    - Python 3.7+
"""

import sys
from pathlib import Path

# Add parent directory to path to import tools package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import FileSystemClient


def main():
    """Demonstrate filesystem client functionality."""
    
    print("="*70)
    print("FILESYSTEM CLIENT DEMO")
    print("="*70)
    
    # Initialize the client
    fs = FileSystemClient()
    print(f"\n✓ Initialized FileSystemClient with base path: {fs.base_path}\n")
    
    # Example 1: Create a file
    print("-" * 70)
    print("1. CREATING A FILE")
    print("-" * 70)
    
    result = fs.create_file(
        path="demo_output.txt",
        content="Hello from the Filesystem Client!\nThis is a test file.\n",
        overwrite=True
    )
    print(f"✓ {result['action'].capitalize()}: {result['path']}")
    print(f"  Size: {result['size']} bytes\n")
    
    # Example 2: Check if file exists
    print("-" * 70)
    print("2. CHECKING FILE EXISTENCE")
    print("-" * 70)
    
    exists_result = fs.file_exists("demo_output.txt")
    print(f"✓ File exists: {exists_result['exists']}")
    if exists_result['exists']:
        print(f"  Size: {exists_result['size']} bytes")
        print(f"  Readable: {exists_result['is_readable']}")
        print(f"  Writable: {exists_result['is_writable']}\n")
    
    # Example 3: Read the file
    print("-" * 70)
    print("3. READING FILE CONTENT")
    print("-" * 70)
    
    read_result = fs.read_file("demo_output.txt")
    print(f"✓ Read file: {read_result['path']}")
    print(f"  Content:\n{read_result['content']}")
    
    # Example 4: Append to the file
    print("-" * 70)
    print("4. APPENDING TO FILE")
    print("-" * 70)
    
    write_result = fs.write_file(
        path="demo_output.txt",
        content="This line was appended!\n",
        append=True
    )
    print(f"✓ {write_result['action'].capitalize()}: {write_result['path']}")
    print(f"  New size: {write_result['size']} bytes\n")
    
    # Read again to show appended content
    read_result = fs.read_file("demo_output.txt")
    print(f"  Updated content:\n{read_result['content']}")
    
    # Example 5: List files
    print("-" * 70)
    print("5. LISTING FILES")
    print("-" * 70)
    
    list_result = fs.list_files(pattern="*.txt")
    print(f"✓ Found {list_result['count']} .txt files in {list_result['directory']}")
    for file_path in list_result['files'][:5]:  # Show first 5
        print(f"  • {file_path}")
    if list_result['count'] > 5:
        print(f"  ... and {list_result['count'] - 5} more\n")
    else:
        print()
    
    # Example 6: List Python files recursively
    print("-" * 70)
    print("6. LISTING PYTHON FILES (RECURSIVE)")
    print("-" * 70)
    
    py_result = fs.list_files(pattern="*.py", recursive=True)
    print(f"✓ Found {py_result['count']} .py files recursively")
    for file_path in py_result['files'][:5]:  # Show first 5
        print(f"  • {file_path}")
    if py_result['count'] > 5:
        print(f"  ... and {py_result['count'] - 5} more\n")
    else:
        print()
    
    # Example 7: Delete the file
    print("-" * 70)
    print("7. DELETING FILE")
    print("-" * 70)
    
    delete_result = fs.delete_file("demo_output.txt")
    print(f"✓ {delete_result['action'].capitalize()}: {delete_result['path']}\n")
    
    # Verify deletion
    exists_result = fs.file_exists("demo_output.txt")
    print(f"✓ File still exists: {exists_result['exists']}\n")
    
    print("="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
