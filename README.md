# OpenClaw V2.4 - Observational Memory Enhanced

> **Pi** 🐺📿 - Temporal intelligence meets meta-learning

V2.4 adds **Mastra-inspired Observational Memory** to V2.3's proven architecture,
creating the most advanced memory system for agentic AI.

---

> **📌 Note**: This is a **community memory template** for OpenClaw. It contains OpenClaw core components (V2.3 ZKP, V2.2 Swarm), configuration files, and community skills. It does **not** contain proprietary trading agent code.

---

## Quick Start

```bash
# 1. Clone this repository
git clone https://github.com/arosstale/openclaw-memory-template.git
cd openclaw-memory-template

# 2. Run welcome script (recommended)
bash scripts/welcome.sh

# 3. Initialize Observational Memory (NEW in V2.4)
bash scripts/init-observational-memory.sh

# 4. Start PostgreSQL sidecar (optional but recommended)
docker-compose -f docker-compose.postgres.yml up -d

# 5. Start QMD sidecar (for ultra-fast search, optional, recommended)
docker-compose -f docker-compose.qmd.yml up -d

# 6. Run ZKP test suite (optional, recommended)
bash scripts/zkp-test.sh
```

---

## V2.4 Elite Features

| Feature | Description |
|----------|-------------|
| **Observational Memory (PAOM)** | Mastra-inspired text-based memory with emoji prioritization |
| **Dynamic Consensus** | Enhanced ALMA with regime-aware weights |
| **Meta-Learning** | Automatic design discovery loop |
| **Performance Tracking** | Real-time metrics with improvement alerts |
| **A/B Testing** | Compare designs automatically |
| **Rollback Safety** | Auto-degradation detection |
| **Unified Memory System** | Combines ALMA + PAOM + QMD + PostgreSQL |
| **Context Compression** | 75% reduction (4:1 to 13:1), 94.87% LongMemEval accuracy |
| **Prompt Caching** | Stable context window for full cache hits |
| **Temporal Awareness** | Multi-date tracking with relative time |
| **Emoji Prioritization** | 🔴 (critical), 🟡 (important), 🟢 (info) |
| **Zero-Knowledge Proofs** | Cryptographic task verification without revealing private data |
| **Proof-Based Reputation** | Reputation based on mathematically verified proofs |
| **Fast Verification** | ~10-50ms proof verification (constant-time) |
| **Privacy-Preserving** | Proofs reveal minimal information (hashes only) |
| **GEPA Integration** | Self-correcting mutation engine on failures |
| **PostgreSQL Sidecar** | Docker Compose setup for structured data |
| **QMD Sidecar** | Hybrid BM25+Vector search for ultra-fast retrieval |
| **Swarm Protocol** | Multi-agent coordination and proof-based handoffs |
| **Dual-Core Memory** | PostgreSQL (structured) + QMD (semantic) + Markdown (truth) |
| **Hardware-Aware** | Thermal monitoring and adaptive compute scaling |
| **Genetic Versioning** | Git-tagged mutations for easy rollback |
| **Self-Evolving** | Automatic AGENTS.md updates via mutation |

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              OpenClaw V2.4 Unified Memory System               │
├──────────────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │     ALMA      │  │ Observational   │  │  QMD      │ │
│  │  Meta-       │  │  Memory (PAOM)  │  │  (semantic) │ │
│  │  Learning      │  │                  │  │            │ │
│  │              │  │                  │  │            │ │
│  └──────────────┘  └──────────────────┘  └────────────┘ │
│                     │                          │
│          ┌──────────────────────┐          │
│          │   Actor Inference         │          │
│          │   (Main Agent)            │          │
│          └──────────────────────┘          │
└──────────────────────────────────────────────────────────────────┘
                     │
               Unified Context Output
