# Dagster+ Serverless & Hybrid Deployment Patterns

This document explains different approaches for deploying both Serverless and Hybrid code locations in the same repository.

## Table of Contents
- [Deployment Types](#deployment-types)
- [Agent Queues](#agent-queues)
- [Repository Structure Patterns](#repository-structure-patterns)
- [GitHub Actions Patterns](#github-actions-patterns)
- [Recommendations](#recommendations)

---

## Deployment Types

### Serverless Deployments
**What it is**: Code runs on fully-managed Dagster+ infrastructure.

**Build Options**:
- **PEX (Python Executable)**: Packages Python code into a single executable file
- **Docker**: Builds a Docker image (managed by Dagster Cloud)

**When to use**:
- Lightweight data processing
- Don't need specialized infrastructure (GPUs, large memory)
- Want zero infrastructure management
- Rapid prototyping and development

**Configuration**:
```yaml
locations:
  - location_name: my-serverless-location
    code_source:
      package_name: my_package.definitions
    working_directory: ./src/
    # No build.registry = Serverless
    # No agent_queue specified (uses default serverless execution)
```

### Hybrid Deployments
**What it is**: Code runs on your own infrastructure (Kubernetes, ECS, Docker, etc.) via Dagster agents.

**Build Options**:
- **Docker only**: Must use Docker images

**When to use**:
- Need specialized compute (GPUs, high memory, specific instance types)
- Heavy computational workloads (ML training, large data processing)
- Need access to private networks/databases
- Compliance requirements for data locality
- Cost optimization for compute-heavy workloads

**Configuration**:
```yaml
locations:
  - location_name: my-hybrid-location
    code_source:
      package_name: my_package.definitions
    working_directory: ./src/
    build:
      registry: ghcr.io/myorg/myrepo/my-hybrid-location  # ← Indicates hybrid!
    agent_queue: hybrid-queue  # Routes to specific agent
```

**Key Identifier**: Presence of `build.registry` field definitively indicates a Hybrid deployment.

---

## Agent Queues

### What Are Agent Queues?

Agent queues route code locations to specific Dagster agents. Think of them as "named execution environments."

### How They Work

1. **Agent Configuration**: When deploying an agent, you specify which queue(s) it serves:
   ```bash
   # Agent configured to serve "hybrid-queue"
   helm install dagster-agent dagster-cloud/dagster-cloud-agent \
     --set dagsterCloud.agentQueues[0]=hybrid-queue
   ```

2. **Location Configuration**: Code locations specify which queue to use:
   ```yaml
   locations:
     - location_name: my-location
       agent_queue: hybrid-queue  # Routes to agents serving this queue
   ```

3. **Routing**: Dagster Cloud routes runs from `my-location` only to agents configured with `hybrid-queue`.

### Common Queue Patterns

**Pattern 1: Separate Queues for Workload Types**
```yaml
# GPU-intensive ML training
- location_name: ml-training
  agent_queue: gpu-queue

# High-memory data processing
- location_name: data-processing
  agent_queue: highmem-queue

# Standard workloads
- location_name: standard-etl
  agent_queue: default-queue
```

**Pattern 2: Environment-Based Queues**
```yaml
# Production workloads
- location_name: prod-pipeline
  agent_queue: prod-queue

# Staging workloads
- location_name: staging-pipeline
  agent_queue: staging-queue
```

**Pattern 3: Team-Based Queues**
```yaml
# Data engineering team's infrastructure
- location_name: data-eng-pipelines
  agent_queue: data-eng-queue

# ML team's infrastructure (with GPUs)
- location_name: ml-pipelines
  agent_queue: ml-queue
```

### Default Queue Behavior

When you **omit `agent_queue`** from a location, it uses the **default queue**:

- **In serverless-only environments**: Runs on Dagster+ managed infrastructure
- **In hybrid environments**: Runs on any agent serving the default queue (agents not configured to ignore it)
- **In mixed environments**: Depends on which agents are serving the default queue

**Key Point**: Omitting `agent_queue` doesn't mean "serverless" - it means "use the default queue". Which infrastructure processes it depends on which agents are serving that queue.

### The `includeDefaultQueue` Setting (Critical!)

When deploying hybrid agents, the **`includeDefaultQueue`** setting controls whether the agent processes runs from the default queue:

**`includeDefaultQueue: true`** (default behavior):
- Agent processes its named queue(s) **AND** the default queue
- Locations without `agent_queue` will run on this agent

**`includeDefaultQueue: false`**:
- Agent **ONLY** processes its explicitly named queue(s)
- Ignores the default queue completely
- Locations without `agent_queue` will NOT run on this agent

**Example Configurations**:

```bash
# Hybrid agent that ONLY serves "hybrid-queue", ignores default queue
# Use this when you want serverless to handle default queue runs
helm install dagster-agent dagster-cloud/dagster-cloud-agent \
  --set dagsterCloud.agentQueues[0]=hybrid-queue \
  --set dagsterCloud.includeDefaultQueue=false

# Hybrid agent that serves "gpu-queue" + default queue
# Locations without agent_queue will run on this agent
helm install dagster-agent dagster-cloud/dagster-cloud-agent \
  --set dagsterCloud.agentQueues[0]=gpu-queue \
  --set dagsterCloud.includeDefaultQueue=true

# Agent that ONLY serves default queue
helm install dagster-agent dagster-cloud/dagster-cloud-agent \
  --set dagsterCloud.includeDefaultQueue=true

# Multiple named queues, no default queue
helm install dagster-agent dagster-cloud/dagster-cloud-agent \
  --set dagsterCloud.agentQueues[0]=data-eng-queue \
  --set dagsterCloud.agentQueues[1]=ml-queue \
  --set dagsterCloud.includeDefaultQueue=false
```

**Best Practice for Mixed Serverless + Hybrid**:
```bash
# Deploy hybrid agents with includeDefaultQueue=false
# This ensures serverless handles all default queue runs
helm install dagster-agent dagster-cloud/dagster-cloud-agent \
  --set dagsterCloud.agentQueues[0]=hybrid-queue \
  --set dagsterCloud.includeDefaultQueue=false
```

Then in your locations:
```yaml
# This runs on serverless (no agent_queue = default queue)
- location_name: serverless-location
  code_source: ...

# This runs on hybrid agents (explicitly routed to hybrid-queue)
- location_name: hybrid-location
  code_source: ...
  build:
    registry: ghcr.io/...
  agent_queue: hybrid-queue  # Routes to hybrid agents
```

---

## Repository Structure Patterns

### Pattern 1: Separate dagster_cloud.yaml Files (This Repo)

**Structure**:
```
/
  .github/workflows/
    deploy-serverless.yml
    deploy-hybrid.yml
  code_locations/
    serverless-location/
      dagster_cloud.yaml      ← Location-specific YAML
      pyproject.toml
      setup.py
      src/
    hybrid-location/
      dagster_cloud.yaml      ← Location-specific YAML
      Dockerfile
      pyproject.toml
      src/
```

**Pros**:
- ✅ Clear separation between locations
- ✅ Each location is self-contained
- ✅ Easy to understand for demos
- ✅ Can have separate workflows per location
- ✅ Easier to deploy locations independently

**Cons**:
- ❌ More workflow files to maintain
- ❌ Not the "standard" Dagster Cloud pattern
- ❌ Slightly more complex GitHub Actions setup

**When to use**:
- Demonstrating both deployment types
- Locations are truly independent
- Different teams own different locations

### Pattern 2: Single dagster_cloud.yaml at Root (Standard Monorepo)

**Structure**:
```
/
  dagster_cloud.yaml          ← Single YAML with all locations
  .github/workflows/
    deploy.yml                ← Single unified workflow
  code_locations/
    serverless-location/
      pyproject.toml
      setup.py
      src/
    hybrid-location/
      Dockerfile
      pyproject.toml
      src/
```

**dagster_cloud.yaml**:
```yaml
locations:
  # Serverless location (no build.registry)
  - location_name: serverless-location
    code_source:
      package_name: serverless_location.definitions
    working_directory: ./code_locations/serverless-location/src/

  # Hybrid location (has build.registry)
  - location_name: hybrid-location
    code_source:
      package_name: hybrid_location.definitions
    working_directory: ./code_locations/hybrid-location/src/
    build:
      registry: ghcr.io/myorg/myrepo/hybrid-location
    agent_queue: hybrid-queue
```

**Pros**:
- ✅ Standard Dagster Cloud monorepo pattern
- ✅ Single workflow, less duplication
- ✅ Easier to see all locations at a glance
- ✅ Simpler mental model

**Cons**:
- ❌ All locations deploy together (less granular control)
- ❌ Harder to have location-specific CI/CD logic

**When to use**:
- Production monorepos
- Locations managed by same team
- Want unified deployment process

### Pattern 3: Hybrid Approach

**Structure**:
```
/
  dagster_cloud.yaml          ← Defines all locations
  .github/workflows/
    deploy-serverless.yml     ← Path-triggered: serverless-location/**
    deploy-hybrid.yml         ← Path-triggered: hybrid-location/**
  code_locations/
    serverless-location/
    hybrid-location/
```

**Pros**:
- ✅ Single source of truth for location config
- ✅ Independent deployment workflows
- ✅ Path-based triggers for efficiency

**Cons**:
- ❌ Need to keep workflow paths in sync with locations
- ❌ More complex workflow logic

---

## GitHub Actions Patterns

### Pattern A: One Workflow Per Location (This Repo)

**Files**:
- `.github/workflows/deploy-serverless.yml`
- `.github/workflows/deploy-hybrid.yml`

**Workflow Triggers**:
```yaml
# deploy-serverless.yml
on:
  push:
    branches: [main]
    paths:
      - 'code_locations/serverless-location/**'
      - '.github/workflows/deploy-serverless.yml'

# deploy-hybrid.yml
on:
  push:
    branches: [main]
    paths:
      - 'code_locations/hybrid-location/**'
      - '.github/workflows/deploy-hybrid.yml'
```

**Pros**:
- ✅ Only builds what changed
- ✅ Clear separation of concerns
- ✅ Can use different Actions versions per location
- ✅ Independent deployment schedules

**Cons**:
- ❌ Duplicate workflow configuration
- ❌ More files to maintain

**Best for**:
- Separate teams owning different locations
- Different deployment requirements per location
- Need to version workflows independently

### Pattern B: Single Unified Workflow

**File**: `.github/workflows/deploy.yml`

**Approach 1: Build Everything**
```yaml
on:
  push:
    branches: [main]

jobs:
  deploy:
    steps:
      # Initialize Dagster Cloud session (reads all locations)
      - uses: dagster-io/dagster-cloud-action/actions/utils/ci-init@v1.11.9

      # Build all locations (PEX or Docker based on config)
      - uses: dagster-io/dagster-cloud-action/actions/utils/dagster-cloud-cli@v1.11.9
        with:
          command: "ci build"

      # Deploy all locations
      - uses: dagster-io/dagster-cloud-action/actions/utils/dagster-cloud-cli@v1.11.9
        with:
          command: "ci deploy"
```

**Approach 2: Conditional Builds Based on Changes**
```yaml
jobs:
  detect-changes:
    outputs:
      serverless: ${{ steps.filter.outputs.serverless }}
      hybrid: ${{ steps.filter.outputs.hybrid }}
    steps:
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            serverless:
              - 'code_locations/serverless-location/**'
            hybrid:
              - 'code_locations/hybrid-location/**'

  deploy-serverless:
    needs: detect-changes
    if: needs.detect-changes.outputs.serverless == 'true'
    steps:
      # Build and deploy serverless location

  deploy-hybrid:
    needs: detect-changes
    if: needs.detect-changes.outputs.hybrid == 'true'
    steps:
      # Build and deploy hybrid location
```

**Approach 3: Parse YAML and Route Dynamically**
```yaml
jobs:
  deploy:
    steps:
      # Parse dagster_cloud.yaml to detect locations
      - name: Parse locations
        id: parse
        run: |
          # Read YAML, check for build.registry field
          # Set outputs for which builds to run

      # Conditional PEX build
      - if: steps.parse.outputs.has_pex_locations == 'true'
        run: |
          cd code_locations/serverless-location
          $DAGSTER_CLOUD_PEX -m dagster_cloud_cli.entrypoint ci build \
            --build-strategy=python-executable

      # Conditional Docker build for hybrid
      - if: steps.parse.outputs.has_hybrid_locations == 'true'
        run: |
          # Build Docker image
          # Push to registry
          # Register with Dagster Cloud
```

**Pros**:
- ✅ Single workflow to maintain
- ✅ DRY (Don't Repeat Yourself)
- ✅ Easier to update Actions versions

**Cons**:
- ❌ More complex conditional logic
- ❌ Harder to debug
- ❌ All locations share same Actions versions

**Best for**:
- Single team managing all locations
- Want unified deployment process
- Locations have similar requirements

### Pattern C: Matrix Builds

**File**: `.github/workflows/deploy.yml`

```yaml
jobs:
  deploy:
    strategy:
      matrix:
        include:
          - location: serverless-location
            path: code_locations/serverless-location
            build_strategy: python-executable

          - location: hybrid-location
            path: code_locations/hybrid-location
            build_strategy: docker
            registry: ghcr.io/myorg/myrepo/hybrid-location

    steps:
      - name: Build ${{ matrix.location }}
        working-directory: ${{ matrix.path }}
        run: |
          if [ "${{ matrix.build_strategy }}" == "python-executable" ]; then
            # PEX build
          else
            # Docker build
          fi
```

**Pros**:
- ✅ DRY configuration
- ✅ Easy to add new locations
- ✅ Parallel builds

**Cons**:
- ❌ Builds everything on every push (unless filtered)
- ❌ Less readable for newcomers

**Best for**:
- Many locations with similar patterns
- Want parallel builds
- Configuration-driven approach

---

## Recommendations

### For This Demo Repository

**Current Setup** (Pattern 1 + Pattern A):
- ✅ Separate `dagster_cloud.yaml` per location - clear for demos
- ✅ Separate workflows - easy to understand each deployment type
- ✅ Path-based triggers - only builds what changes

**Why this works well for demos**:
1. **Clear Examples**: Each location is completely self-contained
2. **Easy to Explain**: "This is a serverless location, this is a hybrid location"
3. **Independent**: Can show one without the other
4. **Realistic**: Mirrors how some customers actually structure repos

### For Production Monorepos

**Recommended** (Pattern 2 + Pattern B):
- Single `dagster_cloud.yaml` at root
- Single unified workflow
- Conditional builds based on path changes

**Why this is better for production**:
1. **Standard Pattern**: Matches Dagster Cloud documentation
2. **Maintainability**: One workflow to update
3. **Atomic Deploys**: All locations deploy together (consistent state)
4. **Simpler**: Less moving parts

### Migration Path

If you start with the demo pattern (separate YAMLs) and want to migrate:

1. **Merge YAMLs**:
   ```bash
   # Combine both dagster_cloud.yaml files into root
   cat code_locations/*/dagster_cloud.yaml > dagster_cloud.yaml
   # Update working_directory paths to include code_locations/
   ```

2. **Update Workflows**:
   - Delete separate workflows
   - Create single unified workflow
   - Point to root dagster_cloud.yaml

3. **Test**:
   ```bash
   # Validate merged YAML
   dagster-cloud ci check --project-dir . --dagster-cloud-yaml-path dagster_cloud.yaml
   ```

---

## Key Takeaways

### Distinguishing Serverless vs Hybrid

**The definitive indicator**: Presence of `build.registry` field in dagster_cloud.yaml

```yaml
# Serverless (no build.registry)
- location_name: my-serverless
  code_source: ...

# Hybrid (has build.registry)
- location_name: my-hybrid
  code_source: ...
  build:
    registry: ghcr.io/...  # ← This makes it hybrid!
```

### Agent Queues

- **Purpose**: Route code locations to specific agents/infrastructure
- **Default behavior**: Omitting `agent_queue` uses the default queue (not necessarily serverless!)
- **`includeDefaultQueue` setting**: Critical for mixed environments - set to `false` on hybrid agents to prevent them from processing default queue runs
- **Best practice for serverless + hybrid**: Deploy hybrid agents with `includeDefaultQueue=false` so serverless handles default queue
- **Hybrid deployments**: Can specify `agent_queue` to route to specific agents, or omit to use default queue
- **Queue routing**: Determined by which agents are configured to serve which queues
- **Flexibility**: Can have multiple queues for different workload types, environments, or teams

### GitHub Actions

- **Separate workflows**: Better for demos, independent teams, or different requirements
- **Unified workflow**: Better for production, single team, consistent deployment
- **Choice depends on**: Team structure, deployment complexity, and maintenance preferences

---

## Additional Resources

- [Dagster Cloud Hybrid Deployment Docs](https://docs.dagster.io/dagster-cloud/deployment/hybrid)
- [Dagster Cloud Serverless Deployment Docs](https://docs.dagster.io/dagster-cloud/deployment/serverless)
- [Agent Configuration](https://docs.dagster.io/dagster-cloud/deployment/agents)
- [dagster_cloud.yaml Reference](https://docs.dagster.io/dagster-cloud/managing-deployments/dagster-cloud-yaml)
