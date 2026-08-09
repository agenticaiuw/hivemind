# Harness derivation — mac-vision — round 234

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Can the mac-vision agent persistently track and verify UI state progression against workbench job contexts or handoffs to ensure accurate visual progress reporting and recovery?"
- **useful because:** This would let the system know what steps in a complex multi-step UI workflow have actually been completed, as seen on screen, not just what the system planned or claimed. It enables reliable recovery, avoids duplicate UI work, and improves trust in automated workflows.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** minutes
- **cost:** low compute, occasional background scans
- **security:** Needs careful design to avoid leaking sensitive UI data outside the owner environment.
- **missing:** route or tool to snapshot and link UI tree state with job handoff records, track claimed vs actual UI progress

### "Should mac-vision be able to autonomously select from owner's current task facts and initiate mac_delegate or mac_run_actions workflows with appropriate confirmations?"
- **useful because:** Currently, mac-vision knows what tasks exist but cannot start or follow through automatically. Allowing it to pick tasks and begin workflows streamlines owner productivity and reduces manual interaction.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds to minutes
- **cost:** moderate due to live interaction and planning
- **security:** Actions that mutate state should require explicit owner confirmation to avoid unintended effects.
- **missing:** better task prioritization and integration route for automatic task start; integration with task facts and delegation APIs

### "Add a typed action broker in mac-vision for classifying each UI action as read-only, reversible mutation, or high-impact mutation to enable safer automation policies."
- **useful because:** Right now mac-vision runs actions broadly without fine-grained control over their impact. A typed classification would improve observability, allow policy gates on high-risk actions, and enable safer automated UI control.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** low to moderate depending on classification complexity
- **security:** Requires logging of action types and possibly explicit confirmation for some actions to prevent harm.
- **missing:** typed action classification layer in the mac-vision control pipeline

### "Create a unified and prioritized Mac task management system that the owner can add to, view, and reprioritize, synced bidirectionally with existing reminders and memory facts, providing a reliable single view of all actionable Mac work."
- **useful because:** Currently, there is no real task list for the mac-vision agent or any Mac agent to read and act from; tasks exist as scattered memory facts or calendar reminders with limited integration. A unified task manager improves owner control and agent coordination.
- **path:** mac-planner → mac-vision
- **model tier:** realtime
- **latency:** seconds to minutes
- **cost:** moderate due to integration and syncing logic
- **security:** Requires access to Reminders and memory facts; proper privacy controls needed.
- **missing:** A persistent, queryable task store with APIs for CRUD and priority updates; seamless syncing with macOS Reminders and memory facts; UI surfaces for owner to interact with tasks.

### "Enable mac-vision to visually recognize and verify UI state drift or unexpected screen variations during multi-step automation, and to pause or recover gracefully instead of blindly continuing or failing silently."
- **useful because:** Today, UI automation risks going wrong if the UI changes unexpectedly, but mac-vision has no robust state awareness or error recovery visible to the owner. Adding UI drift detection improves reliability and trust.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate compute to analyze UI accessibility trees for changes and patterns
- **security:** Requires continuous UI inspection; data must stay local and sensitive UI info not leaked.
- **missing:** A real-time UI state comparator against expected UI states with heuristics for drift, mismatch, and recovery strategies.


## What it asked for

_Nothing._
