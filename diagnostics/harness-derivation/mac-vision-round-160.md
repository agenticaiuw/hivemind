# Harness derivation — mac-vision — round 160

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I want my Mac to autonomously read and interact with any app's UI without disrupting me or stealing focus."
- **useful because:** It enables fully autonomous Mac control, productivity, and task execution without the owner noticing any UI flicker or mouse stealing, vastly improving automation reliability and usefulness.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** realtime
- **latency:** under 1 second for UI state updates and action initiation
- **cost:** moderate API cost for inference, low additional hardware cost
- **security:** Needs strict per-action classification to avoid destructive UI actions; requires user grant of macOS Accessibility for the controlling binary; no screen recording or pixel-based fallback allowed.
- **missing:** macOS Accessibility granted to AI Pendant Agent binary; typed action policy and layered fallback for UI actions; full local UI state reconciliation on Mac without screenshots

### "I want a unified, prioritized task and goal management system that integrates all my workflows, reminders, and agent-identified opportunities into one actionable queue with context."
- **useful because:** Currently, task input and prioritization are siloed and fragmented, causing ambiguity and delays in what to do next. Unified prioritization helps focus scarce attention on highest value work dynamically.
- **path:** mac-planner → relay-realtime → mac-vision → browser-extension
- **model tier:** background
- **latency:** seconds to minutes acceptable
- **cost:** moderate API cost for ranking and context synthesis
- **security:** Careful handling of private data, user control of what is prioritized and surfaced.
- **missing:** cross-surface priority modeling and context fusion; goal dependency graph; explicit task state transitions and finishing feedback

### "I want the mac-vision agent to proactively recognize and act on common UI patterns and workflows on the Mac, like email triage or calendar management, without explicit instructions each time."
- **useful because:** This reduces repetitive command overhead, speeds up task completion, and leverages context-awareness to keep the user up-to-date and productive.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to a few seconds for task recognition and initiation
- **cost:** moderate model use, amortized over workflow segments
- **security:** Needs strict consent and control to avoid unexpected actions; explicit opt-in workflows.
- **missing:** UI workflow pattern library; context-sensitive proactive action triggers; automated learning of repetitive user tasks

### "I want the Mac and pendant to coordinate on voice-command capture so that commands started on the pendant are confirmed and executed safely on the Mac with visual feedback."
- **useful because:** This improves reliability, privacy, and reduces accidental commands by using the pendant as a natural lightweight voice capture interface and the Mac as a capable executor with UI feedback.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** under 1 second from capture to confirmation
- **cost:** low incremental, mostly software integration
- **security:** Requires secure link and user confirmation for destructive commands; voice data must be transient and locally controlled.
- **missing:** tight low-latency link between pendant voice capture and Mac agent; two-stage command confirmation UI

### "I want to see a live prioritized action briefing on any device surface summarizing urgent tasks and agent-suggested actions, updated dynamically throughout the day."
- **useful because:** Centralizes attention management, reduces cognitive load by focusing on what matters now, and keeps the owner aware of high-impact opportunities across devices.
- **path:** mac-planner → browser-extension → relay-realtime → mac-vision
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** moderate API cost for aggregation and ranking
- **security:** Owner controls what data is included and where it is displayed, encryption and privacy respected.
- **missing:** live synchronization of agent findings; cross-surface briefing rendering; dynamic priority scoring


## What it asked for

_Nothing._
