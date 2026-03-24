import { useState } from 'react';
import styles from './DuplicateDetectorPage.module.css';
import ScanInputSection from '../ScanInputSection/ScanInputSection';
import StatusFeedback from '../StatusFeedback/StatusFeedback';
import DuplicateFilesView from '../DuplicateFilesView/DuplicateFilesView';
import SuggestedActions from '../SuggestedActions/SuggestedActions';

export default function DuplicateDetectorPage() {
  const [scanData, setScanData] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);

  const handleScan = async (path) => {
    setIsScanning(true);
    setError(null);
    setScanData(null);

    try {
      const { startScan } = await import('../../api/mockApi');
      const result = await startScan(path);
      setScanData(result);
    } catch (err) {
      setError(err.message || 'Failed to scan directory');
      console.error('Scan error:', err);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className={styles.page} role="tabpanel" id="duplicate-detector-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>Duplicate Detector</h2>
        <p className={styles.description}>
          Find and remove duplicate files to save storage space and reduce your digital carbon footprint.
        </p>
      </div>

      <ScanInputSection onScan={handleScan} isScanning={isScanning} />
      
      {isScanning && (
        <StatusFeedback 
          status="scanning" 
          message="Scanning for duplicate files..." 
        />
      )}
      
      {error && (
        <StatusFeedback 
          status="error" 
          message={error} 
        />
      )}

      {scanData && !isScanning && (
        <div className={styles.results}>
          {scanData.duplicateGroups && scanData.duplicateGroups.length > 0 ? (
            <>
              <SuggestedActions suggestedActions={scanData.suggestedActions} />
              <DuplicateFilesView duplicateGroups={scanData.duplicateGroups} />
            </>
          ) : (
            <StatusFeedback 
              status="success" 
              message="No duplicate files found! Your storage is clean." 
            />
          )}
        </div>
      )}
    </div>
  );
}
