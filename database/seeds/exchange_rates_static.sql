INSERT INTO exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
VALUES
  ('LKR', 1.0 / 310.0, '2026-06-16', 'company', 'official'),
  ('NPR', 1.0 / 150.94, '2026-06-19', 'public_market_rate', 'provisional'),
  ('MMK', 1.0 / 2098.58, '2026-06-19', 'public_market_rate', 'provisional'),
  ('OMR', 1.0 / 0.384985, '2026-06-19', 'public_market_rate', 'provisional'),
  ('AED', 1.0 / 3.6725, '2026-06-19', 'public_market_rate', 'provisional'),
  ('MYR', 1.0 / 4.1390, '2026-06-19', 'public_market_rate', 'provisional')
ON CONFLICT (currency_code, rate_date, source) DO UPDATE
SET
  rate_to_usd = EXCLUDED.rate_to_usd,
  rate_status = EXCLUDED.rate_status;
