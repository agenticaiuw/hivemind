# Harness derivation — mac-vision — round 132

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Proactive computer vision loop that can observe the Mac's UI accessibility structure and pixel-based screenshots, then decide and execute UI interactions autonomously to assist with complex workflows and error recovery."
- **useful because:** This capability would allow the system to anticipate the owner's needs, perform multi-step UI interactions without explicit commands, and handle UI states that current API-only actions cannot manage, thus massively improving productivity and reducing manual effort.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime conversational AI with fallback to background AI for planning
- **latency:** under 1 second for decision-making, with background recovery allowed
- **cost:** moderate - mostly from model inference and screenshot processing
- **security:** needs permission to access UI and screenshots, risk of unintended clicks or actions, requires audit logs and owner override
- **missing:** permission for computerUse.loopEnabled; permission for visionUploadConsented; full UI hierarchy snapshot context; pixel screenshot access

### "Cross-device workflow orchestration using multi-modal input from Mac UI state, voice commands from pendant, and remote relay processing for long-running tasks."
- **useful because:** Combines the strengths of the wearable pendant for voice input, the Mac for executing complex UI and app tasks, and the cloud relay for persistent state and deferred work. This enables seamless, intelligent assistance that feels unified and context-aware.
- **path:** mac-vision → relay-realtime → pendant → mac-planner
- **model tier:** hybrid real-time and background models for coordination
- **latency:** sub-second interaction latency, multi-second for deferred work
- **cost:** higher due to cloud relay and multiple device coordination
- **security:** requires secure inter-device communication, synchronization safeguards, and privacy protections
- **missing:** real-time relay registration and stable connection; robust multi-device state sharing protocols

### "Context-aware assistance that dynamically adapts based on the real-time UI snapshot and user intent inferred from voice commands and ongoing tasks."
- **useful because:** This would allow the system to provide targeted help, shortcuts, and information at the right moment, reducing cognitive load and enhancing efficiency.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime for intent inference and background for context aggregation
- **latency:** under 500 ms for user interactions
- **cost:** moderate due to continuous context processing
- **security:** requires careful data handling and consent management
- **missing:** integration of UI hierarchy snapshot, voice command parsing, and task state from multiple devices

### "Owner-driven safe mode for the Mac-vision AI loop including a live action preview and approval step before execution to prevent unintended states and ensure transparency."
- **useful because:** Gives the owner control and confidence when enabling deep UI interaction by showing intended actions in advance and requiring approval, reducing risk of erroneous or harmful actions.
- **path:** mac-vision → mac-planner → pendant
- **model tier:** realtime for action preview and approval
- **latency:** under 2 seconds for preview and owner response
- **cost:** low but requires UI integration
- **security:** Ensures no action is executed without explicit owner consent
- **missing:** UI for preview display, input capture for confirmation, and integration with mac_run_actions

### "An intelligent help system that watches the Mac UI state and the owner's commands, detects when the owner is stuck or error-prone, and proactively suggests or performs corrective actions to resume workflow smoothly."
- **useful because:** Reduces frustration and downtime by anticipating and resolving roadblocks in real time without explicit owner intervention, improving user productivity and experience.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime anomaly detection with background learning
- **latency:** under 1 second for detection and suggestion
- **cost:** moderate for continuous monitoring and inference
- **security:** Requires transparent operation and opt-in to avoid intrusive behavior
- **missing:** real-time UI and task context sharing, error detection models, integration with action execution tools


## Changes it proposed to its own stack

### `hardware` — Upgrade the pendant and Mac connectivity with a dedicated high-bandwidth, low-latency wireless link in addition to USB, enabling the Mac-vision agent to receive real-time pixel and accessibility UI state continuously from the Mac without impacting owner workflow or requiring physical cables.
- **owner gets:** Provides seamless continuous UI state feeds to the AI agents for faster, more precise proactive assistance and complex multi-device orchestration without user disruption.
- effort: Requires hardware and firmware development for wireless protocol and antenna integration, plus software support on both sides.  ·  risk: Hardware integration may cause interference or reliability issues, mitigated by extensive testing and fallback modes.
- cost: Moderate hardware cost increase, offset by usability gains; minimal increase in power draw.  ·  latency: Significant reduction in UI state transmission latency and increase in throughput.
- security: Requires secure encrypted wireless link to prevent eavesdropping or injection attacks.
- depends on: firmware changes in pendant and Mac software stack


## What it asked for

_Nothing._
## Its own summary

Recorded multiple novel capabilities for proactive computer vision on the Mac, cross-device workflow orchestration, context-aware real-time assistance, owner-driven safe mode for AI actions, and intelligent help systems that detect and recover from user errors. Also proposed hardware improvements for real-time UI state transmission. Each proposal identifies what is missing in permissions, integration, or hardware to enable these transformative features.

**Biggest unknown:** Whether permissions and technical infrastructure for real-time UI observation and secure multi-device coordination will be granted and implemented to enable these advanced capabilities.

