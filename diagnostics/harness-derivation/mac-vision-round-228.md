# Harness derivation — mac-vision — round 228

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Expose a REST API on the Mac agent to read the current UI accessibility tree snapshot as a rich JSON hierarchy, including text, roles, enabled/disabled states, and coordinates, without requiring screen capture. This enables mac-vision to perceive the UI state in detail for safe and precise automation."
- **useful because:** mac-vision needs to see the UI structure without pixels to decide valid next UI actions for automated control. It enables planning and validation of interaction steps.
- **path:** mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** modest CPU and memory on the Mac agent; almost no network cost.
- **security:** No pixel capture, only structure and metadata of accessibility nodes; limited to the authorized Mac agent binary.
- **missing:** GET /vision-loop/tree-snapshot or equivalent route

### "Provide a persistent state store with REST API for mac-vision interaction plans, including claiming multi-step UI automation tasks, reporting step completion or failure, and resuming partial work after interruption. This includes integration with existing /workbench/contexts and /jobs for durability and transparency."
- **useful because:** Allows mac-vision to coordinate complex UI automations robustly without losing progress or repeating destructive steps. Ensures safe recoverability in case of crashes or interruptions.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** tens of seconds
- **cost:** moderate server-side storage and metadata updates; network negligible.
- **security:** Accessible only by authorized agents and with write protections on claiming and finishing steps to prevent conflicts or abuse.
- **missing:** durable mac-vision plan state management routes integrated with workbench and jobs

### "Implement a live event stream API for mac-vision to report step-by-step execution status, including successes, retries, errors, and user confirmations. This stream supports debugging, real-time monitoring, and adaptive recovery for UI automation loops."
- **useful because:** Real-time status feedback allows the orchestration layer or owner agents to intervene, replay, or pause automation to increase trust and safety.
- **path:** mac-vision → faculty-judgement → faculty-perception
- **model tier:** realtime
- **latency:** sub-second to a few seconds
- **cost:** low network bandwidth; server-side event queue cost.
- **security:** Event data contains UI action metadata but no pixel data; accessible to trusted agents only.
- **missing:** streaming mac-vision step event reporting API

### "Expose a prioritized, durable API that delivers the owner's current Mac UI tasks or actionable goals for mac-vision to select and execute. The tasks should have descriptions, deadlines or urgency, and optionally contextual metadata for safe and relevant UI automation."
- **useful because:** Currently mac-vision has no queue or clear input on what the owner wants done. This API connects owner intent and priorities to mac-vision, enabling meaningful automation instead of guesswork.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** minutes
- **cost:** minimal server storage and network usage; mainly metadata.
- **security:** Accessible only to authorized agents to protect privacy and integrity of owner goals.
- **missing:** cross-agent owner UI task queue and prioritization API

### "Implement an owner-facing confirmation UI model that mac-vision uses to ask for explicit approval on potentially destructive or ambiguous UI interactions before executing them. This confirmation uses an approved prompt modality (e.g. voice, pendant UI) and integrates with action execution pipelines."
- **useful because:** To prevent accidents in UI automation, this API lets the owner safely approve or deny sensitive mac-vision actions in context, increasing trust and making the loop safely actionable.
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** seconds to a few seconds
- **cost:** low communication cost; mostly UX logic.
- **security:** Requires secure channel to owner input and explicit user consent; should not allow forced actions without owner approval.
- **missing:** confirmation UI API for mac-vision before destructive or uncertain UI actions

### "Add a mac-vision accessibility trust monitor and emergency stop API that detects changes in the accessibility permission state, and on loss of trust issues an immediate pause or halt signal to the automation loop to prevent unintentional or unsafe UI interactions."
- **useful because:** mac-vision relies on macOS accessibility permission to automate safely. If permission is revoked or changes asynchronously, the loop must stop to avoid unknown side effects or failed actions.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds
- **cost:** minimal system state monitoring cost.
- **security:** Only accessible from authorized mac-vision loop and agents managing permissions.
- **missing:** accessibility permission change detection and emergency stop signal for mac-vision

### "The owner should be able to ask mac-vision for a real-time, interactive visualization of the accessibility tree overlayed on the Mac's UI, showing what controls mac-vision sees, what it plans to click or type in next, and allowing the owner to approve, adjust, or cancel these planned interactions before execution."
- **useful because:** This transparency and interactive control would build owner trust and avoid unintended UI actions, especially in complex or ambiguous automation steps. It leverages the unique position of mac-vision to perceive but not blindly actuate.
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** under 1 second
- **cost:** Moderate CPU and GPU usage on Mac for overlay rendering; network cost for sending interaction data and receiving owner feedback.
- **security:** Requires secure authenticated channels to owner interface; shows sensitive UI structure data only to authorized viewers.
- **missing:** mac-vision real-time accessibility tree visualization and interactive control API

### "The owner should be able to record custom macro workflows on the Mac UI by example, using mac-vision: demonstrating multi-step interactions that mac-vision records as an accessibility tree traversal and UI event sequence, which it can replay or adapt later robustly."
- **useful because:** This would empower the owner to build reusable automation beyond simple scripted steps, making mac-vision a practical general UI automation tool that can learn from live demonstration rather than requiring formal scripting or planning.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to minutes for processing and indexing recorded macros
- **cost:** Storage and CPU costs for capturing, indexing and replaying macro workflows.
- **security:** Recorded macros contain sensitive UI actions and data, must be stored securely and executed only with owner approval.
- **missing:** mac-vision custom macro recording and replay capability


## Changes it proposed to its own stack

### `model-routing` — Route mac-vision UI loop perceptual data along a dedicated low-latency pipeline to a specialized transformer model that can interpret accessibility trees and user intents combined, enabling real-time closed-loop control and error recovery.
- **owner gets:** This routing would vastly improve the intelligence and responsiveness of mac-vision's UI control, supporting more reliable and context-aware interaction automation that feels natural and trustworthy.
- effort: Medium to high, requires significant model and systems engineering, plus new model training and tuning.  ·  risk: Misinterpretation of UI states could cause incorrect actions; recovery and rollback must be robust.
- cost: High model compute cost relative to simpler API-only approaches.  ·  latency: Low latency target under 1 second for real-time interaction.
- security: Requires careful isolation and data privacy handling; model only sees authorized UI data.
- depends on: mac-vision accessibility tree API; mac-vision interaction plan store


## What it asked for

_Nothing._
