import styles from './StatusBadge.module.css';
import { STATUSES } from './statuses.js';

/** The shared status badge. Use it for every status; never show status by color alone. */
export default function StatusBadge({ family, status }) {
  const known = STATUSES[family]?.[status];

  if (!known) {
    // An unknown status is a contract mismatch with the API. Show it plainly rather than guess.
    console.error(`StatusBadge: unknown status "${status}" in family "${family}"`);
    return (
      <span className={`${styles.badge} ${styles.outline}`}>
        <span aria-hidden="true">?</span> {String(status)}
      </span>
    );
  }

  return (
    <span className={`${styles.badge} ${styles[known.tone]}`}>
      {known.glyph ? <span aria-hidden="true">{known.glyph}</span> : null}
      {known.label}
    </span>
  );
}
