# Harness derivation — mac-vision — round 259

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a durable prioritized task list specifically for mac-vision to autonomously process on the owner's Mac."
- **useful because:** Mac-vision needs a live prioritized backlog of owner-intent tasks that are specifically for it to execute. This lets the agent plan and act purposefully with visible progress rather than wandering or waiting for explicit commands each time.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** low; mostly local context and lists
- **security:** Tasks represent owner's intent and possibly sensitive data; must respect permissions and privacy.
- **missing:** live prioritized queue of task facts or intents distinct from routine schedules and calendar reminders; UI workflow coordination primitives; safe action confirmation and escalation pipeline

### "Add a UI state verification extension for workbench contexts that compares planned multi-step workflows with actual visible UI state on screen for resume and error recovery."
- **useful because:** When mac-vision restarts an interrupted multi-step UI action plan, it needs to confirm what steps were actually completed on screen beyond just the recorded steps, to avoid confusion and unsafe assumptions. This extension would close the gap between planned state and actual UI state.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** seconds
- **cost:** moderate; involves reading accessibility state and diffing with workflows
- **security:** Accessing UI state is sensitive; requires accessibility permissions and audit logs.
- **missing:** UI state snapshot and diff capabilities linked to workbench context IDs; APIs for verifying claimed-versus-actual UI state

### "Create a safe starter permission mode 'mac_vision_auto_run' to allow mac-vision agent to run approved reversible Mac UI actions and multi-step workflows under controlled conditions."
- **useful because:** To build confidence and enable real use of mac-vision's interaction capabilities, there should be a safe permission and confirmation flow that allows mac_run_actions and mac_delegate to run with staged escalation from safe reversible actions to broader control.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** seconds
- **cost:** low
- **security:** Broad Mac control needs careful user consent and validation to avoid accidental destructive actions.
- **missing:** Permission framework for mac_vision_auto_run; User confirmation UI and audit logging

### "Create a prioritized automated Mac UI task queue that integrates with owner tasks, facts, and routines, converting high-level owner priorities into discrete Mac UI actions for the mac-vision loop."
- **useful because:** This would let mac-vision perform purposeful computer use from the owner's concrete stated priorities, bridging the gap between owner intention and actionable UI interactions, all managed in a ranked, durable queue.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** minutes
- **cost:** low to moderate, mostly local computation and queue management
- **security:** Sensitive owner task data; requires strict privacy and access control.
- **missing:** Task parsing and prioritization module; Task-to-UI-action conversion logic; Durable prioritised Mac UI task queue

### "Enable autonomous, continuous goal-driven Mac UI interaction by mac-vision with real-time visual task validation and error recovery."
- **useful because:** The owner should be able to delegate to mac-vision a continuous autonomous Mac use mode where the AI perceives the UI state, validates it against goals, recovers from mismatches, and progresses through tasks without waiting for explicit commands. This would make the system truly useful and proactive.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** moderate; real-time vision and interaction coordination
- **security:** Significant control risk; requires robust permission, confirmation, and audit mechanisms.
- **missing:** Real-time UI state monitoring integration with mac-vision loop; Error recovery and retry mechanisms based on observed UI state; Autonomous task progression policies and safety interlocks

### "Enable context-aware mac-vision UI interaction that anticipates owner needs by integrating with calendar, reminders, and real-time system state to prioritize and tailor UI actions dynamically."
- **useful because:** The owner should experience an AI that proactively manages computer interactions based on their current schedule, active tasks, and system state, reducing manual workload and interruptions.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate; requires access to multiple data sources and real-time reasoning
- **security:** Requires careful handling of sensitive calendar and task data with strict privacy controls.
- **missing:** Integration of mac-vision with live calendar and reminders; Dynamic real-time task prioritization engine based on multiple data streams; Adaptive UI action planning based on current system state

### "Provide mac-vision with deep integration to system notifications, system logs, and file events to proactively surface UI tasks and remedial actions before the owner notices issues."
- **useful because:** The owner will benefit from the AI noticing system states and issues early and automatically interacting with relevant UI elements to prevent or fix problems, reducing manual troubleshooting.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** minutes
- **cost:** low to moderate
- **security:** Requires access to system logs and notifications, which are sensitive; needs strict privacy safeguards and user control.
- **missing:** APIs to read system notifications, logs, and file activity in real-time; Policy engine to identify actionable UI tasks from system state; Integration with mac_run_actions and mac_delegate for task execution

