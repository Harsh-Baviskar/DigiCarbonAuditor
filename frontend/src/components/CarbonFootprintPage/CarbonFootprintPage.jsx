import { useState, useCallback, useMemo } from 'react';
import styles from './CarbonFootprintPage.module.css';
import StepIndicator from '../StepIndicator/StepIndicator';
import ScanInputSection from '../ScanInputSection/ScanInputSection';
import StatusFeedback from '../StatusFeedback/StatusFeedback';
import SummaryMetrics from '../SummaryMetrics/SummaryMetrics';
import CarbonImpact from '../CarbonImpact/CarbonImpact';
import EnergyBreakdown from '../EnergyBreakdown/EnergyBreakdown';
import TopContributors from '../TopContributors/TopContributors';
import SuggestedActions from '../SuggestedActions/SuggestedActions';
import DuplicateFilesView from '../DuplicateFilesView/DuplicateFilesView';
import { startScan } from '../../api/api';

/**
 * CarbonFootprintPage - Scan storage and calculate carbon emissions
 * Determines the environmental impact of data storage using real ElectricityMaps API
 */
function getCurrentStep(status, result) {
  if (result) return 3;
  if (status === 'loading' || status === 'success') return 2;
  return 1;
}

export default function CarbonFootprintPage() {
  const [isScanning, setIsScanning] = useState(false);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [fileCount, setFileCount] = useState(null);

  const currentStep = useMemo(() => getCurrentStep(status, result), [status, result]);

  const handleScan = useCallback(async (path, region = 'IN-WE', totalFiles = null) => {
    setIsScanning(true);
    setStatus('loading');
    setError(null);
    setResult(null);
    setFileCount(totalFiles);

    try {
      const data = await startScan(path, region);
      setResult(data);
      setStatus('success');
    } catch (err) {
      setError(err.message || 'Scan failed. Please try again.');
      setStatus('error');
    } finally {
      setIsScanning(false);
    }
  }, []);

  return (
    <div className={styles.page} role="tabpanel" id="carbon-footprint-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>Carbon Footprint Estimator</h2>
        <p className={styles.description}>
          Estimate the carbon footprint of your digital storage by analyzing file sizes and calculating COΓéé emissions based on your region's electricity carbon intensity.
        </p>
      </div>

      <StepIndicator currentStep={currentStep} />

      <section className={styles.scanSection} aria-label="Step 1: Select storage">
        <ScanInputSection onScan={handleScan} isScanning={isScanning} />
      </section>

      <section className={styles.scanSection} aria-label="Step 2: Run scan">
        <StatusFeedback
          status={status}
          error={error}
          scannedPath={result?.scannedPath}
          wastedStorageBytes={result?.summary?.wastedStorageBytes}
          totalFilesCount={fileCount}
        />
      </section>

      {result && (
        <div className={styles.results} aria-label="Step 3: Review results">
          <section className={styles.summarySection} aria-label="Summary metrics">
            <SummaryMetrics summary={result.summary} />
          </section>

          <section className={styles.carbonSection} aria-label="Carbon impact">
            <CarbonImpact result={result} />
          </section>

          <section className={styles.energySection} aria-label="Energy breakdown">
            <EnergyBreakdown result={result} />
          </section>

          <div className={styles.insightGrid}>
            <section className={styles.contributorsSection} aria-label="Top contributors">
              <TopContributors topContributors={result.topContributors} />
            </section>
            <section className={styles.actionsSection} aria-label="Suggested actions">
              <SuggestedActions suggestedActions={result.suggestedActions} />
            </section>
          </div>

          <section className={styles.duplicatesSection} aria-label="Duplicate files detail">
            <DuplicateFilesView duplicateGroups={result.duplicateGroups} />
          </section>
        </div>
      )}
    </div>
  );
}
