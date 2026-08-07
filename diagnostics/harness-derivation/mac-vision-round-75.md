# Harness derivation — mac-vision — round 75

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide an interactive, multimodal confirmation system for mac-vision loop actions, combining pendant button presses, haptic feedback, voice, and visual status on Mac and dashboard."
- **useful because:** Allows the owner to authoritatively approve or decline potentially impactful or irreversible GUI actions in real time without breaking task flow or privacy, increasing trust and safety of the automated computer-use loop.
- **path:** pendant → mac-planner → dashboard → mac-vision
- **model tier:** realtime
- **latency:** under 250 ms for critical confirmations
- **cost:** low to moderate, mostly software and firmware development with minimal hardware changes
- **security:** Must ensure button press translations cannot be spoofed; data must be encrypted end-to-end; guard against accidental or malicious dismissals.
- **missing:** Firmware support for multisensory interaction on pendant; Multi-channel confirmation UI support in mac-vision and planner; Refined action gating policies integrated with multisensory inputs.

### "Allow mac-vision loop to capture and interpret ephemeral UI states including transient dialogs, notifications, and drag-and-drop interactions distinguishing from static window content."
- **useful because:** Many complex Mac GUI workflows depend on temporary UI states that are invisible in accessibility trees alone. Recognizing these states enables the computer-use loop to handle such interactions fluently, reducing errors and missed steps.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** under 1 second for UI state capture and interpretation
- **cost:** medium — requires extending vision model training and inference, plus more frequent UI state polling.
- **security:** Ephemeral UI state parsing may expose sensitive transient data; must be properly scoped and vetted for privacy.
- **missing:** Ephemeral state capture protocols from Mac UI; Vision model training on transient UI elements; Integration with accessibility-based snapshots for fuller state


## Changes it proposed to its own stack

### `hardware` — Design and build a next-generation wearable pendant device with more RAM and CPU power, including a dedicated secure enclave for privacy-preserving local processing of vision and interaction data, plus additional sensors for better context awareness (eye tracking, proximity, gesture). Include multiple hardware buttons and haptic feedback actuators for richer non-voice control and confirmation.
- **owner gets:** To support a fully interactive and privacy-safe computer-use loop that enables natural, eyes-free, and safe control of the MacBook and other surfaces, with less reliance on cloud processing and more on-device autonomy and security.
- effort: High — new hardware design, firmware development, coordination with existing software stack; estimated multi-month engineering project.  ·  risk: Potential delay or failure in hardware development; risk of increased power consumption and size; integration challenges with current system.
- cost: High component cost; increased power draw affects battery life and charging needs.  ·  latency: Lower latency for vision and interaction processing on the device reduces reliance on cloud round trips.
- security: Improves security and privacy by confining sensitive data and decisions to the device hardware enclave.
- depends on: Improved software protocols to leverage enhanced device capabilities; Updated AI models optimized for on-device inference

### `interaction` — Create a developer toolchain and simulation environment for safe testing and auditing of mac-vision GUI automation sequences before deployment on the owner's live Mac, including action replay, state snapshotting, and rollback.
- **owner gets:** This toolchain would give the owner and developers confidence that automated GUI interactions will behave as expected without unexpected destructive actions or errors, reducing risk from the mac-vision loop.
- effort: Medium: development of simulation environment, integration with existing mac-vision components, UI for auditing and replay.  ·  risk: Limited coverage may still leave risks; complexity may delay delivery.
- cost: Moderate development cost, no runtime cost increase.  ·  latency: No direct latency impact on live tasks; enables safer deployment with less human oversight required.
- security: Improves security by enabling thorough testing before deployment, reducing chances of harmful actions.
- depends on: Access to complete UI state and event logging from mac-vision loop; Extend typed action receipts and undo mechanisms


## What it asked for

_Nothing._
