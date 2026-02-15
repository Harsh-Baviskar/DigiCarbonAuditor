import { useState } from 'react';
import { formatBytes, truncateHash } from '../../utils/formatters';
import InfoTooltip from '../InfoTooltip/InfoTooltip';
import styles from './DuplicateFilesView.module.css';

/**
 * Duplicate Files View - Grouped list of duplicate file clusters.
 * Hash, size, duplicate count, and collapsible paths. Progressive disclosure: expand for details.
 */
function DuplicateGroup({ group, index }) {
  const [expanded, setExpanded] = useState(false);
  const paths = group.paths || [];
  const showAll = expanded || paths.length <= 3;
  const visiblePaths = showAll ? paths : paths.slice(0, 3);
  const hasMore = paths.length > 3 && !expanded;

  return (
    <article className={styles.group} aria-labelledby={`group-${index}-heading`}>
      <header className={styles.groupHeader}>
        <div className={styles.groupMeta}>
          <span id={`group-${index}-heading`} className={styles.hash} title={group.hash}>
            {truncateHash(group.hash, 36)}
          </span>
          <span className={styles.size}>{formatBytes(group.fileSizeBytes)}</span>
          <span className={styles.duplicateCount}>
            {group.duplicateCount} duplicate{group.duplicateCount !== 1 ? 's' : ''}
          </span>
        </div>
      </header>
      <div className={styles.pathsContainer}>
        <ul className={styles.pathList} role="list">
          {visiblePaths.map((path, i) => (
            <li key={i} className={styles.pathItem}>
              <code className={styles.path}>{path}</code>
            </li>
          ))}
        </ul>
        {hasMore && (
          <button
            type="button"
            onClick={() => setExpanded(true)}
            className={styles.expandButton}
            aria-expanded={expanded}
            aria-label={`Show ${paths.length - 3} more paths`}
          >
            Show {paths.length - 3} more…
          </button>
        )}
      </div>
    </article>
  );
}

export default function DuplicateFilesView({ duplicateGroups }) {
  const [sectionExpanded, setSectionExpanded] = useState(true);

  if (!duplicateGroups || duplicateGroups.length === 0) {
    return (
      <section className={styles.section} aria-labelledby="duplicates-heading">
        <h2 id="duplicates-heading" className={styles.heading}>
          Duplicate Files
        </h2>
        <p className={styles.empty}>No duplicate groups to display.</p>
      </section>
    );
  }

  return (
    <section className={styles.section} aria-labelledby="duplicates-heading">
      <header className={styles.sectionHeader}>
        <h2 id="duplicates-heading" className={styles.heading}>
          Duplicate Files
          <InfoTooltip
            content="Exact duplicates detected via SHA-256 hash. Files with identical content. Wasteful data = redundant copies consuming unnecessary storage and energy."
            label="How duplicate detection works"
          />
        </h2>
        <button
          type="button"
          onClick={() => setSectionExpanded(!sectionExpanded)}
          className={styles.toggleButton}
          aria-expanded={sectionExpanded}
          aria-controls="duplicates-content"
        >
          {sectionExpanded ? 'Collapse' : 'Expand'}
        </button>
      </header>
      <div id="duplicates-content" className={styles.list} hidden={!sectionExpanded}>
        {duplicateGroups.map((group, index) => (
          <DuplicateGroup key={group.hash} group={group} index={index} />
        ))}
      </div>
    </section>
  );
}
