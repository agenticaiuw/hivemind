# Harness derivation — mac-vision — round 269

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have the Mac vision agent autonomously interpret the UI accessibility tree and act on complex multi-step tasks without risking focus loss or user disruption, using partial UI state validation and plan undo."
- **useful because:** Today, complex multi-step Mac UI workflows require manual intervention or brittle scripting. Allowing the vision agent to handle these natively and safely would unlock powerful hands-free work and error recovery.
- **path:** mac-local-agent → pendant
- **model tier:** realtime
- **latency:** seconds per step
- **cost:** moderate model cost per plan validation and UI step
- **security:** Must prevent unauthorized or unrecoverable UI changes. Requires strict permission and action confirmation pathways.
- **missing:** robust UI partial state validation beyond accessibility tree; undo-capable UI action primitives; coordination with workbench job context for resume and state verification

### "Create a persistent, prioritized task list for the Mac vision agent driven by owner-stated tasks and automated context extraction for clear, ranked work visibility."
- **useful because:** Currently the vision agent has no prioritized queue of what the owner wants done. A durable, ranked task list derived from explicit owner intents and contextual signals would enable focused automation and better outcomes.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** under 1 second to update
- **cost:** low to moderate per update, mostly local data processing
- **security:** Task data must be owner-private and editable only by authorized agents or the owner.
- **missing:** durable task list store and persistence; context analysis and task ranking algorithms; integration with owner facts and day plan

### "Create an integrated confirmation and undo system for mac-vision's UI automation, tying in physical pendant button presses to approve reversible UI actions before committing them."
- **useful because:** This system would prevent accidental UI operations and allow the owner to physically approve or reject proposed changes, reducing risk and giving real-time control over automated workflows.
- **path:** mac-local-agent → pendant
- **model tier:** realtime
- **latency:** 1-2 seconds to respond to button presses and update UI state accordingly
- **cost:** low to moderate, mostly local event handling and state tracking
- **security:** Ensure that physical button signals cannot be spoofed and that the undo system protects against destructive or irreversible actions.
- **missing:** physical event-to-software event bridging; UI action undo infrastructure; persistent state for pending approval and undoable workflows

### "Build a multi-tier Mac UI automation framework where mac-vision can delegate complex browser interactions to the browser extension and synchronize state, enabling combined workflows leveraging the best UI control methods on each surface."
- **useful because:** Mac UI tasks often involve both native app controls and browser elements. Coordinating these hierarchically enables seamless, robust multi-app workflows that no single surface can do alone today.
- **path:** mac-local-agent → browser-extension
- **model tier:** realtime
- **latency:** seconds per action batch
- **cost:** moderate model cost for orchestration plus local communications
- **security:** Ensure permission boundaries between surfaces, and protect against cross-surface spoofing or leakage of sensitive UI state.
- **missing:** tight integration and synchronization mechanisms between mac-vision and browser extension; protocols for shared, stateful multi-surface workflow context; expanded capability ecosystem spanning both surfaces

### "Enable mac-vision to monitor and verify actual UI state during multi-step automation, detecting unexpected modal dialogs, errors, or focus loss, and report or recover gracefully."
- **useful because:** Automation often fails due to unmodelled UI changes. Real-time verification of UI state against expectations makes automation resilient and trustworthy, improving owner confidence and reducing manual fixes.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** real-time or near real-time (less than a second)
- **cost:** moderate, due to continuous UI polling and model-based analysis
- **security:** UI state monitoring must respect owner privacy and avoid leaking sensitive data.
- **missing:** real-time UI state diff and anomaly detection; error and modal dialog recognition patterns; fallback and recovery strategies

### "Provide a visual or spoken UI automation debugging and feedback interface for the owner, showing planned steps, current UI state, and allowing interactive control to pause, undo, or modify the automation flow in real time."
- **useful because:** Owners need transparency and control to trust complex UI automation, especially for tasks involving personal data or critical workflows. Interactive feedback and debugging enable safer and more effective automation.
- **path:** mac-local-agent → pendant → dashboard
- **model tier:** realtime
- **latency:** sub-second to seconds depending on interaction
- **cost:** low to moderate, predominantly local rendering and event processing
- **security:** Access control needed to protect UI automation details from unauthorized viewing or modification.
- **missing:** UI state visualization tools; spoken or visual feedback generation; owner interaction handlers

### "Implement an adaptive automation policy engine that selects the safest, most efficient execution mode for mac-vision actions based on task criticality, user preferences, and real-time context feedback."
- **useful because:** Not all UI automation is equal; some tasks require cautious confirmation, others can be fast and direct. An adaptive policy improves speed, safety, and user trust by optimizing how and when actions run.
- **path:** mac-local-agent
- **model tier:** background
- **latency:** milliseconds to seconds for decision making
- **cost:** low, mainly local decision logic
- **security:** Policy must enforce safeguards to prevent accidental data loss or privacy violations.
- **missing:** task criticality assessment; user preference integration; real-time context monitoring and feedback loop


## What it asked for

_Nothing._
## Its own summary

Proposed a suite of intertwined capabilities centered on full Mac UI automation via mac-vision accessibility loop combined with workbench state integration, physical pendant confirmation, and multi-surface orchestration with the browser. Added concepts for a resilient undo/confirmation system, real-time UI state verification, a prioritized task list, and adaptive automation policy engine based on owner preferences and task criticality. Also proposed a next-gen pendant hardware redesign for richer interaction gestures and increased local processing, enabling future local-side agent autonomy.

**Biggest unknown:** Feasibility and design of tight real-time coordination mechanisms between mac-vision, browser extension, and pendant hardware for confirmation-driven, reversible multi-step workflows remain unproven. Also, integration depth of UI partial state validation and undo infrastructure, and how to safely expose automation debugging feedback to the owner without overwhelming or risking security, remain open questions.

