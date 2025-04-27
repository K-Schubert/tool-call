from pathlib import Path

def delete_file(filepath):
    """
    Delete a file at the specified filepath.

    Args:
        filepath (str): Path to the file to delete

    Returns:
        bool: True if the file was deleted, False otherwise
    """
    file_path = Path(filepath)

    # Check if file exists
    if not file_path.exists():
        print(f"File {filepath} not found")
        return False

    # Delete the file
    file_path.unlink()
    print(f"File {filepath} deleted successfully")
    return True

if __name__ == "__main__":
    # Example usage
    filepath = "example.txt"

    # Create a sample file for testing if it doesn't exist
    if not Path(filepath).exists():
        with open(filepath, 'w') as f:
            f.write("This is a test file that will be deleted.\n")
        print(f"Created test file {filepath}")

    # Delete the file
    delete_file(filepath)
