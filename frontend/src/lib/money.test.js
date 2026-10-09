import { formatMoney, isNegativeMoney } from './money.js';

describe('formatMoney', () => {
  test.each([
    ['412350.00', '$412,350.00'],
    ['0.00', '$0.00'],
    ['0', '$0.00'],
    ['5', '$5.00'],
    ['5.5', '$5.50'],
    ['999.99', '$999.99'],
    ['1000', '$1,000.00'],
    ['1234567.89', '$1,234,567.89'],
    ['007.10', '$7.10'],
    ['-9200.00', '($9,200.00)'],
    ['-0.01', '($0.01)'],
    ['-0.00', '$0.00'],
    ['-0', '$0.00'],
  ])('%s -> %s', (input, expected) => {
    expect(formatMoney(input)).toBe(expected);
  });

  test('keeps precision beyond what a JS number can hold', () => {
    expect(formatMoney('123456789012345678.91')).toBe('$123,456,789,012,345,678.91');
  });

  test('shows None when not applicable', () => {
    expect(formatMoney(null)).toBe('None');
    expect(formatMoney(undefined)).toBe('None');
  });

  test('rejects numbers: money arrives as strings', () => {
    expect(() => formatMoney(412350)).toThrow(TypeError);
  });

  test.each(['', '1.234', '1,000.00', '$5.00', '1e3', ' 5.00', '.50', 'abc', '--5'])(
    'rejects %j',
    (input) => {
      expect(() => formatMoney(input)).toThrow(RangeError);
    },
  );
});

describe('isNegativeMoney', () => {
  test('is true only for amounts below zero', () => {
    expect(isNegativeMoney('-9200.00')).toBe(true);
    expect(isNegativeMoney('-0.00')).toBe(false);
    expect(isNegativeMoney('10.00')).toBe(false);
    expect(isNegativeMoney(null)).toBe(false);
  });
});
