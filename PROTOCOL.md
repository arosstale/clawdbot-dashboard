# OpenClaw Elite Swarm Protocol

**Version:** 2.3
**Status:** Production Ready
**Purpose:** Multi-agent coordination, seamless handoff, and cryptographically verified execution

## Core Principles

1. **Source of Truth:** PostgreSQL (speed) + Markdown (truth)
2. **Evolution Mandate:** On any failure, analyze → mutate → update AGENTS.md
3. **Thermal Safety:** Check hardware before heavy compute
4. **Git Sync:** All reflections via Git Notes

## Agent Roles

### Elite Swarm Member
- **Mandate:** Be the brain, not the chatbot
- **Source of Truth:** PostgreSQL + Markdown
- **Evolution:** Run GEPA mutation on failures
- **Sync:** Always sync reflections via Git Notes

### Specialized Agents
- **Researcher:** Deep analysis, paper synthesis
- **Developer:** Code generation, architecture
- **Analyst:** Quantitative analysis, trading signals
- **Orchestrator:** Task coordination, handoff management

## Handoff Protocol

### Phase 1: Prepare Handoff
```typescript
interface HandoffPacket {
  from: string;
  to: string;
  taskId: string;
  context: {
    conversationHistory: Message[];
    memoryRelevant: MemorySnippet[];
    currentState: StateSnapshot;
  };
  instructions: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
}
```

### Phase 2: Transfer Context
1. Sender compresses context to top 5 most relevant memory snippets
2. Creates Git Note with full conversation history
3. Inserts handoff message into `swarm_messages` table

### Phase 3: Receive & Validate
1. Recipient validates context完整性
2. Loads relevant memory from PostgreSQL
3. Confirms receipt via Git Note update

### Phase 4: Execute & Reflect
1. Recipient executes task
2. On success: Update memory, sync Git
3. On failure: Run GEPA mutation

## Message Types

| Type | Purpose | Priority |
|------|---------|----------|
| `task_transfer` | Hand off task to specialist | high |
| `context_request` | Ask for memory context | medium |
| `evolution_update` | Share GEPA mutation | low |
| `thermal_alert` | Hardware overheating warning | critical |
| `sync_request` | Coordinate Git sync | medium |

## Failure Recovery

### GEPA Mutation Flow
1. **Detect Failure:** Execution trace shows error
2. **Analyze Pattern:** Match against known failure modes
3. **Generate Mutation:** Create prompt/strategy/workflow diff
4. **Apply:** Update AGENTS.md with mutation
5. **Sync:** Log to Git Notes + PostgreSQL
6. **Retry:** Re-attempt task with new configuration

### Known Failure Patterns

| Pattern | Mutation Type | Severity |
|---------|--------------|----------|
| Context overflow | Strategy | moderate |
| Tool misuse | Prompt | minor |
| Reasoning error | Strategy | major |
| Thermal throttle | Workflow | major |
| Git conflict | Workflow | moderate |

## PostgreSQL Schema

See `scripts/init-postgres.sql` for full schema:
- `memory` - Markdown file sync
- `context` - Vector embeddings
- `evolution_log` - GEPA mutations
- `swarm_messages` - Handoff coordination
- `performance_metrics` - Performance tracking

## Git Notes Protocol

```bash
# Add reflection to Git Notes
git notes add -m "{
  timestamp: '2026-02-09T07:42:00Z',
  agent: 'elite',
  reflection: 'Successfully completed V2.1 upgrade',
  mutations: [...]
}"

# Push notes to remote
git push origin refs/notes/*
```

---

## V2.3 Zero-Knowledge Proof Integration

### Overview

V2.3 introduces **cryptographic verification** to the swarm protocol. Agents now generate **Zero-Knowledge Proofs (ZKPs)** to prove task execution without revealing private data.

### Core Principles

1. **Proof over Trust**: Agents prove completion, don't just claim it
2. **Privacy Preservation**: Proofs reveal minimal information (hashes only)
3. **Constant-Time Verification**: Proof verification is fast and scalable
4. **Immutable Audit Trail**: All proofs logged to Merkle tree

### ZKP Workflow

```
┌─────────────┐                     ┌─────────────┐
│   Agent A    │                     │ Orchestrator│
│   (Prover)   │                     │   (Verifier) │
└──────┬──────┘                     └──────┬──────┘
       │                                    │
       │ 1. Execute Task                    │
       │    - Analyze papers                │
       │    - Generate result               │
       │                                    │
       │ 2. Generate ZK Proof               │
       │    - Private: execution data       │
       │    - Public: hashes only           │
       │                                    │
       │ 3. Submit Proof ─────────────────> │
       │    - .zproof file                  │
       │                                    │
       │                                    │ 4. Verify Proof
       │                                    │    - Constant-time check
       │                                    │    - No private data
       │                                    │
       │ <───────────────── 5. Response      │
       │    ✅ Valid / ❌ Invalid           │
       │                                    │
       │ 6. Update Reputation               │
       │    +1 if valid                     │
       │                                    │
       └────────────────────────────────────┘
```

