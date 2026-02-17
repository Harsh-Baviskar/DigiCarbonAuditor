"""
Shared file operations for the Digital Carbon Auditor.

Provides utility functions for recursive directory scanning
and file discovery using pathlib.
"""

from pathlib import Path
from typing import List


def scan_directory(folder_path: str) -> List[Path]:
    """Recursively scan a directory and return all file paths.

    Traverses the given folder and all its subdirectories,
    collecting every file encountered as a Path object.

    Args:
        folder_path: Absolute or relative path to the directory to scan.

    Returns:
        A sorted list of Path objects for every file found.

    Raises:
        FileNotFoundError: If the provided path does not exist.
        NotADirectoryError: If the provided path is not a directory.
    """
    path = Path(folder_path)

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {folder_path}")

    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    files: List[Path] = sorted(
        item for item in path.rglob("*") if item.is_file()
    )

    return files
