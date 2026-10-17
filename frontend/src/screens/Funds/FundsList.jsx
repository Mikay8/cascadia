import { useEffect, useState } from 'react';

import { Banner, Card, DataTable, EmptyState } from '../../components/index.js';
import { ApiError, api } from '../../lib/api.js';
import styles from './FundsList.module.css';

/** Lists the tenant's funds. Calls onSelect(fundId) when one is picked. */
export default function FundsList({ onSelect }) {
  const [funds, setFunds] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    api
      .funds()
      .then((data) => {
        if (!cancelled) setFunds(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Something went wrong.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const columns = [
    { key: 'name', header: 'Fund' },
    { key: 'vintage_year', header: 'Vintage', render: (row) => row.vintage_year ?? 'None' },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (row.status === 'open' ? 'Open' : 'Closed'),
    },
    {
      key: 'actions',
      header: 'Details',
      align: 'end',
      render: (row) => (
        <button type="button" className={styles.link} onClick={() => onSelect(row.id)}>
          Open
        </button>
      ),
    },
  ];

  return (
    <div className={styles.page}>
      <h2 className={styles.title}>Funds</h2>
      {error ? (
        <Banner variant="error" title="Could not load funds">
          {error}
        </Banner>
      ) : null}
      {funds !== null && funds.length === 0 && !error ? (
        <Card>
          <EmptyState title="No funds yet">This tenant has no funds in the demo data.</EmptyState>
        </Card>
      ) : (
        <DataTable
          caption="Funds"
          columns={columns}
          rows={funds ?? []}
          loading={funds === null && !error}
          empty="No funds"
        />
      )}
    </div>
  );
}
