/**
 * API for Digital Carbon Auditor
 * Connects to FastAPI backend at /api/scan (proxied to localhost:8000)
 */

/**
 * Scans a directory for duplicates and carbon footprint.
 * @param {string} path - Directory path to scan
 * @returns {Promise<object>} Scan result from backend
 */
export async function startScan(path) {
  try {
    const response = await fetch('/api/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ path }),
    });

    if (!response.ok) {
      // Extract error message from backend
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `Scan failed with status ${response.status}`;
      throw new Error(errorMessage);
    }

    const data = await response.json();
    
    // Backend returns the exact structure needed by frontend
    return data;
    
  } catch (error) {
    // Network error or fetch failure
    if (error.message === 'Failed to fetch') {
      throw new Error(
        'Cannot connect to backend server. Please ensure the backend is running on port 8000.'
      );
    }
    throw error;
  }
}

