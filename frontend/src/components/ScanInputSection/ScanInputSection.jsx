import { useState, useEffect } from 'react';
import styles from './ScanInputSection.module.css';
import { getCarbonIntensity } from '../../api/api';
import { API_BASE_URL } from '../../api/api';

/**
 * ScanInputSection - Intuitive folder selection for non-technical users.
 * "Browse Folder" opens native OS folder picker.
 * Manual path input available as alternative.
 */
export default function ScanInputSection({ onScan, isScanning }) {
  const [path, setPath] = useState('');
  const [region, setRegion] = useState('IN-WE');
  const [pathError, setPathError] = useState(null);
  const [selectingFolder, setSelectingFolder] = useState(false);
  const [carbonIntensities, setCarbonIntensities] = useState({});
  const [loadingIntensities, setLoadingIntensities] = useState(false);

  // Region definitions
  const regions = [
    { code: 'IN-WE', name: 'India (West)', description: 'High carbon intensity' },
    { code: 'IN-KA', name: 'India (Karnataka)', description: 'High carbon intensity' },
    { code: 'IN-DL', name: 'India (Delhi)', description: 'High carbon intensity' },
    { code: 'FR', name: 'France', description: 'Very low (nuclear)' },
    { code: 'DE', name: 'Germany', description: 'Medium-high carbon intensity' },
    { code: 'GB', name: 'Great Britain', description: 'Low carbon intensity' },
    { code: 'NO', name: 'Norway', description: 'Very low (hydroelectric)' },
    { code: 'US-VA', name: 'United States (Virginia)', description: 'Medium carbon intensity' },
    { code: 'US-TX', name: 'United States (Texas)', description: 'Wind + gas mix' },
    { code: 'US-CA', name: 'United States (California)', description: 'Lower carbon intensity' },
    { code: 'US-NY', name: 'United States (New York)', description: 'Lower carbon intensity' },
  ];

  // Load real carbon intensity values on mount
  useEffect(() => {
    const loadCarbonIntensities = async () => {
      setLoadingIntensities(true);
      const intensities = {};
      
      for (const region of regions) {
        try {
          const intensity = await getCarbonIntensity(region.code);
          intensities[region.code] = intensity;
        } catch (error) {
          console.warn(`Failed to load carbon intensity for ${region.code}:`, error);
          intensities[region.code] = 500; // Default
        }
      }
      
      setCarbonIntensities(intensities);
      setLoadingIntensities(false);
    };

    loadCarbonIntensities();
  }, []);

  const handleInputChange = (e) => {
    setPath(e.target.value);
    setPathError(null);
  };

  const handleRegionChange = (e) => {
    setRegion(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = path.trim();
    if (!trimmed || isScanning) return;
    setPathError(null);

    // Pass the path directly to onScan
    onScan(trimmed, region, null);
  };

  const handleSelectFolderClick = async () => {
    if (isScanning || selectingFolder) return;

    setSelectingFolder(true);
    setPathError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/select-folder`);
      const data = await response.json();

      if (data.path && data.path.trim().length > 0) {
        setPath(data.path);
      } else if (data.error) {
        setPathError(data.error);
      } else {
        setPathError('No folder was selected. Please try again.');
      }
    } catch (error) {
      setPathError('Failed to open folder browser. Make sure the backend is running (python app.py in /backend).');
      console.error('Folder selection error:', error);
    } finally {
      setSelectingFolder(false);
    }
  };

  const hasPath = path.trim().length > 0;

  return (
    <section className={styles.section} aria-labelledby="scan-heading">
      <h2 id="scan-heading" className={styles.heading}>
        Step 1: Select storage location
      </h2>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.actionRow}>
          <button
            type="button"
            onClick={handleSelectFolderClick}
            disabled={isScanning || selectingFolder}
            className={styles.selectButton}
          >
            {selectingFolder ? 'Opening Folder Browser...' : 'Browse Folder'}
          </button>
          {hasPath && (
            <span className={styles.selectedPath} title={path}>
              Selected: {path.length > 40 ? `${path.slice(0, 37)}...` : path}
            </span>
          )}
        </div>

        {pathError && (
          <p id="path-error" className={styles.error} role="alert">
            {pathError}
          </p>
        )}

        <div className={styles.divider}>or paste folder path</div>
        <label htmlFor="scan-path" className={styles.label}>
          Folder path
        </label>
        <div className={styles.inputRow}>
          <input
            id="scan-path"
            type="text"
            value={path}
            onChange={handleInputChange}
            placeholder="e.g., C:\\Users\\Documents or /home/user/Documents"
            disabled={isScanning}
            className={`${styles.input} ${pathError ? styles.inputError : ''}`}
            aria-describedby="scan-hint"
            aria-invalid={!!pathError}
            autoComplete="off"
          />
          <button
            type="submit"
            disabled={isScanning || !hasPath}
            className={styles.submitButton}
            aria-busy={isScanning}
          >
            {isScanning ? 'Scanning...' : 'Start Scan'}
          </button>
        </div>

        <p id="scan-hint" className={styles.hint}>
          Click "Browse Folder" to select a folder using your file explorer, or paste a folder path directly.
        </p>

        <div className={styles.regionSection}>
          <label htmlFor="region-select" className={styles.label}>
            Region (for carbon intensity)
            {loadingIntensities && <span className={styles.loadingIndicator}> — Loading real values...</span>}
          </label>
          <select
            id="region-select"
            value={region}
            onChange={handleRegionChange}
            disabled={isScanning}
            className={styles.select}
          >
            {regions.map(r => {
              const intensity = carbonIntensities[r.code];
              const intensityText = intensity !== undefined ? ` — ${intensity} gCO2/kWh` : ' — Loading...';
              return (
                <option key={r.code} value={r.code}>
                  {r.name}{intensityText}
                </option>
              );
            })}
          </select>
          <p className={styles.regionHint}>
            Real-time carbon intensity data from ElectricityMap API
          </p>
        </div>
      </form>
    </section>
  );
}
