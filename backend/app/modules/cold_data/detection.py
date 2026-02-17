"""
Cold data detection utilities for the Digital Carbon Auditor.

Provides functions to extract file usage metadata and determine
whether a file qualifies as "cold" (inactive beyond a threshold).
"""

from datetime import datetime, timezone
from pathlib import Path


def get_file_usage_metadata(file_path: Path) -> dict:
    """Extract usage metadata for a single file.

    Args:
        file_path: A Path object pointing to the target file.

    Returns:
        A dictionary containing:
            - "file_name": name of the file.
            - "file_path": absolute path as a string.
            - "size_mb": file size in megabytes (rounded to 4 decimals).
            - "last_accessed": UTC datetime of last access.
            - "last_modified": UTC datetime of last modification.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    stat = file_path.stat()

    return {
        "file_name": file_path.name,
        "file_path": str(file_path.resolve()),
        "size_mb": round(stat.st_size / (1024 * 1024), 4),
        "last_accessed": datetime.fromtimestamp(stat.st_atime, tz=timezone.utc),
        "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
    }


def is_cold_file(last_accessed: datetime, threshold_days: int = 180) -> bool:
    """Determine whether a file is cold based on its last access time.

    A file is considered "cold" if it has not been accessed
    for more than `threshold_days` days.

    Args:
        last_accessed: UTC-aware datetime of the file's last access.
        threshold_days: Number of inactive days to qualify as cold.
                        Defaults to 180 (≈ 6 months).

    Returns:
        True if the file has been inactive longer than the threshold.
    """
    now = datetime.now(tz=timezone.utc)
    inactive_days = (now - last_accessed).days
    return inactive_days > threshold_days
