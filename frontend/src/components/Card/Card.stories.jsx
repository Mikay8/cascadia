import Money from '../Money/Money.jsx';
import Card from './Card.jsx';

export default {
  title: 'Components/Card',
  component: Card,
};

export const ClassCard = {
  name: 'Capital stack class',
  render: () => (
    <div style={{ maxWidth: '360px' }}>
      <Card>
        <strong style={{ fontSize: 'var(--cs-type-section-size)' }}>Class A</strong>
        <Money value="5000000.00" size="kpi" />
        <span style={{ fontSize: 'var(--cs-type-small-size)' }}>
          Senior debt · Target rate 3.00% · Payout 1st · Loss 3rd
        </span>
      </Card>
    </div>
  ),
};

export const Empty = {
  render: () => (
    <div style={{ maxWidth: '360px' }}>
      <Card>
        <span style={{ color: 'var(--cs-muted)' }}>No classes yet</span>
      </Card>
    </div>
  ),
};
