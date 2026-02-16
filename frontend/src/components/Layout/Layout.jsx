import Header from '../Header/Header';
import WhyThisMatters from '../WhyThisMatters/WhyThisMatters';
import styles from './Layout.module.css';

/**
 * Layout - Professional page structure following standard web conventions
 * 
 * Structure:
 * 1. Header - Persistent branding at top
 * 2. Intro Section - Value proposition and trust signals (context before action)
 * 3. Main Content - Primary user workflow (folder selection → scan → results)
 * 4. Footer - Minimal credits and context
 * 
 * Uses semantic HTML for accessibility and SEO
 */
export default function Layout({ children }) {
  return (
    <div className={styles.pageWrapper}>
      {/* 1. Professional header - persistent at top */}
      <Header />

      {/* 2. Two-column layout: sidebar (why) + main content area */}
      <div className={styles.contentWrapper}>
        <div className={styles.container}>
          <div className={styles.twoColumnLayout}>
            {/* Left sidebar: Why this matters */}
            <aside className={styles.sidebar}>
              <WhyThisMatters />
            </aside>

            {/* Right column: Main workflow */}
            <div className={styles.mainColumn}>
              {/* Primary user workflow */}
              <main id="main-content" role="main">
                {children}
              </main>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Footer - lightweight, unobtrusive */}
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
