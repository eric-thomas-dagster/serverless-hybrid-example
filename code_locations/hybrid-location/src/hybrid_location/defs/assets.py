"""
Hybrid location assets for heavy computational workloads.
This location is designed to run on self-hosted infrastructure with Dagster+ Hybrid deployment.

These assets demonstrate a complex ML pipeline for fraud detection:
1. Ingest large transaction datasets from Snowflake
2. Apply complex pandas transformations
3. Train ML model for fraud detection (CPU/GPU intensive)
4. Score transactions and write results back to Snowflake
5. Generate business intelligence reports

Routed to agents serving 'hybrid-queue' for specialized infrastructure.
"""
import dagster as dg


@dg.asset(
    kinds={"snowflake", "python"},
    description="Ingests large datasets from Snowflake data warehouse"
)
def raw_customer_transactions(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Load raw transaction data from Snowflake."""
    # In production: query Snowflake tables (e.g., PROD.TRANSACTIONS)
    # In demo_mode: generate sample transaction data
    # Expected fields: transaction_id, customer_id, amount, timestamp, merchant
    # Note: This runs on hybrid-queue with dedicated compute resources
    context.log.info("Starting Snowflake transaction ingestion on hybrid-queue...")
    context.log.info("Demo: This asset runs on self-hosted agents with specialized resources")
    context.log.info("Testing deployment with GHCR authentication configured")
    pass


@dg.asset(
    kinds={"python", "pandas"},
    description="Performs complex transformations on transaction data",
    deps=[raw_customer_transactions]
)
def transformed_transactions(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Apply business rules and transformations to raw transactions."""
    # In production: complex pandas transformations
    # In demo_mode: generate transformed sample data
    pass


@dg.asset(
    kinds={"python", "machine-learning"},
    description="Trains ML model for fraud detection on transaction data",
    deps=[transformed_transactions]
)
def fraud_detection_model(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Train fraud detection model using transaction patterns."""
    # In production: train ML model (CPU/GPU intensive)
    # In demo_mode: generate mock model artifact
    pass


@dg.asset(
    kinds={"snowflake", "python"},
    description="Applies fraud model to transactions and writes results to Snowflake",
    deps=[fraud_detection_model, transformed_transactions]
)
def fraud_scores(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Score transactions for fraud probability and store in data warehouse."""
    # In production: apply model and write to Snowflake
    # In demo_mode: generate sample fraud scores
    pass


@dg.asset(
    kinds={"snowflake", "reporting"},
    description="Generates daily fraud analytics reports",
    deps=[fraud_scores]
)
def daily_fraud_report(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Create aggregated fraud analytics for business intelligence."""
    # In production: create report in Snowflake
    # In demo_mode: generate sample report
    pass
