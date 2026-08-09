# Harness derivation — mac-vision — round 208

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to reliably read and track live UI accessibility tree state for specific Mac apps during an interactive workflow, reporting differences from expected states."
- **useful because:** This allows robust restart and recovery of multi-step workflows by verifying UI state matches expectations before proceeding, reducing errors and improving user trust in automated Mac control.
- **path:** mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** sub-second
- **cost:** low to moderate, mostly NLP and state diffing
- **security:** Must not expose private UI data off device; access controlled strictly to authenticated local components.
- **missing:** UI accessibility tree snapshot with diffing and change detection APIs; Reliable local UI state verifier integrated with workbench context tracking

### "Implement a low-latency layered Mac UI interaction system where mac-vision automatically plans and executes 1-3 mac_run_actions for simple tasks, and escalates to mac_delegate for complex or ambiguous workflows, with execution feedback for each step."
- **useful because:** This delivers efficient, responsive Mac UI automation that dynamically selects the right execution path, improving reliability and user experience while reducing wait times and errors.
- **path:** mac-planner → mac-vision → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** under 1 second for simple runs, moderate for escalated flows
- **cost:** moderate, mostly on orchestration and validation in agent code
- **security:** Must confirm destructive actions; avoid unsafe automation; control escalation strictly.
- **missing:** Direct integration layers in mac-vision to sequence actions and escalate; Execution receipt feedback integrated with UI verification

### "Allow mac-vision to record and attach a timestamped moment marker payload to the existing pendant button press record (s10-l3xe), specifically for confirming workflow progress or manual approval without needing a new gesture or button."
- **useful because:** This provides a non-intrusive physical confirmation mechanism tied to Mac UI automation progress, allowing the owner to explicitly approve or checkpoint steps with minimal overhead or confusion.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** under 100 ms
- **cost:** very low; leverages existing pendant storage and physical button hardware
- **security:** Physical confirmation events must be guarded to prevent accidental or spoofed triggers; explicit user action only.
- **missing:** Payload extension handling on pendant for workflow-specific markers

### "Implement a comprehensive UI interaction receipt system for mac-vision where each executed mac_run_action is accompanied by a screenshot and accessibility tree snapshot validating the actual UI changes on screen, including error reporting if the expected UI state is not achieved."
- **useful because:** This closes the critical gap between claimed UI action success and actual on-screen state, enabling trustworthy automation, debugging, and effective retries or corrective measures in multi-step workflows.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** realtime
- **latency:** 1-2 seconds per step
- **cost:** moderate to high due to image capture, accessibility tree snapshots, and state comparison processing
- **security:** Screenshots and UI states must be locally retained and securely handled to protect sensitive information.
- **missing:** API support for UI snapshot capture post action; Receipt and diff reporting infrastructure integrated with workbench and mac-vision

### "Provide a persistent, owner-visible, ranked Mac task management system that automatically gathers, prioritizes, and presents all actionable work on the Mac surface, including reminders, open windows, running apps, and delegated workflows."
- **useful because:** This gives the owner a single trusted source of truth for what needs to be done on their Mac, improving productivity and reducing mental overhead by surfacing only relevant, timely tasks with clear priority.
- **path:** mac-planner → mac-vision → unified → faculty-judgement → faculty-perception
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** moderate due to aggregation, ranking, and UI presentation work
- **security:** Task data must be locally controlled and owner-visible; privacy preserved for sensitive tasks.
- **missing:** Task aggregation aggregator, including delegated workflow capture; Prioritization metrics beyond structural deadlines; UI for owner task review and management integrated with Mac system

### "Enable mac-vision to perform secure, reversible Mac system configuration changes (network, accessibility, power settings) interactively through the accessibility loop, with step-by-step rollback and confirmation dialogs."
- **useful because:** Owners can make deep system changes safely and automatically with confidence, reducing manual effort and risk of misconfiguration, while maintaining control and the ability to undo changes.
- **path:** mac-planner → mac-vision → faculty-action → faculty-judgement
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate due to system interaction and rollback complexity
- **security:** Require explicit confirmation, strict sandboxing of sensitive operations.
- **missing:** System setting APIs accessible via accessibility automation; Rollback snapshotting and restore integration for system config; Confirmation UI modalities within mac-vision loop

### "Implement a dynamic context-aware Mac UI overlay that visually highlights active automation targets and suggested next steps for the owner to monitor and intervene in mac-vision workflows in real time."
- **useful because:** This transparency allows the owner to understand, guide, and intervene in Mac automation, building trust and providing a human-in-the-loop experience that prevents undesirable automation outcomes.
- **path:** mac-planner → mac-vision → faculty-perception → faculty-judgement
- **model tier:** realtime
- **latency:** sub-second
- **cost:** moderate due to UI overlay rendering and context aggregation
- **security:** Overlay must not expose sensitive data to other apps or observers.
- **missing:** Overlay rendering layer within mac-vision; Real-time context aggregation and workflow status data; Human-intervention event handling


## Changes it proposed to its own stack

### `integration` — Build an integrated Mac task aggregation and ranker service combining reminders, calendar events, open workflows, and current UI focus, feeding a persistent prioritized Mac task list visible to all Mac surfaces and agents.
- **owner gets:** This gives the owner a single central place to see and manage all important work on the Mac, reducing fragmented context and improving productivity.
- effort: Large engineering effort across mac-planner, mac-vision, and memory systems, plus UI work.  ·  risk: Complex synchronization errors, inconsistent state if poorly handled; recovery mode needed.
- cost: Moderate recurring compute costs for aggregation and ranking.  ·  latency: Background service, low latency UI reads.
- security: Task data is sensitive and requires good privacy controls.
- depends on: Enhanced task state capture from workflows; Existing reminders and calendar integration; Work context tracking APIs

### `integration` — Create a real-time mac-vision UI interaction verification and recovery framework that compares expected UI states from planned workflows with live accessibility tree snapshots, triggering automatic correction or graceful failure if discrepancies occur.
- **owner gets:** Drastically increases reliability of automated UI workflows by preventing silent failures due to unexpected UI changes, giving the owner confidence in automation.
- effort: Medium to large; needs lifecycle integration with mac-vision, accessibility API changes, and workbench context observability.  ·  risk: False positives could interrupt workflows, delayed recoveries.
- cost: Moderate due to snapshot and diff overhead during runs.  ·  latency: Incremental latency in action execution steps.
- security: Local, sensitive UI state exposure is contained to trusted processes.
- depends on: Access to accessibility tree snapshots on demand; Framework to persist expected UI states in workflows; Work context tracking

### `hardware` — Extend the pendant firmware to support multiple named payload types on the single physical button press (s10-l3xe record), allowing mac-vision to store distinct confirmation and workflow markers without adding new hardware.
- **owner gets:** Provides a direct, physical, low-latency confirmation mechanism for different workflow states or user approvals on the pendant without increasing device complexity.
- effort: Small to medium firmware development effort.  ·  risk: Firmware bugs could make confirmation signals ambiguous; recovery must be robust.
- cost: Minimal; no new hardware.  ·  latency: Negligible.
- security: Physical button presses must be carefully validated to prevent accidental triggers.


## What it asked for

_Nothing._
