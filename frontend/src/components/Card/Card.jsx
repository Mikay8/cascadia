import styles from './Card.module.css';

/** A bordered panel on the page ground. Base for KPI tiles and capital-stack class cards. */
export default function Card({ as: Tag = 'section', children, ...rest }) {
  return (
    <Tag className={styles.card} {...rest}>
      {children}
    </Tag>
  );
}
