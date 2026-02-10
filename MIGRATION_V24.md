# OpenClaw V2.4 Migration Guide

**Upgrading from V2.3 to V2.4**

---

## What's New

### Observational Memory (PAOM) 🆕

V2.4 introduces Mastra-inspired Observational Memory:

- **Observer Agent**: Extracts observations when messages exceed threshold
- **Reflector Agent**: Condenses observations when observations exceed threshold
- **Emoji Prioritization**: 🔴 (critical), 🟡 (important), 🟢 (info)
- **Three-Date Temporal Tracking**: Observation date, referenced date, relative time
- **94.87% LongMemEval accuracy**

### Enhanced ALMA 🔬

- Better documentation
- Integration examples
- Unified memory system

---

## Migration Steps

### 1. Initialize Observational Memory

```bash
# Initialize PAOM database
bash scripts/init-observational-memory.sh
```

### 2. Update Your Code

**V2.3 (old)**:
```python
from openclaw.memory import Memory
```

**V2.4 (new)**:
```python
from openclaw.observational_memory import ObservationalMemory
from openclaw.memory import UnifiedMemorySystem
```

### 3. Update Configuration

If you have custom memory configuration, update it:

```python
from openclaw.observational_memory import ObservationConfig

config = ObservationConfig(
    observation_threshold=30000,  # 30k tokens
    reflection_threshold=40000,   # 40k tokens
)
```

### 4. Test

```python
from openclaw.observational_memory import ObservationalMemory

# Initialize
om = ObservationalMemory()

# Test
record = om.process_messages(thread_id, messages)
context = om.get_context(thread_id)
stats = om.get_stats(thread_id)
```

---

## Breaking Changes

### New Files

| File | Purpose |
|------|---------|
| `.openclaw/observational_memory/__init__.py` | PAOM main system |
| `.openclaw/observational_memory/types.py` | PAOM configuration |
| `.openclaw/observational_memory/token_counter.py` | Token counting |
| `.openclaw/observational_memory/observer_agent.py` | Observation extraction |
| `.openclaw/observational_memory/reflector_agent.py` | Observation condensation |
| `.openclaw/memory/__init__.py` | Unified memory system |
| `.openclaw/memory/unified_system.py` | Unified system implementation |
| `scripts/init-observational-memory.sh` | Initialize PAOM database |
| `.openclaw/docs/OBSERVATIONAL_MEMORY.md` | PAOM documentation |

### Modified Files

| File | Changes |
|------|----------|
| `README.md` | Updated with V2.4 features |
| `V2.4_RELEASE_NOTES.md` | New changelog |

---

## Rollback Plan

If V2.4 has issues:

```bash
# Rollback to V2.3
git checkout v2.3
git branch -D v2.4

# Clear Observational Memory database
rm -f .openclaw/observational_memory.db

# Restart services
docker-compose restart
```

---

**Version**: 2.4 Migration Guide | **Last Updated**: 2026-02-10
