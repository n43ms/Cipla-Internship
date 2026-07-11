INSERT INTO exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
VALUES
  ('LKR', 1.0 / 368.90, '2026-07-10', 'company', 'official'),
  ('NPR', 1.0 / 89.0, '2026-07-10', 'company', 'official'),
  ('MMK', 1.0 / 4300.0, '2026-07-10', 'company', 'official'),
  ('OMR', 1.0 / 0.46, '2026-07-10', 'company', 'official'),
  ('AED', 1.0, '2026-07-10', 'company', 'official'),
  ('MYR', 1.0 / 4.39, '2026-07-10', 'company', 'official')
ON CONFLICT (currency_code, rate_date, source) DO UPDATE
SET
  rate_to_usd = EXCLUDED.rate_to_usd,
  rate_status = EXCLUDED.rate_status;
