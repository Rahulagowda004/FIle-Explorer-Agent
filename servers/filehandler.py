import os
from typing import Optional
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FileHandler")

# Output schema
class FileRemoverOutput(BaseModel):
    success: bool
    message: str
    removed_file: Optional[str] = None
    
@mcp.tool()
def file_remover(file_path: str) -> FileRemoverOutput:
    """Removes a file from the filesystem given its path."""
    try:
        if not file_path:
            return FileRemoverOutput(success=False, message="No file path provided")
        os.remove(file_path)
        return FileRemoverOutput(success=True, message="File removed successfully.", removed_file=file_path)
    except Exception as e:
        return FileRemoverOutput(success=False, message=str(e))
    
@mcp.tool(name="list_files", description="Lists files in a given directory.")
def list_files(directory: str) -> str:
    """
    Lists files in the specified directory.
    Args:
        directory (str): The path to the directory to list files from.
    """
    try:
        if os.path.isfile(directory):
            return f"'{directory}' is a file, not a directory."
        if not os.path.exists(directory):
            return f"Directory '{directory}' does not exist."
        files = os.listdir(directory)
        return f"Files in '{directory}': {', '.join(files)}"
    except Exception as e:
        return f"no files found in '{directory}': {str(e)}"
    
@mcp.tool(name="read_file", description="Reads the content of a file.")
def read_file(file_path: str) -> str:
    """
    Reads the content of the specified file.
    Args:
        file_path (str): The path to the file to read.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

class FileWriterOutput(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    operation: Optional[str] = None  # "created", "written", "appended"

@mcp.tool(name="write_file", description="Creates a new file with any extension, writes content to an existing file, or appends content if file exists.")
def write_file(file_path: str, content: str = "", append: bool = True) -> FileWriterOutput:
    """
    Creates a new file or writes/appends content to an existing file.
    Args:
        file_path (str): The full path to the file to create or write to (including file extension).
        content (str, optional): The content to write or append to the file. Defaults to empty string.
        append (bool): If True and file exists, append content. If False, overwrite existing content.
    """
    try:
        if not file_path:
            return FileWriterOutput(success=False, message="No file path provided")
        
        # Content can be empty - just create an empty file if needed
        
        # Convert to absolute path and ensure directory exists
        file_path = os.path.abspath(file_path)
        directory = os.path.dirname(file_path)
        
        # Ensure the directory exists
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as dir_error:
            return FileWriterOutput(success=False, message=f"Error creating directory '{directory}': {str(dir_error)}")
        
        # Check if file exists
        file_exists = os.path.exists(file_path)
        
        if file_exists and append:
            # Append to existing file with newline
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write('\n' + content)
            operation = "appended"
            message = f"Content appended to existing file '{file_path}'"
        else:
            # Create new file or overwrite existing
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            if file_exists:
                operation = "overwritten"
                message = f"Content written to existing file '{file_path}' (overwritten)"
            else:
                operation = "created"
                message = f"New file created and content written to '{file_path}'"
        
        return FileWriterOutput(
            success=True, 
            message=message, 
            file_path=file_path, 
            operation=operation
        )
        
    except Exception as e:
        # Use file_path if available
        file_reference = file_path if 'file_path' in locals() else "unknown"
        return FileWriterOutput(success=False, message=f"Error writing to file '{file_reference}': {str(e)}")

# Additional output schemas
class FileSearchOutput(BaseModel):
    success: bool
    message: str
    found_files: list[str] = []
    total_count: int = 0

class DirectoryOutput(BaseModel):
    success: bool
    message: str
    directory_path: Optional[str] = None

@mcp.tool(name="create_directory", description="Create a new directory/folder at the specified path.")
def create_directory(directory_path: str) -> DirectoryOutput:
    """
    Create a new directory/folder at the specified path.
    Args:
        directory_path (str): Full path to the directory to create
    """
    try:
        directory_path = os.path.abspath(directory_path)
        
        if os.path.exists(directory_path):
            return DirectoryOutput(success=False, message=f"Directory '{directory_path}' already exists")
        
        os.makedirs(directory_path, exist_ok=True)
        
        return DirectoryOutput(
            success=True,
            message=f"Directory created successfully: '{directory_path}'",
            directory_path=directory_path
        )
    except Exception as e:
        return DirectoryOutput(success=False, message=f"Error creating directory: {str(e)}")

@mcp.tool(name="remove_directory", description="Remove an empty directory.")
def remove_directory(directory_path: str) -> DirectoryOutput:
    """
    Remove an empty directory.
    Args:
        directory_path (str): Full path to the directory to remove
    """
    try:
        directory_path = os.path.abspath(directory_path)
        
        if not os.path.exists(directory_path):
            return DirectoryOutput(success=False, message=f"Directory '{directory_path}' does not exist")
        
        if not os.path.isdir(directory_path):
            return DirectoryOutput(success=False, message=f"'{directory_path}' is not a directory")
        
        # Check if directory is empty
        if os.listdir(directory_path):
            return DirectoryOutput(success=False, message=f"Directory '{directory_path}' is not empty")
        
        os.rmdir(directory_path)
        
        return DirectoryOutput(
            success=True,
            message=f"Directory removed successfully: '{directory_path}'",
            directory_path=directory_path
        )
    except Exception as e:
        return DirectoryOutput(success=False, message=f"Error removing directory: {str(e)}")

# Additional output schemas
class FileSearchOutput(BaseModel):
    success: bool
    message: str
    found_files: list[str] = []
    total_count: int = 0

class FileCopyOutput(BaseModel):
    success: bool
    message: str
    source_file: Optional[str] = None
    destination_file: Optional[str] = None

class FileRenameOutput(BaseModel):
    success: bool
    message: str
    old_name: Optional[str] = None
    new_name: Optional[str] = None

class FileInfoOutput(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    is_directory: bool = False

@mcp.tool(name="search_files", description="Search for files by pattern in a specified directory.")
def search_files(directory: str, pattern: str = "*") -> FileSearchOutput:
    """
    Search for files matching a pattern in the specified directory.
    Args:
        directory (str): Directory path to search in
        pattern (str): File pattern to search for (e.g., "*.txt", "*report*", "data*")
    """
    import glob
    try:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return FileSearchOutput(success=False, message=f"Directory '{directory}' does not exist")
        
        search_pattern = os.path.join(directory, pattern)
        found_files = glob.glob(search_pattern)
        
        # Get just the filenames, not full paths
        filenames = [os.path.basename(f) for f in found_files if os.path.isfile(f)]
        
        if filenames:
            return FileSearchOutput(
                success=True, 
                message=f"Found {len(filenames)} files matching '{pattern}' in '{directory}'",
                found_files=filenames,
                total_count=len(filenames)
            )
        else:
            return FileSearchOutput(
                success=True, 
                message=f"No files found matching '{pattern}' in '{directory}'",
                found_files=[],
                total_count=0
            )
    except Exception as e:
        return FileSearchOutput(success=False, message=f"Error searching files: {str(e)}")

@mcp.tool(name="copy_file", description="Copy a file from source to destination path.")
def copy_file(source_path: str, destination_path: str) -> FileCopyOutput:
    """
    Copy a file from source to destination path.
    Args:
        source_path (str): Full path to the source file to copy
        destination_path (str): Full path for the copied file
    """
    import shutil
    try:
        
        source_path = os.path.abspath(source_path)
        destination_path = os.path.abspath(destination_path)
        
        if not os.path.exists(source_path):
            return FileCopyOutput(success=False, message=f"Source file '{source_path}' does not exist")
        
        if os.path.exists(destination_path):
            return FileCopyOutput(success=False, message=f"Destination file '{destination_path}' already exists")
        
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        shutil.copy2(source_path, destination_path)
        
        return FileCopyOutput(
            success=True,
            message=f"File copied successfully from '{source_path}' to '{destination_path}'",
            source_file=source_path,
            destination_file=destination_path
        )
    except Exception as e:
        return FileCopyOutput(success=False, message=f"Error copying file: {str(e)}")

@mcp.tool(name="rename_file", description="Rename a file from old path to new path.")
def rename_file(old_path: str, new_path: str) -> FileRenameOutput:
    """
    Rename a file from old path to new path.
    Args:
        old_path (str): Current full path of the file
        new_path (str): New full path for the file
    """
    try:
        old_path = os.path.abspath(old_path)
        new_path = os.path.abspath(new_path)
        
        if not os.path.exists(old_path):
            return FileRenameOutput(success=False, message=f"File '{old_path}' does not exist")
        
        if os.path.exists(new_path):
            return FileRenameOutput(success=False, message=f"File '{new_path}' already exists")
        
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        
        os.rename(old_path, new_path)
        
        return FileRenameOutput(
            success=True,
            message=f"File renamed successfully from '{old_path}' to '{new_path}'",
            old_name=old_path,
            new_name=new_path
        )
    except Exception as e:
        return FileRenameOutput(success=False, message=f"Error renaming file: {str(e)}")

@mcp.tool(name="file_info", description="Get detailed information about a file.")
def file_info(file_path: str) -> FileInfoOutput:
    """
    Get detailed information about a file.
    Args:
        file_path (str): Full path to the file to get information about
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return FileInfoOutput(success=False, message=f"File '{file_path}' does not exist")
        
        # Get file stats
        stat = os.stat(file_path)
        import datetime
        
        created_date = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        modified_date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        return FileInfoOutput(
            success=True,
            message=f"File information for '{file_path}'",
            file_path=file_path,
            size_bytes=stat.st_size,
            created_date=created_date,
            modified_date=modified_date,
            is_directory=os.path.isdir(file_path)
        )
    except Exception as e:
        return FileInfoOutput(success=False, message=f"Error getting file info: {str(e)}")

