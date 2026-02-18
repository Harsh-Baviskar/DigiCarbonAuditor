import styles from './Header.module.css';
import headerBg from '../../assets/carbon-header-bg.jpg';
import TrustBadges from '../TrustBadges/TrustBadges';
import ThemeToggle from '../ThemeToggle/ThemeToggle';

/**
 * Header - Persistent application header
 * Professional, minimal design with app branding
 */
export default function Header() {
  return (
    <header
      className={styles.header}
      role="banner"
      style={{ backgroundImage: `linear-gradient(135deg, rgba(15, 29, 29, 0.5) 0%, rgba(9, 38, 53, 0.65) 100%), url(${headerBg})` }}
    >
      <div className={styles.container}>
        <div className={styles.topRow}>
          <div className={styles.branding}>
            {/* App logo/icon - sustainability symbol */}
            <div className={styles.logo} aria-hidden="true">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 16 16"
                fill="currentColor"
                className={styles.icon}
              >
                <path d="M1.4 1.7c.217.289.65.84 1.725 1.274 1.093.44 2.885.774 5.834.528 2.02-.168 3.431.51 4.326 1.556C14.161 6.082 14.5 7.41 14.5 8.5q0 .344-.027.734C13.387 8.252 11.877 7.76 10.39 7.5c-2.016-.288-4.188-.445-5.59-2.045-.142-.162-.402-.102-.379.112.108.985 1.104 1.82 1.844 2.308 2.37 1.566 5.772-.118 7.6 3.071.505.8 1.374 2.7 1.75 4.292.07.298-.066.611-.354.715a.7.7 0 0 1-.161.042 1 1 0 0 1-1.08-.794c-.13-.97-.396-1.913-.868-2.77C12.173 13.386 10.565 14 8 14c-1.854 0-3.32-.544-4.45-1.435-1.124-.887-1.889-2.095-2.39-3.383-1-2.562-1-5.536-.65-7.28L.73.806z" />
              </svg>
            </div>

            {/* Application name and tagline */}
            <div>
              <h1 className={styles.appName}>Digital Carbon Auditor</h1>
              <p className={styles.tagline}>Measure and reduce your digital footprint</p>
            </div>
          </div>
          <ThemeToggle />
        </div>

        {/* Trust badges */}
        <div className={styles.badgesWrapper}>
          <TrustBadges />
        </div>
      </div>
    </header>
  );
}
