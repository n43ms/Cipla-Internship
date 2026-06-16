INSERT INTO exchange_rates (currency_code, rate_to_usd, rate_date, source, rate_status)
VALUES
  ('LKR', 1.0 / 310.0, '2026-06-16', 'company', 'official'),
  ('NPR', NULL, NULL, 'pending_company_rate', 'missing'),
  ('MMK', NULL, NULL, 'pending_company_rate', 'missing'),
  ('OMR', NULL, NULL, 'pending_company_rate', 'missing'),
  ('AED', NULL, NULL, 'pending_company_rate', 'missing'),
  ('MYR', NULL, NULL, 'pending_company_rate', 'missing')
ON CONFLICT (currency_code, rate_date, source) DO UPDATE
SET
  rate_to_usd = EXCLUDED.rate_to_usd,
  rate_status = EXCLUDED.rate_status;