@mcp.tool(name="clear_file", description="Clear all content from a file (make it empty).")
def clear_file(file_path: str) -> FileWriterOutput:
    """
    Clear all content from a file, making it empty.
    Args:
        file_path (str): Full path to the file to clear
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return FileWriterOutput(success=False, message=f"File '{file_path}' does not exist")
        
        # Clear the file by opening in write mode with empty content
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('')
        
        return FileWriterOutput(
            success=True,
            message=f"File '{file_path}' cleared successfully",
            file_path=file_path,
            operation="cleared"
        )
    except Exception as e:
        return FileWriterOutput(success=False, message=f"Error clearing file: {str(e)}")

@mcp.tool(name="count_lines", description="Count the number of lines in a file.")
def count_lines(file_path: str) -> dict:
    """
    Count the number of lines in a file.
    Args:
        file_path (str): Full path to the file to count lines in
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return {"success": False, "message": f"File '{file_path}' does not exist"}
        
        with open(file_path, 'r', encoding='utf-8') as file:
            line_count = sum(1 for line in file)
        
        return {
            "success": True,
            "message": f"File '{file_path}' contains {line_count} lines",
            "file_path": file_path,
            "line_count": line_count
        }
    except Exception as e:
        return {"success": False, "message": f"Error counting lines: {str(e)}"}

