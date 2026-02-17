import styles from './SegregatorPage.module.css';
import InfoTooltip from '../InfoTooltip/InfoTooltip';

export default function SegregatorPage() {
  return (
    <div className={styles.page} role="tabpanel" id="segregator-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>
          File Segregator
          <InfoTooltip text="Organize files by type, date, or size for better storage management" />
        </h2>
        <p className={styles.description}>
          Coming soon: Automatically organize and segregate files based on type, date, size, and usage patterns.
        </p>
      </div>

      <div className={styles.content}>
        <div className={styles.placeholder}>
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
            <path d="M9 13h6" />
            <path d="M12 10v6" />
          </svg>
          <h3 className={styles.placeholderTitle}>Feature Under Development</h3>
          <p className={styles.placeholderText}>
            This feature will help you organize files into logical groups, making it easier to manage storage and identify cleanup opportunities.
          </p>
        </div>
      </div>
    </div>
  );
}
