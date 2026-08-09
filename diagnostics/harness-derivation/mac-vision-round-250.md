# Harness derivation — mac-vision — round 250

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to read a live accessibility-based UI hierarchy snapshot with action targets on the Mac screen."
- **useful because:** The owner could let mac-vision perceive exactly what UI controls are present and actionable in real time, allowing precise, safe, and verifiable UI manipulation remotely or by voice.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** 200ms to 1s per snapshot
- **cost:** Moderate API and processing cost, mostly local compute on Mac, lightweight data.
- **security:** The capability exposes internal UI structure; need strict permissions and privacy controls, plus safe sandboxing to prevent unintended control.
- **missing:** A new API route providing accessibility tree snapshots on demand or push, tightly integrated with current workbench contexts and jobs.; Mechanisms to plan against the accessibility tree, including focused control and synthetic events.

### "Integrate mac-vision with a persistent Mac UI state and workbench context reconciliation layer."
- **useful because:** mac-vision could verify that planned UI tasks have actually executed correctly by comparing expected UI state from claimed contexts against the real UI hierarchy snapshot, improving trust and correctness in complex workflows.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** seconds
- **cost:** Low to moderate for state management and reconciliation logic, mostly software orchestration.
- **security:** Requires persistent storage of UI snapshot diffs and workbench state, careful access controls to prevent leakage of UI structure.
- **missing:** Persisted UI state store integrated with workbench job and context stores.; Diff and reconciliation algorithms for UI state vs workbench context claims.

### "Provide a prioritized Mac task list specifically for mac-vision to guide UI automation and interaction focus."
- **useful because:** Currently, there is no durable prioritized task list on the Mac visible to mac-vision. Providing this lets mac-vision focus on what matters most, improving productivity and reducing premature mistakes or distractions.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** 100ms to 500ms per update
- **cost:** Low software cost, mostly reads from existing owner memory facts or integration with Reminders and calendar.
- **security:** Must respect privacy of tasks and owner preferences, with permission gating and no leakage to unauthorized surfaces or subsystems.
- **missing:** A dedicated read route or memory projection for prioritized Mac tasks specifically scoped to the mac-vision agent.; Integration hooking into owner fact memory and day plan ranking for task urgency and relevance.

### "Allow mac-vision to upload UI snapshots or accessibility tree digests for remote classification or backup under owner control."
- **useful because:** While mac-vision operates on the Mac using accessibility snapshots, remote classification or backup enables cross-surface consistency, enhanced models, or offline analysis to improve interaction and correction.
- **path:** mac-local-agent → relay
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** Moderate cloud storage and model inference costs when enabled.
- **security:** UI snapshot data is sensitive; must require explicit owner consent, encryption in transit and rest, and strict use policies.
- **missing:** Ownership-controlled opt-in upload framework for UI snapshots from mac-vision to relay or cloud.; Modeling pipelines to use uploaded UI snapshots for improved understanding and troubleshooting.


## Changes it proposed to its own stack

### `integration` — Build a UI-action planner component that uses live accessibility tree snapshots from mac-vision combined with mac_run_actions to generate multi-step UI workflows without manual scripting for the Mac.
- **owner gets:** This would empower the owner to achieve complex multi-application tasks by voice or automation, with guaranteed UI correctness and stepwise action execution and rollback where possible.
- effort: Large software development project involving UI accessibility APIs, planner logic, and execution feedback loops.  ·  risk: Complexity of UI variability could cause failures; mitigated by fallback strategies and user override.
- cost: Moderate server and Mac compute costs during planning and execution phases.  ·  latency: Planning may add latency but execution remains responsive.
- security: Increased UI access surface requires strict sandboxing and user permissions.
- depends on: live accessibility tree snapshot API; persistent UI state reconciliation; mac_run_actions; mac_delegate

### `memory` — Create a durable, agent-visible prioritized task and goal state store on the Mac agent, integrating owner-stated tasks (facts), calendar & reminders, and agent workflow state, exposed via a dedicated API for mac-vision.
- **owner gets:** The owner could see and control what the Mac agent and mac-vision prioritize, and these agents could work reliably from a shared, current task list instead of guessing or waiting for heuristics.
- effort: Medium software development involving integration of existing data sources and API endpoint creation.  ·  risk: Potential inconsistency between sources mitigated by well-defined priority rules and update sync.
- cost: Low server cost, moderate Mac agent software complexity.  ·  latency: Fast enough for real-time use with caching.
- security: Requires careful access controls and privacy filters to avoid leaking sensitive owner data.
- depends on: owner memory task facts; day plan calendar/reminders; existing API for mac-vision interaction


## What it asked for

### `c26-ulf4` (context) — mac-vision capabilities and best full use cases
- why: To know the best way for mac-vision to interact with Mac UI, what UI snapshot or hierarchy data it can use, and how to best integrate it with workflows and task execution.
- would change: I would tailor mac-vision's design and capabilities around documented best practices and recommendations, avoiding duplicate or ineffective implementations, and prioritizing what the owner really needs on the Mac.

