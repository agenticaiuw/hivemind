# Harness derivation — mac-vision — round 230

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A prioritized persistent task queue and work claiming system for mac-vision that delivers structured, ranked UI automation tasks with deadlines and dependencies"
- **useful because:** The owner can assign and track what the mac-vision agent should do on their Mac, ensuring the most urgent and critical UI tasks get done reliably and transparently.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-perception
- **model tier:** realtime
- **latency:** seconds to decision
- **cost:** Low to moderate; mainly storage and messaging overhead, plus model evaluation per task prioritization
- **security:** Tasks contain sensitive UI instructions, so encryption and access control are essential. Risk of task injection or accidental destructive actions must be mitigated by confirmation and ownership checks.
- **missing:** task schema design with priorities and dependencies; UI automation task generator and verifier; Owner intent integration to populate and update tasks

### "A robust UI state verification and reconciliation system for mac-vision that compares planned UI actions against actual on-screen state and recovers from mismatches"
- **useful because:** This ensures the mac-vision UI automation loop operates reliably, can detect when actions failed or the UI changed unexpectedly, and can retry or roll back safely, improving trust and automation success rates.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** realtime
- **latency:** under 1 second per UI step check
- **cost:** Moderate; requires state capture and model evaluations per step, plus storage of UI snapshots for verification
- **security:** UI state may contain sensitive data; requires strong privacy controls and local processing to avoid leaks
- **missing:** UI state snapshot and hash system; Action-step result classification and rollback primitives; Integrations with workbench context verification

### "A consolidated owner intent interface that gathers priority task facts from memory, task state from workbench, and live calendar/reminder overview into a single read/write API for use by mac-vision and allied agents"
- **useful because:** The owner and system get a single source of truth for what is actively prioritized work on the Mac, making coordination of UI and background agent tasks more coherent and aligned with the owner's actual goals.
- **path:** mac-vision → mac-planner → faculty-judgement → owner
- **model tier:** realtime
- **latency:** seconds, no noticeable delay to owner
- **cost:** Low; mostly fetch and merge operations from existing stores, plus some model ranking logic
- **security:** Task and intent info may be private; requires access control and secure storage
- **missing:** Unified task fact and context projection reader; Write path to owner intent memory with proper validation and update rules


## Changes it proposed to its own stack

### `integration` — Integrate the mac-vision UI automation loop with the workbench contexts and job handoff primitives to enable seamless multi-agent workflow continuity and task recovery after interruptions
- **owner gets:** Owner benefits from tasks continuing cleanly across sessions, with progress verified on actual UI state, avoiding repeated manual recovery or lost work due to UI automation failures
- effort: Medium: Requires coordination between mac-vision state tracking and workbench job management APIs; UI state verification tooling needs to be developed  ·  risk: Potential synchronization bugs causing state mismatches or task duplication; recoverable by robust error detection and fallback flows
- cost: Moderate due to added API calls and state storage  ·  latency: Minimal impact on UI automation latency
- security: Requires secure status sharing and authenticated work claims to prevent task hijacking
- depends on: Enable mac-vision computerUse loop; Prioritized task queue for mac-vision


## What it asked for

_Nothing._
