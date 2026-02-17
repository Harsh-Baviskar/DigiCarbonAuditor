"""
File categorization service for the Digital Carbon Auditor.

Orchestrates directory scanning and per-file categorization,
returning a structured report with categorized files and a summary.
"""

from collections import Counter
from typing import Any


from app.shared.file_ops import scan_directory
from app.modules.file_categorization.utils import categorize_file



def categorize_directory(folder_path: str) -> dict[str, Any]:
    """Scan a directory and categorize every file by extension.

    Args:
        folder_path: Absolute or relative path to the target directory.

    Returns:
        A dictionary with two keys:
            - "categorized_files": list of dicts, each containing
              "file_name", "file_path", and "category".
            - "category_summary": dict mapping each category
              to the number of files it contains.
    """
    files = scan_directory(folder_path)

    categorized_files: list[dict[str, str]] = []
    category_counter: Counter[str] = Counter()

    for file in files:
        category = categorize_file(file)

        categorized_files.append({
            "file_name": file.name,
            "file_path": str(file),
            "category": category,
        })

        category_counter[category] += 1

    return {
        "categorized_files": categorized_files,
        "category_summary": dict(category_counter),
    }
