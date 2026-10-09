import styles from './Banner.module.css';

/**
 * Full-width mode banner that sits above the top bar and cannot be dismissed.
 *
 * Variants from the handoff: `support` (support session active), `supportEnding` (last hour,
 * inverted), `audit` (read-only auditor access), `info` (for example a run in progress), and
 * `error` (for example a failed servicer sync). Put the glyph in `title` (◐, ✕, ▲) so the state
 * never depends on color.
 */
export default function Banner({ variant = 'info', title, children, aside }) {
  const urgent = variant === 'error' || variant === 'supportEnding';

  return (
    <div className={`${styles.banner} ${styles[variant]}`} role={urgent ? 'alert' : 'status'}>
      <strong>{title}</strong>
      {children ? <span>{children}</span> : null}
      {aside ? <span className={styles.aside}>{aside}</span> : null}
    </div>
  );
}
