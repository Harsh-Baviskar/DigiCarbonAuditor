import { useState } from 'react';
import styles from './ScanInputSection.module.css';

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
      const response = await fetch('/select-folder');
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
          </label>
          <select
            id="region-select"
            value={region}
            onChange={handleRegionChange}
            disabled={isScanning}
            className={styles.select}
          >
            <option value="IN-WE">India (West) - 447 gCO2/kWh</option>
            <option value="IN-KA">India (Karnataka) - ~450 gCO2/kWh</option>
            <option value="IN-DL">India (Delhi) - ~450 gCO2/kWh</option>
            <option value="FR">France - 25 gCO2/kWh</option>
            <option value="DE">Germany - ~380 gCO2/kWh</option>
            <option value="GB">Great Britain - ~200 gCO2/kWh</option>
            <option value="US-VA">United States (Virginia) - ~360 gCO2/kWh</option>
            <option value="US-TX">United States (Texas) - ~380 gCO2/kWh</option>
            <option value="US-CA">United States (California) - ~177 gCO2/kWh</option>
            <option value="US-NY">United States (New York) - ~120 gCO2/kWh</option>
          </select>
        </div>
      </form>
    </section>
  );
}
