# Harness derivation — mac-vision — round 143

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the Mac-vision loop with full macOS Accessibility permission for AI Pendant Agent, allowing pixel-free, fine-grained control of all Mac UI elements without focus theft."
- **useful because:** This capability would let the owner delegate complex UI tasks safely and efficiently to the AI Pendant without disrupting their current focus or needing repeated manual intervention, vastly extending productivity and convenience on the Mac.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** sub-second response for UI actions
- **cost:** Moderate API cost for state snapshots and planning; negligible for action execution
- **security:** Sensitive as it grants deep control over Mac UI; requires explicit owner consent and robust audit logs.
- **missing:** Explicit owner grant of macOS Accessibility permission to AI Pendant Agent binary; Integration of mac-vision UI loop with pendant command and undo system; Detailed safety checks for actions not to cause focus thieves or unwanted side-effects

### "Implement a unified task/goals prioritization system combining manual task facts, Apple Reminders, and contextual usage data for better autonomous task management on the Mac."
- **useful because:** Currently, the system has no integrated prioritization of what the owner actually needs done; the owner must hand-type tasks or rely on limited calendar/reminder sync without deadlines or dependencies. Combining all input for ranked task guidance would enable the AI Pendant to effectively act on the owner's true priorities autonomously.
- **path:** mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** background
- **latency:** seconds to minutes depending on complexity
- **cost:** Low when built on local indexing and ranking, higher if cloud NLP used
- **security:** Stores sensitive personal goals and schedules; must be private to owner and encrypted.
- **missing:** Consolidation and schema integration of manual tasks with reminders and calendar events; Ranking algorithm for task priority, deadlines, dependencies, and topical relevance; Feedback loop for owner correction and reprioritization

### "Develop a multi-step Mac task delegation framework that integrates with mac_delegate and mac_run_actions to handle complex workflows and ambiguous instructions with automatic task breakdown and error recovery."
- **useful because:** Many Mac tasks span multiple apps and steps that cannot be expressed as short concrete commands. A framework that can interpret, plan, and execute these workflows will enable the owner to use voice or text commands with less friction and higher success rate.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** up to a few seconds per multi-step task
- **cost:** Moderate to high depending on workflow complexity
- **security:** Needs strict confirmation for destructive or sensitive operations.
- **missing:** Robust workflow decomposition and planning engine; Integration with existing mac_delegate and mac_run_actions tooling; Real-time monitoring and rollback of partial failures

### "Allow real-time context sharing between the pendant and mac-vision loop to dynamically adjust Mac UI automation based on wearer intent and environmental cues."
- **useful because:** By letting the Mac-vision loop continuously receive context updates from the pendant—such as voice commands, moment markers, and sensor data—the system can adapt its UI actions dynamically, avoiding mistakes and increasing responsiveness to the owner's current intent.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to low seconds
- **cost:** Low incremental API cost; mostly design and integration complexity
- **security:** Context data may reveal sensitive user state; must be securely transmitted and processed.
- **missing:** Real-time low-latency data channel between pendant and mac-vision; Context interpretation models that fuse multimodal input into UI task guidance; Safety fallback mechanisms for ambiguous or risky command contexts

### "Implement a confirmation and undo protocol for mac-vision UI actions that works seamlessly with the pendant and Mac, ensuring recoverability from mistakes and owner control over automation."
- **useful because:** Direct UI actions can have unintended consequences; an integrated confirmation and undo system mitigates risks, builds trust, and allows the owner to feel safe delegating complex automation to the AI Pendant with mac-vision.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds for confirmation dialog and undo actions
- **cost:** Moderate complexity due to multi-surface coordination and state tracking
- **security:** Requires secure and reliable user identity and authorization before destructive actions.
- **missing:** Design and implementation of undo stack and state snapshots in mac-vision; Pendant UI elements or voice confirmations for action approvals; Inter-agent protocols for action receipt and reversal

### "Create a synchronized visual and voice feedback system that confirms mac-vision loop actions in real-time on the pendant display and optionally through speech, for owner reassurance and transparency."
- **useful because:** The owner receives immediate confirmation of UI automation steps, improving trust, error detection, and situational awareness when the AI Pendant controls the Mac interface, especially without direct visual access to the Mac screen.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to seconds depending on action complexity
- **cost:** Low to moderate; mostly software UI and voice pipeline development
- **security:** Feedback may include sensitive UI element details; data transmission must be secure and private.
- **missing:** Integration between mac-vision action execution and pendant display/voice output; UI design for concise, non-intrusive activity summaries on the pendant; Low-latency communication channel between Mac automation and pendant feedback

### "Enable mac-vision to autonomously perform routine daily Mac maintenance tasks such as cleaning cache, updating software, and organizing files, triggered by a scheduled routine or owner command."
- **useful because:** Routine maintenance is often neglected but critical for smooth Mac operation. Automating it via the AI Pendant reduces owner burden and ensures the Mac runs efficiently without manual intervention.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** minutes, as these tasks are non-urgent
- **cost:** Low for simple maintenance scripts; moderate for complex workflows
- **security:** Requires careful permission controls to avoid undesired file deletion or software changes.
- **missing:** Script library for trusted maintenance tasks; Scheduling integration with owner's routine system; Fallback and error reporting mechanisms for maintenance tasks


## What it asked for

_Nothing._
