"""
Serverless location assets for lightweight data processing.
This location is designed to run on Dagster+ Serverless infrastructure.

These assets demonstrate a simple data pipeline for user event analytics:
1. Ingest events from API
2. Clean and normalize the data
3. Calculate daily metrics
4. Generate engagement scores
"""
import dagster as dg


@dg.asset(
    kinds={"duckdb", "api"},
    description="Fetches raw user events from an API endpoint and stores in DuckDB"
)
def raw_user_events(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Ingest raw user event data from API."""
    # In production: fetch from REST API (e.g., /api/v1/events)
    # In demo_mode: generate sample data
    # Expected fields: user_id, event_type, timestamp, properties
    context.log.info("Starting raw user events ingestion on Dagster+ Serverless...")
    context.log.info("Demo: This asset runs on fully-managed serverless infrastructure")
    pass


@dg.asset(
    kinds={"duckdb", "python"},
    description="Cleans and normalizes raw user events",
    deps=[raw_user_events]
)
def cleaned_user_events(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Clean and normalize user event data."""
    # In production: read from raw_user_events, clean data
    # In demo_mode: generate clean sample data
    pass


@dg.asset(
    kinds={"duckdb", "analytics"},
    description="Aggregates user events into daily metrics",
    deps=[cleaned_user_events]
)
def daily_user_metrics(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Aggregate cleaned events into daily metrics."""
    # In production: aggregate cleaned_user_events by day
    # In demo_mode: generate sample metrics
    pass


@dg.asset(
    kinds={"duckdb", "analytics", "reporting"},
    description="Creates user engagement scores based on activity metrics",
    deps=[daily_user_metrics]
)
def user_engagement_scores(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Calculate user engagement scores from daily metrics."""
    # In production: calculate engagement scores
    # In demo_mode: generate sample scores
    pass
