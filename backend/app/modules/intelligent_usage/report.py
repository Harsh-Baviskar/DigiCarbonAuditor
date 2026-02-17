"""
Intelligent usage report for the Digital Carbon Auditor.

Combines file categorization and cold data detection to produce
a unified report with storage insights and cleanup recommendations.
"""

from collections import Counter
from typing import Any

from app.shared.file_ops import scan_directory
from app.modules.file_categorization.utils import categorize_file
from app.modules.cold_data.detection import get_file_usage_metadata
from app.modules.cold_data.policies import is_cold_candidate


# Approximate carbon emission factor (kg CO₂ per GB stored per year)
CARBON_KG_PER_GB_PER_YEAR = 0.02


def _generate_recommendations(
    cold_files: list[dict[str, Any]],
    cold_category_breakdown: dict[str, int],
    cold_storage_mb: float,
    total_storage_mb: float,
) -> list[str]:
    """
    Industry-safe cleanup recommendations.

    IMPORTANT:
    Cold files are not automatically "waste".
    They are flagged as candidates for review, archival, or tiered storage.
    """

    recommendations: list[str] = []

    # -------------------------------
    # Rule 1: Storage Tiering Insight
    # -------------------------------
    if total_storage_mb > 0:
        cold_pct = (cold_storage_mb / total_storage_mb) * 100

        if cold_pct > 30:
            recommendations.append(
                f"Cold (inactive) data occupies {cold_pct:.1f}% of total storage. "
                "Consider moving older files to archival/cold storage tiers "
                "instead of keeping them in active storage."
            )
        elif cold_pct > 10:
            recommendations.append(
                f"Cold data occupies {cold_pct:.1f}% of storage. "
                "A periodic review can reduce unnecessary storage growth."
            )

    # ------------------------------------------
    # Rule 2: High-Impact Categories (Safe Focus)
    # ------------------------------------------
    high_impact_categories = ["Archives", "Videos"]

    for category in high_impact_categories:
        count = cold_category_breakdown.get(category, 0)
        if count > 0:
            recommendations.append(
                f"{count} inactive {category.lower()} files detected. "
                "These are usually large and good candidates for archival storage "
                "or redundancy checks."
            )

    # -----------------------------------
    # Rule 3: Large Individual Cold Files
    # -----------------------------------
    if cold_files:
        large_cold_files = sorted(
            cold_files,
            key=lambda f: f["size_mb"],
            reverse=True
        )

        biggest = large_cold_files[0]

        if biggest["size_mb"] > 50:
            recommendations.append(
                f"The largest inactive file is '{biggest['file_name']}' "
                f"({biggest['size_mb']:.2f} MB). "
                "Large cold files provide the highest storage + carbon savings "
                "when archived or cleaned up."
            )

    # -----------------------------------
    # Rule 4: Safety Note for Documents
    # -----------------------------------
    if cold_category_breakdown.get("Documents", 0) > 0:
        recommendations.append(
            "Inactive documents were detected. "
            "Documents may still have legal or academic value, so review carefully "
            "before removal."
        )

    return recommendations[:3]


def generate_intelligent_usage_report(
    folder_path: str,
    threshold_days: int = 180,
) -> dict[str, Any]:
    """
    Scan a directory and produce a combined categorization + cold data report.

    Args:
        folder_path: Absolute or relative path to the target directory.
        threshold_days: Inactivity threshold for cold file detection.

    Returns:
        JSON-serializable dictionary containing:
            - total_files
            - total_storage_mb
            - cold_files_count
            - cold_storage_mb
            - estimated_carbon_saving_kg
            - category breakdowns
            - recommendations
    """

    files = scan_directory(folder_path)

    category_counter: Counter[str] = Counter()
    cold_category_counter: Counter[str] = Counter()

    cold_files: list[dict[str, Any]] = []

    total_storage_mb: float = 0.0
    cold_storage_mb: float = 0.0

    # -------------------------------
    # Scan + Categorize + Cold Detect
    # -------------------------------
    for file in files:
        category = categorize_file(file)
        metadata = get_file_usage_metadata(file)

        category_counter[category] += 1
        total_storage_mb += metadata["size_mb"]

        # Industry-grade cold candidate detection
        if is_cold_candidate(
            last_activity=metadata["last_modified"],  # Reliable signal
            category=category,
            size_mb=metadata["size_mb"],
            threshold_days=threshold_days,
        ):
            cold_category_counter[category] += 1
            cold_storage_mb += metadata["size_mb"]

            cold_files.append({
                "file_name": metadata["file_name"],
                "file_path": metadata["file_path"],
                "size_mb": metadata["size_mb"],
                "category": category,
                "last_accessed": metadata["last_accessed"].isoformat(),
                "last_modified": metadata["last_modified"].isoformat(),
            })

    # -------------------------------
    # Generate Recommendations
    # -------------------------------
    recommendations = _generate_recommendations(
        cold_files=cold_files,
        cold_category_breakdown=dict(cold_category_counter),
        cold_storage_mb=cold_storage_mb,
        total_storage_mb=total_storage_mb,
    )

    # -------------------------------
    # Carbon Footprint Estimation
    # -------------------------------
    cold_storage_gb = cold_storage_mb / 1024

    estimated_carbon_saving_kg = round(
        cold_storage_gb * CARBON_KG_PER_GB_PER_YEAR,
        3
    )

    # -------------------------------
    # Final Report Output
    # -------------------------------
    return {
        "total_files": len(files),
        "total_storage_mb": round(total_storage_mb, 4),
        "cold_files_count": len(cold_files),
        "cold_storage_mb": round(cold_storage_mb, 4),

        # Sustainability metric
        "estimated_carbon_saving_kg": estimated_carbon_saving_kg,

        # Categorization analytics
        "category_breakdown": dict(category_counter),
        "cold_category_breakdown": dict(cold_category_counter),

        # Cleanup insights
        "recommendations": recommendations,
    }
