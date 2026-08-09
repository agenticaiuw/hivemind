# Harness derivation — mac-vision — round 175

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Persistent, prioritized, actionable task and goal store shared across devices and surfaces."
- **useful because:** The owner can have a consistent agenda of what to do now, with priority, deadlines, and dependencies, usable by all AI agents and surfaces to coordinate work and reminders.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** background
- **latency:** sub-minute for updates, realtime for queries
- **cost:** Data store costs plus model costs for prioritization and natural language parsing.
- **security:** Task data may be sensitive; store encrypted; explicit user control of task visibility.
- **missing:** Task management UI and API integration; Cross-surface syncing mechanisms; Ownership, priority and dependency schema

### "A real-time system on the Mac that monitors changes in critical applications and system state relevant to the owner's tasks, pushing distilled updates and interaction triggers to mac-vision for proactive assistance."
- **useful because:** Allows the AI system to detect new emails, calendar changes, files updates etc., and proactively suggest or initiate appropriate UI actions or briefings, greatly improving responsiveness and timeliness of assistance.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** seconds to a minute
- **cost:** Model and system state monitoring costs on Mac; minor API and event handling costs.
- **security:** Must respect privacy and permissions; only trigger confirmed or non-destructive actions automatically.
- **missing:** System and application event monitoring integration; Proactive brief or action framework on mac-vision

### "A secure, privacy-preserving streaming interface from pendant audio and sensors to mac-vision and relay for multi-modal context-aware AI interaction."
- **useful because:** Allows tightly integrated audio context and sensor data from the wearable pendant to enhance Mac interaction and cloud AI services, enabling smarter, more responsive assistance tied to the owner's real-world environment.
- **path:** pendant → mac-vision → relay-realtime → unified
- **model tier:** realtime and background
- **latency:** low latency for interaction; background for analysis
- **cost:** Moderate due to streaming, processing, and cloud usage.
- **security:** Strong encryption and explicit user control of data streaming; clear consent required.
- **missing:** Streaming API between pendant and mac-vision; Cloud-side context integration


## Changes it proposed to its own stack

### `integration` — Integrate pendant button gesture events with mac-vision UI interaction loop, allowing wearable gestures to trigger Mac UI automation steps contextually.
- **owner gets:** Enables seamless bridging of wearable device input with Mac UI control, enhancing fluid multi-modal interaction and responsiveness.
- effort: Medium, requires changes to pendant firmware, mac agent event handling, and interaction design.  ·  risk: Misinterpretation of gestures might cause unintended actions; mitigated by confirmation and fallback mechanisms.
- cost: Negligible.  ·  latency: Low latency expected as events are local and immediate.
- security: Requires careful authorization to prevent accidental activation.
- depends on: mac-vision loop enabled; macOS Accessibility permission granted

### `hardware` — Design a pendant with multiple physical buttons or capacitive touch zones, allowing rich gesture vocabulary for triggering different AI agent functions, including mac-vision interactions and moment markers.
- **owner gets:** Expands the owner's physical interaction options with the AI system, enabling rapid, precise, and intuitive triggers of intelligent actions without relying solely on one button or screen.
- effort: High, requires new hardware design, firmware updates, and software integration.  ·  risk: Complexity could confuse; increased hardware cost and power consumption.
- cost: Significant on device cost; minimal on software.  ·  latency: Minimal.
- security: Must ensure deliberate user input and prevent accidental triggers.


## What it asked for

_Nothing._
## Its own summary

Proposed enabling full mac-vision accessibility loop, persistent prioritized task store, pendant-to-Mac gesture integration, real-time system state monitoring for proactive assistance, expanded pendant hardware controls, and secure streaming interface for multi-modal AI context.

**Biggest unknown:** Whether the owner will grant macOS Accessibility permission to fully unlock the vision loop interaction capabilities, and whether missing storage and streaming pieces exist or must be built.

