import { useState, useCallback } from 'react';
import styles from './SegregatorPage.module.css';
import ScanInputSection from '../ScanInputSection/ScanInputSection';
import IntelligentUsageReport from '../IntelligentUsageReport/IntelligentUsageReport';
import { fetchIntelligentUsage } from '../../api/intelligentUsageApi';
import InfoTooltip from '../InfoTooltip/InfoTooltip';

/**
 * SegregatorPage - File segregation and organization
 * Displays intelligent file scanning with categorization and cold data insights
 */
export default function SegregatorPage() {
  const [isScanning, setIsScanning] = useState(false);
  const [intelligentUsageReport, setIntelligentUsageReport] = useState(null);
  const [intelligentUsageLoading, setIntelligentUsageLoading] = useState(false);
  const [intelligentUsageError, setIntelligentUsageError] = useState(null);

  const handleScan = useCallback(async (path) => {
    setIsScanning(true);
    setIntelligentUsageLoading(true);
    setIntelligentUsageError(null);
    setIntelligentUsageReport(null);

    try {
      const data = await fetchIntelligentUsage(path);
      console.log("INTELLIGENT USAGE DATA:", data);
      setIntelligentUsageReport(data);
    } catch (err) {
      console.error(err);
      setIntelligentUsageError(err.message || 'Failed to load report');
    } finally {
      setIsScanning(false);
      setIntelligentUsageLoading(false);
    }
  }, []);

  return (
    <div className={styles.page} role="tabpanel" id="segregator-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>
          File Segregator
          <InfoTooltip text="Organize files by type, date, or size for better storage management" />
        </h2>
        <p className={styles.description}>
          Automatically organize and segregate files based on type, date, size, and usage patterns.
        </p>
      </div>

      <div className={styles.content}>
        {/* Scan Input Section */}
        <section className={styles.scanSection} aria-label="Select folder to scan">
          <ScanInputSection onScan={handleScan} isScanning={isScanning} />
        </section>

        {/* Results Section */}
        {(intelligentUsageReport || intelligentUsageLoading || intelligentUsageError) && (
          <section className={styles.results} aria-label="Segregation report">
            {intelligentUsageLoading && (
              <div className={styles.loadingMessage}>
                Loading intelligent usage analysis...
              </div>
            )}
            {intelligentUsageError && (
              <div className={styles.errorMessage}>
                Error: {intelligentUsageError}
              </div>
            )}
            <IntelligentUsageReport report={intelligentUsageReport} />
          </section>
        )}

        {/* Placeholder when no scan has been performed */}
        {!intelligentUsageReport && !intelligentUsageLoading && !intelligentUsageError && (
          <div className={styles.placeholder}>
            <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
              <path d="M9 13h6" />
              <path d="M12 10v6" />
            </svg>
            <h3 className={styles.placeholderTitle}>Ready to Segregate</h3>
            <p className={styles.placeholderText}>
              Select a folder above to analyze and organize your files into logical groups. 
              We'll help you understand file usage patterns and identify cleanup opportunities.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
