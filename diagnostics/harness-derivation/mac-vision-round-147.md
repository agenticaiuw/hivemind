# Harness derivation — mac-vision — round 147

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to fully operate the Mac UI via accessibility tree traversal without any reliance on screen captures or pixel-based actions."
- **useful because:** This would allow the owner to delegate complex tasks directly through natural language to the Mac, with the system safely navigating the UI precise and non-intrusively, maintaining privacy and responsiveness.
- **path:** mac-vision → mac-planner → unified → relay-realtime
- **model tier:** realtime
- **latency:** under 5 seconds to decide next action
- **cost:** minimal API cost; mostly local computation on the Mac
- **security:** Requires macOS Accessibility permission for the AI Pendant Agent binary only, no screen recording or pixel data leaves device, actions classified by impact and logged for undo.
- **missing:** macOS Accessibility Permission granted; Robust failure modes when access is denied; Action risk classification and undo support; Owner confirmation UI for destructive or disruptive actions

### "Create a system for physical moment bookmarking on the pendant's single button to label the owner's current task context with a timestamped marker."
- **useful because:** The owner can quickly mark moments of interest or transitions in task without disrupting flow, aiding memory recall and retrospective task analysis.
- **path:** pendant → mac-planner → mac-vision
- **model tier:** realtime
- **latency:** under 1 second for button press to marker storage
- **cost:** negligible; uses existing button and sd card write
- **security:** Physical button presses and associated metadata stored locally on pendant and synced to Mac; no user data leaves without explicit permission.
- **missing:** UI for task-to-marker tagging; Integration with mac-vision task prioritization

### "Provide mac-vision agent with contextual situational awareness from multi-surface sensory integration combining pendant mic audio, bridge audio playback, and Mac system events."
- **useful because:** This would allow the Mac AI agent to have richer situational context for more relevant and adaptive computer control and conversation support, beyond just UI state or calendar data.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 2 seconds for sensor fusion and context update
- **cost:** moderate compute for audio feature extraction and event correlation
- **security:** Audio features processed locally; no raw audio or private data leaves device without explicit consent; event data limited to what is needed for agent contextual awareness.
- **missing:** Real-time multi-sensor fusion framework; Cross-surface event synchronization protocols; Privacy-preserving local audio feature extraction

### "Allow mac-vision to query and interact with the owner's active browser tabs via a standardized API that fuses browser-extension data and Mac system state."
- **useful because:** This would enable seamless handoff between Mac desktop automation and live in-browser actions, allowing complex workflows that span local apps and web pages.
- **path:** mac-vision → browser-extension → mac-planner
- **model tier:** realtime
- **latency:** under 2 seconds
- **cost:** minimal API cost on relay and Mac
- **security:** Strict access control to browser sessions; permissions managed on Mac and within browser extension
- **missing:** Unified session management API; Cross-surface browser state synchronization

### "Build a real-time undo and redo framework integrated with mac-vision and mac_run_actions that records all reversible UI actions and allows owner to rollback or replay recent changes."
- **useful because:** This would give the owner confidence to delegate multi-step UI workflows to mac-vision without fear of irreversible errors, improving trust and usability.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 1 second for undo/redo command execution
- **cost:** low server cost, mostly local state management
- **security:** Careful control to prevent abuse of undo system, logging of user actions for traceability
- **missing:** Standardized action receipts and rollback hooks; Multi-step UI action transaction management; Owner-facing UI for undo history

### "Enable mac-vision to retrieve and summarize the owner's active tasks across all surfaces and present a unified natural language task briefing based on priority and deadlines."
- **useful because:** This would help the owner quickly understand what work is pending across devices and contexts without manual checking, enabling more efficient planning and context switching.
- **path:** mac-vision → mac-planner → pendant
- **model tier:** realtime
- **latency:** under 2 seconds
- **cost:** moderate due to reasoning over multiple data sources
- **security:** Task data access must be secure and privacy-respecting, no data leaks between contexts
- **missing:** Cross-surface task aggregation API; Reasoning model tuned for task summarization; Unified presentation UI


## Changes it proposed to its own stack

### `integration` — Develop an integrated task prioritization and dependency planner that merges owner task facts from memory with calendar and reminders data, generating a dynamically ranked actionable task list for mac-vision to act on.
- **owner gets:** This would let mac-vision focus computer UI automation and agent actions on the most important and urgent owner goals, improving productivity and reducing distractions from low priority or outdated tasks.
- effort: medium to high; requires work on memory services, day plan parsing, and mac-vision contextual ranking logic.  ·  risk: Mis-prioritization could cause frustrating delays or omissions; mitigated by transparent logs and owner correction.
- cost: low API and compute cost; mostly local computation on Mac and relay.  ·  latency: under 3 seconds typical response latencies.
- security: No additional data collected; uses existing authorized sources.
- depends on: Confirmed access to calendar and reminders data; Reliable current task facts in memory

### `hardware` — Redesign the pendant hardware to include a dedicated second physical button for richer gesture and moment marker input, allowing more expressive user signaling without latency or finger lift delay.
- **owner gets:** This would enhance the tactile control vocabulary available on the pendant, allowing more nuanced interactions and separating moment marking from speech activation, improving responsiveness.
- effort: medium hardware redesign and firmware update  ·  risk: Increased manufacturing complexity and slight increase in power draw; recovery possible with fallback single-button mode.
- cost: moderate additional hardware cost; low increase in power usage  ·  latency: negligible
- security: No direct additional security risk; button presses are local events with optional sync to Mac
- depends on: Redesign of PCB and enclosure; Firmware and driver updates for two-button support

### `model-routing` — Implement dynamic routing of agent models where mac-vision can delegate natural language understanding or complex planning steps to cloud or local models depending on latency, load, and cost, optimizing owner experience.
- **owner gets:** This would improve responsiveness and cost efficiency of the mac-vision agent, ensuring complex decisions are done in the right place and simple decisions locally for speed.
- effort: low to medium, mostly engineering on routing and orchestration layers  ·  risk: Routing errors could add latency or confusion; fallback mechanisms needed
- cost: may reduce costs by offloading expensive work strategically  ·  latency: optimal paths reduce perceived latency
- security: Routing decisions must preserve data privacy and regulatory limits
- depends on: Stable multi-model infrastructure; Clear model capability metadata


## What it asked for

_Nothing._
