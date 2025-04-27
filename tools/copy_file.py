from pathlib import Path
import shutil

def copy_file(source_filepath, destination_filepath, overwrite=False):
    """
    Copy a file from source_filepath to destination_filepath.

    Args:
        source_filepath (str): Path of the file to copy
        destination_filepath (str): Destination path for the copied file
        overwrite (bool): If True, overwrite existing destination file

    Returns:
        bool: True if the file was copied, False otherwise
    """
    source_path = Path(source_filepath)
    dest_path = Path(destination_filepath)

    # Check if source file exists
    if not source_path.exists():
        print(f"Source file {source_filepath} not found")
        return False

    # Check if destination already exists and overwrite is False
    if dest_path.exists() and not overwrite:
        print(f"Destination file {destination_filepath} already exists. Use overwrite=True to replace it.")
        return False

    # Ensure parent directory of destination exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy the file
    shutil.copy2(source_path, dest_path)
    print(f"File copied from {source_filepath} to {destination_filepath}")
    return True

if __name__ == "__main__":
    # Example usage
    source_filepath = "example.txt"
    destination_filepath = "backup/example_copy.txt"

    # Create a sample file for testing if it doesn't exist
    if not Path(source_filepath).exists():
        with open(source_filepath, 'w') as f:
            f.write("This is a test file that will be copied.\n")
        print(f"Created test file {source_filepath}")

    # Copy the file
    copy_file(source_filepath, destination_filepath)
