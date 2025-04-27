from pathlib import Path

def rename_file(old_filepath, new_filepath):
    """
    Rename a file from old_filepath to new_filepath.

    Args:
        old_filepath (str): Current path of the file
        new_filepath (str): New path for the file

    Returns:
        bool: True if the file was renamed, False otherwise
    """
    old_path = Path(old_filepath)
    new_path = Path(new_filepath)

    # Check if source file exists
    if not old_path.exists():
        print(f"Source file {old_filepath} not found")
        return False

    # Check if destination already exists
    if new_path.exists():
        print(f"Destination file {new_filepath} already exists")
        return False

    # Ensure parent directory of destination exists
    new_path.parent.mkdir(parents=True, exist_ok=True)

    # Rename the file
    old_path.rename(new_path)
    print(f"File renamed from {old_filepath} to {new_filepath}")
    return True

if __name__ == "__main__":
    # Example usage
    old_filepath = "example.txt"
    new_filepath = "renamed_example.txt"

    # Create a sample file for testing if it doesn't exist
    if not Path(old_filepath).exists():
        with open(old_filepath, 'w') as f:
            f.write("This is a test file that will be renamed.\n")
        print(f"Created test file {old_filepath}")

    # Rename the file
    rename_file(old_filepath, new_filepath)
