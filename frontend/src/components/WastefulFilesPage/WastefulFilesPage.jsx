import { useState, useMemo } from 'react';
import styles from './WastefulFilesPage.module.css';
import StepIndicator from '../StepIndicator/StepIndicator';
import ScanInputSection from '../ScanInputSection/ScanInputSection';
import StatusFeedback from '../StatusFeedback/StatusFeedback';
import DuplicateFilesView from '../DuplicateFilesView/DuplicateFilesView';
import SuggestedActions from '../SuggestedActions/SuggestedActions';

function getCurrentStep(isScanning, scanData) {
  if (scanData) return 3;
  if (isScanning) return 2;
  return 1;
}

export default function WastefulFilesPage() {
  const [scanData, setScanData] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);

  const currentStep = useMemo(() => getCurrentStep(isScanning, scanData), [isScanning, scanData]);

  const handleScan = async (path, region = 'IN-WE', fileCount = null) => {
    setIsScanning(true);
    setError(null);
    setScanData(null);

    try {
      const { startScan } = await import('../../api/api');
      const result = await startScan(path, region);
      setScanData(result);
    } catch (err) {
      setError(err.message || 'Failed to scan directory');
      console.error('Scan error:', err);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className={styles.page} role="tabpanel" id="wasteful-files-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>Wasteful Files Detector</h2>
        <p className={styles.description}>
          Find and remove duplicate and wasteful files to save storage space and reduce your digital carbon footprint.
        </p>
      </div>

      <StepIndicator currentStep={currentStep} />

      <ScanInputSection onScan={handleScan} isScanning={isScanning} />
      
      {isScanning && (
        <StatusFeedback 
          status="scanning" 
          message="Scanning for wasteful and duplicate files..." 
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
              message="No wasteful or duplicate files found! Your storage is clean." 
            />
          )}
        </div>
      )}
    </div>
  );
}
