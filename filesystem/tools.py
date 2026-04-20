"""LangChain tool wrappers for filesystem operations with Human-in-the-Loop support.

This module provides LangChain tool decorators for filesystem operations that can be
used with agents and the HumanInTheLoopMiddleware for approval workflows.

Example usage with HITL:
    from langchain.agents import create_agent
    from langchain.agents.middleware import HumanInTheLoopMiddleware
    from langgraph.checkpoint.memory import InMemorySaver
    from filesystem.tools import (
        create_file_tool, read_file_tool, write_file_tool, 
        delete_file_tool, list_files_tool
    )
    
    agent = create_agent(
        model="gpt-4",
        tools=[create_file_tool, read_file_tool, write_file_tool, 
               delete_file_tool, list_files_tool],
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "create_file": True,  # Require approval for file creation
                    "write_file": True,   # Require approval for writing
                    "delete_file": True,  # Require approval for deletion
                    "read_file": False,   # Auto-approve reads (safe operation)
                    "list_files": False,  # Auto-approve listing (safe operation)
                },
            ),
        ],
        checkpointer=InMemorySaver(),
    )
"""
from typing import Optional
from langchain_core.tools import tool
from .filesystem_client import FileSystemClient


# Create a default filesystem client instance
_fs_client = FileSystemClient()


@tool
def create_file_tool(
    path: str,
    content: str = "",
    overwrite: bool = False
) -> dict:
    """Create a new file with optional content.
    
    This tool creates a new file at the specified path. Use this when you need to
    create a new file for any purpose. Parent directories will be created automatically
    if they don't exist.
    
    Args:
        path: Path where the file should be created (relative or absolute)
        content: Initial content to write to the file (default: empty string)
        overwrite: If True, overwrite the file if it already exists. If False, 
                  raise an error if the file exists (default: False) 
        
    Returns:
        Dictionary with status, action, path, and file size
        
    Example:
        create_file_tool(path="notes.txt", content="Hello World", overwrite=False)
    """
    try:
        result = _fs_client.create_file(path=path, content=content, overwrite=overwrite)
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }


@tool
def read_file_tool(path: str) -> dict:
    """Read the contents of a file.
    
    This tool reads and returns the complete contents of a text file. Use this
    when you need to examine the contents of an existing file.
    
    Args:
        path: Path to the file to read (relative or absolute)
        
    Returns:
        Dictionary with status, path, content, size, and modification time
        
    Example:
        read_file_tool(path="config.json")
    """
    try:
        result = _fs_client.read_file(path=path)
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }


@tool
def write_file_tool(
    path: str,
    content: str,
    append: bool = False
) -> dict:
    """Write content to a file, creating it if it doesn't exist.
    
    This tool writes or appends content to a file. If the file doesn't exist, it
    will be created. Use this when you need to modify or add content to a file.
    
    Args:
        path: Path to the file to write (relative or absolute)
        content: Content to write to the file
        append: If True, append content to the end of the file. If False, 
               overwrite the entire file with new content (default: False)
        
    Returns:
        Dictionary with status, action (written/appended), path, and file size
        
    Example:
        write_file_tool(path="log.txt", content="New log entry\\n", append=True)
    """
    try:
        result = _fs_client.write_file(path=path, content=content, append=append)
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }


@tool
def delete_file_tool(path: str) -> dict:
    """Delete a file from the filesystem.
    
    This tool permanently deletes a file. Use with caution as this operation
    cannot be undone. The file must exist and be a regular file (not a directory).
    
    Args:
        path: Path to the file to delete (relative or absolute)
        
    Returns:
        Dictionary with status, action, and path of deleted file
        
    Example:
        delete_file_tool(path="temp_file.txt")
    """
    try:
        result = _fs_client.delete_file(path=path)
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }


@tool
def file_exists_tool(path: str) -> dict:
    """Check if a file exists and get its metadata.
    
    This tool checks whether a file exists at the specified path and returns
    metadata about it if it does. Use this when you need to verify a file's
    existence before performing other operations.
    
    Args:
        path: Path to check (relative or absolute)
        
    Returns:
        Dictionary with exists status, path, and metadata if file exists
        (size, modified time, readable, writable flags)
        
    Example:
        file_exists_tool(path="config.json")
    """
    try:
        result = _fs_client.file_exists(path=path)
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }


@tool
def list_files_tool(
    directory: Optional[str] = None,
    pattern: str = "*",
    recursive: bool = False
) -> dict:
    """List files in a directory with optional filtering.
    
    This tool lists all files in a directory, optionally filtering by a glob pattern
    and searching recursively through subdirectories. Use this when you need to
    discover what files are available.
    
    Args:
        directory: Directory path to list files from. If not provided, uses current
                  working directory (default: None)
        pattern: Glob pattern to filter files, e.g., "*.txt", "data_*.csv" 
                (default: "*" for all files)
        recursive: If True, search recursively in all subdirectories. If False,
                  only list files in the specified directory (default: False)
        
    Returns:
        Dictionary with status, directory, pattern, files list, and count
        
    Example:
        list_files_tool(directory="logs", pattern="*.log", recursive=True)
    """
    try:
        result = _fs_client.list_files(
            directory=directory,
            pattern=pattern,
            recursive=recursive
        )
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }


FILE_SYSTEM_TOOLS = [
    create_file_tool,
    read_file_tool,
    write_file_tool,
    delete_file_tool,
    file_exists_tool,
    list_files_tool
]
