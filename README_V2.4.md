# OpenClaw V2.4 - ALMA-Enhanced

This is OpenClaw V2.4 with ALMA meta-learning integration.

## What's New?

- ✅ Meta-learning for optimal memory designs
- ✅ Dynamic consensus weights
- ✅ A/B testing framework
- ✅ Performance tracking
- ✅ Rollback safety

## Quick Start

```bash
# Import ALMA
import sys
sys.path.insert(0, '.openclaw/alma')
from alma import get_consensus, TradingMemory, MetaLearningAgent

# Use ALMA
consensus = get_consensus()
weights = consensus.get_weights(['StrategyA', 'StrategyB'])
```

## Documentation

See `monitoring/memory_templates/OPENCLAW_V24_ALMA_ENHANCED.md` for full documentation.
