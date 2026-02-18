/**
 * Real API client for Digital Carbon Auditor backend
 * Connects to Flask backend at the configured API URL
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Converts a path/folder size input to storage in TB
 * For now, this accepts a numeric value (in GB) and converts to TB
 * @param {string|number} pathOrSize - The size in GB
 * @returns {number} Size in TB
 */
function parseStorageSize(pathOrSize) {
  const num = parseFloat(pathOrSize);
  if (isNaN(num)) {
    throw new Error('Invalid storage size. Please enter a number in GB (e.g., 500).');
  }
  if (num <= 0) {
    throw new Error('Storage size must be greater than 0 GB.');
  }
  return num / 1024; // Convert GB to TB
}

/**
 * Calls the backend /calculate endpoint
 * @param {number} storageTb - Storage size in TB
 * @param {string} region - Region for carbon intensity (default: IN-WE)
 * @returns {Promise<object>} Calculation result
 */
async function callBackendCalculate(storageTb, region = 'IN-WE') {
  const response = await fetch(`${API_BASE_URL}/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      storage_tb: storageTb,
      region: region,
    }),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Uploads a folder (as zip) to the backend for scanning
 * @param {File} zipFile - The zip file containing the folder
 * @param {string} region - Region for carbon intensity (default: IN-WE)
 * @returns {Promise<object>} Scan result
 */
async function callBackendUpload(zipFile, region = 'IN-WE') {
  const formData = new FormData();
  formData.append('file', zipFile);
  formData.append('region', region);

  const response = await fetch(`${API_BASE_URL}/upload-folder`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Transforms category breakdown from backend into file type array format
 * @param {object} categoryBreakdown - Backend category data {category: size}
 * @param {number} totalBytes - Total storage bytes
 * @returns {array} Formatted file type array with percentages
 */
function transformCategoryBreakdown(categoryBreakdown, totalBytes) {
  if (!categoryBreakdown || !totalBytes) return [];

  return Object.entries(categoryBreakdown)
    .map(([category, sizeBytes]) => ({
      type: category,
      count: 0, // Backend doesn't provide file count per category
      sizeBytes: sizeBytes,
      percentOfTotal: totalBytes > 0 ? ((sizeBytes / totalBytes) * 100).toFixed(1) : 0,
    }))
    .sort((a, b) => b.sizeBytes - a.sizeBytes);
}

/**
 * Creates suggested actions based on carbon impact
 * @param {object} result - Backend calculation result
 * @returns {array} Suggested actions array
 */
function createSuggestedActions(result) {
  const actions = [];
  const carbonKg = result.carbon_kg_per_year || 0;
  const storageGb = (result.storage_tb || 0) * 1024;

  // Primary action: reduce storage
  if (carbonKg > 0) {
    actions.push({
      id: '1',
      action: `Reduce storage footprint (currently ${storageGb.toFixed(2)} GB)`,
      impactBytes: (storageGb * 1024 * 1024 * 1024) * 0.1, // Assume 10% reduction potential
      impactLabel: `~${(carbonKg * 0.1).toFixed(1)} kg CO2`,
      type: 'safe',
      reason: `Removing 10% of storage could save ${(carbonKg * 0.1).toFixed(1)} kg CO2/year`,
    });
  }

  // Secondary action: optimize energy source (informational)
  actions.push({
    id: '2',
    action: 'Consider carbon-neutral storage or renewable energy providers',
    impactBytes: 0,
    impactLabel: 'Variable',
    type: 'review_needed',
    reason: 'Moving to renewable-powered data centers can reduce carbon footprint by 50-100%',
  });

  return actions;
}

/**
 * Calls the backend /calculate endpoint via GET for folder paths or numeric sizes
 * @param {string} pathOrSize - Folder path or numeric size in GB
 * @param {string} region - Region for carbon intensity (default: IN-WE)
 * @returns {Promise<object>} Calculation result
 */
async function callBackendCalculateViaGet(pathOrSize, region = 'IN-WE') {
  const numValue = parseFloat(pathOrSize);
  
  let url = `${API_BASE_URL}/calculate?region=${encodeURIComponent(region)}`;
  
  if (!isNaN(numValue) && numValue > 0) {
    // It's a numeric storage size in GB
    url += `&data_size=${numValue}`;
  } else {
    // It's a folder path
    url += `&path=${encodeURIComponent(pathOrSize)}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Backend error: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Scanning by accepting a storage size or file upload
 * Integrates with the backend to calculate carbon emissions
 * @param {string|File} pathOrFile - Path string or File object for upload
 * @param {string} region - Region for carbon intensity (default: IN-WE)
 * @returns {Promise<object>} Scan result with carbon calculations
 */
export async function startScan(pathOrFile, region = 'IN-WE') {
  try {
    let result;

    // If it's a File object, upload it
    if (pathOrFile instanceof File) {
      result = await callBackendUpload(pathOrFile, region);
    } else {
      // Use GET endpoint for folder paths and numeric sizes
      result = await callBackendCalculateViaGet(pathOrFile, region);
    }

    console.log('Backend response:', result);
    console.log('Backend response keys:', Object.keys(result));

    // Backend now returns real API-based calculations with ElectricityMap carbon intensity
    // Response includes: carbon_intensity_gco2_per_kwh, energy_kwh_per_year, carbon_kg_per_year, etc.
    const normalizedResult = {
      // From backend (either GET or POST endpoint)
      storage_tb: result.storage_tb || (result.data_size_gb || 0) / 1024,
      storage_gb: result.storage_gb || result.data_size_gb,
      energy_kwh_per_year: result.energy_kwh_per_year,
      carbon_kg_per_year: result.carbon_kg_per_year || result.carbon_footprint_kg,
      carbon_cost_estimate: result.carbon_cost_estimate,
      region: result.region,
      carbon_intensity_gco2_per_kwh: result.carbon_intensity_gco2_per_kwh,
      calculation_method: result.calculation_method
    };

    console.log('Real carbon values from backend (ElectricityMap API):', {
      region: normalizedResult.region,
      carbon_intensity_gco2_per_kwh: normalizedResult.carbon_intensity_gco2_per_kwh,
      energy_kwh_per_year: normalizedResult.energy_kwh_per_year,
      carbon_kg_per_year: normalizedResult.carbon_kg_per_year,
      carbon_cost_estimate: normalizedResult.carbon_cost_estimate,
      calculation_method: normalizedResult.calculation_method
    });

    const totalBytes = (normalizedResult.storage_tb || 0) * 1024 * 1024 * 1024 * 1024;
    const categoryBreakdown = result.category_breakdown || {};

    // Transform backend response to match frontend expectations
    const transformedResult = {
      success: true,
      scannedPath: pathOrFile instanceof File ? pathOrFile.name : pathOrFile,
      region: normalizedResult.region,
      carbonIntensity: normalizedResult.carbon_intensity_gco2_per_kwh,
      summary: {
        totalFiles: result.estimated_files || result.files_scanned || 0,
        totalStorageBytes: totalBytes,
        duplicateFilesCount: 0, // Not provided by backend
        wastedStorageBytes: 0, // Not provided by backend
      },
      topContributors: {
        byFileType: transformCategoryBreakdown(categoryBreakdown, totalBytes),
        byFolderDuplication: [], // Not provided by backend
      },
      suggestedActions: createSuggestedActions(normalizedResult),
      duplicateGroups: [], // Not provided by backend
      // Carbon calculation data from ElectricityMap API - ensure proper number conversion
      energyKwhPerYear: Number(normalizedResult.energy_kwh_per_year ?? 0),
      carbonKgPerYear: Number(normalizedResult.carbon_kg_per_year ?? 0),
      carbonCostEstimate: Number(normalizedResult.carbon_cost_estimate ?? 0),
    };

    console.log('Transformed result:', transformedResult);
    console.log('Carbon values:', {
      energyKwhPerYear: transformedResult.energyKwhPerYear,
      carbonKgPerYear: transformedResult.carbonKgPerYear,
      carbonCostEstimate: transformedResult.carbonCostEstimate,
      rawBackend: {
        energy_kwh_per_year: result.energy_kwh_per_year,
        carbon_kg_per_year: result.carbon_kg_per_year,
        carbon_cost_estimate: result.carbon_cost_estimate,
      }
    });
    return transformedResult;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error(`Failed to scan: ${error.message}`);
  }
}

/**
 * Fetches carbon intensity for a specific region
 * @param {string} region - ISO region code (e.g., 'IN-WE', 'US-CA', 'FR')
 * @returns {Promise<number>} Carbon intensity in gCO2/kWh
 */
export async function getCarbonIntensity(region = 'IN-WE') {
  try {
    // Use a small data size (0.1 GB) to fetch minimal data but get the carbon intensity
    const response = await fetch(`${API_BASE_URL}/calculate?data_size=0.1&region=${encodeURIComponent(region)}`);
    
    if (!response.ok) {
      console.warn(`Failed to fetch carbon intensity for ${region}, using default`);
      return 500; // Default fallback
    }
    
    const data = await response.json();
    return data.carbon_intensity_gco2_per_kwh ?? 500;
  } catch (error) {
    console.warn(`Error fetching carbon intensity for ${region}:`, error);
    return 500; // Default fallback
  }
}

