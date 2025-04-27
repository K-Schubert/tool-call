from pathlib import Path
import os
from datetime import datetime

def list_directory(directory=".", pattern="*", include_hidden=False, sort_by="name"):
    """
    List files in a directory with optional filtering and sorting.

    Args:
        directory (str): Directory to list files from
        pattern (str): Glob pattern for filtering files (e.g., "*.txt", "*.py")
        include_hidden (bool): If True, include hidden files (starting with .)
        sort_by (str): Sort method - "name", "size", "modified", or "created"

    Returns:
        list: List of file information dictionaries
    """
    dir_path = Path(directory)

    # Check if directory exists
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Directory {directory} not found or is not a directory")
        return []

    # Get all files matching pattern
    files = list(dir_path.glob(pattern))

    # Filter out hidden files if not included
    if not include_hidden:
        files = [f for f in files if not f.name.startswith('.')]

    # Get file info
    file_info = []
    for file in files:
        if file.is_file():  # Only include files, not directories
            stats = file.stat()
            info = {
                "name": file.name,
                "path": str(file),
                "size": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "is_file": file.is_file(),
                "is_dir": file.is_dir()
            }
            file_info.append(info)

    # Sort the files
    if sort_by == "name":
        file_info.sort(key=lambda x: x["name"])
    elif sort_by == "size":
        file_info.sort(key=lambda x: x["size"])
    elif sort_by == "modified":
        file_info.sort(key=lambda x: x["modified"])
    elif sort_by == "created":
        file_info.sort(key=lambda x: x["created"])

    # Print summary
    print(f"Found {len(file_info)} files in {directory}")

    return file_info

if __name__ == "__main__":
    # Example usage
    directory = "tools"
    pattern = "*.py"

    # List all Python files in current directory
    files = list_directory(directory, pattern)

    # Print the results
    for file in files:
        print(f"{file['name']} - {file['size']} bytes - Modified: {file['modified']}")
