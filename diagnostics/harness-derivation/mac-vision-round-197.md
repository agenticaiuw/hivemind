# Harness derivation — mac-vision — round 197

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Resume and coordinate complex multi-step workflows on the Mac with robust stateful tracking and visibility verification via the workbench and job handoff system."
- **useful because:** Allows the Mac vision agent to pick up interrupted workflows safely, verify actual UI state against system records, and complete complex multi-app tasks reliably.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** modest API cost per workflow step, dominated by model usage for plan interpretation and state reconciliation
- **security:** Requires read access to workbench context and job state, and some write access to track progress. No destructive control beyond what already exists.
- **missing:** integration of UI state verification with workbench context diff; resume/continue workflow functionality

### "Maintain a prioritized and topical task list specifically for the Mac surface, derived from the owner's stated goals and ongoing workflows."
- **useful because:** Enables the Mac vision and delegate agents to operate from a coherent prioritized agenda rather than ad hoc instructions, improving planning and action coherence.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** sub-minute
- **cost:** low API cost for task list maintenance and prioritization models
- **security:** Task list is a read-write memory store scoped to the Mac surface only. No destructive capabilities added.
- **missing:** task prioritization beyond structural rules; integration of owner-stated goals with reminders and routines

### "Add a focused confirmation and mouse interaction safety layer to the accessibility-driven Mac UI actions to prevent accidental focus stealing or destructive clicks."
- **useful because:** Prevents user disruption from fallback real mouse clicks when accessibility click actions fail, ensuring that background or unfocused windows are not accidentally activated or clicked destructively.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** sub-second
- **cost:** minimal API cost, mostly local logic
- **security:** May require local heuristics for safe UI target detection; no new destructive capability added.
- **missing:** fine-grained ui_click failure detection and fallback control; user preference integration for confirmation

### "Synchronize live voice-command plans with complex multi-step delegated workflows on the Mac, feeding back progress, UI state verification, and user intervention signals in real time."
- **useful because:** Keeps the Mac assistant and voice control tightly coordinated for reliable, resumable multi-app workflows that adjust dynamically to user interruptions and UI state.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** moderate compute and API cost due to continuous state sync and interpretation
- **security:** Requires read/write access to workflow state, job handoff, UI state projections; no new destructive powers.
- **missing:** live workflow state synchronization; user intervention signal capture and forwarding

### "Record and replay verified UI interaction patterns by mac-vision to automate repetitive tasks while ensuring correctness against UI state snapshots."
- **useful because:** Increases efficiency on Mac by automating common UI workflows with high confidence, reducing errors from UI changes or interruptions.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** low to moderate cost dominated by storage and interaction recording
- **security:** Requires recording UI state snapshots with user consent; stored interaction data must be secured; no new destructive capabilities added.
- **missing:** UI interaction recording and replay engine; UI state snapshot integration; user consent and security controls

### "Create a comprehensive Mac UI state synchronization and verification capability that continuously captures the accessibility tree and compares it against planned UI action effects and system workflow state, alerting when discrepancies arise to allow robust, resumable multi-step workflows."
- **useful because:** This ensures the Mac vision agent and delegating agents have trusted knowledge of what the user interface truly shows versus what the system thinks, preventing lost progress, errors, and enabling reliable task handoff and resumption.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** moderate API and compute costs for continuous accessibility tree capture and comparison
- **security:** Requires access to accessibility tree data and workflow state; sensitive UI state data must be protected; no additional control privileges are needed.
- **missing:** continuous accessibility tree capture and storage; UI state diff and anomaly detection; integration with workflow state for reconciliation

### "Develop a cross-surface task and goal coordination layer that consolidates and prioritizes tasks from owner memory facts, scheduled routines, reminders, and active workflows into a single real-time prioritized agenda usable by all agents including mac-vision."
- **useful because:** This will provide a coherent, contextual, and actionable task list that the owner can trust as a single source of truth. It improves multi-agent coordination, planning, and execution, reducing fragmentation and ad hoc task handling.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** sub-minute
- **cost:** low to moderate cost for data consolidation, ranking, and API calls
- **security:** Requires read access to owner memory facts, scheduled routines, reminders, and workflows; no new destructive control rights.
- **missing:** consolidation logic for disparate task sources; real-time priority ranking algorithm; API to expose prioritized agenda to agents


## Changes it proposed to its own stack

### `interaction` — Implement a specialized fallback-intercept heuristic layer in the mac-vision accessibility UI action executor that detects when an accessibility 'ui_click' degrades to a raw mouse click on a background window and pauses execution to request user confirmation before continuing or aborting.
- **owner gets:** Prevents unexpected focus theft and unintended destructive actions caused by fallback mouse clicks in accessibility-driven Mac UI automation, improving safety and peace of mind during automated workflows.
- effort: Medium; requires changes to the mac-vision UI action executor pipeline and integration with user prompt/confirmation system.  ·  risk: May introduce latency or require fallback for non-interactive scenarios; false positives could cause nuisance.
- cost: Low; mostly computational and minor user prompt overhead.  ·  latency: Small increase during fallback detection and confirmation steps.
- security: No increased privileges; confirmation protects against unintended actions.
- depends on: mac_run_actions; mac_delegate

### `hardware` — Add a dedicated hardware button on the pendant for mac-vision confirmation of risky UI actions, allowing immediate explicit owner approval or cancellation of actions that might steal focus or cause destructive changes in the Mac UI automation without requiring voice or screen interaction.
- **owner gets:** Gives the owner a fast, physical, reliable, and unambiguous way to intervene in UI automation on the Mac, improving safety and control over potentially risky remote actions.
- effort: Medium hardware firmware update plus integration with the pendant and mac-vision software stack.  ·  risk: Requires hardware firmware testing to avoid lost or missed inputs; misuse can block UI actions until confirmed.
- cost: Minimal; uses existing button hardware and low-power signaling.  ·  latency: Negligible hardware latency; improves real-time responsiveness of confirmations.
- security: Enhances security by adding explicit physical permission channel.
- depends on: mac-vision access to pendant input signals


## What it asked for

_Nothing._
