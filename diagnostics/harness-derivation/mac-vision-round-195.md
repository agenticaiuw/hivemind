# Harness derivation — mac-vision — round 195

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide the owner with a durable, dynamic prioritized Mac task list that integrates the owner's typed tasks, reminders, calendar events, and active workflows with deadlines, dependencies, and topical urgency."
- **useful because:** The owner currently lacks a cohesive prioritized task list on the Mac, limiting agent effectiveness. Such a task list would enable better planning, action prioritization, and status reporting across all Mac-related work from a single source of truth.
- **path:** mac-planner → mac-vision → mac-terminal
- **model tier:** background
- **latency:** seconds-level
- **cost:** low, mostly local computation and store reads
- **security:** Needs to keep personal task details private and respect existing permission boundaries. Requires no external transmission of task content without owner's explicit consent.
- **missing:** Task capture from voice and text inputs into a durable canonical task store that agents can read/write.; Semantic ranking model aware of deadlines, dependencies, and priorities.; UI integration to view and manage this list directly on Mac surfaces.

### "Implement a Mac workflow recovery and resume system that uses both the official job/workbench state and the actual on-screen UI state observed by mac-vision, enabling robust continuation after interruptions or failures."
- **useful because:** Workflows currently cannot be resumed after interruption because there is no connection between promised and actual UI or file system state. Combining job bookkeeping with visual state improves accuracy and reduces lost progress.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to a minute
- **cost:** medium due to UI state processing and job reconciliation
- **security:** Requires trusted internal access to Mac accessibility data and job states to avoid leaking user actions or data externally.
- **missing:** A mechanism to diff and reconcile UI state from accessibility tree with job-handoff state.; Persisted reconciliation metadata and conflict resolution policies.; Integration with the mac_run_actions tool for active intervention based on reconciliation.

### "Add a browser harness that supports durable authenticated sessions, privacy-protected page watchers, self-healing command queues, active tab context events, and cross-surface browser health reporting."
- **useful because:** The owner uses multiple authenticated browser sessions for private and public tasks. The system needs reliable, resumable browser control with privacy bounds and liveness monitoring for stable operation.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** medium due to cross-surface state and privacy processing
- **security:** Must strictly separate private data, redact sensitive fields, and ensure no external leaks without explicit consent.
- **missing:** Durable browser session persistence and recovery recipes.; Active tab event streams with selection capture.; Privacy classification and redaction logic.; Cross-surface lease and health management protocols.

### "Provide the owner a live, reconciled Mac UI state checker for any active workflow step that compares the promised UI state from the job/workbench ledger with the actual visible accessibility tree, detecting and reporting divergence early to enable smarter recovery and action."
- **useful because:** Currently, workflows on the Mac may get stuck or lost when the actual UI state diverges from the job ledger's promise, causing wasted effort and frustration. A tool that continuously reconciles promised versus actual UI state can alert and enable corrective actions early, improving reliability and trust.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** low to medium depending on reconciliation complexity
- **security:** Requires trusted local access to sensitive UI data and job records without leaking outside. All state remains local and ephemeral.
- **missing:** A reconciliation engine that compares job ledger UI expectations with live accessibility tree snapshots.; A reporting mechanism in the agent UI and logs for divergences and suggested recovery steps.; Test harness and error injection for progressive improvement.

### "Enable the owner to designate selective gesture triggers on the pendant's physical buttons (single, double, long press) mapped to context-sensitive Mac actions or scripts, with priority arbitration among concurrent consumers."
- **useful because:** The physical button on the pendant is a scarce and valuable input resource. Allowing the owner to allocate gesture triggers dynamically and contextually across multiple Mac-related agents and workflows maximizes its utility without conflicts or accidental activations.
- **path:** pendant → mac-planner → mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** low, leveraging existing physical button event logging and dispatch mechanisms
- **security:** Requires secure and exclusive management of physical trigger mapping assignments, with explicit owner overrides to prevent unauthorized hijacking.
- **missing:** A multiplexed gesture interpreter on the pendant that handles assignment and arbitration.; Cross-surface protocol to announce, request, and release trigger mapping.; Fallback and conflict resolution policy with user feedback.


## Changes it proposed to its own stack

### `integration` — Add a persistent, inferred task priority and dependency graph layer that unifies owner-stated tasks, calendar events, reminders, and active workflows dynamically updated with contextual signals, priorities, and conflict detection.
- **owner gets:** The owner currently has tasks, calendar events, and reminders scattered with only crude priority, making juggling complex work difficult. A unified priority graph with inferred dependencies and conflicts will allow the owner and AI to focus on what matters and reduce cognitive load.
- effort: large, requiring significant design of graph model, heuristics, and API changes.  ·  risk: Errors in inference might occasionally misprioritize work; mitigated by owner override and incremental roll-out.
- cost: Moderate, mostly storage and compute with occasional user prompts.  ·  latency: Low, background updates.
- security: Sensitive task data stays local; no new external exposures beyond current task store.
- depends on: GET /memory/facts; GET /day-plan; GET /workbench/contexts


## What it asked for

_Nothing._
