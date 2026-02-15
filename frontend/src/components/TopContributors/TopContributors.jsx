import { useState } from 'react';
import { formatBytes } from '../../utils/formatters';
import InfoTooltip from '../InfoTooltip/InfoTooltip';
import styles from './TopContributors.module.css';

const INITIAL_ROWS = 5;

/**
 * TopContributors - Insight-oriented view of what drives storage and duplication.
 * Helps users understand where waste originates. Progressive disclosure: top 5 by default.
 */
export default function TopContributors({ topContributors }) {
  const [expanded, setExpanded] = useState(false);

  if (!topContributors) return null;

  const { byFileType, byFolderDuplication } = topContributors;

  const maxPercent = Math.max(...byFileType.map((f) => f.percentOfTotal), 1);
  const maxWastedBytes = Math.max(...byFolderDuplication.map((f) => f.wastedBytes), 1);
  const showFileTypes = expanded ? byFileType : byFileType.slice(0, INITIAL_ROWS);
  const showFolders = expanded ? byFolderDuplication : byFolderDuplication.slice(0, INITIAL_ROWS);
  const hasMoreFileTypes = byFileType.length > INITIAL_ROWS;
  const hasMoreFolders = byFolderDuplication.length > INITIAL_ROWS;
  const hasMore = hasMoreFileTypes || hasMoreFolders;

  return (
    <section className={styles.section} aria-labelledby="contributors-heading">
      <h2 id="contributors-heading" className={styles.heading}>
        Top Contributors
        <InfoTooltip
          content="File types ranked by storage consumed. Folders ranked by duplicate waste. Helps identify high-impact cleanup targets."
          label="How Top Contributors works"
        />
      </h2>

      <div className={styles.grid}>
        <div className={styles.card}>
          <h3 className={styles.subheading}>By file type (storage)</h3>
          <ul className={styles.list} role="list">
            {showFileTypes.map(({ type, count, sizeBytes, percentOfTotal }) => (
              <li key={type} className={styles.row}>
                <div className={styles.rowHeader}>
                  <span className={styles.type}>{type}</span>
                  <span className={styles.percent}>{percentOfTotal}%</span>
                </div>
                <div className={styles.barTrack}>
                  <div
                    className={styles.barFill}
                    style={{ width: `${(percentOfTotal / maxPercent) * 100}%` }}
                    role="presentation"
                  />
                </div>
                <span className={styles.meta}>
                  {count.toLocaleString()} files · {formatBytes(sizeBytes)}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className={styles.card}>
          <h3 className={styles.subheading}>By folder (duplication)</h3>
          <ul className={styles.list} role="list">
            {showFolders.map(({ folder, duplicateCount, wastedBytes }) => (
              <li key={folder} className={styles.row}>
                <div className={styles.rowHeader}>
                  <code className={styles.folder}>{folder}</code>
                  <span className={styles.wasted}>{formatBytes(wastedBytes)}</span>
                </div>
                <div className={styles.barTrack}>
                  <div
                    className={styles.barFillWaste}
                    style={{ width: `${(wastedBytes / maxWastedBytes) * 100}%` }}
                    role="presentation"
                  />
                </div>
                <span className={styles.meta}>{duplicateCount} duplicate files</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {hasMore && (
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className={styles.expandButton}
          aria-expanded={expanded}
        >
          {expanded ? 'Show less' : 'Show all'}
        </button>
      )}
    </section>
  );
}
