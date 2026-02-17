import styles from './GoogleDrivePage.module.css';

export default function GoogleDrivePage() {
  return (
    <div className={styles.page} role="tabpanel" id="google-drive-panel">
      <div className={styles.header}>
        <h2 className={styles.title}>Upload Google Drive</h2>
        <p className={styles.description}>
          Connect your Google Drive to analyze cloud storage carbon footprint and identify wasteful files stored in the cloud.
        </p>
      </div>

      <div className={styles.content}>
        <div className={styles.placeholder}>
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L4.5 12.5l3.5 6h8l3.5-6L12 2z" />
            <path d="M4.5 12.5h15" />
            <path d="M16 18.5L12 2" />
            <path d="M8 18.5L12 2" />
          </svg>
          <h3 className={styles.placeholderTitle}>Feature Under Development</h3>
          <p className={styles.placeholderText}>
            This feature will allow you to connect your Google Drive account, scan cloud-stored files, and estimate the carbon impact of your cloud storage usage.
          </p>
        </div>
      </div>
    </div>
  );
}
