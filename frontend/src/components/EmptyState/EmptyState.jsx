import styles from './EmptyState.module.css';

/**
 * Explains why there is nothing here and what to do next. Also used for "permission denied" on
 * a direct link: say who the user is signed in as and whom to ask, then link somewhere useful.
 */
export default function EmptyState({ title, children, action, headingLevel = 2 }) {
  const Heading = `h${headingLevel}`;

  return (
    <div className={styles.empty}>
      <Heading className={styles.title}>{title}</Heading>
      {children ? <p className={styles.body}>{children}</p> : null}
      {action}
    </div>
  );
}
