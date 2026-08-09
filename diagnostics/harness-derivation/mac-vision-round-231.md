# Harness derivation — mac-vision — round 231

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a full mac-vision accessibility loop capability on the Mac agent that exports the current UI hierarchy snapshot, a live step-by-step UI automation plan, step validation, and rollback prompts."
- **useful because:** This capability lets mac-vision confidently automate complex multi-step tasks on the Mac UI using accessibility features safely, provide stepwise explanations, detect unreachable UI elements, and recover from failures.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 1s per step
- **cost:** low API cost since mostly running locally on Mac
- **security:** Requires macOS Accessibility permission and careful gating to avoid focus theft or accidental UI clicks. Step confirmation and rollback help safety.
- **missing:** A dedicated mac-vision route exposing UI tree, plan, validations; Integration with existing computerUse loop on mac-planner; Recovery and rollback logic in UI automation

### "Enhance workbench and jobs API to include real-time UI snapshot state or links from the mac-vision accessibility loop to detect desyncs between claimed workflow state and actual UI state on screen."
- **useful because:** This enables robust reconciliation of automated workflows with live UI state, allowing mac-vision or other agents to correct or alert on mismatches, improving reliability of multi-step UI tasks.
- **path:** mac-planner → mac-vision
- **model tier:** realtime
- **latency:** under 1s for state sync
- **cost:** low API cost locally
- **security:** Exposes internal state of Mac UI, so requires macOS Accessibility and privacy gating.
- **missing:** Integration between workbench job contexts and accessibility snapshots; New API routes or extensions to include UI state

### "Provide a richer, structured priority task list capability with dependency, urgency, and completion status fields for mac-vision to consume and act on live."
- **useful because:** Current live task list is sparse. A richer prioritized task queue lets mac-vision plan computer use better, handle multi-tasking, and respond dynamically to owner needs and device state.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds for updates
- **cost:** modest storage and API cost
- **security:** Needs owner control and transparency to avoid task conflicts or runaway automation.
- **missing:** Task dependency and urgency schema; Enhanced UI or voice interface for owner to manage tasks; Task queue integration with memory projection

### "Allow the owner to visually confirm and correct the live UI interaction plan on the Mac before automation proceeds, via a mac-vision assisted visual UI validation interface."
- **useful because:** This would give the owner direct control and insight into what the automation intends to press/click/act on next in the Mac UI, reducing risk and surprises from accessibility-driven automation.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 2s max interaction lag
- **cost:** moderate development cost for UI and communication layers, low per-call API cost
- **security:** Requires explicit owner consent for UI state sharing and input interception, needs safe fallback if validation is declined or timed out.
- **missing:** A GUI overlay or side panel rendering next UI action steps; Interactive approval/correction callbacks; Integration with mac-vision accessibility loop

### "Enable multi-agent coordinated recovery workflows when UI automation fails on the Mac, with automatic UI state snapshot sharing, error detection, and fallback retries."
- **useful because:** Currently UI automation failures risk deadlock or silent errors. Coordinated recovery using live UI snapshots and agent collaboration would improve robustness and user trust.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** realtime
- **latency:** under 1s for error detection and retry trigger
- **cost:** moderate cost for integration and state sync
- **security:** Exposes live UI accessibility state for error detection; must ensure privacy and security of UI content.
- **missing:** Automated UI failure detection heuristics; Inter-agent UI state sharing protocols; Workflow for coordinated fallback and retry

### "Provide the owner with a dynamic multi-level priority task manager that integrates reminders, owner tasks, live workflow states, and UI automation status to guide mac-vision's autonomous activity on the Mac."
- **useful because:** The owner currently lacks a consolidated prioritized task list for the Mac. A richer dynamic manager would enable smarter, context-aware automation scheduling, improving task throughput and reducing conflicts.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds for update and recalculation
- **cost:** modest due to caching and batching
- **security:** Requires owner visibility and control interfaces to prevent unwanted automation.
- **missing:** Task dependency and urgency modeling; Integration of reminders, memory, workflows, and UI states into one task queue; UI for owner task management and override


## What it asked for

_Nothing._