# Additional advanced output schemas
class FileCompareOutput(BaseModel):
    success: bool
    message: str
    files_identical: Optional[bool] = None
    differences_found: Optional[int] = None

class BulkOperationOutput(BaseModel):
    success: bool
    message: str
    processed_files: list[str] = []
    failed_files: list[str] = []
    total_processed: int = 0

class FileBackupOutput(BaseModel):
    success: bool
    message: str
    original_file: Optional[str] = None
    backup_file: Optional[str] = None

@mcp.tool(name="compare_files", description="Compare the content of two files to check if they are identical.")
def compare_files(file1_path: str, file2_path: str) -> FileCompareOutput:
    """
    Compare the content of two files to see if they are identical.
    Args:
        file1_path (str): Full path to the first file to compare
        file2_path (str): Full path to the second file to compare
    """
    try:
        file1_path = os.path.abspath(file1_path)
        file2_path = os.path.abspath(file2_path)
        
        if not os.path.exists(file1_path):
            return FileCompareOutput(success=False, message=f"File '{file1_path}' does not exist")
        
        if not os.path.exists(file2_path):
            return FileCompareOutput(success=False, message=f"File '{file2_path}' does not exist")
        
        with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
            content1 = f1.readlines()
            content2 = f2.readlines()
        
        if content1 == content2:
            return FileCompareOutput(
                success=True,
                message=f"Files '{file1_path}' and '{file2_path}' are identical",
                files_identical=True,
                differences_found=0
            )
        else:
            differences = sum(1 for a, b in zip(content1, content2) if a != b)
            differences += abs(len(content1) - len(content2))  # Add line count difference
            
            return FileCompareOutput(
                success=True,
                message=f"Files '{file1_path}' and '{file2_path}' are different ({differences} differences found)",
                files_identical=False,
                differences_found=differences
            )
    except Exception as e:
        return FileCompareOutput(success=False, message=f"Error comparing files: {str(e)}")

@mcp.tool(name="backup_file", description="Create a backup copy of a file with timestamp.")
def backup_file(file_path: str) -> FileBackupOutput:
    """
    Create a backup copy of a file with a timestamp suffix.
    Args:
        file_path (str): Full path to the file to backup
    """
    import shutil
    import datetime
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return FileBackupOutput(success=False, message=f"File '{file_path}' does not exist")
        
        # Create backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(directory, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        
        return FileBackupOutput(
            success=True,
            message=f"Backup created successfully: '{backup_path}'",
            original_file=file_path,
            backup_file=backup_path
        )
    except Exception as e:
        return FileBackupOutput(success=False, message=f"Error creating backup: {str(e)}")