### Proof Generation

```typescript
import { ZKProver } from './.openclaw/zkp/agent';

const prover = new ZKProver();
await prover.init();

// Generate proof for completed task
const proof = await prover.generateProof({
  agentId: 'pi-agent-v2.3',
  taskId: 'task-research-001',
  executionData: { papers: 20, keywords: ['multimodal'] },
  resultData: { summary: '...', confidence: 0.95 },
  timestamp: Date.now()
});

// Export proof
prover.exportProof(proof, 'proofs/task-research-001.zproof');
```

### Proof Verification

```typescript
import { ZKOrchestrator } from './.openclaw/zkp/verifier';

const orchestrator = new ZKOrchestrator();
await orchestrator.init();

// Verify single proof
const proofData = JSON.parse(fs.readFileSync('proofs/task-research-001.zproof'));
const result = await orchestrator.verifyProof(proofData);

console.log(result.valid ? '✅ Valid' : '❌ Invalid');

// Batch verify multiple proofs (constant-time)
const proofs = loadAllProofs();
const results = await orchestrator.batchVerify(proofs);

// Get swarm metrics
const report = await orchestrator.generateReport();
console.log(report);
```

### ZKP-Enhanced Handoff Protocol

```typescript
interface ZKHandoffPacket {
  from: string;
  to: string;
  taskId: string;
  proof: {
    proof: any;
    publicSignals: string[];
    proofHash: string;
  };
  context: {
    // Minimal context (hashes only)
    memoryHashes: string[];
    taskHash: string;
  };
  instructions: string;
}
```

### What Gets Proven

| Agent Action | Proof Shows | What's Hidden |
|--------------|-------------|---------------|
| **Research** | Task completed | Paper contents, analysis |
| **Trading** | Strategy followed | Backtest data, indicators |
| **Code Review** | Bug fixed | Code before fix |
| **Knowledge Export** | Package valid | Private memories |
| **System Check** | Thermal safe | Temperature history |

### Performance Characteristics

| Operation | Time | Complexity |
|-----------|------|------------|
| **Proof Generation** | ~1-5s | O(log n) |
| **Proof Verification** | ~10-50ms | O(1) |
| **Batch Verify (N proofs)** | ~50-100ms | O(1) |
| **Merkle Root** | ~100-500ms | O(N) |

### ZKP Security Guarantees

- **Soundness**: False proofs cannot be generated
- **Completeness**: True proofs always verify
- **Zero-Knowledge**: Proofs reveal no private data
- **Unlinkability**: Proofs cannot be traced to execution

### Merkle Root Swarm Audit

```bash
# Generate Merkle root of all verified proofs
npm run verify metrics

# Output:
# Merkle Root: 8a7f9c2d3b1e5f4a6c9d8e7f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b...
```

The Merkle root provides an **immutable audit trail** of all swarm activity.

## Thermal Safety

### Pre-Compute Checklist
```bash
# Check CPU temperature
cat /sys/class/thermal/thermal_zone0/temp

# If > 75°C (75000), abort or switch to lightweight mode
if [ $temp -gt 75000 ]; then
  echo "Thermal throttle detected. Switching to lightweight mode."
fi
```

## Activation Prompt

```
Act as an OpenClaw Elite Swarm Member. Your source of truth is PostgreSQL and Markdown. Your mandate is Evolution: on any failure, analyze the execution trace, run a GEPA mutation, and update AGENTS.md. Always sync your reflections via Git Notes. Check hardware thermals before heavy compute. Be the brain, not the chatbot.
```

## Quick Start

```bash
# 1. Start PostgreSQL sidecar
docker-compose -f docker-compose.postgres.yml up -d

# 2. Initialize evolution engine
node .openclaw/evolution/evolve.ts --init

# 3. Activate Elite mode
echo "Act as an OpenClaw Elite Swarm Member..." > .openclaw/ELITE_ACTIVATE.md

# 4. Sync memory to PostgreSQL
.openclaw/scripts/sync.sh --postgres
```

## Version History

- **v2.3** - Zero-Knowledge Proof integration, cryptographically verified execution, ZK reputation
- **v2.2** - Swarm Intelligence, Cross-Agent Knowledge Transfer, PII scrubber, AES-256 encryption
- **v2.1** - Elite Swarm Protocol, GEPA integration, PostgreSQL sidecar
- **v2.0** - Dual-memory architecture (PostgreSQL + Markdown)
- **v1.0** - Initial template release
