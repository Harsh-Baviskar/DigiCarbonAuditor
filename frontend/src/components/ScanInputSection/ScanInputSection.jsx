import { useState, useRef } from 'react';
import styles from './ScanInputSection.module.css';

/**
 * ScanInputSection - Intuitive folder selection for non-technical users.
 * "Select Folder" uses system picker where supported; manual input as fallback.
 * Accepts storage size in GB and region for carbon intensity calculation.
 */
export default function ScanInputSection({ onScan, isScanning }) {
  const [path, setPath] = useState('');
  const [region, setRegion] = useState('IN-WE');
  const [pathError, setPathError] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [folderSizeGB, setFolderSizeGB] = useState(null);
  const fileInputRef = useRef(null);

  const calculateFolderSize = (files) => {
    let totalBytes = 0;
    for (let i = 0; i < files.length; i++) {
      totalBytes += files[i].size;
    }
    // Convert bytes to GB
    return totalBytes / (1024 * 1024 * 1024);
  };

  const handleFolderSelect = (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    // Get the full folder path from webkitRelativePath (shows relative path from selected folder)
    const firstFile = files[0];
    const relativePath = firstFile.webkitRelativePath || firstFile.name;
    // Extract the root folder path
    const folderPath = relativePath.split('/')[0];
    
    // Calculate total size from all files
    const calculatedSizeGB = calculateFolderSize(files);
    
    // Store both folder path and files for later use
    // Display: folder path (size in GB, number of files)
    setPath(`${folderPath} (${calculatedSizeGB.toFixed(2)} GB, ${files.length} files)`);
    setSelectedFiles(files);
    setFolderSizeGB(calculatedSizeGB);
    setPathError(null);
    e.target.value = '';
  };

  const handleInputChange = (e) => {
    setPath(e.target.value);
    setSelectedFiles(null);
    setFolderSizeGB(null);
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
    
    // Check if this looks like a folder selection (contains size and file count)
    const folderMatch = trimmed.match(/^(.+?)\s*\(\s*([\d.]+)\s*GB,\s*(\d+)\s*files?\s*\)$/i);
    if (folderMatch) {
      // Extract folder name and calculated size from the display string
      const folderName = folderMatch[1].trim();
      const sizeGB = parseFloat(folderMatch[2]);
      const fileCount = parseInt(folderMatch[3]);
      console.log(`Folder selected: ${folderName}, ${sizeGB} GB, ${fileCount} files`);
      // Pass the actual calculated size (in GB) so backend doesn't need to guess
      onScan(sizeGB.toString(), region, fileCount);
    } else {
      // Manual input - user should enter size in GB (no file count available)
      const sizeNum = parseFloat(trimmed);
      if (isNaN(sizeNum) || sizeNum <= 0) {
        setPathError('Please select a folder or enter a valid storage size in GB (e.g., 500).');
        return;
      }
      onScan(trimmed, region);
    }
  };

  const handleSelectFolderClick = () => {
    if (isScanning) return;
    fileInputRef.current?.click();
  };

  const hasPath = path.trim().length > 0;

  return (
    <section className={styles.section} aria-labelledby="scan-heading">
      <h2 id="scan-heading" className={styles.heading}>
        Step 1: Select storage location
      </h2>
      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          ref={fileInputRef}
          type="file"
          webkitdirectory=""
          directory=""
          multiple
          onChange={handleFolderSelect}
          className={styles.hiddenInput}
          aria-hidden="true"
          tabIndex={-1}
        />
        <div className={styles.actionRow}>
          <button
            type="button"
            onClick={handleSelectFolderClick}
            disabled={isScanning}
            className={styles.selectButton}
          >
            Select Folder
          </button>
          {hasPath && (
            <span className={styles.selectedPath} title={path}>
              Selected: {path.length > 40 ? `${path.slice(0, 37)}ΓÇª` : path}
            </span>
          )}
        </div>
        <div className={styles.divider}>or type storage size</div>
        <label htmlFor="scan-path" className={styles.label}>
          Storage size (in GB)
        </label>
        <div className={styles.inputRow}>
          <input
            id="scan-path"
            type="text"
            value={path}
            onChange={handleInputChange}
            placeholder="e.g., 500 (for 500 GB) or select a folder above"
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
            {isScanning ? 'ScanningΓÇª' : 'Start Scan'}
          </button>
        </div>
        {pathError && (
          <p id="path-error" className={styles.error} role="alert">
            {pathError}
          </p>
        )}
        <p id="scan-hint" className={styles.hint}>
          Select a folder to automatically calculate its size, or manually enter storage size in GB (e.g., 500).
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
            <option value="IN-WE">India (West) - 447 gCOΓéé/kWh</option>
            <option value="IN-KA">India (Karnataka) - ~450 gCOΓéé/kWh</option>
            <option value="IN-DL">India (Delhi) - ~450 gCOΓéé/kWh</option>
            <option value="FR">France - 25 gCOΓéé/kWh</option>
            <option value="DE">Germany - ~380 gCOΓéé/kWh</option>
            <option value="GB">Great Britain - ~200 gCOΓéé/kWh</option>
            <option value="US-VA">United States (Virginia) - ~360 gCOΓéé/kWh</option>
            <option value="US-TX">United States (Texas) - ~380 gCOΓéé/kWh</option>
            <option value="US-CA">United States (California) - ~177 gCOΓéé/kWh</option>
            <option value="US-NY">United States (New York) - ~120 gCOΓéé/kWh</option>
          </select>
        </div>
      </form>
    </section>
  );
}
