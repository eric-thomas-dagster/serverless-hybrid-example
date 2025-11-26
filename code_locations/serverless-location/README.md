# Serverless Location

This code location contains lightweight data processing assets designed to run on **Dagster+ Serverless** infrastructure.

## Assets

### Pipeline Overview

```
raw_user_events (API ingestion)
    ↓
cleaned_user_events (Data cleaning)
    ↓
daily_user_metrics (Aggregation)
    ↓
user_engagement_scores (Scoring)
```

### Asset Details

1. **raw_user_events**
   - **Kinds**: `duckdb`, `api`
   - **Description**: Fetches raw user events from an API endpoint and stores in DuckDB
   - **Dependencies**: None

2. **cleaned_user_events**
   - **Kinds**: `duckdb`, `python`
   - **Description**: Cleans and normalizes raw user events
   - **Dependencies**: `raw_user_events`

3. **daily_user_metrics**
   - **Kinds**: `duckdb`, `analytics`
   - **Description**: Aggregates user events into daily metrics
   - **Dependencies**: `cleaned_user_events`

4. **user_engagement_scores**
   - **Kinds**: `duckdb`, `analytics`, `reporting`
   - **Description**: Creates user engagement scores based on activity metrics
   - **Dependencies**: `daily_user_metrics`

## Technology Stack

- **DuckDB**: Lightweight embedded database for analytics
- **Python**: Data processing and transformations
- **REST APIs**: External data ingestion

## Local Development

```bash
# Install dependencies
uv sync

# Start Dagster UI
uv run dg dev

# Validate definitions
uv run dg check defs

# List all assets
uv run dg list defs
```

## Deployment

This location deploys to **Dagster+ Serverless** via GitHub Actions (`.github/workflows/deploy-serverless.yml`).

Deployment is triggered on:
- Push to `main`/`master` branch
- Changes to `code_locations/serverless-location/**`

## Configuration

See `dagster_cloud.yaml` for deployment configuration:
- Location name: `serverless-location`
- Entry point: `serverless_location/definitions.py`
- Working directory: `src`
