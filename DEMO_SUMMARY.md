# Demo Summary: Serverless & Hybrid Monorepo

## Overview

This demo showcases a **monorepo architecture** with two separate Dagster code locations configured for different deployment types:
- **Serverless Location**: Lightweight data processing on Dagster+ Serverless
- **Hybrid Location**: Heavy computational workloads on Dagster+ Hybrid (self-hosted)

## Key Demo Points

### 1. Monorepo Structure
- Single repository with multiple independent code locations
- Each location has its own `pyproject.toml`, dependencies, and deployment config
- Separate GitHub Actions workflows for independent CI/CD

### 2. Deployment Type Selection

**Serverless Location** demonstrates when to use serverless:
- API data ingestion (`raw_user_events`)
- Lightweight transformations (`cleaned_user_events`)
- Quick analytics (`daily_user_metrics`, `user_engagement_scores`)
- No infrastructure management needed
- Cost-effective for variable workloads

**Hybrid Location** demonstrates when to use hybrid:
- Large data warehouse queries (`raw_customer_transactions` from Snowflake)
- Heavy pandas operations (`transformed_transactions`)
- ML model training (`fraud_detection_model`) - CPU/GPU intensive
- Custom infrastructure requirements
- Data locality and compliance needs

### 3. Asset Organization

#### Serverless Assets (4 total)
```
raw_user_events → cleaned_user_events → daily_user_metrics → user_engagement_scores
```
- Linear pipeline
- Lightweight operations
- DuckDB for local analytics

#### Hybrid Assets (5 total)
```
raw_customer_transactions → transformed_transactions → fraud_detection_model
                                      ↓                         ↓
                                      └─────→ fraud_scores ←───┘
                                                    ↓
                                            daily_fraud_report
```
- Complex dependency graph
- Resource-intensive operations
- Enterprise data warehouse integration

### 4. CI/CD Setup

**Separate Workflows**:
- `deploy-serverless.yml` - Triggers on changes to `code_locations/serverless-location/**`
- `deploy-hybrid.yml` - Triggers on changes to `code_locations/hybrid-location/**`

**Independent Deployments**:
- Changes to serverless location don't trigger hybrid deployment
- Changes to hybrid location don't trigger serverless deployment
- Each workflow validates definitions before deploying

**GitHub Container Registry (GHCR)**:
- Hybrid workflow builds Docker images and pushes to GHCR
- Images tagged with branch name, commit SHA, and `latest`
- Automatic caching for faster builds
- Integrated with GitHub Actions permissions (no separate registry credentials needed)

### 5. Agent Queues for Workload Routing

**Configuration**:
The hybrid location is configured with `agent_queue: hybrid-queue` in `dagster_cloud.yaml`.

**Benefits**:
- **Dedicated Resources**: Routes heavy ML workloads to GPU-enabled agents
- **Environment Isolation**: Run locations in different VPCs or cloud accounts
- **Resource Optimization**: Reserve expensive infrastructure only where needed
- **High Availability**: Multiple agents can serve the same queue

**Quick Setup**:
```yaml
# Docker agent configuration
environment:
  DAGSTER_CLOUD_AGENT_QUEUES_INCLUDE_DEFAULT_QUEUE: "true"
  DAGSTER_CLOUD_AGENT_QUEUES_ADDITIONAL_QUEUES: "hybrid-queue"
```

See `AGENT_SETUP.md` for complete configuration examples.

### 6. Multiple Agents (Advanced)

The hybrid location can be configured with:
- **High availability**: Multiple agent replicas serving `hybrid-queue`
- **Isolation**: Agents in different environments with specialized access
- **Specialized hardware**: GPU agents for ML, high-memory agents for data processing

## Technologies Demonstrated

### Serverless Location
- DuckDB (embedded analytics database)
- REST API ingestion
- Python data processing
- Lightweight transformations

### Hybrid Location
- Snowflake (enterprise data warehouse)
- Pandas (complex data transformations)
- Machine Learning (fraud detection)
- Heavy computation

## Assets Summary

