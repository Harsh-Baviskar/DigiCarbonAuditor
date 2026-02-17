import styles from './WhyThisMatters.module.css';

/**
 * WhyThisMatters - Lightweight value communication for non-technical users.
 * Answers "What do I gain?" without overwhelming. Data-oriented, concise.
 */
const POINTS = [
  {
    title: 'Storage optimization',
    description: '30ΓÇô50% of organizational storage is redundant. Free space without adding hardware.',
  },
  {
    title: 'Carbon reduction',
    description: 'Data centers use 1ΓÇô2% of global electricity. Less waste = lower emissions.',
  },
  {
    title: 'Cost and efficiency',
    description: 'Reduced storage costs, faster backups, and simpler data management.',
  },
];

export default function WhyThisMatters() {
  return (
    <aside className={styles.aside} aria-labelledby="why-heading">
      <h2 id="why-heading" className={styles.heading}>
        Why this matters
      </h2>
      <ul className={styles.list}>
        {POINTS.map(({ title, description }) => (
          <li key={title} className={styles.item}>
            <strong className={styles.title}>{title}</strong>
            <span className={styles.description}>{description}</span>
          </li>
        ))}
      </ul>
    </aside>
  );
}
