import { useEffect, useState } from 'react';

import { Banner, Button, Card, DataTable, Money, StatusBadge } from '../../components/index.js';
import { ApiError, api } from '../../lib/api.js';
import styles from './FundDetail.module.css';

/** API loan statuses mapped onto the design-system loan status family. */
const LOAN_STATUS = {
  current: 'current',
  delinquent: 'late90',
  defaulted: 'default',
  paid_off: 'paidOff',
};

/** One fund: share classes in rank order with commitments, plus the loan book. */
export default function FundDetail({ fundId, onBack }) {
  const [fund, setFund] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setFund(null);
    setError('');
    api
      .fund(fundId)
      .then((data) => {
        if (!cancelled) setFund(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Something went wrong.');
      });
    return () => {
      cancelled = true;
    };
  }, [fundId]);

  const loanColumns = [
    { key: 'borrower', header: 'Borrower' },
    {
      key: 'status',
      header: 'Status',
      render: (row) => <StatusBadge family="loan" status={LOAN_STATUS[row.status] ?? 'current'} />,
    },
    {
      key: 'principal',
      header: 'Principal',
      align: 'end',
      render: (row) => <Money value={row.principal} />,
    },
    {
      key: 'outstanding_balance',
      header: 'Outstanding',
      align: 'end',
      render: (row) => <Money value={row.outstanding_balance} />,
    },
  ];

  return (
    <div className={styles.page}>
      <Button variant="ghost" onClick={onBack}>
        ← All funds
      </Button>
      {error ? (
        <Banner variant="error" title="Could not load the fund">
          {error}
        </Banner>
      ) : null}
      {fund ? (
        <>
          <h2 className={styles.title}>{fund.name}</h2>
          <p className={styles.meta}>
            Vintage {fund.vintage_year ?? 'None'} · {fund.status === 'open' ? 'Open' : 'Closed'}
          </p>
          <h3 className={styles.section}>Share classes</h3>
          <div className={styles.classes}>
            {fund.share_classes.map((cls) => (
              <Card key={cls.id}>
                <h4 className={styles.className}>
                  {cls.name} <span className={styles.rank}>rank {cls.rank}</span>
                </h4>
                {cls.commitments.length === 0 ? (
                  <p className={styles.muted}>No commitments.</p>
                ) : (
                  <ul className={styles.commitments}>
                    {cls.commitments.map((c, i) => (
                      <li key={i} className={styles.commitment}>
                        <span>{c.investor_name}</span>
                        <Money value={c.amount} strong />
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            ))}
          </div>
          <h3 className={styles.section}>Loans</h3>
          <DataTable
            caption="Loans"
            columns={loanColumns}
            rows={fund.loans}
            empty="No loans in this fund"
          />
        </>
      ) : !error ? (
        <p className={styles.muted}>Loading…</p>
      ) : null}
    </div>
  );
}
