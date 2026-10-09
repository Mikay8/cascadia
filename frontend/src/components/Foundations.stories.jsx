// Token reference for design review. Switch Light and Dark in the toolbar to compare modes.

const ROLES = [
  ['--cs-bg', 'Page ground'],
  ['--cs-surface', 'Nav, panels, table headers'],
  ['--cs-raised', 'Inputs, drawers'],
  ['--cs-text', 'Ink'],
  ['--cs-muted', 'Metadata, labels'],
  ['--cs-rule', 'Row rules, bar tracks'],
  ['--cs-link', 'Links and ghost buttons'],
  ['--cs-primary', 'Primary button, focus ring'],
  ['--cs-primary-hover', 'Primary hover'],
  ['--cs-on-primary', 'Text on primary'],
  ['--cs-payout', 'Payout cascade fill'],
  ['--cs-payout-tint', 'Payout tiers, positive badges'],
  ['--cs-payout-ink', 'Text on payout tint'],
  ['--cs-loss', 'Loss cascade fill'],
  ['--cs-loss-tint', 'Loss tiers, alerts, failed checks'],
  ['--cs-loss-ink', 'Text on loss tint'],
  ['--cs-neutral-tint', 'Added: neutral badges, info banners'],
  ['--cs-loss-strong', 'Added: last-hour support banner'],
  ['--cs-on-loss-strong', 'Added: text on loss strong'],
  ['--cs-inverse', 'Added: Default badge, markers'],
  ['--cs-on-inverse', 'Added: text on inverse'],
];

const TYPE = [
  ['page', 'Page title', 'Waterfall runs'],
  ['section', 'Section', 'Per class'],
  ['panel', 'Panel', 'Reconciliation checks'],
  ['kpi', 'KPI figure', '$412,350.00'],
  ['body', 'Body and table', 'Each run allocates one period of settled cash.'],
  ['small', 'Small', 'Settled, Q3 2026 · as of Sep 30'],
  ['overline', 'Overline', 'TABLE HEADER'],
];

const SPACE = [1, 2, 3, 4, 5, 6, 7, 8];

export default { title: 'Foundations/Tokens' };

export const Colors = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-1)' }}>
      <p style={{ margin: 0, color: 'var(--cs-muted)' }}>
        Ramp values are placeholders until Broadsheet is exported. Roles are final.
      </p>
      {ROLES.map(([name, use]) => (
        <div key={name} style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          <span
            style={{
              width: 'var(--space-7)',
              height: 'var(--space-5)',
              flex: 'none',
              background: `var(${name})`,
              boxShadow: 'inset 0 0 0 1px var(--cs-rule)',
            }}
          />
          <code style={{ width: '22ch' }}>{name}</code>
          <span style={{ color: 'var(--cs-muted)' }}>{use}</span>
        </div>
      ))}
    </div>
  ),
};

export const Typography = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-3)' }}>
      {TYPE.map(([key, role, sample]) => (
        <div key={key} style={{ display: 'grid', gridTemplateColumns: '16ch 1fr', alignItems: 'baseline' }}>
          <span style={{ color: 'var(--cs-muted)', fontSize: 'var(--cs-type-small-size)' }}>{role}</span>
          <span
            style={{
              fontSize: `var(--cs-type-${key}-size)`,
              lineHeight: `var(--cs-type-${key}-line)`,
              fontWeight: ['body', 'small', 'overline'].includes(key)
                ? 'var(--cs-weight-regular)'
                : 'var(--cs-weight-bold)',
              letterSpacing: key === 'overline' ? 'var(--cs-type-overline-tracking)' : undefined,
            }}
          >
            {sample}
          </span>
        </div>
      ))}
    </div>
  ),
};

export const InvestorPortalTypography = {
  name: 'Typography (investor portal)',
  decorators: [
    (Story) => (
      <div data-audience="portal">
        <Story />
      </div>
    ),
  ],
  render: Typography.render,
};

export const Spacing = {
  render: () => (
    <div style={{ display: 'grid', gap: 'var(--space-2)' }}>
      {SPACE.map((step) => (
        <div key={step} style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          <code style={{ width: '10ch' }}>--space-{step}</code>
          <span style={{ width: `var(--space-${step})`, height: 'var(--space-3)', background: 'var(--cs-payout)' }} />
        </div>
      ))}
    </div>
  ),
};
