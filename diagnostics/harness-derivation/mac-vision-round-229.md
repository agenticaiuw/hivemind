# Harness derivation — mac-vision — round 229

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide me a prioritized and metadata-rich task list of what the owner explicitly wants done on the Mac now, including due dates and dependencies."
- **useful because:** Currently, no live source of prioritized Mac tasks exists for the mac-vision agent to work from. This capability enables progressive, meaningful Mac automation aligned to what the owner cares about.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** under 2 seconds
- **cost:** low, single API call plus memory projection
- **security:** Must respect owner data confidentiality and only expose explicitly allowed tasks.
- **missing:** A writable persistent Mac task store with priority and metadata, plus UI to edit them.

### "Detect and report discrepancies between intended workflow steps and actual Mac UI state by integrating UI snapshots (accessibility trees) with workbench context data."
- **useful because:** This improves automation observability and allows recovery or retries on failed or diverged workflows, enhancing owner trust in Mac vision automation.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** under 3 seconds
- **cost:** medium, requires UI snapshot processing and context diffing
- **security:** Only metadata and accessibility structure read, no screen pixels or private content leaked beyond owner.
- **missing:** A metadata reconciliation engine, incremental snapshot merging, and UI/context correlation schema.

### "Enable natural language and pendant button-driven injection of explicit Mac task goals that the owner can update or reprioritize live."
- **useful because:** Gives the owner direct, low-friction control over what the Mac vision agent works on, increasing ownership and responsiveness of automation.
- **path:** pendant → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** instant to sub-second response
- **cost:** low, simple command parsing and memory fact writes
- **security:** Needs explicit owner confirmation for intrusive or destructive commands.
- **missing:** A small natural language UI on the pendant or voice, plus task injection API tied to memory/facts.

### "Provide real-time or near-real-time status and progress feedback for multi-step mac_delegate workflows back to the owner via voice and dashboard interfaces."
- **useful because:** Owners need visible evidence and trust in long-running or ambiguous Mac tasks, improving confidence and allowing intervention if stuck or failed.
- **path:** mac-vision → relay-realtime → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** under 5 seconds
- **cost:** medium, requires message routing and UI updates
- **security:** Progress info is about owner activities and must be secured.
- **missing:** A progress monitoring and feedback channel linking mac_delegate and user-facing surfaces.

### "Continuously monitor and detect anomalies or stalls in Mac UI automation workflows and proactively notify the owner via pendant announcements or dashboard alerts."
- **useful because:** Automation can stall or fail silently, reducing owner trust. Proactive anomaly detection encourages owner confidence and faster recovery.
- **path:** mac-vision → pendant → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** seconds to detect and notify
- **cost:** medium, requires log analysis and pattern recognition
- **security:** Sensitive task and UI state data remains private to the owner.
- **missing:** An anomaly detection model trained on normal vs. stalled Mac automation run patterns.

### "Enable the Mac vision agent to directly observe and reason about the real-time accessibility tree and actual UI state on the Mac during automated workflows, not just the intended workflow steps, and compare this to the claimed workbench contexts to detect discrepancies and recover automatically."
- **useful because:** Current automation workflows only track intended steps without real-time observation of actual on-screen UI state. Direct real-time UI feedback integrated with workflow contexts would create a closed loop, enabling automatic recovery from UI changes, dynamic adaptation to unexpected UI states, and increased automation reliability and owner trust.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** under 5 seconds
- **cost:** medium, requires continuous UI snapshot processing and memory comparison
- **security:** Only authorized agents observe accessibility data, ensuring no pixel or privacy leaks; data handled locally or encrypted for relay.
- **missing:** A persistent, queryable UI snapshot storage and correlation engine integrated with workbench context tracking.; Continuous data flow from the mac-vision agent accessibility observer module to this system.; Automatic reconciliation and recovery logic in the mac-vision automation system.

### "Implement an always-on local UI state observer in the mac-vision agent that persistently collects incremental diffs of the Mac's accessibility tree and UI structure while running automation workflows, providing a timeline of UI states that can be efficiently queried and compared to workflow steps."
- **useful because:** This gives unprecedented observability and forensic ability into how Mac UI automation actually progresses, enabling better diagnosis, error recovery, and auditing of automation runs. It also supports incremental learning and adaptive planning based on real UI conditions.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** real-time to low seconds
- **cost:** medium, requires local storage and efficient diff algorithms
- **security:** Sensitive UI metadata retained only locally or encrypted; must ensure no sensitive data leaks.
- **missing:** Incremental UI diff capture and storage module in mac-vision.; Query API for UI state timeline linked to workflow steps.; Integration with run logging and error recovery subsystems.

### "Add a capability that allows the owner to tag any moment during Mac UI automation by pressing the pendant button once, capturing and timestamping the current UI state and workflow step, for later review and debugging."
- **useful because:** This gives the owner a direct way to mark points of interest or issues during automation runs, aiding in debugging, progress review, and training improvements.
- **path:** pendant → mac-vision → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** instantaneous on button press
- **cost:** low, small write operation and metadata capture
- **security:** Button press metadata and UI context stored securely and accessed only by authorized agents and the owner.
- **missing:** Integration of pendant button hardware event with mac-vision UI snapshot module and timestamping.; Storage for tagged moments and associated metadata.; Dashboard UI for review and playback of tagged moments.


## Changes it proposed to its own stack

### `hardware` — Add a second physical input button to the pendant device to allow independent non-conversational triggers and richer state toggling gestures.
- **owner gets:** The pendant's single button is fully booked for conversation start and stop. A second button would allow more expressive and reliable interaction patterns without delaying critical microphone activation.
- effort: Medium hardware design and firmware update effort.  ·  risk: Minimal risk; additional button to be integrated carefully to avoid power drain or interference.
- cost: Small increase in hardware cost; negligible power draw increase.  ·  latency: None.
- security: None.

### `integration` — Create a typed event stream and cross-surface notification system that relays key state changes from mac-vision, pendant, and relay-realtime agents, including task progress, hardware status, and explicit owner-interaction events.
- **owner gets:** This unified event fabric enables seamless real-time awareness and control of current state and task execution from any device or interface, minimizing cognitive load and errors.
- effort: Medium backend and agent integration effort, requires schema design and API extension.  ·  risk: Event ordering and consistency challenges; mitigated by strong typing and versioning.
- cost: Moderate API and backend costs due to increased event volume.  ·  latency: Minor impact, events mostly asynchronous.
- security: Requires careful authentication and authorization to prevent data leakage.
- depends on: workbench/contexts

### `model-routing` — Route UI snapshot and accessibility tree data streams through a specialized, high-priority, low-latency model tier dedicated to real-time UI state analysis and anomaly detection for mac-vision workflows.
- **owner gets:** This allows immediate detection of UI automation failures, unexpected modal dialogs, or state drifts, enabling faster recovery and more consistent automation outcomes, increasing owner trust and workflow efficiency.
- effort: Medium engineering effort to build a dedicated event stream pipeline and configure/maintain the model tier for real-time processing.  ·  risk: Possible increased compute resource use and cost; mitigated by efficient filtering and event prioritization.
- cost: Moderate due to real-time processing needs and higher priority model allocation.  ·  latency: Low latency to meet real-time requirements.
- security: Data streams must be securely routed and access-controlled.
- depends on: vision-loop/preflight; relay_event_push


## What it asked for

_Nothing._
