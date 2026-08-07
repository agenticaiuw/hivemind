# Harness derivation — mac-vision — round 43

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a fully autonomous and safe computer-use loop on the Mac that uses vision and UI hierarchy data to perform complex UI interactions with minimal owner intervention"
- **useful because:** The owner could have hands-free, highly capable Mac control for multi-step or ambiguous tasks that require visual context and interaction when APIs or terminal commands are insufficient, improving productivity and accessibility
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → relay-realtime
- **model tier:** gpt-5.6-luna for planning/judgement, gpt-4.1-mini for vision, gpt-realtime-2.1 for pendant voice interaction
- **latency:** Real-time or near real-time interaction within 100-200ms for UI responses
- **cost:** Moderate API spend due to vision processing, plus computational cost for planning and voice interaction; dominant cost is vision inference
- **security:** Privacy risk from screen capture and vision upload; risks from autonomous UI control. Requires strict gating, explicit owner consent, and robust action confirmation protocols.
- **missing:** Owner consent for vision upload and computer use loop activation; Accessibility API trust and Screen Recording permission granted to the AI Pendant Agent; Gating UI or interaction model for owner to approve or reject high-impact or destructive UI actions; Robust UI hierarchy snapshot feed integrated with vision processing; Multi-agent coordination protocols for vision-based UI action selection and corrective action; Offline fallback mode with local processing for privacy-sensitive tasks


## Changes it proposed to its own stack

### `hardware` — Add a dedicated local vision co-processor and secure enclave on the MacBook for real-time UI snapshot processing and vision inference without sending raw screen data to the cloud
- **owner gets:** Ensures privacy-preserving and low-latency vision-based computer use capabilities, enabling the owner to safely perform autonomous UI interactions without raw screen data leaving the device
- effort: High — involves hardware design and integration with Mac agent software  ·  risk: Hardware integration complexity; fallback needed if hardware unavailable
- cost: Moderate additional hardware cost and power draw for vision co-processor  ·  latency: Significant reduction in processing latency for vision tasks
- security: Enhanced security by limiting sensitive data exposure
- depends on: software support for a local vision inference pipeline; agent coordination protocols for managing vision data and UI actions

### `model-routing` — Route vision-based UI interpretation and decision-making to specialized models optimized for real-time interactive visual tasks, while delegating abstract planning to higher-tier models
- **owner gets:** Optimizes use of compute resources by matching problem complexity to model capacity, improving responsiveness of autonomous computer use loop and overall system efficiency
- effort: Moderate — requires engineering on model infrastructure and routing logic  ·  risk: Potential model coordination inconsistencies, manageable by fallback logic
- cost: Saves cost by avoiding overuse of costly large models for routine vision tasks  ·  latency: Reduces latency in UI action decision-making
- security: None significant
- depends on: existing multi-model infrastructure; model specialization and benchmarking

### `interaction` — Implement a real-time, multimodal confirmation interface on the AI Pendant device combining voice, haptic, and visual signals to confirm or abort high-impact Mac UI actions before execution
- **owner gets:** Provides a natural, immediate, and robust safety gating mechanism that allows the owner to control the AI's computer use actions in situ with minimal friction
- effort: Medium, requires software and firmware development on pendant and integration with Mac agent  ·  risk: User annoyance if excessive confirmation requests; fallback to less sensitive gating modes possible
- cost: Minimal software and device resource cost  ·  latency: Minimal added latency, handled asynchronously
- security: Enhances security by reducing risk of unintended destructive actions
- depends on: hardware with haptic and visual feedback capabilities; voice interaction capability; agent coordination for action gating

### `memory` — Develop a short-term episodic memory buffer specifically for UI interaction context to remember recent UI states, owner's confirmations, and recent computer-use tasks
- **owner gets:** Provides continuity and context awareness in autonomous computer use tasks to avoid repetitive or conflicting actions and enable smooth multi-step workflows
- effort: Low to medium, software-only development  ·  risk: Memory overflow or stale context can cause incorrect actions, mitigated by memory pruning and verification
- cost: Low, mostly in RAM and minor compute  ·  latency: None significant
- security: Value lies in local-only context retention, minimal data leakage risk
- depends on: integration with UI snapshot feeds; agent access to confirmation state and task status

### `context` — Provide a unified, real-time context graph aggregating UI hierarchy snapshot data, app status, user intent signals, and computer use loop state for coordinated reasoning across surfaces
- **owner gets:** Enables all agents including mac-vision to collaboratively understand the current Mac environment and user needs for accurate and safe autonomous UI operation
- effort: Medium to high, involving data streaming, merging, normalization and API development  ·  risk: Data synchronization delays or inconsistencies, mitigated by fallback mechanisms
- cost: Moderate due to continuous data flow  ·  latency: Minimal with optimized data handling
- security: Sensitive user data aggregation requires strong access control and encryption
- depends on: UI snapshot providers; agent integration; secure storage and streaming infrastructure


## What it asked for

_Nothing._
## Its own summary

Discovered Mac agent tools 'mac_run_actions' and 'mac_delegate' for reversible single-step and multi-step Mac UI actions. Confirmed Mac agent computerUse.loopEnabled = false, visionUploadConsented = false, missing accessibility and screen recording permissions block safe computer-use loop activation. Requested pending UI tasks status from faculty-perception and faculty-judgement. Identified that owner consent and permission grants are prerequisites for enabling the computer-use loop safely. Next steps: Await tasks, seek consent for permissions, then enable UI snapshots and vision-based action selection.

**Biggest unknown:** Owner consent and permissions required to activate computer-use loop on Mac-vision.

