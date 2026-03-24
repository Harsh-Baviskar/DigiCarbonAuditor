/**
 * Formatting utilities for consistent display across the dashboard.
 */

/**
 * Format bytes to human-readable size (e.g., 1.5 GB, 256 MB).
 */
export function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Truncate long hash for display, keeping prefix and suffix.
 */
export function truncateHash(hash, maxLength = 24) {
  if (hash.length <= maxLength) return hash;
  const half = Math.floor((maxLength - 3) / 2);
  return `${hash.slice(0, half)}...${hash.slice(-half)}`;
}

/**
 * Convert storage bytes to estimated carbon impact (kg CO2e/year).
 * Uses simplified model: ~0.2 kg CO2e per GB-year (typical data center, global avg).
 */
export function bytesToCarbonKg(bytes) {
  const gb = bytes / (1024 * 1024 * 1024);
  return gb * 0.2;
}

/**
 * Format carbon impact for display. Returns intuitive primary + optional equivalence.
 * e.g. "~0.4 kg CO2e/year" and "≈ 12 smartphone charges"
 */
export function formatCarbonImpact(bytes) {
  const kg = bytesToCarbonKg(bytes);
  if (kg < 0.01) return null;
  const primary = `~${kg < 1 ? kg.toFixed(2) : Math.round(kg)} kg CO₂e/year`;
  // 1 kg CO2e ≈ 50 smartphone charges (rough)
  const charges = Math.round(kg * 50);
  const equivalence = charges >= 1 ? `≈ ${charges} smartphone charge${charges !== 1 ? 's' : ''}` : null;
  return { primary, equivalence };
}
