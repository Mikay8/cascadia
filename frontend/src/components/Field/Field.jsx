import { useId } from 'react';

import styles from './Field.module.css';

/**
 * Labeled text input or textarea with optional hint and error. The label sits above the
 * control, as in the handoff. Money inputs still send strings; the back end parses them.
 */
export default function Field({ label, hint, error, multiline = false, rows = 3, ...rest }) {
  const id = useId();
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const Control = multiline ? 'textarea' : 'input';

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {label}
      </label>
      <Control
        id={id}
        className={`${styles.control} ${error ? styles.invalid : ''}`}
        aria-invalid={error ? true : undefined}
        aria-describedby={[hintId, errorId].filter(Boolean).join(' ') || undefined}
        rows={multiline ? rows : undefined}
        {...rest}
      />
      {hint ? (
        <span id={hintId} className={styles.hint}>
          {hint}
        </span>
      ) : null}
      {error ? (
        <span id={errorId} className={styles.error}>
          <span aria-hidden="true">▲ </span>
          {error}
        </span>
      ) : null}
    </div>
  );
}
