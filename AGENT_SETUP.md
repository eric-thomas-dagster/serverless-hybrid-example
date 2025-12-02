# Agent Configuration for Hybrid Deployment

This document explains how to configure Dagster+ Hybrid agents to work with the hybrid-location code location using **agent queues**.

## Overview

The `hybrid-location` is configured with `agent_queue: hybrid-queue` in its `dagster_cloud.yaml`. This means:
- Requests from this location will be placed on the "hybrid-queue"
- Only agents configured to serve "hybrid-queue" will process these requests
- This allows you to dedicate specific infrastructure (GPU, high memory, etc.) for this workload

## Agent Queue Configuration

### Why Use Agent Queues?

Agent queues allow you to:
1. **Route workloads to appropriate infrastructure** - Send ML/heavy compute to GPU-enabled agents
2. **Isolate environments** - Run different locations in different VPCs or cloud accounts
3. **Resource optimization** - Dedicate expensive hardware only where needed
4. **High availability** - Run multiple agents serving the same queue for redundancy

### Configuration by Deployment Type

#### Docker

Create or update your `docker-compose.yaml` for the hybrid agent:

```yaml
version: '3.7'

services:
  dagster-cloud-agent:
    image: dagster/dagster-cloud-agent:latest
    container_name: dagster-cloud-agent
    restart: always
    environment:
      DAGSTER_CLOUD_API_TOKEN: "${DAGSTER_CLOUD_API_TOKEN}"
      DAGSTER_CLOUD_DEPLOYMENT: "prod"
      DAGSTER_CLOUD_URL: "${DAGSTER_CLOUD_URL}"
      # Agent queue configuration
      DAGSTER_CLOUD_AGENT_QUEUES_INCLUDE_DEFAULT_QUEUE: "false"
      DAGSTER_CLOUD_AGENT_QUEUES_ADDITIONAL_QUEUES: "hybrid-queue"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - dagster-network

networks:
  dagster-network:
```

**Or** using the configuration file approach with `dagster.yaml`:

```yaml
# dagster.yaml
instance:
  agent_queues:
    include_default_queue: true
    additional_queues:
      - hybrid-queue
```

#### Kubernetes (Helm)

Update your Helm values file:

```yaml
# values.yaml
dagsterCloud:
  apiToken: "your-api-token"
  deployment: "prod"

  # Agent queue configuration
  agentQueues:
    includeDefaultQueue: false
    additionalQueues:
      - hybrid-queue

# Optional: Configure resources for heavy workloads
resources:
  limits:
    cpu: "8"
    memory: "32Gi"
    nvidia.com/gpu: "1"  # If using GPU
  requests:
    cpu: "4"
    memory: "16Gi"
```

Then deploy with Helm:

```bash
helm repo add dagster-cloud https://dagster-io.github.io/helm-user-cloud
helm repo update

helm upgrade --install dagster-cloud-agent dagster-cloud/dagster-cloud-agent \
  --namespace dagster-cloud \
  --create-namespace \
  --values values.yaml
```

#### Amazon ECS

Update your CloudFormation template or ECS task definition:

```yaml
# In your task definition, add environment variables:
environment:
  - name: DAGSTER_CLOUD_API_TOKEN
    value: !Ref ApiToken
  - name: DAGSTER_CLOUD_DEPLOYMENT
    value: prod
  - name: DAGSTER_CLOUD_AGENT_QUEUES_INCLUDE_DEFAULT_QUEUE
    value: "false"
  - name: DAGSTER_CLOUD_AGENT_QUEUES_ADDITIONAL_QUEUES
    value: "hybrid-queue"

# Configure appropriate resources for ML workloads
cpu: 4096  # 4 vCPU
memory: 16384  # 16 GB
```

## Understanding `include_default_queue`

The `include_default_queue` setting controls whether hybrid agents process serverless workloads:

- **false**: Agent ONLY serves "hybrid-queue", ignoring the default queue (recommended for mixed serverless + hybrid environments)
- **true**: Agent serves both "hybrid-queue" AND the default queue (processes unspecified code locations)

**Recommendation**: Set to `false` for mixed serverless + hybrid deployments. This ensures serverless locations are handled by Dagster+ managed infrastructure, not by your hybrid agents which would fail trying to run serverless workloads.

## Multiple Agent Configurations

### Scenario 1: High Availability (Same Queue)

Run multiple agents serving the same queue for redundancy:

