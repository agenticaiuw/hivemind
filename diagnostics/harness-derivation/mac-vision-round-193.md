# Harness derivation — mac-vision — round 193

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Create a synchronization layer between mac-vision's actual UI state observations and the workbench workflow claims to verify real vs claimed UI progress and enable robust retry, undo, or handoff of UI tasks."
- **useful because:** The system currently cannot verify if the UI changes mac-vision intended actually took place versus what the workflow claims. This makes UI automation fragile and error-prone. A sync layer would dramatically improve reliability and trust in multi-step Mac workflows.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** background sync with real-time error alerts
- **cost:** low to moderate for state comparison and storage
- **security:** UI state details are sensitive and must be tightly access-controlled.
- **missing:** Data model for expected UI states and mapping to accessibility tree snapshots.; Route and storage support for actual UI state snapshots linked to workflow context ids.; Logic to compare claimed and actual state and trigger recovery workflows.

### "Develop a dynamic UI error recovery skill for mac-vision on the pendant firmware that detects interaction failures via accessibility fallback to pixel checks and triggers remedial steps or owner notifications."
- **useful because:** To enhance system resilience, when accessibility actions silently fall back to mouse clicks or fail, this skill on the pendant could detect errors, log failure context, attempt retries or simpler UI paths, and escalate for owner review to avoid broken workflows.
- **path:** pendant → mac-vision → unified
- **model tier:** gpt-4.1-mini
- **latency:** near-real time for detection, background for resolution
- **cost:** minimal embedded compute and network cost, low server-side sync
- **security:** Firmware must be secure to avoid false error injection or suppressing owner-meaningful interaction events.
- **missing:** API for delivering UI interaction failure feedback from Mac to pendant firmware.; Local state storage and logic on pendant firmware for retry policies and escalation.; Protocol to notify owner via pendant UI and escalate to mac-vision or other agents.

### "Implement a conversation-driven task initiation interface for mac-vision that lets the owner verbally start complex, multi-step Mac tasks without command-line detail by describing goals, which the system translates into UI action plans and workflows."
- **useful because:** This reduces friction and complexity for the owner in starting sophisticated Mac automation by natural language intent, handling translation into accessibility-based UI action sequences, leveraging the enabled mac-vision accessibility and delegate capabilities.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** real-time interactive
- **cost:** medium API use for language understanding and plan synthesis
- **security:** Verbal commands should be confirmed before executing destructive or sensitive actions.
- **missing:** Owner conversation interface on pendant or Mac.; Mapping from goal descriptions to mac-vision accessibility UI workflows.; Error recovery and confirmation dialogs integrated with vision loop and delegate workflows.

### "Add a mac-vision capability for context-sensitive, low-impact UI micro-optimizations on the Mac, such as automatically dismissing known persistent notification banners, clearing helper tooltips, or preloading frequent apps or documents to speed workflows."
- **useful because:** This capability would improve daily Mac user experience by reducing minor UI irritations and delays that slow the owner's flow, without requiring manual interaction or separate task requests.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini
- **latency:** small background adjustments with occasional real-time execution
- **cost:** minimal compute, occasional use of accessibility API
- **security:** Must avoid any destructive or risky actions; read-only or reversible only.
- **missing:** Database of known UI annoyances and their automated dismissal workflows.; Integration with mac-vision accessibility loop for continuous monitoring.; Owner preferences and override controls to enable/disable specific micro-optimizations.


## Changes it proposed to its own stack

### `integration` — Add a typed confirmation and escalation policy for mac-vision that intercepts destructive UI actions and requires explicit owner approval before execution, and can escalate to pixel-based capture and manual review when accessibility actions fail or are ambiguous.
- **owner gets:** This protects the owner from unintended destructive actions initiated by automation, addressing the owner's preference for 'confirm before sending mail, deleting files, or buying'. It also provides a fallback when accessibility automation is insufficient to validate UI state before changes.
- effort: Medium engineering effort across Mac agent and pendant integration, plus UX design.  ·  risk: Owner inconvenience if overused, false positives blocking useful automation. Recovery is manual override or temporary bypass.
- cost: Minimal API and compute cost, no hardware cost.  ·  latency: Negligible except on escalation steps requiring owner attention.
- security: Increases security by adding manual control layer.
- depends on: mac-vision accessibility automation enabled; priority task manager capability

### `integration` — Create a real-time UI state broadcasting protocol between mac-vision's accessibility automation and other system agents (like mac-planner and unified) to share exact UI control structure and current focus/action state, enabling coordinated multi-agent control and reducing conflicting actions.
- **owner gets:** Currently, isolated agents may attempt independent UI interactions without awareness of each other's state or intentions, risking conflicts or redundant work. Real-time shared UI context would improve fluidity, safety, and efficiency of Mac automation.
- effort: Medium engineering to build a message bus or shared state sync, plus UI and security design.  ·  risk: Data privacy risk from broadcasting UI state; requires encryption and narrow access control.
- cost: Moderate network and CPU usage for real-time updates.  ·  latency: Low latency needed for fluid coordination.
- security: Must tightly secure UI state data to prevent leakage.
- depends on: mac-vision accessibility loop enabled; inter-agent communication protocols


## What it asked for

_Nothing._
