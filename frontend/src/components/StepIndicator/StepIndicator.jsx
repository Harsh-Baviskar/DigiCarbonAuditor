import styles from './StepIndicator.module.css';

/**
 * StepIndicator - Guided flow: Select → Scan → Review.
 * Reduces cognitive load by showing users where they are in the process.
 * Current step highlighted; completed steps marked for confidence.
 */
const STEPS = [
  { id: 1, label: 'Select storage', shortLabel: 'Select' },
  { id: 2, label: 'Run scan', shortLabel: 'Scan' },
  { id: 3, label: 'Review results', shortLabel: 'Review' },
];

export default function StepIndicator({ currentStep }) {
  return (
    <nav
      className={styles.nav}
      aria-label="Progress"
      role="navigation"
    >
      <ol className={styles.list}>
        {STEPS.map((step) => {
          const isActive = step.id === currentStep;
          const isComplete = step.id < currentStep;
          return (
            <li
              key={step.id}
              className={`${styles.step} ${isActive ? styles.active : ''} ${isComplete ? styles.complete : ''}`}
              aria-current={isActive ? 'step' : undefined}
            >
              <span className={styles.number} aria-hidden="true">
                {isComplete ? '✓' : step.id}
              </span>
              <span className={styles.label}>{step.label}</span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
