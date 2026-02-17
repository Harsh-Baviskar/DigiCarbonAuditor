import { useState } from 'react';
import styles from './CarbonFootprintPage.module.css';
import ScanInputSection from '../ScanInputSection/ScanInputSection';
import StatusFeedback from '../StatusFeedback/StatusFeedback';
import SummaryMetrics from '../SummaryMetrics/SummaryMetrics';

export default function CarbonFootprintPage() {
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
    <div className={styles.page} role="tabpanel" id="carbon-footprint-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>Carbon Footprint Estimator</h2>
        <p className={styles.description}>
          Estimate the carbon footprint of your digital storage by analyzing file sizes and calculating CO₂ emissions.
        </p>
      </div>

      <ScanInputSection onScan={handleScan} isScanning={isScanning} />
      
      {isScanning && (
        <StatusFeedback 
          status="scanning" 
          message="Analyzing your files..." 
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
          <SummaryMetrics summary={scanData.summary} />
        </div>
      )}
    </div>
  );
}
