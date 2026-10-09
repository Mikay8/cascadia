import Card from '../Card/Card.jsx';
import Money from '../Money/Money.jsx';
import styles from './KpiTile.module.css';

/**
 * A headline figure with its label and provenance. `value` is a money string from the API.
 * `action` is usually a "Show calculation" link, since every number must be traceable.
 */
export default function KpiTile({ label, value, caption, action, loading = false }) {
  if (loading) {
    return (
      <Card aria-busy="true" aria-label={`${label}, loading`}>
        <span className={styles.label}>{label}</span>
        <span className={`${styles.skeleton} ${styles.skeletonValue}`} />
        <span className={`${styles.skeleton} ${styles.skeletonCaption}`} />
      </Card>
    );
  }

  return (
    <Card>
      <span className={styles.label}>{label}</span>
      <Money value={value} size="kpi" />
      {caption || action ? (
        <span className={styles.footer}>
          <span className={styles.caption}>{caption}</span>
          {action}
        </span>
      ) : null}
    </Card>
  );
}
