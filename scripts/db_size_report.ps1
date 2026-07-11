param(
    [int]$FreeTierLimitMb = 500,
    [switch]$PrintSqlOnly
)

$ErrorActionPreference = "Stop"

function Get-DatabaseUrl {
    if ($env:DATABASE_URL) {
        return $env:DATABASE_URL
    }

    $envPath = Join-Path (Get-Location) ".env"
    if (-not (Test-Path $envPath)) {
        throw "DATABASE_URL is not set and .env was not found."
    }

    $line = Get-Content $envPath |
        Where-Object { $_ -match "^\s*DATABASE_URL\s*=" } |
        Select-Object -First 1

    if (-not $line) {
        throw "DATABASE_URL is not set in environment or .env."
    }

    return ($line -replace "^\s*DATABASE_URL\s*=\s*", "").Trim('"').Trim("'")
}

function Convert-ToPsqlUrl([string]$DatabaseUrl) {
    return $DatabaseUrl -replace "^postgresql\+psycopg://", "postgresql://"
}

$sql = @"
with db_size as (
  select pg_database_size(current_database()) as bytes
),
relations as (
  select
    n.nspname as schema_name,
    c.relname as relation_name,
    c.relkind,
    pg_total_relation_size(c.oid) as bytes
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'public'
    and c.relkind in ('r', 'm', 'i')
),
sections as (
  select 'database_total' as section, current_database() as name, bytes
  from db_size
  union all
  select 'largest_relations', schema_name || '.' || relation_name, bytes
  from relations
  order by bytes desc
  limit 25
)
select section, name, pg_size_pretty(bytes) as size, bytes
from sections
order by section, bytes desc;
"@

Write-Output "Database size report"
Write-Output "Free-tier reference limit: $FreeTierLimitMb MB"
Write-Output "Database URL: [redacted]"
Write-Output ""

if ($PrintSqlOnly) {
    Write-Output "Dry run: SQL only; no database connection attempted."
    Write-Output $sql
    exit 0
}

$databaseUrl = Convert-ToPsqlUrl (Get-DatabaseUrl)
$limitBytes = [int64]$FreeTierLimitMb * 1024 * 1024

psql $databaseUrl -v ON_ERROR_STOP=1 -c $sql

$currentBytesSql = "select pg_database_size(current_database());"
$currentBytes = (psql $databaseUrl -t -A -v ON_ERROR_STOP=1 -c $currentBytesSql).Trim()
if ($currentBytes -match "^\d+$") {
    $headroomBytes = $limitBytes - [int64]$currentBytes
    $headroomMb = [math]::Round($headroomBytes / 1MB, 1)
    Write-Output ""
    Write-Output "Estimated free-tier headroom: $headroomMb MB"
}