**Agent 1:**
```yaml
agentQueues:
  includeDefaultQueue: false
  additionalQueues:
    - hybrid-queue
```

**Agent 2 (identical configuration):**
```yaml
agentQueues:
  includeDefaultQueue: false
  additionalQueues:
    - hybrid-queue
```

Both agents will process requests from the hybrid-queue in a load-balanced fashion.

### Scenario 2: Specialized Infrastructure

Dedicate different agents for different workload types:

**GPU Agent (for ML training):**
```yaml
agentQueues:
  includeDefaultQueue: false  # Only serve specialized queue
  additionalQueues:
    - hybrid-queue
```

**General Purpose Agent (for other workloads):**
```yaml
agentQueues:
  includeDefaultQueue: true  # Serve all other locations
  additionalQueues: []
```

### Scenario 3: Multi-Environment Isolation

Run agents in different VPCs/cloud accounts:

**Production VPC Agent:**
```yaml
# In production VPC with access to production Snowflake
agentQueues:
  includeDefaultQueue: false
  additionalQueues:
    - hybrid-queue
```

**Staging VPC Agent:**
```yaml
# In staging VPC with access to staging resources
agentQueues:
  includeDefaultQueue: true
  additionalQueues:
    - staging-queue
```

## Verifying Agent Configuration

### Check Agent Status

In the Dagster+ UI:
1. Navigate to **Deployment** → **Agents**
2. Verify your agent appears with status "Running"
3. Check the **Queues** column shows "default, hybrid-queue"

### Test Queue Routing

1. **Materialize an asset** from the hybrid-location
2. **Check the run details** - it should show `agent_queue: hybrid-queue`
3. **Verify execution** happens on the correct agent (check agent logs)

### Agent Logs

**Docker:**
```bash
docker logs dagster-cloud-agent
```

**Kubernetes:**
```bash
kubectl logs -n dagster-cloud -l app=dagster-cloud-agent
```

**ECS:**
```bash
aws ecs describe-tasks --cluster your-cluster --tasks task-id
```

## GitHub Container Registry (GHCR) Setup

The hybrid-location uses GHCR for Docker images. No additional agent configuration is needed, but ensure:

1. **Agent has internet access** to pull from `ghcr.io`
2. **Images are public** OR **agent has credentials** to pull private images

### For Private GHCR Images

If using private repository images, configure image pull secrets:

**Kubernetes:**
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT \
  --namespace dagster-cloud
```

**Docker:**
```bash
docker login ghcr.io -u YOUR_GITHUB_USERNAME -p YOUR_GITHUB_PAT
```

## Troubleshooting

### Agent Not Picking Up Jobs

**Symptoms**: Jobs stay queued, never execute

**Solutions**:
1. Verify agent queue configuration matches `dagster_cloud.yaml`
2. Check `includeDefaultQueue` setting
3. Ensure agent is running and connected (check Dagster+ UI)
4. Review agent logs for errors

### Wrong Agent Processing Jobs

**Symptoms**: GPU workloads running on CPU-only agents

**Solutions**:
1. Set `includeDefaultQueue: false` on specialized agents
2. Verify queue names match exactly (case-sensitive)
3. Check multiple agents aren't fighting for the same queue

### Image Pull Failures

**Symptoms**: Jobs fail with "ImagePullBackOff" or similar

**Solutions**:
1. Verify image exists in GHCR: `https://github.com/YOUR_ORG/YOUR_REPO/pkgs/container/hybrid-location`
2. Check image visibility (public vs private)
3. Configure image pull secrets if needed
4. Ensure agent has network access to `ghcr.io`

## Best Practices

1. **Use `includeDefaultQueue: false` for mixed serverless + hybrid environments** to ensure serverless locations run on Dagster+ managed infrastructure
2. **Use descriptive queue names** that indicate the workload type (e.g., `gpu-queue`, `high-memory-queue`)
3. **Run multiple agents** serving the same queue for high availability
4. **Monitor agent resource usage** to ensure adequate capacity
5. **Test queue routing** in a staging environment before production
6. **Document your agent topology** - which queues, which infrastructure, which locations

## Additional Resources

- [Dagster+ Multiple Agents Documentation](https://docs.dagster.io/dagster-plus/deployment/agents/running-multiple-agents)
- [Agent Queue Configuration Reference](https://docs.dagster.io/dagster-plus/deployment/agents/agent-queues)
- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
