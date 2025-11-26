# Dagster+ Serverless & Hybrid Monorepo Demo

This repository demonstrates a **monorepo setup** with two separate Dagster code locations configured for different deployment types:

1. **Serverless Location** - Lightweight data processing pipelines running on Dagster+ Serverless
2. **Hybrid Location** - Heavy computational workloads running on self-hosted infrastructure with Dagster+ Hybrid

## Architecture Overview

```
serverless-hybrid-example/
├── code_locations/
│   ├── serverless-location/          # Dagster+ Serverless deployment
│   │   ├── src/serverless_location/
│   │   │   ├── defs/
│   │   │   │   └── assets.py        # Lightweight data processing assets
│   │   │   └── definitions.py
│   │   ├── pyproject.toml
│   │   └── dagster_cloud.yaml
│   │
│   └── hybrid-location/              # Dagster+ Hybrid deployment
│       ├── src/hybrid_location/
│       │   ├── defs/
│       │   │   └── assets.py        # Heavy computation & ML assets
│       │   └── definitions.py
│       ├── pyproject.toml
│       └── dagster_cloud.yaml
│
└── .github/workflows/
    ├── deploy-serverless.yml         # CI/CD for serverless location
    └── deploy-hybrid.yml             # CI/CD for hybrid location
```

## Code Locations

### Serverless Location

**Purpose**: Lightweight API ingestion and data processing

**Assets**:
- `raw_user_events` - Fetches events from REST API
- `cleaned_user_events` - Data cleaning and normalization
- `daily_user_metrics` - Daily aggregations
- `user_engagement_scores` - Engagement scoring

**Technology Stack**: DuckDB, Python, REST APIs

**Deployment**: Dagster+ Serverless (fully managed execution)

### Hybrid Location

**Purpose**: Heavy computational workloads and ML training

**Assets**:
- `raw_customer_transactions` - Ingest from Snowflake data warehouse
- `transformed_transactions` - Complex pandas transformations
- `fraud_detection_model` - ML model training (CPU/GPU intensive)
- `fraud_scores` - Apply model to transactions
- `daily_fraud_report` - Business intelligence reporting

**Technology Stack**: Snowflake, Pandas, Machine Learning, Python

**Deployment**: Dagster+ Hybrid (runs on your infrastructure)

## Getting Started

### Prerequisites

- Python 3.10-3.13
- [uv](https://docs.astral.sh/uv/) package manager
- Dagster+ account
- (For Hybrid) Self-hosted Dagster agent running

### Local Development

#### Serverless Location

```bash
cd code_locations/serverless-location
uv sync
uv run dg dev
```

#### Hybrid Location

```bash
cd code_locations/hybrid-location
uv sync
uv run dg dev
```

### Validation

Check that definitions load correctly:

```bash
# From either location directory
uv run dg check defs
uv run dg list defs
```

## Deployment

### GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

- `DAGSTER_CLOUD_API_TOKEN` - Your Dagster+ API token
- `DAGSTER_CLOUD_ORGANIZATION_ID` - Your Dagster+ organization ID
- `DAGSTER_CLOUD_URL` - Your Dagster+ instance URL (e.g., `https://myorg.dagster.cloud`)

**Note**: `GITHUB_TOKEN` is automatically provided by GitHub Actions for pushing to GitHub Container Registry.

### Automatic Deployment

The repository includes separate GitHub Actions workflows:

- **`deploy-serverless.yml`** - Deploys serverless location on changes to `code_locations/serverless-location/**`
- **`deploy-hybrid.yml`** - Builds Docker image, pushes to GitHub Container Registry (GHCR), and deploys hybrid location on changes to `code_locations/hybrid-location/**`

Both workflows trigger on:
- Push to `main` or `master` branch
- Pull requests

#### GitHub Container Registry (GHCR)

The hybrid deployment uses GHCR for container images:

**Image Location**: `ghcr.io/YOUR_ORG/YOUR_REPO/hybrid-location:latest`

**Features**:
- Automatic image building and pushing on every commit
- Multi-tag strategy (branch, SHA, latest)
- Layer caching for faster builds
- Integrated with GitHub Actions permissions

**Viewing Images**: Navigate to your repository's "Packages" tab on GitHub to see published images.

### Deployment Configuration

Each code location has its own `dagster_cloud.yaml` that specifies:
- Location name
- Code source (Python file path)
- Working directory
- Executable path
- **Agent queue** (for hybrid deployments only)

## When to Use Each Deployment Type

### Use Serverless When:
- ✅ Lightweight data transformations
- ✅ API integrations and data ingestion
- ✅ Quick prototyping and development
- ✅ No infrastructure management needed
- ✅ Cost optimization for variable workloads

### Use Hybrid When:
- ✅ Heavy computational requirements (ML training, large data processing)
- ✅ Need specific hardware (GPUs, large memory)
- ✅ Connecting to internal/VPC resources
- ✅ Compliance requirements for data locality
- ✅ Custom infrastructure configurations

## Agent Queues & Multiple Agents

### Agent Queue Configuration

The **hybrid-location** is configured with `agent_queue: hybrid-queue` in its `dagster_cloud.yaml`. This routes all requests from this location to agents specifically configured to serve the "hybrid-queue".

**Benefits**:
- **Dedicated Resources**: Route ML/heavy compute to GPU-enabled agents
- **Environment Isolation**: Run different locations in different VPCs or cloud accounts
- **Resource Optimization**: Reserve expensive hardware only for workloads that need it
- **High Availability**: Run multiple agents serving the same queue

### Quick Start: Configure Your Agent

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

**Amazon ECS (Task Definition):**
```yaml
environment:
  - name: DAGSTER_CLOUD_AGENT_QUEUES_INCLUDE_DEFAULT_QUEUE
    value: "true"
  - name: DAGSTER_CLOUD_AGENT_QUEUES_ADDITIONAL_QUEUES
    value: "hybrid-queue"
```

### Multiple Agent Scenarios

For the hybrid deployment, you can run multiple agents for:

1. **High Availability** - Run multiple replicas in the same environment serving the same queue
2. **Isolation** - Run agents in different infrastructure environments (different VPCs, cloud accounts)
3. **Specialized Hardware** - Dedicate GPU agents for ML workloads, high-memory agents for data processing

### Detailed Setup Instructions

See **[AGENT_SETUP.md](./AGENT_SETUP.md)** for comprehensive documentation including:
- Complete agent configuration examples for Docker, Kubernetes, and ECS
- Multi-agent topology patterns
- Troubleshooting guide
- GHCR image pull configuration
- Best practices

### Additional Resources

- [Dagster+ Multiple Agents Documentation](https://docs.dagster.io/dagster-plus/deployment/agents/running-multiple-agents)
- [Agent Queue Configuration Reference](https://docs.dagster.io/dagster-plus/deployment/agents/agent-queues)

## Demo Mode

Both locations include placeholder `pass` statements in asset functions with comments indicating:
- Production implementation (real data sources, processing)
- Demo mode (sample data generation for local testing)

This allows running the demo without actual API keys or database connections.

## Learn More

- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster+ Serverless](https://docs.dagster.io/dagster-plus/deployment/serverless)
- [Dagster+ Hybrid](https://docs.dagster.io/dagster-plus/deployment/hybrid)
- [Dagster Components](https://docs.dagster.io/guides/build/components)
- [Dagster University](https://courses.dagster.io/)

## Support

For questions or issues:
- [Dagster Slack Community](https://dagster.io/slack)
- [GitHub Issues](https://github.com/dagster-io/dagster/issues)
