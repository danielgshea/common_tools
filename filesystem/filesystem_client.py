"""File system operations client.

This module provides a clean interface for file system operations including
creating, reading, writing, and deleting files.
"""
import os
from pathlib import Path
from typing import Optional, Union


class FileSystemClient:
    """Client for performing file system operations."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """Initialize the FileSystem client.
        
        Args:
            base_path: Optional base directory path. If provided, all operations
                      will be relative to this path. Options:
                      - Explicit path parameter (highest priority)
                      - FILESYSTEM_BASE_PATH environment variable
                      - Current working directory (default)
                      
        Environment Variables:
            FILESYSTEM_BASE_PATH: Base directory for file operations
            
        Examples:
            >>> # Use current working directory (default)
            >>> client = FileSystemClient()
            
            >>> # Explicit base path
            >>> client = FileSystemClient(base_path="/path/to/project")
            
            >>> # Via environment variable
            >>> os.environ['FILESYSTEM_BASE_PATH'] = '/path/to/project'
            >>> client = FileSystemClient()
        """
        if base_path:
            self.base_path = Path(base_path).resolve()
        else:
            env_base = os.getenv('FILESYSTEM_BASE_PATH')
            self.base_path = Path(env_base).resolve() if env_base else Path.cwd()
        
    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolve a path relative to base_path.
        
        Args:
            path: File path (can be relative or absolute)
            
        Returns:
            Resolved absolute path
        """
        path = Path(path)
        if path.is_absolute():
            return path
        return (self.base_path / path).resolve()
    
    def create_file(
        self, 
        path: Union[str, Path], 
        content: str = "", 
        overwrite: bool = False
    ) -> dict:
        """Create a new file with optional content.
        
        Args:
            path: Path to the file to create
            content: Initial content for the file (default: empty string)
            overwrite: If True, overwrite existing file. If False, raise error if file exists.
            
        Returns:
            Dictionary with status and file information
            
        Raises:
            FileExistsError: If file exists and overwrite is False
            PermissionError: If insufficient permissions to create file
        """
        file_path = self._resolve_path(path)
        
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {file_path}")
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        file_path.write_text(content, encoding='utf-8')
        
        return {
            'status': 'success',
            'action': 'created' if not file_path.exists() or not overwrite else 'overwritten',
            'path': str(file_path),
            'size': file_path.stat().st_size
        }
    
    def read_file(self, path: Union[str, Path]) -> dict:
        """Read the contents of a file.
        
        Args:
            path: Path to the file to read
            
        Returns:
            Dictionary with file content and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If insufficient permissions to read file
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        content = file_path.read_text(encoding='utf-8')
        stats = file_path.stat()
        
        return {
            'status': 'success',
            'path': str(file_path),
            'content': content,
            'size': stats.st_size,
            'modified': stats.st_mtime
        }
    
    def write_file(
        self, 
        path: Union[str, Path], 
        content: str,
        append: bool = False
    ) -> dict:
        """Write content to an existing file or create a new one.
        
        Args:
            path: Path to the file to write
            content: Content to write to the file
            append: If True, append to existing content. If False, overwrite.
            
        Returns:
            Dictionary with status and file information
            
        Raises:
            PermissionError: If insufficient permissions to write file
        """
        file_path = self._resolve_path(path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        return {
            'status': 'success',
            'action': 'appended' if append else 'written',
            'path': str(file_path),
            'size': file_path.stat().st_size
        }
    
    def delete_file(self, path: Union[str, Path]) -> dict:
        """Delete a file.
        
        Args:
            path: Path to the file to delete
            
        Returns:
            Dictionary with status information
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If insufficient permissions to delete file
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        file_path.unlink()
        
        return {
            'status': 'success',
            'action': 'deleted',
            'path': str(file_path)
        }
    
    def file_exists(self, path: Union[str, Path]) -> dict:
        """Check if a file exists.
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with existence status and file information if it exists
        """
        file_path = self._resolve_path(path)
        exists = file_path.exists() and file_path.is_file()
        
        result = {
            'exists': exists,
            'path': str(file_path)
        }
        
        if exists:
            stats = file_path.stat()
            result.update({
                'size': stats.st_size,
                'modified': stats.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK)
            })
        
        return result
    
    def list_files(
        self, 
        directory: Optional[Union[str, Path]] = None,
        pattern: str = "*",
        recursive: bool = False
    ) -> dict:
        """List files in a directory.
        
        Args:
            directory: Directory path (default: base_path)
            pattern: Glob pattern to filter files (default: "*" for all files)
            recursive: If True, search recursively in subdirectories
            
        Returns:
            Dictionary with list of files
            
        Raises:
            NotADirectoryError: If path is not a directory
        """
        dir_path = self._resolve_path(directory) if directory else self.base_path
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")
        
        # Use rglob for recursive, glob for non-recursive
        glob_method = dir_path.rglob if recursive else dir_path.glob
        files = [str(f) for f in glob_method(pattern) if f.is_file()]
        
        return {
            'status': 'success',
            'directory': str(dir_path),
            'pattern': pattern,
            'recursive': recursive,
            'files': files,
            'count': len(files)
        }
