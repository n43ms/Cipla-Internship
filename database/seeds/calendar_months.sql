INSERT INTO calendar_months (
  month_start_date,
  month_label,
  fiscal_year,
  fiscal_month_number,
  calendar_year,
  calendar_month_number
)
SELECT
  month_start::date,
  to_char(month_start, 'YYYY-MM'),
  CASE
    WHEN EXTRACT(MONTH FROM month_start) >= 4
      THEN 'FY' || to_char(month_start + interval '1 year', 'YY')
    ELSE 'FY' || to_char(month_start, 'YY')
  END,
  ((EXTRACT(MONTH FROM month_start)::int + 8) % 12) + 1,
  EXTRACT(YEAR FROM month_start)::int,
  EXTRACT(MONTH FROM month_start)::int
FROM generate_series('2024-04-01'::date, '2027-03-01'::date, interval '1 month') AS month_start
ON CONFLICT (month_start_date) DO UPDATE
SET
  month_label = EXCLUDED.month_label,
  fiscal_year = EXCLUDED.fiscal_year,
  fiscal_month_number = EXCLUDED.fiscal_month_number,
  calendar_year = EXCLUDED.calendar_year,
  calendar_month_number = EXCLUDED.calendar_month_number;
