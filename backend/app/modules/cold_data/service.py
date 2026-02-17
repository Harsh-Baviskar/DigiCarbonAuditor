"""
Cold data detection service for the Digital Carbon Auditor.

Orchestrates directory scanning, metadata extraction, and cold file
identification, returning a structured report with results and summary.
"""

from typing import Any

from app.shared.file_ops import scan_directory
from app.modules.cold_data.detection import get_file_usage_metadata, is_cold_file


def detect_cold_files(
    folder_path: str,
    threshold_days: int = 180,
) -> dict[str, Any]:
    """Scan a directory and identify all cold (inactive) files.

    Args:
        folder_path: Absolute or relative path to the target directory.
        threshold_days: Number of inactive days to classify a file as cold.
                        Defaults to 180.

    Returns:
        A dictionary with two keys:
            - "cold_files": list of metadata dicts for each cold file,
              including file_name, file_path, size_mb,
              last_accessed, and last_modified.
            - "cold_summary": dict with total_files_scanned,
              cold_files_count, cold_storage_mb, and threshold_days.
    """
    files = scan_directory(folder_path)

    cold_files: list[dict[str, Any]] = []
    total_cold_size_mb: float = 0.0

    for file in files:
        metadata = get_file_usage_metadata(file)

        if is_cold_file(metadata["last_accessed"], threshold_days):
            cold_files.append({
                "file_name": metadata["file_name"],
                "file_path": metadata["file_path"],
                "size_mb": metadata["size_mb"],
                "last_accessed": metadata["last_accessed"].isoformat(),
                "last_modified": metadata["last_modified"].isoformat(),
            })
            total_cold_size_mb += metadata["size_mb"]

    return {
        "cold_files": cold_files,
        "cold_summary": {
            "total_files_scanned": len(files),
            "cold_files_count": len(cold_files),
            "cold_storage_mb": round(total_cold_size_mb, 4),
            "threshold_days": threshold_days,
        },
    }
