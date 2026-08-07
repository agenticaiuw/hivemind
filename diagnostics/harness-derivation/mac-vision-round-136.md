# Harness derivation — mac-vision — round 136

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a mac-vision visual UI hierarchy snapshot and analysis feed to inform action planning."
- **useful because:** A detailed snapshot of the Mac's current UI hierarchy and analysis of visible elements would allow the system to plan precise, contextually aware UI interactions, improving automation success and error recovery.
- **path:** mac-vision → mac-planner
- **model tier:** realtime low-latency
- **latency:** under 1 second per snapshot
- **cost:** light CPU usage, moderate context data bandwidth
- **security:** UI data may contain private information; needs careful handling and encryption.
- **missing:** permission computerUse.loopEnabled; context ui_hierarchy_snapshot

### "Coordinate mac-vision with mac-planner and faculty-perception agents for shared situational awareness and action planning."
- **useful because:** By sharing visual UI state and analyzing it collaboratively, the system can divide labor between typed actions and visual control effectively, reducing errors and increasing automation success rate.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** realtime low-latency
- **latency:** under 500ms response per update
- **cost:** minimal API cost, moderate internal messaging overhead
- **security:** Shared data must be encrypted and contain no persistent sensitive info without owner consent.
- **missing:** context ui_hierarchy_snapshot; permission computerUse.loopEnabled

### "Enable fully autonomous visual GUI manipulation and navigation on the Mac via mac-vision, combining pixel-level screen understanding, direct mouse and keyboard input, and contextual UI hierarchy awareness."
- **useful because:** This would enable the system to control the Mac visually in ways no typed API or accessibility can, allowing complex multi-step workflows in any app or UI context, proactive error recovery, and seamless integration of typed and pixel-based control.
- **path:** mac-vision → mac-planner
- **model tier:** realtime low-latency visual model
- **latency:** sub-second realtime response
- **cost:** high GPU and CPU use for image processing and input synthesis, moderate API calls
- **security:** Requires full screenshot access and input control, sensitive data exposure, must have strict owner consent and fail-safe undo capability.
- **missing:** permission computerUse.loopEnabled; permission visionUploadConsented; context ui_hierarchy_snapshot; hardware support for input event injection

### "Implement proactive visual error detection and recovery on the Mac using mac-vision's real-time screen capture and UI analysis, to catch unexpected UI states or conditions and automatically correct or notify the owner."
- **useful because:** Currently, if UI workflows break or unexpected dialogs occur, they stall automation or require manual intervention. A vision-based error detection system can improve reliability and reduce owner frustration by handling interruptions automatically or alerting promptly.
- **path:** mac-vision → mac-planner
- **model tier:** realtime low-latency visual and language models
- **latency:** under 1 second
- **cost:** moderate CPU and GPU for image analysis and state classification
- **security:** Screenshots contain private data; must have strict privacy controls and owner opt-in.
- **missing:** permission computerUse.loopEnabled; permission visionUploadConsented; context ui_hierarchy_snapshot

### "Create a unified contextual memory and UI state cache shared between mac-vision, mac-planner, and faculty-perception to store recent UI snapshots, parsed UI elements, and task states for robust multi-agent coordination."
- **useful because:** This shared memory would prevent duplication of visual parsing effort, enable consistent contextual understanding across agents, and allow recovery or rollback of UI task states.
- **path:** mac-vision → mac-planner → faculty-perception
- **model tier:** realtime low-latency orchestrated model
- **latency:** under 250ms per synchronization update
- **cost:** low CPU, moderate memory and network bandwidth for context sync
- **security:** Must encrypt and secure sensitive UI and task data, respect user privacy, and allow selective forgetting.
- **missing:** context ui_hierarchy_snapshot; integration middleware for multi-agent shared memory


## What it asked for

_Nothing._
