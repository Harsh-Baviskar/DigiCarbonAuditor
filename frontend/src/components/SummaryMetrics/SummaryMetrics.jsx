import { formatBytes, formatCarbonImpact } from '../../utils/formatters';
import InfoTooltip from '../InfoTooltip/InfoTooltip';
import styles from './SummaryMetrics.module.css';

/**
 * Summary Metrics - Key statistics displayed as simple cards.
 * Carbon impact shown for wasted storage to communicate environmental cost intuitively.
 */
export default function SummaryMetrics({ summary }) {
  if (!summary) return null;

  const wastedCarbon = formatCarbonImpact(summary.wastedStorageBytes);

  const metrics = [
    {
      label: 'Total files scanned',
      value: summary.totalFiles.toLocaleString(),
      subtext: null,
      tooltip: null,
    },
    {
      label: 'Total storage size',
      value: formatBytes(summary.totalStorageBytes),
      subtext: null,
      tooltip: null,
    },
    {
      label: 'Duplicate files',
      value: summary.duplicateFilesCount.toLocaleString(),
      subtext: null,
      tooltip:
        'Exact duplicates identified via cryptographic hash (SHA-256). Same content, different paths.',
    },
    {
      label: 'Wasted storage (duplication)',
      value: formatBytes(summary.wastedStorageBytes),
      subtext: wastedCarbon
        ? { primary: wastedCarbon.primary, equivalence: wastedCarbon.equivalence }
        : null,
      tooltip:
        'Storage occupied by duplicate copies. Estimated carbon based on typical data center energy use (~0.2 kg CO₂e per GB-year).',
    },
  ];

  return (
    <section className={styles.section} aria-labelledby="metrics-heading">
      <h2 id="metrics-heading" className={styles.heading}>
        Summary
      </h2>
      <div className={styles.grid} role="list">
        {metrics.map(({ label, value, subtext, tooltip }) => (
          <article
            key={label}
            className={styles.card}
            role="listitem"
          >
            <span className={styles.value}>{value}</span>
            {subtext && (
              <span className={styles.carbonImpact} title={subtext.equivalence}>
                {subtext.primary}
                {subtext.equivalence && (
                  <span className={styles.equivalence}> · {subtext.equivalence}</span>
                )}
              </span>
            )}
            <span className={styles.labelWrapper}>
              <span className={styles.label}>{label}</span>
              {tooltip && (
                <InfoTooltip
                  content={tooltip}
                  label={`${label}: more info`}
                />
              )}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}
