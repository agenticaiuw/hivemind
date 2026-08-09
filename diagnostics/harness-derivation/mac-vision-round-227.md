# Harness derivation — mac-vision — round 227

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Can my Mac-vision agent read my current priority tasks and dynamically execute them on my Mac using UI automation?"
- **useful because:** Currently, mac-vision lacks a task queue and prioritization. This capability lets it read the owner's actual task facts, rank them, and dispatch concrete Mac or browser actions via mac_run_actions or browser_run_actions. It enables deliberate, goal-driven Mac interactions aligned with owner priorities.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** under 10 seconds per task action batch
- **cost:** low API calls per invocation, mostly logic and planned UI actions locally
- **security:** Permissions to control the Mac via accessibility are needed. All actions must confirm destructive steps before execution.
- **missing:** A task queue or prioritization system for Mac UI automation tasks; Integration layer to select and dispatch mac_run_actions or browser_run_actions based on task type.

### "How to chain and recover multi-step Mac UI workflows for mac-vision?"
- **useful because:** mac_delegate supports multi-step tasks but lacks formal chaining or recovery strategies. This capability defines a protocol to compose UI automation steps, handle failures by rollback or retries, and allow resumption after interruptions. It improves reliability and robustness of complex UI workflows.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** depends on workflow complexity, incremental steps
- **cost:** main cost is logic and state management, minimal API calls
- **security:** Recovery steps must be safe and reversible where possible, or require explicit owner approval for destructive operations.
- **missing:** A stateful workflow chaining and recovery protocol for Mac UI automation.; Integration with mac_delegate and mac_run_actions.

### "Can mac-vision provide live readiness and status monitoring for its computer use loop and permissions?"
- **useful because:** Before enabling proactive UI control, continuous confirmation of macOS accessibility permissions, input event delivery, and loop readiness is essential. A live dashboard or alert system prevents unauthorized or failed automation actions and lets the owner trust the system's state.
- **path:** mac-vision → dashboard
- **model tier:** background
- **latency:** real-time updates within seconds.
- **cost:** low, mostly state polling and condition check logic
- **security:** Exposing permissions and readiness state must be securely accessed, no control exposure.
- **missing:** A live readiness check system integrated with vision-loop/preflight and other OS permission monitoring.; Dashboard or UI surface to display status and alerts.


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secondary physical input button or multi-gesture hardware input to the pendant to allow mac-vision agent a secure, unambiguous physical token for active user confirmations and transaction approvals during complex UI workflows.
- **owner gets:** The single existing user button is overloaded and cannot support distinct gestures reliably for different confirmation types. A dedicated button or input expands mac-vision's interaction capabilities with minimal latency and no screen focus loss.
- effort: Medium: requires design, firmware changes, and mechanical integration into future pendant hardware versions.  ·  risk: Potential hardware complexity and increased cost. Must ensure no accidental confirmations; physical button must be distinct and purposeful.
- cost: Additional hardware cost of button and minimal power draw increase; negligible API cost  ·  latency: No latency; improves confirmation and interaction speed.
- security: Improves security by enabling explicit physical confirmation rather than gesture guessing.

### `integration` — Implement a robust multi-step UI interaction orchestration layer in mac-vision agent that chains mac_delegate and mac_run_actions calls with built-in failure detection, rollback, and resumption capabilities connected to owner state and memory facts.
- **owner gets:** This orchestration ensures that complex multi-step workflows are executed reliably, can recover gracefully from interruptions or errors, and remain aligned with owner intent without redundant or failed actions.
- effort: Medium to high: requires design, state management, and integration with existing agent workflows and memory.  ·  risk: Increased system complexity and partial failure management complexity. Must handle edge cases where UI state changes externally or owner intervenes.
- cost: Moderate software engineering effort; nominal runtime cost.  ·  latency: May add slight execution overhead during workflow steps.
- security: Needs careful permission and impact checks to prevent unsafe actions.
- depends on: mac_delegate; mac_run_actions; memory/facts


## What it asked for

_Nothing._
