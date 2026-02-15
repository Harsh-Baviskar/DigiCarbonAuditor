import InfoTooltip from '../InfoTooltip/InfoTooltip';
import styles from './SuggestedActions.module.css';

/**
 * SuggestedActions - Decision support: ranked actions by impact with confidence labels.
 * Safe = exact hash match, low risk. Review Needed = requires human verification.
 */
export default function SuggestedActions({ suggestedActions }) {
  if (!suggestedActions || suggestedActions.length === 0) return null;

  return (
    <section className={styles.section} aria-labelledby="actions-heading">
      <h2 id="actions-heading" className={styles.heading}>
        Suggested Actions
        <InfoTooltip
          content="Actions ranked by potential storage saved. Safe = exact duplicates (hash match). Review Needed = verify before removal."
          label="How suggested actions work"
        />
      </h2>
      <ol className={styles.list} role="list">
        {suggestedActions.map((item) => (
          <li key={item.id} className={styles.item}>
            <div className={styles.itemHeader}>
              <span className={styles.impact}>{item.impactLabel}</span>
              <span
                className={`${styles.badge} ${item.type === 'safe' ? styles.badgeSafe : styles.badgeReview}`}
                title={item.reason}
              >
                {item.type === 'safe' ? 'Safe' : 'Review needed'}
              </span>
            </div>
            <p className={styles.action}>{item.action}</p>
            {item.reason && (
              <p className={styles.reason} title={item.reason}>
                {item.reason}
              </p>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
