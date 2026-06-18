create or replace view mv_latest_validation_errors as
select
    ve.*
from validation_errors ve
join mv_latest_file_ingestion_status latest
  on latest.source_file_id = ve.source_file_id
 and latest.ingestion_run_id = ve.ingestion_run_id;
