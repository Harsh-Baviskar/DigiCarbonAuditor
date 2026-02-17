"""
File categorization utilities for the Digital Carbon Auditor.

Provides extension-based classification of files into
predefined categories such as Documents, Images, Videos, etc.
"""

from pathlib import Path

FILE_CATEGORIES: dict[str, set[str]] = {
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf",
        ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".md",
    },
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
        ".webp", ".ico", ".tiff", ".tif",
    },
    "Videos": {
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
        ".webm", ".m4v", ".mpg", ".mpeg",
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",
        ".xz", ".iso",
    },
    "Code": {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java",
        ".c", ".cpp", ".h", ".cs", ".go", ".rb", ".rs",
        ".html", ".css", ".scss", ".json", ".xml", ".yaml",
        ".yml", ".sql", ".sh", ".bat",
    },
}

# Pre-compute a reverse lookup: extension -> category
_EXTENSION_TO_CATEGORY: dict[str, str] = {
    ext: category
    for category, extensions in FILE_CATEGORIES.items()
    for ext in extensions
}


def categorize_file(file_path: Path) -> str:
    """Classify a file into a category based on its extension.

    Args:
        file_path: A Path object pointing to the file.

    Returns:
        One of: "Documents", "Images", "Videos",
        "Archives", "Code", or "Others".
    """
    extension = file_path.suffix.lower()
    return _EXTENSION_TO_CATEGORY.get(extension, "Others")
