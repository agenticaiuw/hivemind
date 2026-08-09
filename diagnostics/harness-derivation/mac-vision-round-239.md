# Harness derivation — mac-vision — round 239

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Create a prioritized Mac work queue for the owner's stated tasks and reminders to drive mac-vision interaction."
- **useful because:** Enables proactive and context-aware task execution on the Mac, leveraging live owner task facts and Reminders, allowing the system to know what to do next and in what order.
- **path:** mac-planner → mac-vision → unified
- **model tier:** background
- **latency:** seconds
- **cost:** low (local computation)
- **security:** Tasks data is owner private and stored locally; no external exposure.
- **missing:** richer deadline and dependency modeling; numeric priority beyond structural

### "Add mac-vision capability to verify actual UI state against planned UI actions and report mismatches or successes for robust interaction."
- **useful because:** Detecting and recovering from UI mismatches ensures reliability and trust in autonomous UI control, enabling the system to retry, escalate, or notify the owner if something unexpected happens.
- **path:** mac-vision → unified → mac-planner
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** medium (local verification plus some model inference)
- **security:** UI state is local, never sent externally without consent.
- **missing:** live UI state diff engine; reliable state model of UI controls versus screen

### "Design a continuous interactive feedback loop between mac-vision and the owner for UI actions including confirmation, undo, and error reporting."
- **useful because:** This empowers the owner to guide and oversee AI-driven UI interactions in real-time with minimal disruption, increasing trust and usability of automation on the Mac.
- **path:** mac-vision → relay-realtime → unified
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** medium
- **security:** Owner interaction data is private and local or protected in transit.
- **missing:** UI action intent presentation layer; owner feedback capture mechanism; undo and rollback integration

### "Enable mac-vision to autonomously perform multi-step UI workflows on the Mac with failover, retry, and adaptive decision-making based on current UI accessibility tree state."
- **useful because:** Autonomous and adaptive UI control allows complex tasks to be executed reliably without owner intervention, improving automation potential and reducing manual effort.
- **path:** mac-vision → unified → mac-planner
- **model tier:** realtime
- **latency:** seconds to minutes
- **cost:** medium to high due to complex logic
- **security:** Actions occur locally, but mistakes in UI control could temporarily disrupt owner work.
- **missing:** dynamic UI state sensing and interpretation; workflow state management; error recovery mechanisms

### "Provide the owner with a unified, AI-curated, dynamic Mac task and goal manager that integrates all known task sources (owner-stated task facts, calendar events, reminders, workflows) with deadline, priority, and dependency modeling."
- **useful because:** Today, the owner cannot see or act on a coherent prioritized task list for the Mac that combines all inputs and reasons about urgency or dependencies. This is foundational for any intelligent, autonomous Mac assistant.
- **path:** mac-planner → mac-vision → unified
- **model tier:** background
- **latency:** seconds
- **cost:** medium
- **security:** All task data is private; no data leaves the system without consent.
- **missing:** integrated task/dueDate/priority/dependency model; UI for owner to view, edit, and reprioritize tasks

### "Enable mac-vision to autonomously validate and adapt UI interaction plans in real-time by sensing accessibility tree changes, detecting mismatches, retrying or escalating to the owner for decisions."
- **useful because:** The current system commits to UI actions without ability to detect failed steps due to ephemeral UI changes, leading to brittleness. Real-time verification and fallback improves robustness and owner trust.
- **path:** mac-vision → unified
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** medium to high
- **security:** UI state and interactions remain local and private.
- **missing:** live accessibility tree diff and interpretation engine; real-time UI verification loop

### "Create a real-time owner interaction protocol for mac-vision UI automation that allows the owner to confirm, modify, undo, or escalate actions via pendant or Mac UI feedback and input channels."
- **useful because:** This protocol empowers the owner to maintain control and oversight over AI UI automation, reducing risk and increasing acceptance of autonomous actions.
- **path:** mac-vision → relay-realtime → unified
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** medium
- **security:** Owner feedback and input remain private and local.
- **missing:** interactive UI feedback presentation and input capture mechanisms; undo and rollback integration


## Changes it proposed to its own stack

### `interaction` — Implement a real-time visual debugging and approval UI for mac-vision on the MacBook display, showing detected UI elements, planned steps, and status to enable owner oversight and prompt input.
- **owner gets:** This makes AI-driven UI automation transparent and trustworthy by letting the owner see what the AI is doing live, prevent mistakes, and approve or modify plans before execution.
- effort: medium to high  ·  risk: UI latency or overload, accidental input interference; recover by disabling the debug UI.
- cost: low  ·  latency: small added latency to UI actions
- security: local UI data exposure; no external sharing without explicit consent
- depends on: computerUse.loopEnabled; accessibility grant

### `hardware` — Add a dedicated small hardware LED or display on the MacBook to indicate mac-vision agent activity status and error states for owner situational awareness without disrupting workflow.
- **owner gets:** Provides lightweight, always-available feedback about the AI agent's control actions and errors, increasing owner trust and reducing surprises from the AI's unattended UI manipulation.
- effort: medium  ·  risk: Hardware integration complexity; owners ignoring LED.
- cost: modest hardware cost and power  ·  latency: none
- security: no direct impact; only indicators

### `model-routing` — Route mac-vision UI action planning to specialized AI submodules: one for deterministic UI control sequences from state, one for fallback guessing from partial UI states, and one for escalation to owner with detailed status.
- **owner gets:** This modular AI approach improves reliability by combining clear deterministic planning, AI fallback reasoning, and human-in-the-loop support when automation struggles, optimizing success and trust.
- effort: high  ·  risk: Complex coordination among AI modules; degraded automation if coordination fails
- cost: medium  ·  latency: small added planning latency
- security: local data only; internal only
- depends on: mac-vision UI state access; owner interaction feedback loop

### `context` — Create a robust state synchronization system between mac-vision's planned UI actions and actual on-screen accessibility tree to enable detection and correction of UI mismatches in complex workflows.
- **owner gets:** Without this synchronization, mac-vision cannot detect if a UI step failed or the screen changed unexpectedly, leading to automation failures and user frustration.
- effort: high  ·  risk: Complexity in state management and reconciliation; mitigated with robust rollback and escalation strategies.
- cost: medium  ·  latency: some added processing time for state comparison
- security: all data remains local
- depends on: vision-loop accessibility tree API; mac_delegate workflow context


## What it asked for

_Nothing._
