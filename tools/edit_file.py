import os
from pathlib import Path

def edit_file(filepath, content="", append=False):
    """
    Edit an existing file by replacing content or appending content.

    Args:
        filepath (str): Path to the file to edit
        content (str): Content to write or append to the file
        append (bool): If True, append the content to the file; if False, replace the file content

    Returns:
        str: Full path of the edited file
    """
    file_path = Path(filepath)

    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File {filepath} not found")

    # Read the current content
    current_content = file_path.read_text()

    # Determine the new content based on the operation
    if append:
        new_content = current_content + content
        print(f"Appended content to {filepath}")
    else:
        new_content = content
        print(f"Replaced content in {filepath}")

    # Write the new content back to the file
    file_path.write_text(new_content)

    return str(file_path)

if __name__ == "__main__":
    # Example usage
    filepath = "example.txt"

    # Create a sample file for testing if it doesn't exist
    if not Path(filepath).exists():
        with open(filepath, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3\n")

    # Examples of different editing operations
    # 1. Append content
    edit_file(filepath, content="\nLine 4\nLine 5", append=True)

    # 2. Replace entire content
    edit_file(filepath, content="Completely new content")
