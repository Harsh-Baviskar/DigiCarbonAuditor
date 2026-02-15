import { useState, useEffect } from 'react';
import { formatCarbonImpact } from '../../utils/formatters';
import styles from './StatusFeedback.module.css';

/**
 * StatusFeedback - Scanning progress and completion state.
 * Clear status, mock file count, and background explanations build trust.
 */
export default function StatusFeedback({
  status,
  error,
  scannedPath,
  wastedStorageBytes,
}) {
  const [simulatedCount, setSimulatedCount] = useState(0);

  // Mock progress during loading: simulates file count for user feedback (no backend)
  useEffect(() => {
    if (status !== 'loading') return;
    setSimulatedCount(0);
    const interval = setInterval(() => {
      setSimulatedCount((prev) => Math.min(prev + 47, 1247));
    }, 100);
    return () => clearInterval(interval);
  }, [status]);

  if (!status || status === 'idle') {
    return (
      <section className={styles.section} aria-live="polite">
        <p className={styles.message}>
          Select a folder or enter a path, then click Start Scan to analyze duplicates and carbon impact.
        </p>
      </section>
    );
  }

  if (status === 'loading') {
    return (
      <section className={styles.section} aria-live="polite" aria-busy="true">
        <div className={styles.progressBar} role="progressbar" aria-valuetext="Scanning storage">
          <div className={styles.progressFill} />
        </div>
        <p className={styles.message}>
          Scanning storage… {simulatedCount > 0 && `${simulatedCount.toLocaleString()} files processed.`}
        </p>
        <p className={styles.explanation}>
          Reading files, computing hashes for duplicate detection, and estimating carbon footprint.
        </p>
      </section>
    );
  }

  if (status === 'error') {
    return (
      <section className={styles.section} role="alert">
        <div className={styles.errorBanner}>
          <p className={styles.errorTitle}>Scan failed</p>
          <p className={styles.errorMessage}>{error || 'An unexpected error occurred.'}</p>
        </div>
      </section>
    );
  }

  if (status === 'success') {
    const carbon = wastedStorageBytes
      ? formatCarbonImpact(wastedStorageBytes)
      : null;
    return (
      <section className={styles.section} aria-live="polite">
        <div className={styles.successBanner}>
          <p className={styles.successMessage}>
            Scan completed successfully.
            {carbon && (
              <span className={styles.carbonHint}>
                Removing duplicates could save {carbon.primary}
                {carbon.equivalence && ` (${carbon.equivalence})`}.
              </span>
            )}
            {scannedPath && (
              <span className={styles.scannedPath}> Scanned: {scannedPath}</span>
            )}
          </p>
        </div>
      </section>
    );
  }

  return null;
}
