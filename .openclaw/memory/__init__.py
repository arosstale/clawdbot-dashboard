# OpenClaw Memory System Documentation

This directory contains documentation for OpenClaw's memory systems.

---

## Memory Architecture

OpenClaw V2.4 uses a **multi-tier memory architecture**:

```
┌─────────────────────────────────────────────────────────┐
│              OpenClaw Memory System                 │
├────────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │     Ephemeral │  │   Working       │  │  Durable     │ │
│  │ (Session)     │  │ (Observational) │  │ (PostgreSQL) │ │
│  │              │  │   Memory        │  │             │ │
│  └──────────────┘  └──────────────────┘  └────────────┘ │
│                     │                          │
│          ┌──────────────────────┐          │
│          │   Actor Inference         │          │
│          │   (Main Agent)            │          │
│          └──────────────────────┘          │
│                                         │
└─────────────────────────────────────────────────┘
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

### Performance

| Model | LongMemEval | Baseline |
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

---

## ALMA

Dynamic consensus weights and meta-learning for strategy optimization.

### Features

- ✅ **Dynamic weights**: Real-time adjustment based on performance
- ✅ **Meta-learning**: Automatic design discovery
- ✅ **Regime awareness**: Different weights for trending vs ranging markets
- ✅ **Performance tracking**: Real-time metrics with improvement alerts

### Usage

```python
from openclaw.alma import get_consensus, TradingMemory

# Get consensus
consensus = get_consensus(enabled=True)

# Get weights
weights = consensus.get_weights(['StrategyA', 'StrategyB'])

# Record performance
memory = TradingMemory()
memory.update_strategy_performance('StrategyA', {
    'win_rate': 75.0,
    'avg_return': 3.5,
    'max_drawdown': -2.0,
    'num_trades': 50,
    'regime': 'TRENDING'
})

# Get best strategies
best = memory.get_best_strategies(limit=5)
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

## QMD (Optional)

Hybrid BM25 + Vector search for ultra-fast semantic retrieval.

### Features

- ✅ **Local-first**: Zero cloud dependency with Bun + node-llama-cpp
- ✅ **Hybrid search**: Vector (70%) + BM25 (30%) for precision
- ✅ **Auto-indexing**: Real-time indexing of `.openclaw/memory/` folder
- ✅ **Context prevention**: Offloads search to prevent context choke on Pi hardware

---

## PostgreSQL

Durable storage for historical data and agent reflections.

### Setup

```bash
# Start PostgreSQL sidecar
docker-compose -f docker-compose.postgres.yml up -d

# Check health
docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_elite

# Access pgadmin at http://localhost:5050
# Default: admin@openclaw.local / admin_change_me
```

### Schema

See `docker-compose.postgres.yml` for complete schema.

---

## Integration Examples

### Trading Agent with PAOM + ALMA

```python
from openclaw.observational_memory import ObservationalMemory
from openclaw.alma import get_consensus

# Initialize
om = ObservationalMemory()
alma = get_consensus()

# Process trade signal
messages = [
    {"role": "user", "content": "Buy BTC at $50k", "timestamp": "2026-02-10T10:00:00Z"},
]
record = om.process_messages("trading-thread", messages)

# Get weights
weights = alma.get_weights(['StrategyA', 'StrategyB'])

# Build context
context = f"""
{om.get_context("trading-thread")}

## Strategy Weights
{format_weights(weights)}
"""

# Generate response
response = llm.generate(context)
```

---

## Configuration

### Observational Memory

```python
from openclaw.observational_memory import ObservationConfig

config = ObservationConfig(
    observation_threshold=30000,  # 30k tokens
    reflection_threshold=40000,   # 40k tokens
    observer_temperature=0.3,      # Extraction temperature
    reflector_temperature=0.0,      # Condensation temperature
)
```

### ALMA

```python
from openclaw.alma import get_consensus

consensus = get_consensus(
    enabled=True,
    message_tokens=30000,
    observation_tokens=40000
)
```

---

## Best Practices

1. **Use Unified Memory System** - Combines all systems
2. **Monitor token usage** - Avoid context window overflow
3. **Regular reflections** - Clean old observations
4. **Track performance** - Enable meta-learning improvements
5. **Use appropriate tier** - Ephemeral for session, Durable for history

---

📚 **For detailed documentation, see individual component docs.**
