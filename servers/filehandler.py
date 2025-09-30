import os
import subprocess
import platform
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json
import hashlib

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FileHandler")

# Existing output schemas
class FileRemoverOutput(BaseModel):
    success: bool
    message: str
    removed_file: Optional[str] = None

class FileWriterOutput(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    operation: Optional[str] = None

class FileSearchOutput(BaseModel):
    success: bool
    message: str
    found_files: list[str] = []
    total_count: int = 0

class DirectoryOutput(BaseModel):
    success: bool
    message: str
    directory_path: Optional[str] = None

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

class DriveSearchOutput(BaseModel):
    success: bool
    message: str
    found_items: list[dict] = []
    total_count: int = 0
    search_type: str = "both"
    search_path: Optional[str] = None

# New output schemas for additional tools
class FileOpenOutput(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    application: Optional[str] = None

class TimeOutput(BaseModel):
    success: bool
    message: str
    current_time: str
    current_date: str
    timestamp: str
    timezone: str
    formatted_time: Optional[str] = None

class SystemInfoOutput(BaseModel):
    success: bool
    message: str
    operating_system: str
    platform: str
    current_user: str
    current_directory: str
    python_version: str

class FileHashOutput(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    md5_hash: Optional[str] = None
    sha256_hash: Optional[str] = None
    file_size: Optional[int] = None

class DuplicateFinderOutput(BaseModel):
    success: bool
    message: str
    duplicate_groups: list[dict] = []
    total_duplicates: int = 0
    space_wasted: int = 0

# ==================== NEW TOOLS ====================

@mcp.tool(name="get_current_time", description="Get current date, time, and timestamp information.")
def get_current_time(format_string: Optional[str] = None) -> TimeOutput:
    """
    Get current date and time information.
    Args:
        format_string (str, optional): Custom format string (e.g., "%Y-%m-%d %H:%M:%S")
    """
    try:
        now = datetime.now()
        
        # Default formats
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        timezone = now.astimezone().tzname()
        
        # Custom format if provided
        formatted_time = None
        if format_string:
            try:
                formatted_time = now.strftime(format_string)
            except ValueError:
                formatted_time = f"Invalid format string: {format_string}"
        
        return TimeOutput(
            success=True,
            message=f"Current time: {current_time} on {current_date}",
            current_time=current_time,
            current_date=current_date,
            timestamp=timestamp,
            timezone=timezone,
            formatted_time=formatted_time
        )
    except Exception as e:
        return TimeOutput(
            success=False,
            message=f"Error getting time: {str(e)}",
            current_time="",
            current_date="",
            timestamp="",
            timezone=""
        )

@mcp.tool(name="open_file", description="Open a file with the default system application or specified application.")
def open_file(file_path: str, application: Optional[str] = None) -> FileOpenOutput:
    """
    Open a file with the default system application or specified application.
    Args:
        file_path (str): Full path to the file to open
        application (str, optional): Specific application to open with (e.g., "notepad", "code")
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return FileOpenOutput(
                success=False, 
                message=f"File '{file_path}' does not exist"
            )
        
        system = platform.system().lower()
        
        if application:
            # Open with specific application
            try:
                if system == "windows":
                    subprocess.run([application, file_path], check=True)
                else:
                    subprocess.run([application, file_path], check=True)
                    
                return FileOpenOutput(
                    success=True,
                    message=f"File opened with {application}: '{file_path}'",
                    file_path=file_path,
                    application=application
                )
            except subprocess.CalledProcessError:
                return FileOpenOutput(
                    success=False,
                    message=f"Failed to open file with {application}. Application may not be installed."
                )
        else:
            # Open with default application
            try:
                if system == "windows":
                    os.startfile(file_path)
                elif system == "darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
                
                return FileOpenOutput(
                    success=True,
                    message=f"File opened with default application: '{file_path}'",
                    file_path=file_path,
                    application="default"
                )
            except Exception as e:
                return FileOpenOutput(
                    success=False,
                    message=f"Failed to open file: {str(e)}"
                )
                
    except Exception as e:
        return FileOpenOutput(
            success=False,
            message=f"Error opening file: {str(e)}"
        )

@mcp.tool(name="get_system_info", description="Get system information including OS, platform, user, and current directory.")
def get_system_info() -> SystemInfoOutput:
    """Get comprehensive system information."""
    try:
        import sys
        
        operating_system = platform.system()
        platform_info = platform.platform()
        current_user = os.getenv('USERNAME') or os.getenv('USER') or "unknown"
        current_directory = os.getcwd()
        python_version = sys.version
        
        message = f"System: {operating_system}, User: {current_user}, Directory: {current_directory}"
        
        return SystemInfoOutput(
            success=True,
            message=message,
            operating_system=operating_system,
            platform=platform_info,
            current_user=current_user,
            current_directory=current_directory,
            python_version=python_version
        )
    except Exception as e:
        return SystemInfoOutput(
            success=False,
            message=f"Error getting system info: {str(e)}",
            operating_system="unknown",
            platform="unknown",
            current_user="unknown",
            current_directory="unknown",
            python_version="unknown"
        )

@mcp.tool(name="calculate_file_hash", description="Calculate MD5 and SHA256 hash for a file.")
def calculate_file_hash(file_path: str) -> FileHashOutput:
    """
    Calculate MD5 and SHA256 hash for a file.
    Args:
        file_path (str): Full path to the file to hash
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return FileHashOutput(
                success=False,
                message=f"File '{file_path}' does not exist"
            )
        
        if os.path.isdir(file_path):
            return FileHashOutput(
                success=False,
                message=f"'{file_path}' is a directory, not a file"
            )
        
        # Calculate hashes
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        file_size = 0
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
                file_size += len(chunk)
        
        md5_result = md5_hash.hexdigest()
        sha256_result = sha256_hash.hexdigest()
        
        return FileHashOutput(
            success=True,
            message=f"Hash calculated for '{file_path}'",
            file_path=file_path,
            md5_hash=md5_result,
            sha256_hash=sha256_result,
            file_size=file_size
        )
    except Exception as e:
        return FileHashOutput(
            success=False,
            message=f"Error calculating hash: {str(e)}"
        )

@mcp.tool(name="find_duplicates", description="Find duplicate files in a directory based on file content hash.")
def find_duplicates(directory: str, check_subdirectories: bool = True) -> DuplicateFinderOutput:
    """
    Find duplicate files in a directory based on file content hash.
    Args:
        directory (str): Directory path to search for duplicates
        check_subdirectories (bool): Whether to include subdirectories (default: True)
    """
    try:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return DuplicateFinderOutput(
                success=False,
                message=f"Directory '{directory}' does not exist"
            )
        
        file_hashes = {}
        total_files = 0
        
        # Walk through directory
        if check_subdirectories:
            file_generator = os.walk(directory)
        else:
            file_generator = [(directory, [], os.listdir(directory))]
        
        for root, dirs, files in file_generator:
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    # Skip very large files (>100MB) for performance
                    file_size = os.path.getsize(file_path)
                    if file_size > 100 * 1024 * 1024:
                        continue
                    
                    # Calculate hash
                    hash_md5 = hashlib.md5()
                    with open(file_path, 'rb') as f:
                        while chunk := f.read(8192):
                            hash_md5.update(chunk)
                    
                    file_hash = hash_md5.hexdigest()
                    
                    if file_hash not in file_hashes:
                        file_hashes[file_hash] = []
                    
                    file_hashes[file_hash].append({
                        "path": file_path,
                        "name": file_name,
                        "size": file_size
                    })
                    total_files += 1
                    
                except (OSError, PermissionError):
                    continue
        
        # Find duplicates
        duplicate_groups = []
        total_duplicates = 0
        space_wasted = 0
        
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                duplicate_groups.append({
                    "hash": file_hash,
                    "files": files,
                    "count": len(files),
                    "size_each": files[0]["size"]
                })
                total_duplicates += len(files) - 1  # Don't count the original
                space_wasted += (len(files) - 1) * files[0]["size"]
        
        if duplicate_groups:
            message = f"Found {len(duplicate_groups)} groups of duplicates ({total_duplicates} duplicate files)"
        else:
            message = f"No duplicate files found in '{directory}'"
        
        return DuplicateFinderOutput(
            success=True,
            message=message,
            duplicate_groups=duplicate_groups,
            total_duplicates=total_duplicates,
            space_wasted=space_wasted
        )
        
    except Exception as e:
        return DuplicateFinderOutput(
            success=False,
            message=f"Error finding duplicates: {str(e)}"
        )

@mcp.tool(name="open_directory", description="Open a directory in the file explorer.")
def open_directory(directory_path: str) -> FileOpenOutput:
    """
    Open a directory in the system file explorer.
    Args:
        directory_path (str): Full path to the directory to open
    """
    try:
        directory_path = os.path.abspath(directory_path)
        
        if not os.path.exists(directory_path):
            return FileOpenOutput(
                success=False,
                message=f"Directory '{directory_path}' does not exist"
            )
        
        if not os.path.isdir(directory_path):
            return FileOpenOutput(
                success=False,
                message=f"'{directory_path}' is not a directory"
            )
        
        system = platform.system().lower()
        
        try:
            if system == "windows":
                subprocess.run(["explorer", directory_path])
            elif system == "darwin":  # macOS
                subprocess.run(["open", directory_path])
            else:  # Linux
                subprocess.run(["xdg-open", directory_path])
            
            return FileOpenOutput(
                success=True,
                message=f"Directory opened in file explorer: '{directory_path}'",
                file_path=directory_path,
                application="file_explorer"
            )
        except Exception as e:
            return FileOpenOutput(
                success=False,
                message=f"Failed to open directory: {str(e)}"
            )
            
    except Exception as e:
        return FileOpenOutput(
            success=False,
            message=f"Error opening directory: {str(e)}"
        )

@mcp.tool(name="get_file_permissions", description="Get file or directory permissions and ownership information.")
def get_file_permissions(path: str) -> dict:
    """
    Get file or directory permissions and ownership information.
    Args:
        path (str): Full path to the file or directory
    """
    try:
        path = os.path.abspath(path)
        
        if not os.path.exists(path):
            return {"success": False, "message": f"Path '{path}' does not exist"}
        
        import stat
        
        # Get file stats
        file_stat = os.stat(path)
        
        # Get permissions in octal format
        permissions = oct(file_stat.st_mode)[-3:]
        
        # Get detailed permissions
        mode = file_stat.st_mode
        permissions_str = stat.filemode(mode)
        
        # Get ownership info (works better on Unix systems)
        owner_uid = file_stat.st_uid
        group_gid = file_stat.st_gid
        
        # Get readable/writable status
        is_readable = os.access(path, os.R_OK)
        is_writable = os.access(path, os.W_OK)
        is_executable = os.access(path, os.X_OK)
        
        return {
            "success": True,
            "message": f"Permissions for '{path}'",
            "path": path,
            "permissions_octal": permissions,
            "permissions_string": permissions_str,
            "is_readable": is_readable,
            "is_writable": is_writable,
            "is_executable": is_executable,
            "owner_uid": owner_uid,
            "group_gid": group_gid,
            "is_directory": os.path.isdir(path)
        }
    except Exception as e:
        return {"success": False, "message": f"Error getting permissions: {str(e)}"}

@mcp.tool(name="create_shortcut", description="Create a desktop shortcut to a file or directory (Windows only).")
def create_shortcut(target_path: str, shortcut_name: str, desktop: bool = True) -> dict:
    """
    Create a desktop shortcut to a file or directory (Windows only).
    Args:
        target_path (str): Path to the file or directory to create shortcut for
        shortcut_name (str): Name for the shortcut (without .lnk extension)
        desktop (bool): Whether to create on desktop (True) or current directory (False)
    """
    try:
        if platform.system().lower() != "windows":
            return {"success": False, "message": "Shortcuts are only supported on Windows"}
        
        target_path = os.path.abspath(target_path)
        if not os.path.exists(target_path):
            return {"success": False, "message": f"Target path '{target_path}' does not exist"}
        
        try:
            import winshell
            
            if desktop:
                desktop_path = winshell.desktop()
                shortcut_path = os.path.join(desktop_path, f"{shortcut_name}.lnk")
            else:
                shortcut_path = os.path.join(os.getcwd(), f"{shortcut_name}.lnk")
            
            winshell.CreateShortcut(
                Path=shortcut_path,
                Target=target_path,
                Icon=(target_path, 0),
                Description=f"Shortcut to {target_path}"
            )
            
            return {
                "success": True,
                "message": f"Shortcut created: '{shortcut_path}'",
                "shortcut_path": shortcut_path,
                "target_path": target_path
            }
            
        except ImportError:
            return {"success": False, "message": "winshell module not available. Install with: pip install winshell"}
        except Exception as e:
            return {"success": False, "message": f"Error creating shortcut: {str(e)}"}
            
    except Exception as e:
        return {"success": False, "message": f"Error creating shortcut: {str(e)}"}

@mcp.tool(name="monitor_directory", description="Monitor a directory for recent changes (files modified in last N hours).")
def monitor_directory(directory: str, hours: int = 24) -> dict:
    """
    Monitor a directory for recent changes (files modified in last N hours).
    Args:
        directory (str): Directory path to monitor
        hours (int): Number of hours to look back for changes (default: 24)
    """
    try:
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return {"success": False, "message": f"Directory '{directory}' does not exist"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_changes = []
        
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mtime > cutoff_time:
                        recent_changes.append({
                            "file": file_name,
                            "path": file_path,
                            "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                            "size": os.path.getsize(file_path)
                        })
                except (OSError, PermissionError):
                    continue
        
        # Sort by modification time (newest first)
        recent_changes.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "success": True,
            "message": f"Found {len(recent_changes)} files modified in last {hours} hours",
            "directory": directory,
            "hours_monitored": hours,
            "recent_changes": recent_changes,
            "total_changes": len(recent_changes)
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error monitoring directory: {str(e)}"}

@mcp.tool(name="cleanup_temp_files", description="Find and optionally delete temporary files in common temp directories.")
def cleanup_temp_files(delete_files: bool = False, max_age_days: int = 7) -> BulkOperationOutput:
    """
    Find and optionally delete temporary files in common temp directories.
    Args:
        delete_files (bool): Whether to actually delete files (default: False - just list)
        max_age_days (int): Only consider files older than this many days (default: 7)
    """
    try:
        import tempfile
        
        # Common temp directories
        temp_dirs = [
            tempfile.gettempdir(),
            "C:\\Windows\\Temp" if platform.system().lower() == "windows" else "/tmp",
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp") if platform.system().lower() == "windows" else None
        ]
        
        # Filter out None values
        temp_dirs = [d for d in temp_dirs if d and os.path.exists(d)]
        
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        temp_files = []
        processed_files = []
        failed_files = []
        
        # Common temp file patterns
        temp_patterns = ['.tmp', '.temp', '.log', '.bak', '.cache']
        
        for temp_dir in temp_dirs:
            try:
                for file_name in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file_name)
                    
                    if os.path.isfile(file_path):
                        try:
                            # Check if it's a temp file and old enough
                            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                            is_temp = any(file_name.lower().endswith(pattern) for pattern in temp_patterns)
                            
                            if is_temp and mtime < cutoff_time:
                                temp_files.append({
                                    "name": file_name,
                                    "path": file_path,
                                    "size": os.path.getsize(file_path),
                                    "modified": mtime.strftime("%Y-%m-%d %H:%M:%S")
                                })
                                
                                if delete_files:
                                    try:
                                        os.remove(file_path)
                                        processed_files.append(file_name)
                                    except Exception as e:
                                        failed_files.append(f"{file_name}: {str(e)}")
                                        
                        except (OSError, PermissionError):
                            continue
            except (OSError, PermissionError):
                continue
        
        if delete_files:
            message = f"Cleanup completed: {len(processed_files)} files deleted, {len(failed_files)} failed"
        else:
            message = f"Found {len(temp_files)} temporary files older than {max_age_days} days"
        
        return BulkOperationOutput(
            success=True,
            message=message,
            processed_files=processed_files if delete_files else [f["name"] for f in temp_files],
            failed_files=failed_files,
            total_processed=len(processed_files) if delete_files else len(temp_files)
        )
        
    except Exception as e:
        return BulkOperationOutput(
            success=False,
            message=f"Error cleaning temp files: {str(e)}"
        )

# ==================== EXISTING TOOLS (keeping all previous tools) ====================

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
        
        file_path = os.path.abspath(file_path)
        directory = os.path.dirname(file_path)
        
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as dir_error:
            return FileWriterOutput(success=False, message=f"Error creating directory '{directory}': {str(dir_error)}")
        
        file_exists = os.path.exists(file_path)
        
        if file_exists and append:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write('\n' + content)
            operation = "appended"
            message = f"Content appended to existing file '{file_path}'"
        else:
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
        file_reference = file_path if 'file_path' in locals() else "unknown"
        return FileWriterOutput(success=False, message=f"Error writing to file '{file_reference}': {str(e)}")

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
            differences += abs(len(content1) - len(content2))
            
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
                    continue
        
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
        
        file_info.sort(key=lambda x: x["size"])
        
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
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if message:
            content = f"[{timestamp}] {message}"
        else:
            content = f"[{timestamp}]"
        
        file_exists = os.path.exists(file_path)
        
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        
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

@mcp.tool(name="quick_search", description="Fast search in common user directories (Documents, Desktop, Downloads, etc.)")
def quick_search(
    search_pattern: str,
    search_type: str = "both",
    max_results: int = 30
) -> DriveSearchOutput:
    """
    Quick search in common user directories for faster results.
    Args:
        search_pattern (str): Pattern to search for
        search_type (str): "files", "folders", or "both" (default: "both")
        max_results (int): Maximum results (default: 30)
    """
    import fnmatch
    import time
    try:
        start_time = time.time()
        
        user_home = os.path.expanduser("~")
        search_paths = [
            os.path.join(user_home, "Documents"),
            os.path.join(user_home, "Desktop"), 
            os.path.join(user_home, "Downloads"),
            os.path.join(user_home, "Pictures"),
            os.path.join(user_home, "Videos"),
            "C:\\Users\\Public",
            "C:\\temp",
            "C:\\tmp"
        ]
        
        search_paths.append(os.getcwd())
        
        found_items = []
        count = 0
        pattern = search_pattern.lower()
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
                
            if count >= max_results:
                break
                
            try:
                for root, dirs, files in os.walk(search_path):
                    depth = root.replace(search_path, '').count(os.sep)
                    if depth >= 2:
                        dirs.clear()
                        continue
                        
                    if count >= max_results:
                        break
                    
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'__pycache__', 'node_modules'}]
                    
                    if search_type in ["folders", "both"]:
                        for dir_name in dirs:
                            if count >= max_results:
                                break
                            if pattern in dir_name.lower() or fnmatch.fnmatch(dir_name.lower(), pattern):
                                full_path = os.path.join(root, dir_name)
                                found_items.append({
                                    "name": dir_name,
                                    "type": "folder", 
                                    "path": full_path,
                                    "parent_directory": root
                                })
                                count += 1
                    
                    if search_type in ["files", "both"]:
                        for file_name in files[:50]:
                            if count >= max_results:
                                break
                            if pattern in file_name.lower() or fnmatch.fnmatch(file_name.lower(), pattern):
                                full_path = os.path.join(root, file_name)
                                try:
                                    file_size = os.path.getsize(full_path)
                                    found_items.append({
                                        "name": file_name,
                                        "type": "file",
                                        "path": full_path,
                                        "parent_directory": root,
                                        "size_bytes": file_size
                                    })
                                    count += 1
                                except (OSError, PermissionError):
                                    continue
                                    
            except (PermissionError, OSError):
                continue
        
        elapsed_time = round(time.time() - start_time, 2)
        
        if found_items:
            message = f"Quick search found {count} items in {elapsed_time}s"
        else:
            message = f"No items found in common directories ({elapsed_time}s)"
        
        return DriveSearchOutput(
            success=True,
            message=message,
            found_items=found_items,
            total_count=count,
            search_type=search_type,
            search_path="Common user directories"
        )
        
    except Exception as e:
        return DriveSearchOutput(
            success=False,
            message=f"Error in quick search: {str(e)}"
        )

@mcp.tool(name="search_drive", description="Search for files and/or folders across entire drive or specified path with pattern matching.")
def search_drive(
    search_pattern: str, 
    search_path: str = "C:\\", 
    search_type: str = "both", 
    max_results: int = 50,
    case_sensitive: bool = False,
    max_depth: int = 3
) -> DriveSearchOutput:
    """
    Search for files and/or folders across the entire drive or specified path.
    Args:
        search_pattern (str): Pattern to search for (e.g., "*.txt", "config", "*report*")
        search_path (str): Root path to start search from (default: "C:\\")
        search_type (str): What to search for - "files", "folders", or "both" (default: "both")
        max_results (int): Maximum number of results to return (default: 50)
        case_sensitive (bool): Whether search should be case sensitive (default: False)
        max_depth (int): Maximum directory depth to search (default: 3 for speed)
    """
    import fnmatch
    import time
    try:
        search_path = os.path.abspath(search_path)
        if not os.path.exists(search_path):
            return DriveSearchOutput(
                success=False, 
                message=f"Search path '{search_path}' does not exist"
            )
        
        found_items = []
        count = 0
        start_time = time.time()
        timeout = 10.0
        
        pattern = search_pattern if case_sensitive else search_pattern.lower()
        
        def should_include_item(item_name, item_path, is_directory):
            if search_type == "files" and is_directory:
                return False
            if search_type == "folders" and not is_directory:
                return False
            
            check_name = item_name if case_sensitive else item_name.lower()
            
            return fnmatch.fnmatch(check_name, pattern) or pattern in check_name
        
        skip_dirs = {
            'System Volume Information', '$Recycle.Bin', 'Windows', 'Program Files', 
            'Program Files (x86)', 'AppData', 'ProgramData', 'Recovery', 'pagefile.sys',
            'hiberfil.sys', 'swapfile.sys', '.git', 'node_modules', '__pycache__'
        }
        
        for root, dirs, files in os.walk(search_path):
            if time.time() - start_time > timeout:
                break
                
            if count >= max_results:
                break
            
            current_depth = root.replace(search_path, '').count(os.sep)
            if current_depth >= max_depth:
                dirs.clear()
                continue
                
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
                
            try:
                if search_type in ["folders", "both"]:
                    for dir_name in dirs:
                        if count >= max_results or time.time() - start_time > timeout:
                            break
                        if should_include_item(dir_name, root, True):
                            full_path = os.path.join(root, dir_name)
                            found_items.append({
                                "name": dir_name,
                                "type": "folder",
                                "path": full_path,
                                "parent_directory": root
                            })
                            count += 1
                
                if search_type in ["files", "both"]:
                    for file_name in files[:100]:
                        if count >= max_results or time.time() - start_time > timeout:
                            break
                        if should_include_item(file_name, root, False):
                            full_path = os.path.join(root, file_name)
                            try:
                                file_size = os.path.getsize(full_path)
                                found_items.append({
                                    "name": file_name,
                                    "type": "file",
                                    "path": full_path,
                                    "parent_directory": root,
                                    "size_bytes": file_size
                                })
                                count += 1
                            except (OSError, PermissionError):
                                continue
                                
            except (PermissionError, OSError):
                continue
        
        elapsed_time = round(time.time() - start_time, 2)
        
        if found_items:
            message = f"Found {count} items matching '{search_pattern}' in {elapsed_time}s"
            if count >= max_results:
                message += f" (limited to {max_results} results)"
            if elapsed_time >= timeout:
                message += " (search timed out - try narrowing search path)"
        else:
            message = f"No items found matching '{search_pattern}' in {elapsed_time}s"
        
        return DriveSearchOutput(
            success=True,
            message=message,
            found_items=found_items,
            total_count=count,
            search_type=search_type,
            search_path=search_path
        )
        
    except Exception as e:
        return DriveSearchOutput(
            success=False, 
            message=f"Error during drive search: {str(e)}"
        )
        
if __name__ == "__main__":
    mcp.run(transport="stdio")