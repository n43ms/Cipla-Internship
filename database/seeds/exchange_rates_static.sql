INSERT INTO exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
VALUES
  ('LKR', 1.0 / 310.0, '2026-06-16', 'company', 'official'),
  ('NPR', 1.0 / 151.06361, '2026-06-19', 'public_market_rate', 'provisional'),
  ('MMK', 1.0 / 2104.074172, '2026-06-19', 'public_market_rate', 'provisional'),
  ('OMR', 1.0 / 0.384497, '2026-06-19', 'public_market_rate', 'provisional'),
  ('AED', 1.0 / 3.6725, '2026-06-19', 'public_market_rate', 'provisional'),
  ('MYR', 1.0 / 4.114387, '2026-06-19', 'public_market_rate', 'provisional')
ON CONFLICT (currency_code, rate_date, source) DO UPDATE
SET
  rate_to_usd = EXCLUDED.rate_to_usd,
  rate_status = EXCLUDED.rate_status;
