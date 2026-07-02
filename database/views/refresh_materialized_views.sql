CREATE OR REPLACE FUNCTION refresh_dashboard_materialized_views()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  IF to_regclass('mv_execution_kpis') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_execution_kpis;
  END IF;

  IF to_regclass('mv_unmatched_events') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_unmatched_events;
  END IF;

  IF to_regclass('mv_execution_event_matrix') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_execution_event_matrix;
  END IF;

  IF to_regclass('mv_workflow_governance') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_workflow_governance;
  END IF;

  IF to_regclass('mv_intervention_mix') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_intervention_mix;
  END IF;

  IF to_regclass('mv_budget_utilization') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_budget_utilization;
  END IF;

  IF to_regclass('mv_doctor_roi') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_doctor_roi;
  END IF;

  IF to_regclass('mv_data_quality') IS NOT NULL THEN
    REFRESH MATERIALIZED VIEW mv_data_quality;
  END IF;
END;
$$;