@mcp.tool(name="find_in_files", description="Search for text content within files in a specified directory.")
def find_in_files(directory: str, search_text: str, file_pattern: str = "*") -> dict:
    """
    Search for specific text content within files in a directory.
    Args:
        directory (str): Directory path to search in
        search_text (str): Text to search for within files
        file_pattern (str): File pattern to search in (default: "*")
    """
    import glob
    try:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return {"success": False, "message": f"Directory '{directory}' does not exist"}
        
        search_pattern = os.path.join(directory, file_pattern)
        files = glob.glob(search_pattern)
        
        results = []
        for file_path in files:
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line_num, line in enumerate(lines, 1):
                            if search_text.lower() in line.lower():
                                results.append({
                                    "file": os.path.basename(file_path),
                                    "line_number": line_num,
                                    "line_content": line.strip()
                                })
                except Exception:
                    continue  # Skip files that can't be read
        
        if results:
            return {
                "success": True,
                "message": f"Found '{search_text}' in {len(set(r['file'] for r in results))} files",
                "search_text": search_text,
                "matches": results,
                "total_matches": len(results)
            }
        else:
            return {
                "success": True,
                "message": f"No matches found for '{search_text}'",
                "search_text": search_text,
                "matches": [],
                "total_matches": 0
            }
    except Exception as e:
        return {"success": False, "message": f"Error searching files: {str(e)}"}

@mcp.tool(name="bulk_delete", description="Delete multiple files by pattern in a specified directory.")
def bulk_delete(directory: str, pattern: str = "*backup*") -> BulkOperationOutput:
    """
    Delete multiple files matching a pattern in a specified directory.
    Args:
        directory (str): Directory path to search in
        pattern (str): Pattern to match files for deletion (default: "*backup*")
    """
    import glob
    try:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return BulkOperationOutput(success=False, message=f"Directory '{directory}' does not exist")
        
        search_pattern = os.path.join(directory, pattern)
        files = glob.glob(search_pattern)
        
        processed_files = []
        failed_files = []
        
        for file_path in files:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    processed_files.append(os.path.basename(file_path))
                except Exception as e:
                    failed_files.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        return BulkOperationOutput(
            success=True,
            message=f"Deleted {len(processed_files)} files. {len(failed_files)} failures.",
            processed_files=processed_files,
            failed_files=failed_files,
            total_processed=len(processed_files)
        )
    except Exception as e:
        return BulkOperationOutput(success=False, message=f"Error in bulk delete: {str(e)}")

@mcp.tool(name="file_stats", description="Get comprehensive statistics about all files in a specified directory.")
def file_stats(directory: str) -> dict:
    """
    Get comprehensive statistics about all files in the specified directory.
    Args:
        directory (str): Directory path to analyze
    """
    try:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return {"success": False, "message": f"Directory '{directory}' does not exist"}
        
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        if not files:
            return {
                "success": True,
                "message": "No files found in directory",
                "directory": directory,
                "total_files": 0,
                "total_size_bytes": 0,
                "average_size_bytes": 0,
                "largest_file": None,
                "smallest_file": None,
                "file_types": {}
            }
        
        file_info = []
        total_size = 0
        
        for file in files:
            file_path = os.path.join(directory, file)
            size = os.path.getsize(file_path)
            file_info.append({"name": file, "size": size})
            total_size += size
        
        # Sort by size
        file_info.sort(key=lambda x: x["size"])
        
        # Count file types
        file_types = {}
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "success": True,
            "message": f"Statistics for {len(files)} files in '{directory}'",
            "directory": directory,
            "total_files": len(files),
            "total_size_bytes": total_size,
            "average_size_bytes": round(total_size / len(files), 2),
            "largest_file": {"name": file_info[-1]["name"], "size": file_info[-1]["size"]},
            "smallest_file": {"name": file_info[0]["name"], "size": file_info[0]["size"]},
            "file_types": file_types
        }
    except Exception as e:
        return {"success": False, "message": f"Error getting file stats: {str(e)}"}

@mcp.tool(name="append_timestamp", description="Append current timestamp to a file.")
def append_timestamp(file_path: str, message: str = "") -> FileWriterOutput:
    """
    Append current timestamp with optional message to a file.
    Args:
        file_path (str): Full path to the file to append timestamp to
        message (str): Optional message to include with timestamp
    """
    import datetime
    try:
        file_path = os.path.abspath(file_path)
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if message:
            content = f"[{timestamp}] {message}"
        else:
            content = f"[{timestamp}]"
        
        # Check if file exists
        file_exists = os.path.exists(file_path)
        
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        
        # Append with newline
        with open(file_path, 'a', encoding='utf-8') as file:
            if file_exists:
                file.write('\n' + content)
            else:
                file.write(content)
        
        operation = "appended" if file_exists else "created"
        return FileWriterOutput(
            success=True,
            message=f"Timestamp {operation} to '{file_path}'",
            file_path=file_path,
            operation=operation
        )
    except Exception as e:
        return FileWriterOutput(success=False, message=f"Error appending timestamp: {str(e)}")

if __name__ == "__main__":
    mcp.run(transport="stdio")