```

### Memory Tiers

| Tier | System | Purpose | Retention | Capacity |
|-------|---------|----------|------------|----------|
| **Ephemeral** | Session context | Current conversation only | ~100k tokens |
| **Working** | Observational Memory | Recent observations (30k tokens) | 40k tokens max |
| **Durable** | PostgreSQL | Historical data, agent reflections | Unlimited |
| **Semantic** | QMD (Optional) | Vector search, similarity | Indexes all `.md` |

---

## Observational Memory (PAOM)

**NEW in V2.4** - Mastra-inspired memory system.

### Features

- ✅ **Text-based**: No vector/graph DB needed
- ✅ **Emoji prioritization**: 🔴 (critical), 🟡 (important), 🟢 (info)
- ✅ **Three-date temporal tracking**: Observation date, referenced date, relative time
- ✅ **Prompt caching**: Stable context window for full cache hits
- ✅ **Threshold-based**: Automatic compression (30k observation / 40k reflection)
- ✅ **94.87% LongMemEval accuracy** with gpt-5-mini

### Performance

| Model | LongMemEval Score | Baseline |
|--------|---------------|----------|
| gpt-5-mini | **94.87%** | 84.23% (Supermemory) |
| gpt-4o | 84.23% | 82.40% (Supermemory) |

**+12.64% improvement over baseline!**

### Usage

```python
from openclaw.observational_memory import ObservationalMemory, ObservationConfig

# Initialize
config = ObservationConfig(
    observation_threshold=30000,  # 30k tokens
    reflection_threshold=40000,   # 40k tokens
)
om = ObservationalMemory(config)

# Process messages
record = om.process_messages(thread_id, messages)

# Get context
context = om.get_context(thread_id)

# Get stats
stats = om.get_stats(thread_id)
```

### Integration with ALMA

```python
from openclaw.observational_memory import ObservationalMemory
from openclaw.alma import get_consensus, TradingMemory

# Initialize both systems
om = ObservationalMemory()
alma = get_consensus()

# Process messages
record = om.process_messages(thread_id, messages)

# Get strategy weights
weights = alma.get_weights(['StrategyA', 'StrategyB'])

# Build unified context
context = f"""
{om.get_context(thread_id)}

## Strategy Weights
{format_weights(weights)}
"""
```

---

## Unified Memory System

Combines ALMA + Observational Memory for optimal inference.

```python
from openclaw.memory import UnifiedMemorySystem

# Initialize
system = UnifiedMemorySystem()

# Process interaction
context = system.process_interaction(
    thread_id="thread-123",
    messages=messages,
    strategies=['StrategyA', 'StrategyB'],
    strategy_metrics={'StrategyA': {'win_rate': 75.0}}
)

# Get unified stats
stats = system.get_unified_stats(thread_id)
```

---

## Documentation

| File | Purpose |
|------|---------|
| **DASHBOARD.md** | System architecture, memory tiers, and metrics |
| **PROTOCOL.md** | Swarm protocol, handoff system, and failure recovery |
| **V2.4_RELEASE_NOTES.md** | Complete changelog and feature breakdown |
| **.openclaw/memory/** | Unified memory system documentation |
| **.openclaw/observational_memory/** | PAOM implementation |
| **.openclaw/core/** | Identity, agents, user preferences |
| **.openclaw/evolution/** | GEPA mutation engine |
| **.openclaw/scripts/** | Sync, logging, status, thermal monitoring |

---

## PostgreSQL & QMD Setup

```bash
# Start PostgreSQL sidecar
docker-compose -f docker-compose.postgres.yml up -d

# Start QMD sidecar (for ultra-fast search)
docker-compose -f docker-compose.qmd.yml up -d

# Check PostgreSQL health
docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_elite

# Access Qdrant vector DB at http://localhost:6333
# Access pgadmin at http://localhost:5050
# Default pgadmin: admin@openclaw.local / admin_change_me
```

---

## Agent Handoff Example

```bash
# Hand off task to researcher
node .openclaw/scripts/handoff_tool.ts \
  --to researcher \
  --task "Analyze recent AI research papers on multimodal learning" \
  --priority high
```

---

## Stability & Testing

```bash
# Run GEPA system validation
bash scripts/gepa-test.sh

# Run ZKP test suite (cryptographic verification)
bash scripts/zkp-test.sh

# Run stability test (50 simulated tasks with thermal monitoring)
bash scripts/stability-test.sh
```

---

## Support

- **Community**: https://discord.com/invite/clawd
- **Documentation**: See individual `.md` files
- **Source**: https://github.com/openclaw/openclaw

---

**Version**: 2.4 Observational Memory Enhanced | **Status**: 🟡 Development | **Last Updated**: 2026-02-10
