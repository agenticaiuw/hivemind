# Harness derivation — mac-vision — round 190

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide the owner with a dynamically prioritized, unified Mac task queue that integrates and ranks actionable tasks from memory facts, reminders, and workbench contexts."
- **useful because:** The owner needs a single, actionable list of what they want done on their Mac that is always current and ranked by priority, deadline, and impact. Currently, no such list exists automatically — only manually entered tasks or unconnected data sources. This capability would empower consistent, focused action and reduce cognitive load.
- **path:** mac-planner → mac-vision → dashboard
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** Moderate API calls, low compute for ranking and integration
- **security:** Data stays local; priority ranking logic transparent to owner
- **missing:** Better integration between memory facts, reminders, workbench contexts, and a UI surface to display and act on the unified queue.; Ranking heuristics that combine deadlines, priorities, and inferred urgency.; Writable APIs or local stores for updating task statuses and accepting owner feedback.

### "Enable the mac-vision agent to reconcile claimed workbench contexts with actual on-screen UI states to detect divergence and offer error recovery or manual handover."
- **useful because:** Current capabilities report only claimed-versus-actual on-disk states for work but have no answer for UI state mismatches, which can break workflows silently. Having this agent check UI state against workbench claims would improve reliability, prevent loss of work, and enable smoother resumption or manual intervention.
- **path:** mac-vision → mac-planner → dashboard
- **model tier:** background
- **latency:** seconds
- **cost:** Low compute, mostly local UI polling
- **security:** UI data is sensitive but read-only; error states reported only to owner
- **missing:** A new public API or extension of /workbench/contexts/:contextId to include accessibility UI state inspection.; Mechanisms to snapshot UI accessibility trees linked to contexts.; Logic to compare UI state with context data and flag inconsistencies.; Recovery workflows or manual override UI.

### "Allow dynamic creation, update, and resolution of multi-step task workflows on Mac, backed by visual UI state and progress tracking, enabling mac-vision to continuously execute and adjust tasks until completion."
- **useful because:** Currently, multi-step tasks are clumsy to automate. Owners need a persistent, stateful workflow manager that understands UI state, tracks progress, and adapts to interruptions or errors for reliable task automation end to end.
- **path:** mac-planner → mac-vision → dashboard
- **model tier:** realtime
- **latency:** seconds
- **cost:** Moderate compute for state tracking and workflow planning
- **security:** Workflow state and UI data are sensitive; access controlled and local where possible
- **missing:** An API for saving multi-step task workflows including UI state markers.; Integration of UI accessibility snapshots into workflow state.; Logic for detecting, retrying, or handing off interrupted workflows.; Capability for mac-vision to write and resume long tasks.; Better user controls for monitoring and overriding such workflows.


## What it asked for

_Nothing._
