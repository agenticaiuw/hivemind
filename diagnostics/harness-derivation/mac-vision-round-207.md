# Harness derivation — mac-vision — round 207

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to safely plan and execute multi-step workflows on the Mac through a typed action plan API."
- **useful because:** Allows mac-vision to turn high-level owner intents and tasks into concrete action sequences and complex workflows, enabling true multi-step Mac automation beyond single actions.
- **path:** mac-planner → mac-vision → mac-terminal → unified
- **model tier:** realtime
- **latency:** up to 10 seconds per plan execution
- **cost:** Moderate API cost dominated by LLM planning; low execution cost on Mac
- **security:** Plan execution requires strict validation and confirmation for destructive actions; actions to be reversible where possible; user confirmation for high-impact steps.
- **missing:** POST /plan route live implementation; POST /execute route live implementation; Typed plan specification schema; Reversible action tooling support

### "Create a persistent, prioritized Mac task manager integrated with owner intent and memory facts, surfaced to mac-vision for actionable queue workflows."
- **useful because:** A prioritized list of true tasks the owner wants done on the Mac, integrated with a persistent queue, allows mac-vision and other agents to pick up, act on, and resume work efficiently while reflecting owner priorities.
- **path:** mac-planner → mac-vision → mac-terminal → unified
- **model tier:** realtime
- **latency:** under 1 second for fetching and ranking tasks
- **cost:** Low API cost dominated by memory query and lightweight ranking
- **security:** Task ownership and priority must be protected; integration only with authorized memory and reminders sources; write-back actions need user confirmation.
- **missing:** Task queue management API; Integration between memory facts, reminders, calendar, and persistent mac task queue; Prioritization mechanism beyond structural date and priority in Reminders

### "Add UI state verification and discrepancy detection for mac-vision to confirm claimed UI states match the actual on-screen state during task execution."
- **useful because:** Unlike jobs that check file-level state on disk, mac-vision's true check of success or failure is whether the UI reflects expected changes. Verification and discrepancy detection enable reliable continuation or error recovery.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** under 2 seconds per state verification
- **cost:** Minimal computational cost, modest bandwidth for UI state snapshots
- **security:** UI state contains sensitive user information; data must be kept local or encrypted in transit; verification/reporting tools must respect privacy and consent.
- **missing:** UI state capture and comparison tooling; Integration with workbench contexts to register claim-vs-actual UI state diffs; Automated recovery or re-planning capability on mismatch

### "Enable mac-vision to combine owner voice commands with live accessibility UI data to propose and verify interactive Mac UI workflows in real time, minimizing mistaken clicks and resuming interrupted tasks safely."
- **useful because:** Combining voice intent, live UI state from accessibility trees, and step-by-step verification gives mac-vision the ability to handle complex Mac UI workflows on behalf of the owner reliably and with minimal interference.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** realtime
- **latency:** seconds to under 10 seconds per interaction cycle
- **cost:** Moderate cost dominated by LLM inference and real-time interaction
- **security:** Requires permission to read accessibility UI; requires strict user consent and error handling to avoid unintended clicks; privacy protections for UI data.
- **missing:** Live accessibility UI state streaming API; Voice command integration with mac-vision loop; Workflow step verification and rollback; Inter-agent coordination on interaction state

### "A real-time dynamic Mac task management and handoff system that integrates memory facts, owner priorities, and active workbench contexts with mac-vision for seamless task resumption."
- **useful because:** The owner can delegate Mac work dynamically, trust the system to pick up, pause, and resume tasks without loss or duplication, respecting true intent and priorities.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** sub-second to seconds for handoff and resume
- **cost:** Low API compute cost, moderate coordination complexity
- **security:** Task claims and handoffs must be secure and verified; privacy of task content preserved; user intent honored strictly.
- **missing:** Persistent workbench context store active in the Mac agent; Bidirectional task claim and update synchronization; Conflict resolution for task ownership between agents

### "A protective permission and confirmation framework for mac-vision that allows maximum control without accidental destructive actions, using typed action classification and user confirmations."
- **useful because:** The owner gets strong assurance that the system will never perform destructive actions without explicit confirmation, while allowing fluid automation.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** sub-second confirmations
- **cost:** Minimal compute cost for classification and confirmation dialogs.
- **security:** Permissions and confirmations must not be bypassable; logging of confirmations required for audit.
- **missing:** Typed action classification middleware; User-facing confirmation UI integrated with mac-vision actions


## Changes it proposed to its own stack

### `integration` — Integrate mac-vision tightly with voice interaction and accessibility UI state streaming to enable responsive, real-time interactive Mac UI workflows with error recovery.
- **owner gets:** The owner gains reliable voice-driven control of Mac UI actions that minimizes errors and recovers gracefully from interruptions or unexpected UI changes.
- effort: Large engineering effort due to low-level UI integration, concurrency, and error handling.  ·  risk: Potential for accidental UI actions if integration is buggy; requires strong testing and user controls.
- cost: Moderate compute and network cost for real-time UI streaming and interpretation.  ·  latency: Low latency needed for responsive interaction.
- security: Requires continued accessibility permissions and privacy protections on UI data.
- depends on: mac-vision agent loop enabled; voice interaction enabled; accessibility UI streaming API


## What it asked for

_Nothing._
