import Header from '../Header/Header';
import Navigation from '../Navigation/Navigation';
import WhyThisMatters from '../WhyThisMatters/WhyThisMatters';
import whyThisMattersImg from '../../assets/whythismatter.jpg';
import styles from './Layout.module.css';

/**
 * Layout - Professional page structure following standard web conventions
 *
 * Structure:
 * 1. Header - Persistent branding at top
 * 2. Navigation - Main section navigation
 * 3. Intro Section - Value proposition and trust signals (context before action)
 * 4. Main Content - Primary user workflow (folder selection → scan → results)
 * 5. Footer - Minimal credits and context
 *
 * Uses semantic HTML for accessibility and SEO
 */
export default function Layout({ children, activeSection, onSectionChange }) {
  return (
    <div className={styles.pageWrapper}>
      {/* 1. Professional header - persistent at top */}
      <Header />

      {/* 2. Navigation bar - section switching */}
      <Navigation activeSection={activeSection} onSectionChange={onSectionChange} />

      {/* 3. Main content area */}
      <div className={styles.contentWrapper}>
        <div className={styles.container}>
          <main id="main-content" role="main">
            {children}
          </main>
        </div>
      </div>

      {/* 4. Why this matters section - above footer */}
      <section className={styles.whySection}>
        <div className={styles.whyLayout}>
          <div className={styles.whyText}>
            <WhyThisMatters />
          </div>
          <div className={styles.whyImage}>
            <img 
              src={whyThisMattersImg} 
              alt="Why digital carbon auditing matters" 
              className={styles.whyImg}
            />
          </div>
        </div>
      </section>

      {/* 5. Footer - lightweight, unobtrusive */}
      <footer className={styles.footer} role="contentinfo">
        <div className={styles.container}>
          <p className={styles.footerText}>
            Digital Carbon Auditor · Helping reduce digital environmental impact
          </p>
        </div>
      </footer>
    </div>
  );
}
