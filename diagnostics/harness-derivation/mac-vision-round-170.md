# Harness derivation — mac-vision — round 170

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the Agent to fully control and interact with the Mac applications and UI beyond simple reversible actions, by enabling a high-confidence accessibility-driven UI automation loop that never relies on screen pixels or user disruptive focus switching."
- **useful because:** This would empower the owner to automate, troubleshoot, and complete complex multi-step workflows on their Mac involving any installed app reliably and safely, elevating productivity and reducing manual repetitive work. Today, this is blocked by macOS Accessibility permissions.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** subsecond to 2 seconds per UI step
- **cost:** Low model cost per step, moderate orchestration overhead
- **security:** Requires macOS Accessibility permission grant specifically to the running binary; potential risk if misused to issue disruptive or destructive UI commands. Confirmation gating on destructive actions mitigates risk.
- **missing:** macOS Accessibility permission granted to AI Pendant Agent binary; Fine-grained UI element semantic classification and action safety checking; A robust undo and recovery system for UI steps

### "A fully integrated, durable, and privacy-sensitive browser session manager with strong authentication handling and session resume capabilities, tied to the Mac UI automation for authenticated workflows that require typing, clicking, and multi-step inputs"
- **useful because:** The owner should be able to ask the AI system to interact with any web service inside their authenticated browser environment reliably, completing workflows like order checking, form submission, and mailbox triage, without manual intervention.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** seconds to low tens of seconds per multi-step browser interaction
- **cost:** Moderate model cost due to dialogue and interaction complexity; some backend orchestration cost
- **security:** Must maintain privacy boundaries, ensure session security, never send sensitive credentials externally, and allow owner override or confirmation for sensitive steps
- **missing:** Durable browser session layer with heartbeat and lease management; Authentication state capture and replay; Privacy-bounded context extraction from active tabs; Typed step journaling with irreversible-action checkpoints

### "A dynamic priority-driven task and goal manager that aggregates input from the owner's hand-typed task facts, calendar/reminders, and ad hoc quick captures, then ranks, clusters, and recommends next actions with context-aware urgency and deadline sensitivity"
- **useful because:** Currently, the owner has no usable, persistent, comprehensive prioritized task list automatically derived and available across all agent surfaces. This capability enables clear daily focus and reduces cognitive load.
- **path:** mac-planner → mac-vision → unified
- **model tier:** background
- **latency:** seconds to minutes for recomputation, realtime latency for interaction queries
- **cost:** Low to moderate cost, mostly background processing with occasional peak when recalculating priorities
- **security:** Must respect task sensitivity and privacy; user control over what is aggregated and prioritized is essential
- **missing:** Automatic aggregation and weighting of multiple task sources; Contextual NLP ranking beyond structural priority; Persistent ranked and clustered task storage with inter-agent sync

### "An integrated next-action summarizer agent that listens to live user speech and computer UI events on the Mac, plus incoming remote voice and text, to produce a prioritized and contextual next actions briefing updated continuously."
- **useful because:** This provides the owner an always up-to-date, spoken and visual to-do and context summary that reflects real-time activity and plans, improving situational awareness and boosting productivity.
- **path:** relay-realtime → mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** seconds
- **cost:** Moderate to high due to multi-channel real-time processing, but amortized over continuous usage.
- **security:** Requires privacy safeguards to ensure that sensitive speech and UI data is processed securely and only used to produce actionable summaries, with owner control over outputs.
- **missing:** Real-time event processing across modalities; Cross-surface synchronization and summarization mechanisms; Dialogue policy integration for spoken briefing


## Changes it proposed to its own stack

### `hardware` — Design and develop a new pendant prototype device with more than one user button and multiple LEDs, plus additional sensors and a fuel gauge for battery state monitoring. Include a dedicated hardware gesture recognizer for diverse input gestures without latency overhead.
- **owner gets:** More user input options, better battery monitoring, and richer feedback allow the owner to trigger varied actions, confirm critical operations, and monitor device health reliably without interrupting workflow.
- effort: Large hardware redesign, prototyping, firmware rewrite, testing over several months.  ·  risk: Complex redesign risks delays and possible initial stability issues; requires requalification of new device firmware and components.
- cost: High in hardware manufacturing cost and development cost; low in ongoing CPU model costs.  ·  latency: No significant latency change in software; improved real-time responsiveness to button gestures.
- security: No change, but a stronger physical control interface decreases risk of accidental or unauthorized command triggers.


## What it asked for

_Nothing._
