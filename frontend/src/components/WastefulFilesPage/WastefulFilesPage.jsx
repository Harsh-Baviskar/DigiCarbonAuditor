import styles from './WastefulFilesPage.module.css';
import InfoTooltip from '../InfoTooltip/InfoTooltip';

export default function WastefulFilesPage() {
  return (
    <div className={styles.page} role="tabpanel" id="wasteful-files-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>
          Wasteful Files Detector
          <InfoTooltip text="Identify large, old, or unused files that waste storage space" />
        </h2>
        <p className={styles.description}>
          Coming soon: Detect files that are consuming unnecessary storage—large media files, temporary files, old downloads, and more.
        </p>
      </div>

      <div className={styles.content}>
        <div className={styles.placeholder}>
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            <path d="M10 11v6" />
            <path d="M14 11v6" />
          </svg>
          <h3 className={styles.placeholderTitle}>Feature Under Development</h3>
          <p className={styles.placeholderText}>
            This feature will identify files that haven't been accessed in a long time, temporary files, and other space-wasting content to help you clean up efficiently.
          </p>
        </div>
      </div>
    </div>
  );
}
