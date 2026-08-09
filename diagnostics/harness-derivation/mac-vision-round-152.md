# Harness derivation — mac-vision — round 152

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have my Mac agent automatically prepare and narrate a daily interactive briefing that integrates my calendar events, critical reminders, pending agent tasks, and relevant system status updates with one-shot voice commands for taking action or deferring tasks."
- **useful because:** The owner currently sees individual lists of overdue reminders, agent-generated tasks, and calendar events separately without an integrated briefing or voice interface organizing priorities and enabling immediate responses, so this would massively improve daily productivity and focus.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** under 2 seconds for spoken briefing and actionable suggestions
- **cost:** moderate API cost dominated by multi-source data aggregation and synthesis into coherent audio
- **security:** Requires read access to personal calendar, reminders, task memory, and system status, plus safe write and action permissions on the Mac. Voice interaction must respect privacy and afford opt-in muting or consent gating.
- **missing:** An integrated prioritized task model that unifies reminders, agent tasks, and calendar events with scoring; A multi-surface voice interaction design including concise briefing narrations and command handling; Expanded Mac action safety layer including explicit owner confirmations for destructive commands

### "Enable the mac-vision agent to take full control of Mac UI workflows by combining granted macOS Accessibility permissions with a safe typed action policy layer that classifies each UI control interaction for observability and reversibility, avoiding pixel-based fallbacks and silent focus theft."
- **useful because:** Currently, mac-vision cannot leverage the complete macOS Accessibility API to navigate complex UI workflows autonomously without risking focus theft or degraded reliability. A typed action policy layer would enhance trust, safety, and functionality.
- **path:** mac-vision → mac-planner → pendant
- **model tier:** realtime
- **latency:** under 1 second for UI action planning and reporting
- **cost:** low API compute cost, mostly code complexity for action classification and tracking
- **security:** Requires strict security to prevent unauthorized UI control; should include audit logs and owner confirmation on destructive operations.
- **missing:** Typed action classification layer for macOS Accessibility UI controls; Owner-facing permission or confirmation dialogs integrated with the pendant; Granular observability and undo tracking within the mac-vision agent

### "Add a safe physical confirmation gesture capability on the AI pendant to approve or cancel asynchronous high-impact Mac UI automation tasks started by mac-vision, integrated tightly with the typed action policy layer for reversible operations and audit logging."
- **useful because:** Currently, the owner cannot securely approve or cancel mac-vision initiated asynchronous UI tasks without risking unwanted or destructive actions. This feature would ensure physical human-in-the-loop consent and reduce accidental damage or unwanted commands.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 500 ms turn-around for confirmation feedback
- **cost:** negligible hardware cost, moderate software integration cost
- **security:** Must be tamper-resistant, securely link physical input to task approval, and prevent spoofing or accidental confirmation.
- **missing:** Firmware-level confirmation gesture recognition on the pendant button separated from the main microphone button; Integration of physical confirmation events into the mac-vision typed action control layer; Audit logging and fail-safe task cancel mechanisms

### "Enable mac-vision to record timestamped detailed logs and snapshots of UI states before and after every critical UI action in complex workflows, enabling precise undo, replay, and audit by the owner."
- **useful because:** Currently, there is no fine-grained recording of mac-vision's UI automation steps with state snapshots, making undo, replay, and trust difficult. This capability would provide full transparency and control to the owner.
- **path:** mac-vision → mac-planner → pendant
- **model tier:** background
- **latency:** non-real-time, allow minutes for replay or audit
- **cost:** medium CPU and storage cost on the Mac, moderate backend storage for snapshots and logs.
- **security:** Logs must be encrypted and access controlled, as they contain sensitive UI state data and user actions.
- **missing:** Detailed UI snapshot capture and diff tooling; Efficient event log and snapshot storage; Replay and undo control UI on mac-vision and pendant


## Changes it proposed to its own stack

### `hardware` — Design and build a second physical button on the AI pendant dedicated exclusively to confirmation actions (approve/cancel) separate from the main microphone button, with very low latency and tamper-resistant hardware.
- **owner gets:** Separates confirmation input from the conversation-start button, removing ambiguity in gesture detection and allowing safer physical transaction approvals without delaying microphone activation or conversation start.
- effort: Moderate hardware design and manufacturing effort, moderate firmware changes to handle multi-button input and debounce logic.  ·  risk: If button malfunctions or fails, could block all confirmations or cause unintended cancellations; mitigate with firmware fallback and diagnostics.
- cost: Adds low hardware component cost (~$1-2 per unit), negligible power change, minimal changes to existing Bluetooth link.  ·  latency: Low latency added due to direct hardware interrupt handling.
- security: Increases security through explicit physical consent pathway, reduces accidental activations.


## What it asked for

_Nothing._
