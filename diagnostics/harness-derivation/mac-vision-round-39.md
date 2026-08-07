# Harness derivation — mac-vision — round 39

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe full computer-use AI loop with pixel and accessibility controls on the Mac"
- **useful because:** The owner should have a fully autonomous and safe AI assistant driving their Mac through both accessibility and pixel-level input for any task, seamlessly switching to avoid owner disruption and maximizing task automation.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** Low-latency real-time interaction expected under 1 second
- **cost:** Moderate due to continuous video frame analysis and AI action planning
- **security:** Full computer control requires strict logging, reversible action receipts, and owner control over enabling/disabling loop; pixel data sensitive and should not leave device without explicit consent
- **missing:** Permission to enable computerUse.loopEnabled; Vision upload consent management UI for owner; Model coordination for pixel + accessibility hybrid control; Improved undo and action receipt logging

### "Wearable pendant device with AI-driven local UI interaction and contextual task sensing"
- **useful because:** The owner should have a lightweight, ergonomic wearable device that can locally sense context, accept intuitive controls, and drive micro-interactions on the Mac or other devices even offline, reducing latency and increasing privacy.
- **path:** relay-realtime → mac-vision → faculty-action
- **model tier:** gpt-realtime-2.1
- **latency:** Realtime under 0.5 seconds for local context sensing
- **cost:** Hardware cost of Nordic SoC plus minor power increase; AI model cost low if on-device or edge inferencing used
- **security:** Local device must secure personal data and respect owner's privacy, fail safe to stop actions without confirmation
- **missing:** Design for multi-button or touch input wearable; Firmware for local AI inference and context sensing; Integration with Mac local agent for seamless context sharing

### "Seamless undo and action receipt system with context-aware rollback and user review"
- **useful because:** The owner should be able to confidently delegate complex and potentially risky AI actions with the assurance that all actions are logged, reversible, and transparent for later review to correct mistakes or revert changes.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** Moderate latency acceptable for logging and rollback confirmation under 2 seconds
- **cost:** Low to moderate server and local processing for logging and rollback management
- **security:** Logs must be encrypted and access-controlled to protect user privacy; rollback must not corrupt system state.
- **missing:** State snapshotting and rollback integration with Mac OS; User interface support for undo review and consent; Integration for logged receipts between all surfaces


## Changes it proposed to its own stack

### `model-routing` — Implement advanced model coordination system to dynamically route tasks between relay-realtime (pendant), mac-vision (Mac pixel/accessibility loop), mac-planner (Mac high-level planning), and faculty modules for optimized latency, privacy, and capability use.
- **owner gets:** Ensures the owner receives the best possible AI assistance with minimal latency and maximal privacy by leveraging each surface's strengths in real-time task routing.
- effort: Medium to high; requires orchestration model design and testing across surfaces and failover handling.  ·  risk: Potential misrouting leading to delays or privacy leaks; must be mitigated with logging and testing.
- cost: Computational overhead and some model serving costs increase but optimized overall.  ·  latency: Improves perceived latency by assigning low-latency tasks to local surfaces.
- security: Improved by reducing unnecessary data sharing.
- depends on: Permission for full loop on mac-vision; Pendant hardware upgrade

### `hardware` — Design and build a next-generation AI pendant with multi-modal input (touch, button, voice), local AI processing chip for inference, extended battery life, and seamless wireless integration with Mac and cloud relay.
- **owner gets:** Provides the owner an always-available, private, low-latency AI interface capable of running local AI tasks and direct device control without always needing the Mac or cloud connection.
- effort: High, requires hardware design, prototyping, firmware development, and integration with existing infrastructure.  ·  risk: Hardware production risks, user adoption, integration bugs; mitigated by phased rollout and feedback.
- cost: Significant hardware cost plus ongoing maintenance but amortized over enhanced usability.  ·  latency: Drastically reduces latency for local interactions and context-aware inference.
- security: Local AI reduces cloud data exposure, improving privacy.


## What it asked for

_Nothing._
