import { useState } from 'react';
import styles from './Navigation.module.css';

const NAV_ITEMS = [
  { id: 'carbon-footprint', label: 'Carbon Footprint Estimator' },
  { id: 'wasteful-files', label: 'Wasteful Files Detector' },
  { id: 'segregator', label: 'Segregator' },
  { id: 'google-drive', label: 'Upload Google Drive' },
];

export default function Navigation({ activeSection, onSectionChange }) {
  return (
    <nav className={styles.navigation} role="navigation" aria-label="Main navigation">
      <div className={styles.container}>
        <ul className={styles.navList} role="tablist">
          {NAV_ITEMS.map((item) => (
            <li key={item.id} role="presentation">
              <button
                className={`${styles.navButton} ${activeSection === item.id ? styles.active : ''}`}
                onClick={() => onSectionChange(item.id)}
                role="tab"
                aria-selected={activeSection === item.id}
                aria-controls={`${item.id}-panel`}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
