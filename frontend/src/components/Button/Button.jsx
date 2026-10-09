import { useId } from 'react';

import styles from './Button.module.css';

/**
 * Primary, secondary, or ghost button.
 *
 * Own-work rule from the handoff: when an action exists but this user may not take it (for
 * example approving their own change), show it disabled with `disabledReason`, never hidden.
 * The back end enforces the rule; this only explains it.
 */
export default function Button({
  variant = 'secondary',
  type = 'button',
  disabled = false,
  disabledReason,
  busy = false,
  children,
  ...rest
}) {
  const reasonId = useId();
  const showReason = disabled && disabledReason;

  const button = (
    <button
      type={type}
      className={`${styles.button} ${styles[variant]}`}
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      aria-describedby={showReason ? reasonId : undefined}
      {...rest}
    >
      {busy ? <span className={styles.spinner} aria-hidden="true" /> : null}
      {children}
    </button>
  );

  if (!showReason) return button;

  return (
    <span className={styles.withReason}>
      {button}
      <span id={reasonId} className={styles.reason}>
        {disabledReason}
      </span>
    </span>
  );
}
