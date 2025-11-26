# Hybrid Location

This code location contains heavy computational workloads and ML training assets designed to run on **Dagster+ Hybrid** (self-hosted infrastructure).

## Assets

### Pipeline Overview

```
raw_customer_transactions (Snowflake ingestion)
    ↓
transformed_transactions (Complex transformations)
    ↓
fraud_detection_model (ML training)
    ↓ ↘
    ↓   transformed_transactions
    ↓ ↙
fraud_scores (Model inference)
    ↓
daily_fraud_report (BI reporting)
```

### Asset Details

1. **raw_customer_transactions**
   - **Kinds**: `snowflake`, `python`
   - **Description**: Ingests large datasets from Snowflake data warehouse
   - **Dependencies**: None
   - **Resources**: High memory, data warehouse access

2. **transformed_transactions**
   - **Kinds**: `python`, `pandas`
   - **Description**: Performs complex transformations on transaction data
   - **Dependencies**: `raw_customer_transactions`
   - **Resources**: High CPU, large memory for pandas operations

3. **fraud_detection_model**
   - **Kinds**: `python`, `machine-learning`
   - **Description**: Trains ML model for fraud detection on transaction data
   - **Dependencies**: `transformed_transactions`
   - **Resources**: CPU/GPU intensive, model storage

4. **fraud_scores**
   - **Kinds**: `snowflake`, `python`
   - **Description**: Applies fraud model to transactions and writes results to Snowflake
   - **Dependencies**: `fraud_detection_model`, `transformed_transactions`
   - **Resources**: Model inference, data warehouse writes

5. **daily_fraud_report**
   - **Kinds**: `snowflake`, `reporting`
   - **Description**: Generates daily fraud analytics reports
   - **Dependencies**: `fraud_scores`
   - **Resources**: BI report generation

## Technology Stack

- **Snowflake**: Enterprise data warehouse
- **Pandas**: Complex data transformations
- **Python**: ML model training and inference
- **Machine Learning**: Fraud detection algorithms

## Why Hybrid?

This location uses Hybrid deployment because:
- **Heavy computation**: ML training requires significant CPU/GPU resources
- **Large datasets**: Processing millions of transactions from Snowflake
- **Infrastructure control**: Need specific hardware configurations
- **Data locality**: Snowflake connection requires VPC access
- **Custom resources**: GPU availability for ML training

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

This location deploys to **Dagster+ Hybrid** via GitHub Actions (`.github/workflows/deploy-hybrid.yml`).

### Deployment Workflow

The workflow performs the following steps:
1. **Validates** Dagster definitions (`dg check defs`)
2. **Builds** a Docker image with all dependencies
3. **Pushes** to GitHub Container Registry (GHCR) at `ghcr.io/YOUR_ORG/YOUR_REPO/hybrid-location`
4. **Deploys** to Dagster+ with GHCR image reference
5. **Self-hosted agent** pulls the image from GHCR and runs containers

### Container Registry

**Image Location**: `ghcr.io/YOUR_ORG/YOUR_REPO/hybrid-location:latest`

The workflow creates multiple tags:
- `latest` (on main branch)
- `main-{git-sha}` (specific commit)
- `pr-{number}` (for pull requests)

**Viewing Images**: Navigate to your GitHub repository → Packages tab

### Deployment Triggers

Deployment is triggered on:
- Push to `main`/`master` branch
- Changes to `code_locations/hybrid-location/**`
- Changes to `.github/workflows/deploy-hybrid.yml`

## Agent Requirements

### Infrastructure Requirements

Your Dagster hybrid agent should have:
- **Access to Snowflake** (credentials via environment variables)
- **Memory**: 8GB+ for pandas operations (16GB+ recommended)
- **CPU**: 4+ cores for parallel processing
- **GPU**: Optional but recommended for ML training
- **Container runtime**: Docker or Kubernetes
- **Network**: Access to `ghcr.io` for pulling container images

### Agent Queue Configuration

This location is configured with `agent_queue: hybrid-queue` in `dagster_cloud.yaml`.

**Configure your agent to serve this queue:**

**Docker (docker-compose.yaml):**
```yaml
services:
  dagster-cloud-agent:
    image: dagster/dagster-cloud-agent:latest
    environment:
      DAGSTER_CLOUD_AGENT_QUEUES_INCLUDE_DEFAULT_QUEUE: "true"
      DAGSTER_CLOUD_AGENT_QUEUES_ADDITIONAL_QUEUES: "hybrid-queue"
```

**Kubernetes (Helm values.yaml):**
```yaml
dagsterCloud:
  agentQueues:
    includeDefaultQueue: true
    additionalQueues:
      - hybrid-queue
```

**Why Agent Queues?**
- Routes heavy ML/compute workloads to agents with appropriate resources (GPU, high memory)
- Isolates this location from other workloads
- Enables dedicated infrastructure for resource-intensive operations

## Configuration

See `dagster_cloud.yaml` for deployment configuration:
- **Location name**: `hybrid-location`
- **Entry point**: `hybrid_location/definitions.py`
- **Working directory**: `src`
- **Agent queue**: `hybrid-queue` ← Routes to specialized agents

## Multiple Agents & Advanced Setup

For production deployments, consider:
- **High availability**: Run multiple agent replicas serving `hybrid-queue`
- **Specialized hardware**: Dedicate GPU-enabled agents for this location
- **Environment isolation**: Run agents in dedicated VPC with Snowflake access
- **Resource limits**: Configure appropriate CPU/memory/GPU limits

### Example: GPU-Enabled Agent (Kubernetes)

```yaml
dagsterCloud:
  agentQueues:
    includeDefaultQueue: false  # Only serve hybrid-queue
    additionalQueues:
      - hybrid-queue

resources:
  limits:
    cpu: "8"
    memory: "32Gi"
    nvidia.com/gpu: "1"
  requests:
    cpu: "4"
    memory: "16Gi"
```

See **[../../AGENT_SETUP.md](../../AGENT_SETUP.md)** for comprehensive setup documentation including:
- Complete agent configuration examples
- Multi-agent topology patterns
- Troubleshooting guide
- GHCR image pull configuration
