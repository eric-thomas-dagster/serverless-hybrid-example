"""
Serverless location assets for lightweight data processing.
This location is designed to run on Dagster+ Serverless infrastructure.
"""
import dagster as dg


@dg.asset(
    kinds={"duckdb", "api"},
    description="Fetches raw user events from an API endpoint and stores in DuckDB"
)
def raw_user_events(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Ingest raw user event data from API."""
    # In production: fetch from REST API
    # In demo_mode: generate sample data
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
