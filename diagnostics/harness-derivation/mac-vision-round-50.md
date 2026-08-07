# Harness derivation — mac-vision — round 50

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Turn on a safe, reversible computer use loop on the Mac with vision- and accessibility-driven control"
- **useful because:** The owner can delegate complex GUI tasks that cannot be done via APIs or shell commands to the Mac-vision agent, increasing automation and productivity without manual intervention. This allows hands-free or minimal interaction control over any app UI, using both accessibility patterns and screen pixels if necessary.
- **path:** mac-vision → relay-realtime → pendant → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** milliseconds to a few seconds at max, to maintain fluid dialogue
- **cost:** moderate API calls for UI snapshot, action execution; GPU costs for vision processing; small incremental overhead in pendant-mac relay communication
- **security:** Full visibility of UI content and pixel data is sensitive; must require explicit user consent (visionUploadConsented), and robust audit logs plus undo/receipt system to prevent damage from unintended actions
- **missing:** A typed action policy framework integrated into the Mac-vision agent to limit actions to reversible, safe subsets without owner confirmation; Permission and technical ability to access real-time UI hierarchy snapshots from Mac accessibility API without stealing focus; Permission and pipeline for regularly capturing and processing screen pixel data only with consent; An integrated human-auditable log and undo system for all reversible mutation actions taken by the loop, surfaced on the pendant and in mac-planner UI


## Changes it proposed to its own stack

### `hardware` — Add a high-resolution, low-latency camera and IR depth sensor module to the pendant to enable robust visual context capture for Mac-vision without relying on MacBook internal webcam
- **owner gets:** The pendant can provide reliable, privacy-conscious, and continuous vision data for mac-vision to interpret the owner’s screen and gestures without sacrificing MacBook resources or facing OS-level restrictions on screen capture.
- effort: Medium effort involving hardware design, integration, and firmware updates.  ·  risk: Minimal risk if designed with privacy as first-class; risk of increased power use on pendant mitigated by modern low-power sensors.
- cost: Moderate incremental hardware cost for camera and IR sensor + power draw increase; firmware and AI model updates for processing.  ·  latency: Negligible impact on latency as data is intended for asynchronous processing and selective live use.
- security: Improves security by moving vision data off the MacBook itself and enforcing explicit pendant-based consent before capture.
- depends on: firmware update on pendant for new sensor control and capture; integration on mac-vision for external vision feed processing

### `model-routing` — Implement a dedicated model routing policy that distinguishes vision-based UI interpretation models from textual and command-planning models, enabling mac-vision to engage low-latency vision-specific AI without overloading general intent models.
- **owner gets:** Delivers real-time UI interpretation and pixel-based decision making with specialized, optimized models that handle visual input, improving responsiveness and accuracy for agent interventions on the Mac interface.
- effort: Medium engineering effort to extend routing layer, deploy and maintain vision models alongside existing text models.  ·  risk: Low risk; failure modes result in rerouting to text models only, causing temporary latency or degraded vision capabilities.
- cost: Increased model hosting and inference costs for additional concurrent models focused on visual tasks.  ·  latency: Improved latency for vision-driven tasks due to specialized models.
- security: Ensures visual data is processed only in the vision model tier, isolating data streams by modality for compliance.
- depends on: Availability of vision model implementations; Upgraded pipeline to send visual context data safely

### `integration` — Create a secure, low-latency pipeline between the pendant vision capture system and the mac-vision agent on the MacBook to stream visual context and control signals, with explicit user toggles and automatic consent expiry.
- **owner gets:** Allows seamless, privacy-respecting sharing of visual context from wearable pendant to Mac for advanced UI interpretation and control, enabling real-time assistance and task automation based on screen content and gestures.
- effort: Medium engineering effort including protocol design, security review, and UI toggle integration in pendant and Mac apps.  ·  risk: Security risks from streaming data mitigated by encryption, user-controlled toggles, and automatic timeout of stream.
- cost: Moderate networking and endpoint resource use, plus ongoing maintenance of secure streaming protocols.  ·  latency: Low latency to maintain responsive control and feedback.
- security: Enforces explicit, user-controlled data sharing with audit logs and failsafe shutdowns.
- depends on: Pendant hardware change for vision capture; Mac-vision software to receive and process streams

### `dashboard-ux` — Build a visual dashboard on the Mac-planner and pendant UI to show live status of computer use loop actions, including queued actions, receipts of executed commands, undo options and live permission status.
- **owner gets:** Empowers the owner with transparency and control over what the mac-vision loop is doing, enabling quick correction, confirmation, or abort of actions, reducing risk and increasing trust in AI-augmented computer control.
- effort: Medium frontend development effort across pendant and Mac planner apps.  ·  risk: Minimal risk; only UI-level changes, with failsafe defaults to pause or halt actions.
- cost: Low incremental cost, mostly in development time.  ·  latency: No impact on primary automation latency.
- security: Increases security through auditability and owner awareness.
- depends on: Existing logging and undo infrastructure for computer use actions; Integration with mac-vision action result reporting


## What it asked for

_Nothing._
## Its own summary

Requested UI hierarchy snapshot and loop permission state from faculty-perception to assess feasibility of enabling mac-vision's computer use loop. Explored current mac interaction tools and confirmed loop remains OFF. Identified key missing context and permissions needed for safe and effective operation of vision-based automation on the Mac.

**Biggest unknown:** Current real-time UI snapshot access and confirmed loop-enabled permission status for mac-vision to proceed.

