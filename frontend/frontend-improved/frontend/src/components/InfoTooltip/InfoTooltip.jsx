import { useState, useRef, useEffect } from 'react';
import styles from './InfoTooltip.module.css';

/**
 * InfoTooltip - Contextual help for data confidence and transparency.
 * Provides short technical explanations on hover/focus without cluttering the UI.
 */
export default function InfoTooltip({ content, label = 'More information' }) {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState('bottom');
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);

  const show = () => setVisible(true);
  const hide = () => setVisible(false);

  // Position tooltip above if near bottom of viewport (progressive enhancement)
  useEffect(() => {
    if (!visible || !triggerRef.current || !tooltipRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const spaceBelow = window.innerHeight - rect.bottom;
    setPosition(spaceBelow < tooltipRect.height + 8 ? 'top' : 'bottom');
  }, [visible]);

  return (
    <span className={styles.wrapper}>
      <button
        ref={triggerRef}
        type="button"
        className={styles.trigger}
        aria-label={label}
        aria-describedby={visible ? 'tooltip-content' : undefined}
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
      >
        <InfoIcon />
      </button>
      {visible && (
        <div
          ref={tooltipRef}
          id="tooltip-content"
          role="tooltip"
          className={`${styles.tooltip} ${styles[position]}`}
          onMouseEnter={show}
          onMouseLeave={hide}
        >
          {content}
        </div>
      )}
    </span>
  );
}

function InfoIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M12 16v-4M12 8h.01" />
    </svg>
  );
}
