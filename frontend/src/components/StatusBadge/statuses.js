// Status families from the handoff component sheet (wireframes 0a). Every badge pairs a glyph
// with a word so status never depends on color. Same glyph means the same idea across families:
// ● done or healthy, ◐ waiting on someone, ▲ needs attention, ✕ failed.

export const STATUSES = {
  loan: {
    current: { glyph: '●', label: 'Current', tone: 'payout' },
    late30: { glyph: '◔', label: '30–59 late', tone: 'neutral' },
    late60: { glyph: '◑', label: '60–89 late', tone: 'neutral' },
    late90: { glyph: '◕', label: '90+ late', tone: 'loss' },
    default: { glyph: '■', label: 'Default', tone: 'inverse' },
    paidOff: { glyph: '✓', label: 'Paid off', tone: 'outline' },
  },
  settlement: {
    settled: { glyph: '●', label: 'Settled', tone: 'payout' },
    pending: { glyph: '◐', label: 'Pending', tone: 'neutral' },
    reversed: { glyph: '↺', label: 'Reversed', tone: 'outline' },
    disputed: { glyph: '▲', label: 'Disputed', tone: 'loss' },
  },
  ruleset: {
    draft: { glyph: '○', label: 'Draft', tone: 'neutral' },
    pendingApproval: { glyph: '◐', label: 'Pending approval', tone: 'outline' },
    active: { glyph: '●', label: 'Active', tone: 'payout' },
    superseded: { glyph: '', label: 'Superseded', tone: 'struck' },
  },
  run: {
    draft: { glyph: '○', label: 'Draft', tone: 'neutral' },
    pendingApproval: { glyph: '◐', label: 'Pending approval', tone: 'outline' },
    executed: { glyph: '●', label: 'Executed', tone: 'payout' },
    failed: { glyph: '✕', label: 'Failed', tone: 'loss' },
    partial: { glyph: '◑', label: 'Partial', tone: 'loss' },
  },
};

export const FAMILIES = Object.keys(STATUSES);
