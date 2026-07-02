INSERT INTO countries (name, code, default_currency_code)
VALUES
  ('Nepal', 'NP', 'NPR'),
  ('Sri Lanka', 'LK', 'LKR'),
  ('Myanmar', 'MM', 'MMK'),
  ('Oman', 'OM', 'OMR'),
  ('UAE', 'AE', 'AED'),
  ('Malaysia', 'MY', 'MYR')
ON CONFLICT (code) DO UPDATE
SET
  name = EXCLUDED.name,
  default_currency_code = EXCLUDED.default_currency_code;
