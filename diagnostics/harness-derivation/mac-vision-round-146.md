# Harness derivation — mac-vision — round 146

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to autonomously interact with the Mac UI through accessibility APIs, to perform complex multi-step computer tasks driven by vision-based UI understanding."
- **useful because:** Currently, mac-vision can observe the accessibility tree but cannot act. This capability would enable the system to autonomously operate applications by interpreting UI controls and making safe decisions on clicks and input. It would unlock powerful automation that feels proactive and intelligent, bridging vision perception to actual control, especially for tasks where API access is unavailable or limited.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** up to 30 seconds per complex UI task
- **cost:** moderate; mainly compute on the Mac and relay bandwidth for context
- **security:** requires macOS Accessibility permission explicitly granted by the owner; all actions logged and reversible where possible; no silent clicks without owner consent; fallback to owner prompts when uncertain.
- **missing:** Owner explicit trust grant for macOS Accessibility for AI Pendant Agent binary

### "Create a system for the owner to specify and manage multi-step complex goals on the Mac that mac-vision can observe, prioritize, and plan actions for."
- **useful because:** Currently, there is no organized or machine-readable store of the owner's goals for computer tasks. Creating such a system would allow the mac-vision agent to know exactly what the owner wants done, prioritize, and work proactively toward those goals, making computer use highly relevant and efficient.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** minutes to hours for goal synthesis
- **cost:** low to moderate compute cost; data stored locally
- **security:** goals are sensitive data stored securely on the owner's Mac; user control over what is active and editable at any time
- **missing:** UI to create, edit and confirm goals; Backend to persist and query goals; Integration with mac-vision and planner agents for action synthesis

### "Ship a context-aware computer-use undo and action receipt system integrated with mac-vision that enables full action reversal on the Mac UI and logs reversible operations."
- **useful because:** Current reversible control patches exist but are basic. True undo with receipts anchored to UI context and action history would build user trust in AI-driven UI interactions, making automation safer and less fearful of breaking anything during long multi-step workflows.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** seconds to restore UI state
- **cost:** moderate for storage and computation of UI snapshots and action logs
- **security:** Action logs must be secure and tamper-evident; undo commands must be authorized by the owner; ensure no unauthorized changes are replayed.
- **missing:** Efficient UI state snapshot and diffing technology; Local undo state store on the Mac; Action receipt protocol and user UI for confirmations

### "Enable mac-vision to safely control Mac UI contextually using the pendant's tactile buttons as physical action approval triggers for specific UI commands."
- **useful because:** The owner can delegate complex UI tasks to mac-vision and confirm each critical action in the flow with a tasteful tactile physical confirmation, avoiding silent or accidental clicks, enhancing trust and safety.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** seconds per gesture click approval
- **cost:** low computational cost; relay bandwidth for commands and confirmations
- **security:** Requires secure and trustworthy link to pendant; physical button presses confirm specific UI actions; prevents malicious or mistaken UI operations.
- **missing:** Integration with pendant firmware gesture handling and secure messaging; UI for feedback on awaiting confirmation and error status

### "Create a cross-device multi-modal owner intention capture system combining voice, typed notes, and pendant gestures that feeds into mac-vision for active task planning and prioritization."
- **useful because:** Currently, the owner's intentions are fragmented and not fully captured. A unified capture system would allow mac-vision and other agents to have precise, structured, and prioritized understanding of what the owner wants done.
- **path:** mac-vision → relay-realtime → browser-extension
- **model tier:** background
- **latency:** minutes
- **cost:** moderate compute and storage
- **security:** Sensitive user data must be encrypted and access controlled.
- **missing:** Multi-modal capture frontends and message bus; Contextual recognition fusion and priorities

### "Implement a secure ephemeral session system for mac-vision allowing time-limited external Mac UI control access for trusted 3rd parties or automated processes, approved by the owner through the pendant confirmation button."
- **useful because:** Owners may want delegated help with complex Mac tasks from trusted parties or automation, but need a secure, time-limited, and fully controlled access system to prevent misuse or persistence of control.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** background
- **latency:** minutes
- **cost:** low computing and relay bandwidth cost, mostly design and secure protocols
- **security:** Critical to ensure trust boundaries, session expiration, and owner confirmation for all sessions. Logs and audit trail mandatory.
- **missing:** Authentication and session management infrastructure; Integration with pendant confirmation button for approval; UI for session management


## Changes it proposed to its own stack

### `hardware` — Add a second tactile button on the pendant strictly for confirmation of irreversible or sensitive UI actions triggered by mac-vision, separating action confirmation from the main microphone power button.
- **owner gets:** Currently, the pendant has very limited gesture vocabulary on a single button, which restricts modal input confirmation workflows. A dedicated confirmation button would provide a physical, low-latency, and obvious explicit approval for critical computer interactions, improving safety and trust.
- effort: Medium firmware and hardware design, testing, and integration effort.  ·  risk: Hardware malfunction or miswiring could disable confirmation input; recovered by software fail-safe allowing fallback to explicit owner prompting.
- cost: Low cost (~$1-$3 extra in components) and minimal additional power draw.  ·  latency: Negligible latency impact on interactions.
- security: Improves security by clearly separating confirmation intent physically.


## What it asked for

### `c15-mmk7` (context) — mac-vision agent current task list
- why: I want to know what the owner currently wants done on this Mac to prioritize any computer actions or vision-driven interventions.
- would change: Having an active prioritized list of tasks would allow mac-vision to plan and execute computer use more effectively and relevantly.

