"""
Shared file operations for the Digital Carbon Auditor.

Provides utility functions for recursive directory scanning
and file discovery using os.walk for maximum reliability.
"""

import os
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
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Path does not exist: {folder_path}")

    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    files: List[Path] = []

    # Use os.walk for maximum reliability in scanning all files
    for root, dirs, files_in_dir in os.walk(folder_path):
        for file in files_in_dir:
            file_path = os.path.join(root, file)
            files.append(Path(file_path))

    return sorted(files)
