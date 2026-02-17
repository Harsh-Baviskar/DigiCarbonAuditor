/**
 * Intelligent Usage API (Real Backend)
 * Fetches file categorization + cold data report from Flask backend.
 */

export async function fetchIntelligentUsage(path) {
    const params = new URLSearchParams({
        path: path,
        threshold_days: 180,
    });

    const response = await fetch(
        `/api/intelligent-usage?${params.toString()}`
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Intelligent usage scan failed");
    }

    // Normalize snake_case -> camelCase
    return {
        totalFiles: data.total_files ?? 0,
        totalStorageMB: data.total_storage_mb ?? 0,
        coldFilesCount: data.cold_files_count ?? 0,
        coldStorageGB: (data.cold_storage_mb ? data.cold_storage_mb / 1024 : 0).toFixed(2),
        estimatedCarbonSavingKg: (data.estimated_carbon_saving_kg ?? 0).toFixed(3),
        categoryBreakdown: data.category_breakdown || {},
        recommendations: data.recommendations || []
    };
}
