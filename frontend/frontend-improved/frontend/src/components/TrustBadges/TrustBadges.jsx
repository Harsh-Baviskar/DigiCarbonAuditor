import styles from './TrustBadges.module.css';

/**
 * TrustBadges - Non-functional requirements visibility for enterprise users.
 * Builds confidence: local processing, read-only, secure detection.
 * Kept minimal to avoid clutter while addressing common concerns.
 */
const BADGES = [
  {
    label: 'Local scan',
    detail: 'No uploads',
  },
  {
    label: 'Read-only',
    detail: 'No changes unless you approve',
  },
  {
    label: 'Hash-based',
    detail: 'Secure duplicate detection',
  },
];

export default function TrustBadges() {
  return (
    <div className={styles.wrapper} role="complementary" aria-label="Privacy and security">
      {BADGES.map(({ label, detail }) => (
        <span key={label} className={styles.badge} title={detail}>
          <span className={styles.label}>{label}</span>
          <span className={styles.detail}>{detail}</span>
        </span>
      ))}
    </div>
  );
}
