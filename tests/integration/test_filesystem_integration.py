"""Integration tests for filesystem operations.

These tests use real file I/O operations in a temporary directory.
"""

import pytest
from pathlib import Path


@pytest.mark.integration
class TestFileSystemIntegration:
    """Integration tests for FileSystemClient."""
    
    def test_create_and_read_file(self, filesystem_client):
        """Test creating and reading a file."""
        # Create a file
        content = "Hello, World!"
        result = filesystem_client.create_file("test.txt", content=content)
        
        assert result['status'] == 'success'
        assert result['action'] == 'created'
        assert 'test.txt' in result['path']
        assert result['size'] > 0
        
        # Read the file back
        read_result = filesystem_client.read_file("test.txt")
        
        assert read_result['status'] == 'success'
        assert read_result['content'] == content
        assert read_result['size'] == len(content)
    
    def test_write_and_append_file(self, filesystem_client):
        """Test writing and appending to a file."""
        # Create initial file
        filesystem_client.create_file("append_test.txt", content="Line 1\n")
        
        # Append to the file
        result = filesystem_client.write_file("append_test.txt", content="Line 2\n", append=True)
        
        assert result['status'] == 'success'
        assert result['action'] == 'appended'
        
        # Read and verify
        read_result = filesystem_client.read_file("append_test.txt")
        assert read_result['content'] == "Line 1\nLine 2\n"
    
    def test_overwrite_file(self, filesystem_client):
        """Test overwriting an existing file."""
        # Create initial file
        filesystem_client.create_file("overwrite_test.txt", content="Original")
        
        # Overwrite with create_file
        result = filesystem_client.create_file("overwrite_test.txt", content="New", overwrite=True)
        
        assert result['status'] == 'success'
        
        # Verify content was overwritten
        read_result = filesystem_client.read_file("overwrite_test.txt")
        assert read_result['content'] == "New"
    
    def test_file_exists(self, filesystem_client):
        """Test checking if a file exists."""
        # Check non-existent file
        result = filesystem_client.file_exists("nonexistent.txt")
        assert result['exists'] is False
        
        # Create file and check again
        filesystem_client.create_file("exists_test.txt", content="test")
        result = filesystem_client.file_exists("exists_test.txt")
        
        assert result['exists'] is True
        assert result['size'] > 0
        assert result['is_readable'] is True
        assert result['is_writable'] is True
    
    def test_delete_file(self, filesystem_client):
        """Test deleting a file."""
        # Create a file
        filesystem_client.create_file("delete_test.txt", content="Delete me")
        
        # Verify it exists
        assert filesystem_client.file_exists("delete_test.txt")['exists'] is True
        
        # Delete it
        result = filesystem_client.delete_file("delete_test.txt")
        
        assert result['status'] == 'success'
        assert result['action'] == 'deleted'
        
        # Verify it's gone
        assert filesystem_client.file_exists("delete_test.txt")['exists'] is False
    
    def test_list_files(self, filesystem_client, temp_test_dir):
        """Test listing files in a directory."""
        # Create multiple files
        filesystem_client.create_file("file1.txt", content="1")
        filesystem_client.create_file("file2.txt", content="2")
        filesystem_client.create_file("file3.log", content="3")
        
        # List all files
        result = filesystem_client.list_files()
        
        assert result['status'] == 'success'
        assert result['count'] == 3
        assert len(result['files']) == 3
        
        # List only .txt files
        result = filesystem_client.list_files(pattern="*.txt")
        
        assert result['count'] == 2
        assert all(f.endswith('.txt') for f in result['files'])
    
    def test_list_files_recursive(self, filesystem_client, temp_test_dir):
        """Test recursive file listing."""
        # Create nested directory structure
        subdir = temp_test_dir / "subdir"
        subdir.mkdir()
        
        filesystem_client.create_file("root_file.txt", content="root")
        filesystem_client.create_file("subdir/nested_file.txt", content="nested")
        
        # Non-recursive should find only 1
        result = filesystem_client.list_files(pattern="*.txt", recursive=False)
        assert result['count'] == 1
        
        # Recursive should find both
        result = filesystem_client.list_files(pattern="*.txt", recursive=True)
        assert result['count'] == 2
    
    def test_create_file_with_nested_path(self, filesystem_client):
        """Test creating a file in a nested directory."""
        # Create file in nested path (directories should be created)
        result = filesystem_client.create_file("nested/dir/file.txt", content="nested")
        
        assert result['status'] == 'success'
        assert 'nested/dir/file.txt' in result['path']
        
        # Verify we can read it
        read_result = filesystem_client.read_file("nested/dir/file.txt")
        assert read_result['content'] == "nested"
    
    def test_error_file_not_found(self, filesystem_client):
        """Test error when reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            filesystem_client.read_file("nonexistent.txt")
    
    def test_error_file_exists_no_overwrite(self, filesystem_client):
        """Test error when creating file that exists without overwrite."""
        filesystem_client.create_file("duplicate.txt", content="original")
        
        with pytest.raises(FileExistsError):
            filesystem_client.create_file("duplicate.txt", content="duplicate", overwrite=False)
    
    def test_error_delete_nonexistent(self, filesystem_client):
        """Test error when deleting non-existent file."""
        with pytest.raises(FileNotFoundError):
            filesystem_client.delete_file("nonexistent.txt")
