# Harness derivation — mac-vision — round 76

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a safe and privacy-respecting computer use loop for mac-vision to act as the owner's intelligent Mac interface."
- **useful because:** The owner should be able to delegate complex UI navigation and multi-app workflows directly to mac-vision, saving time and cognitive effort. This enables near-human-level assistance with any software UI on the Mac, beyond simple typed commands.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** gpt-4.1-mini for UI understanding and action decisions, gpt-5.6-luna for overall session management and orchestration.
- **latency:** Sub-second decision latency for UI interactions with background orchestration taking seconds for complex workflows.
- **cost:** Moderate cost primarily from UI analysis and multi-step planning; action execution calls are low cost.
- **security:** Full gaze and screen content awareness; requires explicit owner consent, opt-in controls, and encryption to avoid leaks or abuse.
- **missing:** A robust UI snapshot permission and privacy architecture to enable UI hierarchy capture safely.; Clear, owner-configurable policy settings for loopEnabled and visionUploadConsented toggles.; Outcome verification mechanisms to ensure mac-vision changes only what is intended.; Emergency stop or pause controls accessible to the owner in real-time.

### "Allow mac-vision to request and receive UI accessibility hierarchy snapshots in real time from faculty-perception to facilitate precise UI navigation without screen captures."
- **useful because:** Current mac-vision cannot progress without real-time UI structure data; enabling this would allow accurate and context-aware UI actions while respecting privacy.
- **path:** mac-vision → faculty-perception
- **model tier:** gpt-4.1-mini for UI parsing and navigation decisions.
- **latency:** Sub-second snapshot retrieval during interaction cycles.
- **cost:** Low, mainly message passing and parsing costs.
- **security:** Requires strict access control and data minimization to prevent leaking sensitive UI content.
- **missing:** A secure, permissioned protocol for real-time UI hierarchy snapshot requests and delivery between surfaces.


## Changes it proposed to its own stack

### `model-routing` — Integrate gpt-4.1-mini mac-vision for real-time UI understanding and action decisions with gpt-5.6-luna mac-planner and relay-realtime for orchestration and voice interaction to achieve seamless multi-modal Mac control.
- **owner gets:** This ensures that mac-vision can execute UI operations in lockstep with planning and vocal commands, making complex Mac workflows more natural and accessible.
- effort: Medium integration work to design message passing, context synchronization, and fallback strategies.  ·  risk: Increased system complexity may cause coordination bugs; requires monitoring and graceful fallback on failures.
- cost: Small increase in API calls and compute due to coordination.  ·  latency: Moderate impact due to orchestration delays, minimized by asynchronous messaging.
- security: Needs careful handling of data privacy in routing messages and state.
- depends on: mac-vision loop enabled; owner consent on vision data

### `interaction` — Create an explicit owner permission and control interface for managing computerUse loop activation, visionUploadConsented states, privacy boundaries around UI screenshots or hierarchy data, and emergency stop controls accessible via pendant voice commands or Mac UI.
- **owner gets:** Safe and clear owner controls are essential for privacy, trust, and preventing unwanted or mistaken mac-vision actions, enabling confident use of powerful UI automation.
- effort: Medium to high, involves UI design, secure state management, and integration with hardware buttons and voice recognition.  ·  risk: Incorrect implementation could lead to accidental privacy compromise or inability to halt actions promptly.
- cost: Low to moderate increase in UI and backend management logic.  ·  latency: Negligible except for control command processing which should be immediate.
- security: High, this layer needs robust security measures to protect control interfaces from misuse or hacking.
- depends on: hardware support for pendant controls; relay-realtime voice interaction

### `hardware` — Add a dedicated physical button and LED indicator on the pendant to enable/disable mac-vision computerUse loop and vision consent states quickly and visibly, including a long-press emergency stop feature.
- **owner gets:** Provides a tactile, reliable fail-safe control for the owner to instantly stop or start the AI's UI control, improving safety and trust in powerful automation.
- effort: Low to medium, requires pendant redesign and firmware update to handle the new button and indicator states.  ·  risk: Physical button failure or accidental press could disrupt experience, needs debounce and press pattern logic.
- cost: Small increase in hardware cost and complexity.  ·  latency: None, device local control.
- security: Physical actuation greatly reduces remote hacking risk for control toggles.
- depends on: pendant hardware revision; firmware update to support new controls


## What it asked for

_Nothing._
