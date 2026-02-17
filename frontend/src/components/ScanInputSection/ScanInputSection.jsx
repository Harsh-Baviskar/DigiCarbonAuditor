import { useState, useRef } from 'react';
import styles from './ScanInputSection.module.css';

/**
 * ScanInputSection - Intuitive folder selection for non-technical users.
 * Note: Browser security prevents reading full paths from folder picker.
 * Users must type the complete absolute path manually.
 */
export default function ScanInputSection({ onScan, isScanning }) {
  const [path, setPath] = useState('');
  const [pathError, setPathError] = useState(null);
  const [pickerHint, setPickerHint] = useState(null);
  const fileInputRef = useRef(null);

  const handleFolderSelect = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    // Get folder name from browser (but not full path due to security)
    const firstPath = files[0].webkitRelativePath || files[0].name;
    const folderName = firstPath.split('/')[0] || firstPath;
    
    // Show helpful hint with common Windows paths
    const username = 'YourName'; // Users will need to replace this
    setPickerHint(
      `Selected folder: "${folderName}". Please type the complete path below. Common paths:\n` +
      `• C:\\Users\\${username}\\Documents\n` +
      `• C:\\Users\\${username}\\Downloads\n` +
      `• C:\\Users\\${username}\\Desktop`
    );
    
    e.target.value = '';
  };

  const handleInputChange = (e) => {
    setPath(e.target.value);
    setPathError(null);
    setPickerHint(null); // Clear picker hint when user starts typing
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = path.trim();
    if (!trimmed || isScanning) return;
    setPathError(null);
    onScan(trimmed);
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
              Selected: {path.length > 40 ? `${path.slice(0, 37)}…` : path}
            </span>
          )}
        </div>
        <div className={styles.divider}>or type full path</div>
        <label htmlFor="scan-path" className={styles.label}>
          Directory path (full absolute path required)
        </label>
        <div className={styles.inputRow}>
          <input
            id="scan-path"
            type="text"
            value={path}
            onChange={handleInputChange}
            placeholder="e.g. C:\Users\aradh\Documents or C:\Users\aradh\Downloads"
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
            {isScanning ? 'Scanning…' : 'Start Scan'}
          </button>
        </div>
        {pathError && (
          <p id="path-error" className={styles.error} role="alert">
            {pathError}
          </p>
        )}
        {pickerHint && (
          <p className={styles.hint} style={{ whiteSpace: 'pre-line', marginTop: '0.5rem' }}>
            {pickerHint}
          </p>
        )}
        {!pickerHint && (
          <p id="scan-hint" className={styles.hint}>
            Choose a folder or enter a path to analyze for duplicates and carbon footprint.
          </p>
        )}
      </form>
    </section>
  );
}
