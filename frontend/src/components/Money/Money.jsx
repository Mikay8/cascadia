import { formatMoney, isNegativeMoney } from '../../lib/money.js';
import styles from './Money.module.css';

/**
 * Displays a money string from the API: two decimals, separators, tabular figures, negatives in
 * parentheses. It formats only; it never calculates (hard rule 2).
 */
export default function Money({ value, size = 'body', strong = false }) {
  const text = formatMoney(value);
  const className = `${styles.money} ${styles[size]} ${strong ? styles.strong : ''}`;

  if (!isNegativeMoney(value)) return <span className={className}>{text}</span>;

  // Screen readers often skip parentheses, so say "minus" out loud.
  return (
    <span className={className}>
      <span aria-hidden="true">{text}</span>
      <span className={styles.srOnly}>minus {text.slice(1, -1)}</span>
    </span>
  );
}
