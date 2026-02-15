import WhyThisMatters from '../WhyThisMatters/WhyThisMatters';
import TrustBadges from '../TrustBadges/TrustBadges';
import styles from './Layout.module.css';

/**
 * Layout - Page-level wrapper with value communication and trust cues.
 * WhyThisMatters answers "What do I gain?"; TrustBadges address privacy concerns.
 */
export default function Layout({ children }) {
  return (
    <div className={styles.wrapper}>
      <header className={styles.header}>
        <div className={styles.headerTop}>
          <div>
            <h1 className={styles.title}>Digital Carbon Auditor</h1>
            <p className={styles.subtitle}>
              Estimate carbon footprint and identify duplicate storage
            </p>
          </div>
          <WhyThisMatters />
        </div>
        <TrustBadges />
      </header>
      <main className={styles.main} id="main-content">
        {children}
      </main>
    </div>
  );
}
