# Harness derivation — mac-vision — round 274

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a dynamically ranked and richly detailed prioritized task list for mac-vision that the owner can manage and the agent can act from to drive Mac UI automation."
- **useful because:** Today the system has no real prioritized work queue for mac-vision, just two typed facts and reminders read through without actionable ranking or dependency handling. A rich prioritized task list tightly integrated with UI state would make Mac automation truly owner-responsive and effective.
- **path:** mac-local-agent → mac-vision → pendant
- **model tier:** background
- **latency:** seconds to a minute
- **cost:** moderate prompt and query load per update, negligible hardware cost
- **security:** Task data stored locally and used only for owner automation; requires careful handling of permissions and UI control to avoid unintended actions.
- **missing:** A robust multi-dimensional task ranking system beyond the current basic critical flags; A durable persistent task store that integrates owner intent, reminders, memory facts, and UI state; UI snapshot and workbench context integration with task state; Rich metadata for tasks (priority, deadlines, dependencies, tags, owner notes)

### "Enable a persistent coordination state that links mac-vision UI snapshots with workbench contexts, showing claimed versus actual state on screen and enabling resume and reconciliation of interrupted workflows."
- **useful because:** Currently, the system cannot verify or resume multi-step tasks with accurate knowledge of what was really on the Mac screen during interruptions. A persistent coordination layer would enable reliability and smooth recovery of complex automated tasks.
- **path:** mac-local-agent → mac-vision → workbench
- **model tier:** background
- **latency:** minutes
- **cost:** moderate
- **security:** Secure binding of UI snapshots to context histories without leaking sensitive screen data outside owner control.
- **missing:** Persistent storage for UI snapshots linked to workbench context IDs; Reliable validation of UI state against intended actions; UI snapshot diff and replay tools

### "Enable mac-vision to perform multi-application complex workflows with full context-aware local planning, including fallbacks and recovery strategies, beyond short reversible actions."
- **useful because:** Many Mac tasks require multiple application and contextual steps that cannot be easily expressed in short reversible UI actions. Local AI planning with full context and recovery would allow mac-vision to automate complex workflows securely and robustly.
- **path:** mac-local-agent → mac-vision
- **model tier:** background
- **latency:** minutes
- **cost:** Moderate compute, mostly background planning with occasional real-time interaction.
- **security:** Requires careful sandboxing and owner control to avoid unintended multi-app automation side-effects; clear logs and undo support needed.
- **missing:** Local AI planning capability integrated with mac-vision UI automation; Contextual knowledge of multi-application state and dependencies; Mechanisms for fallback, retry and recovery in workflows

### "Enable mac-vision to inject directly owned notes, corrections, and annotations into the owner's task and memory facts store based on what is observed during UI automation, improving memory augmentation and task refinement over time."
- **useful because:** Currently, mac-vision executes tasks but cannot add knowledge or clarifications interactively into the owner's facts store. This would make the UI automation loop a learning, improving assistant that gathers context and refines ongoing work.
- **path:** mac-local-agent → mac-vision → memory
- **model tier:** background
- **latency:** minutes
- **cost:** Low compute; mostly background updates.
- **security:** Facts updated by mac-vision must be clearly labeled as agent-generated and editable by the owner to avoid confusion or error propagation.
- **missing:** API for mac-vision to write to memory facts with provenance and classification; UI triggers for mac-vision to capture notes or corrections from observed state


## Changes it proposed to its own stack

### `hardware` — Augment the pendant firmware to support an expanded physical trigger protocol that allows multiple distinct action confirmations or cancellations linked to mac-vision accessibility automations, using existing payload channels without adding gesture complexity.
- **owner gets:** Provides quick, low-latency, physical confirmation or cancellation options for critical UI automations initiated by mac-vision, improving responsiveness without disrupting normal button function or relying on software timing.
- effort: Medium firmware development and testing, integration with mac-vision agent software.  ·  risk: Minimal risk to existing button functions as only the communication protocol changes; thorough testing required to avoid accidental triggers.
- cost: Negligible hardware cost; uses existing button and firmware storage infrastructure.  ·  latency: Provides near-instant physical input without software wait.
- security: Limited to owner device and encrypted payloads; no new outward connectivity.
- depends on: mac-vision loop enabled and stable; mac-vision integration with task coordination


## What it asked for

_Nothing._
## Its own summary

Proposed a prioritized task list for mac-vision, UI snapshot-workbench context synchronization, pendant firmware trigger enhancement, typed action broker for Mac UI automation, multi-application workflow planning, integration across pendant, mac-vision, and workbench for robust task delegation, and memory facts injection by mac-vision for dynamic task refinement.

**Biggest unknown:** The existence and readiness of workbench contexts and vision-loop UI snapshot integrations are the main unknowns required to advance coordination and robust interruption handling.

