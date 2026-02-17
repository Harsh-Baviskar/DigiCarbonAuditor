"""
Cold data policies for the Digital Carbon Auditor.

Industry-grade cold detection is not based only on time.
Instead, we apply safe heuristics:

- Age (inactive duration)
- File size impact
- Category risk (archives/videos are higher impact)
"""

from datetime import datetime, timezone


HIGH_IMPACT_CATEGORIES = {"Archives", "Videos"}
SAFE_CATEGORIES = {"Documents", "Images"}


def is_cold_candidate(
    *,
    last_activity: datetime,
    category: str,
    size_mb: float,
    threshold_days: int = 180,
    min_size_mb: float = 10.0,
) -> bool:
    """
    Determine whether a file is a cold storage candidate.

    Industry logic:
    - File must be inactive beyond threshold_days
    - AND either:
        - belongs to high-impact category (archives/videos)
        - OR is very large

    Args:
        last_activity: Last modified/accessed timestamp (UTC).
        category: File category (Documents, Videos, etc.)
        size_mb: File size in MB
        threshold_days: Inactivity threshold
        min_size_mb: Minimum size to consider for cold impact

    Returns:
        True if file should be flagged as cold candidate.
    """

    now = datetime.now(timezone.utc)
    inactive_days = (now - last_activity).days

    # Not old enough → not cold
    if inactive_days <= threshold_days:
        return False

    # High-impact categories → cold candidate
    if category in HIGH_IMPACT_CATEGORIES:
        return True

    # Very large files → cold candidate even if category is Others
    if size_mb >= min_size_mb:
        return True

    # Otherwise, do not flag (safe default)
    return False