### "Build a sophisticated UI action rollback and history system with visual checkpoints for mac-vision, enabling the owner to undo, redo, or audit recent mac-vision-driven UI changes easily."
- **useful because:** The owner needs confidence in mac-vision's interaction by having a clear way to backtrack unwanted UI actions and understand what changes were made automatically, facilitating trust and ease of recovery.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** seconds
- **cost:** moderate; involves storing UI state diffs and action logs
- **security:** Sensitive UI interaction data must be encrypted and access-controlled; undo actions must not accidentally expose or corrupt state.
- **missing:** UI state snapshot and diff capture mechanism; Persistent history log for UI actions; Undo/redo command integration with mac_run_actions and mac_delegate


## Changes it proposed to its own stack

### `integration` — Integrate real-time mac-vision accessibility tree perception with the workbench context system to provide visual step verification and synchronization of UI state with workflow progress.
- **owner gets:** This integration would let the owner know exactly what mac-vision has done on the Mac screen, verify that UI actions were successful before moving on, and enable smooth recovery from interruptions.
- effort: Moderate; requires changes to both mac-vision and workbench context backends and APIs.  ·  risk: Breakage would delay UI progress verification and require fallback to less robust methods.
- cost: Small increase in computation and data transfer for the accessibility tree snapshots and diffs.  ·  latency: Minimal if optimized for incremental updates.
- security: Requires continued strict access controls over accessibility data.

### `model-routing` — Route mac-vision interactions through a multi-tier model stack that grounds high-latency planning and reasoning off-device, while enabling low-latency real-time perception and action on the Mac.
- **owner gets:** Optimizes cost and responsiveness: heavyweight reasoning off the Mac, fast UI interaction on-device. Enables more complex workflows without lagging the user.
- effort: High; requires architectural change in routing and APIs.  ·  risk: Complex model routing bugs or mismatches degrading user experience temporarily.
- cost: Potentially higher model invocation costs but overall savings from improved latency and batching.  ·  latency: Significant improvement in real-time interaction responsiveness.
- security: Requires secure communication between model layers and device to protect data privacy.
- depends on: Real-time UI state monitoring integration

### `hardware` — Add a haptic feedback module and multi-gesture capacitive touch inputs to the pendant to allow the owner to control mac-vision actions discreetly, confirm critical UI interactions, and provide nuanced physical input without screen or voice interaction.
- **owner gets:** Provides a private, tactile interface to control AI-driven Mac interactions and confirms safety-critical actions through haptics and touch gestures, enhancing usability and safety without raising privacy concerns.
- effort: High; requires hardware design, PCB changes, firmware updates, and integration with mac-vision agent.  ·  risk: Hardware bugs or failures could reduce control; firmware complexity increases; owner learning curve for gestures.
- cost: Moderate increase in hardware BOM cost and power consumption.  ·  latency: Low latency physical controls improve responsiveness.
- security: Additional input channel must be secured to avoid spoofing or accidental triggers.


## What it asked for

### `c27-88b5` (context) — workbench contexts
- why: To check for existence and live shape of workbench contexts and confirm the APIs available for mac-vision to read and verify UI state progression in multi-step workflows.
- would change: If these APIs exist and are fully functional, I can confidently propose detailed capabilities around UI verification and automated continuation of interrupted workflows. If they do not or have gaps, I will propose alternative approaches.

## Its own summary

Recorded major new capabilities and foundational changes for mac-vision: autonomous continuous UI interaction with real-time validation, integration of UI state with workbench contexts, multi-tier model routing, context-aware UI action prioritization, proactive task surfacing from system state, UI action rollback and audit, and pendant hardware enhancements for tactile control and confirmation.

**Biggest unknown:** Whether the workbench context UI verification APIs are fully implemented and usable for deep UI state reconciliation, and how the owner prefers to handle real-time action confirmations safely.

