import { useState, useMemo } from 'react';
import styles from './WastefulFilesPage.module.css';
import StepIndicator from '../StepIndicator/StepIndicator';
import ScanInputSection from '../ScanInputSection/ScanInputSection';
import StatusFeedback from '../StatusFeedback/StatusFeedback';
import WastefulFilesStatistics from '../WastefulFilesStatistics/WastefulFilesStatistics';
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
      // Validate path
      if (!path || path.trim() === '') {
        throw new Error('Please select a folder or enter a valid folder path');
      }

      console.log('Starting waste detection scan for:', path);

      // Call the waste-detect endpoint via vite proxy
      const response = await fetch('/waste-detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path.trim() })
      });

      console.log('Response status:', response.status);
      
      const data = await response.json();
      console.log('Response data:', data);

      if (!response.ok) {
        const errorMessage = data.detail || data.error || `Scan failed with status ${response.status}`;
        throw new Error(errorMessage);
      }

      // Check if scan had errors
      if (data.scanStatus === 'error') {
        throw new Error(data.error || data.detail || 'Scan encountered an unexpected error');
      }

      setScanData(data);
    } catch (err) {
      const errorMsg = err.message || 'Failed to scan directory';
      setError(errorMsg);
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
          {(scanData.duplicateGroups?.length > 0 || 
            scanData.oldFiles?.length > 0 || 
            scanData.systemFiles?.length > 0) ? (
            <>
              <WastefulFilesStatistics scanData={scanData} />
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
