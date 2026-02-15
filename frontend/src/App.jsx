import { useState, useCallback, useMemo } from 'react';
import Layout from './components/Layout/Layout';
import StepIndicator from './components/StepIndicator/StepIndicator';
import ScanInputSection from './components/ScanInputSection/ScanInputSection';
import SummaryMetrics from './components/SummaryMetrics/SummaryMetrics';
import TopContributors from './components/TopContributors/TopContributors';
import SuggestedActions from './components/SuggestedActions/SuggestedActions';
import DuplicateFilesView from './components/DuplicateFilesView/DuplicateFilesView';
import StatusFeedback from './components/StatusFeedback/StatusFeedback';
import { startScan } from './api/mockApi';
import styles from './App.module.css';

/**
 * Dashboard - Guided flow: Select → Scan → Review.
 * Step indicator reduces cognitive load; StatusFeedback builds trust.
 */
function getCurrentStep(status, result) {
  if (result) return 3;
  if (status === 'loading' || status === 'success') return 2;
  return 1;
}

export default function App() {
  const [isScanning, setIsScanning] = useState(false);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const currentStep = useMemo(() => getCurrentStep(status, result), [status, result]);

  const handleScan = useCallback(async (path) => {
    setIsScanning(true);
    setStatus('loading');
    setError(null);
    setResult(null);

    try {
      const data = await startScan(path);
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
    <Layout>
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
        />
      </section>

      {result && (
        <div className={styles.results} aria-label="Step 3: Review results">
          <section className={styles.summarySection} aria-label="Summary metrics">
            <SummaryMetrics summary={result.summary} />
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
    </Layout>
  );
}