| Asset | Location | Kinds | Description |
|-------|----------|-------|-------------|
| `raw_user_events` | Serverless | api, duckdb | API data ingestion |
| `cleaned_user_events` | Serverless | python, duckdb | Data cleaning |
| `daily_user_metrics` | Serverless | analytics, duckdb | Daily aggregations |
| `user_engagement_scores` | Serverless | analytics, reporting, duckdb | Engagement scoring |
| `raw_customer_transactions` | Hybrid | snowflake, python | Data warehouse ingestion |
| `transformed_transactions` | Hybrid | python, pandas | Complex transformations |
| `fraud_detection_model` | Hybrid | python, machine-learning | ML model training |
| `fraud_scores` | Hybrid | snowflake, python | Model inference |
| `daily_fraud_report` | Hybrid | snowflake, reporting | BI reporting |

## Running Locally

### Serverless Location
```bash
cd code_locations/serverless-location
uv sync
uv run dg dev  # Opens UI at http://localhost:3000
```

### Hybrid Location
```bash
cd code_locations/hybrid-location
uv sync
uv run dg dev  # Opens UI at http://localhost:3000
```

## Deployment Requirements

### GitHub Secrets
Both workflows require:
- `DAGSTER_CLOUD_API_TOKEN`
- `DAGSTER_CLOUD_ORGANIZATION_ID`
- `DAGSTER_CLOUD_URL`
- `GITHUB_TOKEN` (automatically provided by GitHub Actions for GHCR)

### Dagster+ Setup
- **Serverless**: No additional setup required
- **Hybrid**: Self-hosted agent must be running, connected to Dagster+, and configured to serve `hybrid-queue`

### Container Registry
- Hybrid images stored in **GitHub Container Registry (GHCR)**
- Location: `ghcr.io/YOUR_ORG/YOUR_REPO/hybrid-location`
- Automatic image building and tagging on every commit
- Agent pulls images directly from GHCR

### Agent Queue Setup
For hybrid deployment, configure your agent to serve the `hybrid-queue`:
```yaml
# Example: Docker agent
environment:
  DAGSTER_CLOUD_AGENT_QUEUES_INCLUDE_DEFAULT_QUEUE: "true"
  DAGSTER_CLOUD_AGENT_QUEUES_ADDITIONAL_QUEUES: "hybrid-queue"
```

See `AGENT_SETUP.md` for complete configuration details.

## Demo Talking Points

1. **Flexibility**: Choose the right deployment type for each workload
2. **Isolation**: Independent code locations with separate dependencies
3. **CI/CD**: Automated deployment with validation and GHCR image management
4. **Scalability**: Serverless auto-scales, hybrid runs on your infrastructure
5. **Cost Optimization**: Use serverless for variable workloads, hybrid for predictable heavy workloads
6. **Organization**: Monorepo keeps related projects together while maintaining independence
7. **Agent Queues**: Route specific workloads to dedicated infrastructure (GPU, high-memory)
8. **Container Management**: GHCR integration provides seamless image versioning and distribution

## Validation

Both locations have been validated:
```bash
✓ All component YAML validated successfully
✓ All definitions loaded successfully
✓ Serverless location: 4 assets
✓ Hybrid location: 5 assets
```

## Next Steps for Customization

1. Implement actual data processing logic (currently placeholder `pass` statements)
2. Add resource configurations (databases, APIs, cloud storage)
3. Create schedules and sensors for automation
4. Add tests using `pytest` and Dagster's testing utilities
5. Configure agent queues for advanced routing (hybrid only)
6. Add more complex pipelines as needed

## Documentation References

- [Dagster+ Serverless Docs](https://docs.dagster.io/dagster-plus/deployment/serverless)
- [Dagster+ Hybrid Docs](https://docs.dagster.io/dagster-plus/deployment/hybrid)
- [Multiple Agents Guide](https://docs.dagster.io/dagster-plus/deployment/agents/running-multiple-agents)
- [Dagster Components](https://docs.dagster.io/guides/build/components)
