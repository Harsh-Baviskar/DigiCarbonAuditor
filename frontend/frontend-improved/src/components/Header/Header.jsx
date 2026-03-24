import styles from './Header.module.css';
import headerBg from '../../assets/carbon-header-bg.jpg';
import TrustBadges from '../TrustBadges/TrustBadges';
import ThemeToggle from '../ThemeToggle/ThemeToggle';

/**
 * Header - Refined application header
 * Clean, professional design with subtle depth
 */
export default function Header() {
  return (
    <header
      className={styles.header}
      role="banner"
      style={{ 
        backgroundImage: `linear-gradient(135deg, rgba(29, 53, 41, 0.92) 0%, rgba(15, 38, 28, 0.95) 100%), url(${headerBg})` 
      }}
    >
      <div className={styles.container}>
        <div className={styles.topRow}>
          <div className={styles.branding}>
            {/* Refined leaf icon */}
            <div className={styles.logoWrapper}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className={styles.logo}
                aria-hidden="true"
              >
                <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.67C7.52 17.35 9.43 12 17 10zm-5 0C4 10 1.9 16.17-0.18 21.34l1.89.67C3.52 17.35 5.43 12 12 10zm3-2c0 1.1.9 2 2 2s2-.9 2-2-.9-2-2-2-2 .9-2 2z"/>
              </svg>
            </div>

            {/* Application branding */}
            <div className={styles.brandContent}>
              <h1 className={styles.appName}>Digital Carbon Auditor</h1>
              <p className={styles.tagline}>Measure • Understand • Reduce</p>
            </div>
          </div>
          
          <div className={styles.actions}>
            <ThemeToggle />
          </div>
        </div>

        {/* Trust badges */}
        <TrustBadges />
      </div>
    </header>
  );
}
