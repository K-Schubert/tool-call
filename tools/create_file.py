import os
from pathlib import Path

def create_file(filename, filepath=".", content=""):
    """
    Create a file at the specified filepath with the given filename and content.

    Args:
        filename (str): Name of the file to create (with extension)
        filepath (str): Path where the file should be created (default: current directory)
        content (str): Content to write to the file

    Returns:
        str: Full path of the created file
    """
    # Create full path
    full_path = Path(filepath) / filename

    # Only try to create directories if filepath is not just the current directory
    if filepath != "." and filepath != "./":
        os.makedirs(filepath, exist_ok=True)

    # Create file with content
    full_path.write_text(content)

    print(f"File '{filename}' created at '{filepath}'")
    if content:
        print("File created with content")
    else:
        print("Empty file created")
    return str(full_path)

if __name__ == "__main__":
    # Example usage
    filename = "example.txt"
    filepath = "tools"

    # Create file with content
    content = "This is a sample file content.\nHello World!"
    create_file("sample.py", filepath, content)
