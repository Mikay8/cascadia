import styles from './DataTable.module.css';

/**
 * Data table with a sticky header. Money and count columns set `align: 'end'` so figures line up.
 *
 * columns: [{ key, header, align?: 'start' | 'end', render?: (row) => node }]
 * rows: objects with a unique `id`
 * `loading` shows skeleton rows; `empty` is shown when there are no rows (usually an EmptyState).
 * Row actions go in the last column: a History link, then an overflow menu.
 */
export default function DataTable({
  caption,
  columns,
  rows = [],
  loading = false,
  loadingRows = 3,
  empty = 'Nothing to show',
}) {
  const alignClass = (column) => (column.align === 'end' ? styles.end : '');

  let body;
  if (loading) {
    body = Array.from({ length: loadingRows }, (_, index) => (
      <tr key={`loading-${index}`} aria-hidden="true">
        {columns.map((column) => (
          <td key={column.key}>
            <span className={styles.skeleton} />
          </td>
        ))}
      </tr>
    ));
  } else if (rows.length === 0) {
    body = (
      <tr>
        <td colSpan={columns.length} className={styles.emptyCell}>
          {empty}
        </td>
      </tr>
    );
  } else {
    body = rows.map((row) => (
      <tr key={row.id}>
        {columns.map((column) => (
          <td key={column.key} className={alignClass(column)}>
            {column.render ? column.render(row) : row[column.key]}
          </td>
        ))}
      </tr>
    ));
  }

  return (
    <table className={styles.table} aria-busy={loading || undefined}>
      {caption ? <caption className={styles.caption}>{caption}</caption> : null}
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column.key} scope="col" className={alignClass(column)}>
              {column.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>{body}</tbody>
    </table>
  );
}
