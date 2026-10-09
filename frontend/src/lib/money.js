// Formats money strings from the API for display. Hard rule 2: the front end never does money
// math, so this works on the decimal string only. It never converts to a JS number, which would
// lose precision on large amounts and invite arithmetic.

const DECIMAL = /^(-)?(\d+)(?:\.(\d{1,2}))?$/;

export const NOT_APPLICABLE = 'None';

/**
 * Format a decimal string as US dollars per the handoff money rule:
 * "412350.00" -> "$412,350.00", "-9200" -> "($9,200.00)", null -> "None".
 *
 * Throws on anything that is not a plain decimal string with at most two places. The back end
 * owns rounding, so a third decimal place means an upstream bug and must fail loudly.
 */
export function formatMoney(value) {
  if (value === null || value === undefined) return NOT_APPLICABLE;
  if (typeof value !== 'string') {
    throw new TypeError(`Money must be a decimal string from the API, got ${typeof value}`);
  }

  const match = DECIMAL.exec(value);
  if (!match) throw new RangeError(`Not a money string with at most two decimals: "${value}"`);

  const [, minus, whole, fraction = ''] = match;
  const digits = whole.replace(/^0+(?=\d)/, '');
  const cents = fraction.padEnd(2, '0');
  const grouped = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const formatted = `$${grouped}.${cents}`;

  const isZero = /^0*$/.test(digits + cents);
  return minus && !isZero ? `(${formatted})` : formatted;
}

/** True when the string is negative and not zero, for screen-reader labels. */
export function isNegativeMoney(value) {
  return typeof value === 'string' && formatMoney(value).startsWith('(');
}
