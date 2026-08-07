# Harness derivation — mac-vision — round 49

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a cross-device interactive permission repair assistant to safely guide the owner through granting and maintaining Accessibility and Screen Recording permissions on the Mac for the AI Pendant Agent."
- **useful because:** This capability unlocks the ability of the mac-vision loop to see and act on the Mac UI and screen pixels, which is essential for many computer use automation tasks that cannot be done via APIs. It improves safety by making permission granting explicit, contextual, and user-driven, preventing silent or unauthorized control. It also supports maintaining these permissions over time and recovering from permission loss dynamically.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** realtime
- **latency:** sub-second for interaction, longer for background permission state polling
- **cost:** moderate because it consists mostly of prompts and UI read/write actions rather than heavy LLM compute
- **security:** High trust is required; must not activate full control mode without explicit owner confirmation at each step. Sensitive permission states are handled only locally or with encrypted relay communication. Prompting design must avoid social engineering risks.
- **missing:** a detailed, user-friendly permission state visualization and interactive guidance UI; integration of cross-device state sync for permission status and user prompts; a non-invasive periodic permission check and reminder infrastructure; robust fail-safe logic to disable mac-vision actions automatically if permissions get revoked or corrupted

### "Allow the mac-vision loop to verify and validate UI hierarchy snapshots and permission states locally with cryptographic attestation from the pendant before enabling computer use actions."
- **useful because:** This capability adds a robust security layer to ensure that mac-vision actions only proceed when valid UI and permission states are confirmed securely by the trusted pendant device, preventing spoofing or unauthorized control activation.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** must execute within a second to avoid delays in interaction
- **cost:** low to moderate compute cost for cryptographic verification
- **security:** High security requirement to prevent any spoofing or bypass attempt; requires secure hardware root of trust on pendant.
- **missing:** protocols for cryptographic attestation; firmware and mac-vision loop code to perform verification and validation


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure hardware button or switch on the pendant specifically for the owner to instantaneously enable or disable the mac-vision computer use loop permissions and actions on the Mac.
- **owner gets:** This allows the owner to physically and rapidly intervene on mac-vision control capability in case of any unwanted behavior or security concerns without needing to navigate any software interface or wait to disable digitally. It gives ultimate and immediate physical safe control over automation permissions.
- effort: Moderate hardware design and firmware update, plus integration with existing permission gating logic in the mac-vision loop.  ·  risk: Risk of physical button malfunction or accidental toggling, mitigated with confirmation presses or multi-step gestures.
- cost: Low incremental hardware cost and minimal additional power draw.  ·  latency: No latency impact; intended for real-time immediate control.
- security: Improves security by providing a fail-safe out of software control.
- depends on: current mac-vision permission gating mechanisms; firmware update infrastructure

### `integration` — Develop a privacy-preserving protocol and encrypted sync mechanism between the mac-vision loop, pendant, relay, and mac-planner to share real-time permission states, user confirmations, UI observations, and repair prompts securely across devices for the cross-device permission repair assistant.
- **owner gets:** Ensures that the owner always experiences consistent, transparent, and secure prompting and repair of necessary permissions regardless of device used, preventing permission confusion and enabling seamless, user-driven recovery without exposing sensitive UI or permission details externally.
- effort: Significant software engineering on all involved components to define secure protocols, encrypt data, handle offline scenarios, and UI/UX design for prompting.  ·  risk: Improper encryption or sync bugs could expose sensitive permission or UI state; careful design and review required.
- cost: Moderate compute and bandwidth cost due to encryption and frequent state sync.  ·  latency: Minor; primarily background and asynchronous.
- security: Strong security impact; demands high trust and cryptographic integrity.
- depends on: hardware support for encryption; relay and pendant secure channels; mac-vision loop permission state awareness

### `dashboard-ux` — Create a dedicated dashboard section visible on the owner's Mac and the pendant with a live display of the current mac-vision permission states including Accessibility, Screen Recording, and vision consent, plus step-by-step repair guidance, progress saving, and history of recent permission changes with explanations.
- **owner gets:** Provides the owner with a transparent, easy-to-understand control center to monitor and resolve permission issues, reducing confusion and improving trust and control over computer use automation capabilities tied to these permissions.
- effort: Medium frontend and backend work to aggregate permission states, UI/UX design for clarity and accessibility, integration with cross-device sync protocol.  ·  risk: Minimal; UI-only except permission state reading.
- cost: Low to moderate, mostly UI rendering and state polling.  ·  latency: Negligible, as mostly event-driven.
- security: Moderate, must securely fetch and show sensitive permission state only to owner.
- depends on: integration encryption and sync; mac-vision loop permission data

### `model-routing` — Implement a specialized context-aware permission and repair prompt model tier that runs in realtime to interpret mac-vision loop permission states, owner responses, and UI hierarchy snapshots to generate clear, empathetic, and concise instruction dialogs and confirmation requests to the owner.
- **owner gets:** This makes permission granting and repair a natural conversation rather than a confusing technical chore, improving owner understanding, reducing errors, and increasing safe adoption of mac-vision capabilities.
- effort: Medium to high AI/ML engineering to train and route permission conversation models, plus integration with existing mac-vision context and dialog systems.  ·  risk: Model misinterpretation or prompt confusion; needs thorough testing and fallback prompts.
- cost: Moderate, requires realtime model inference on owner interaction moments.  ·  latency: Must be low latency for smooth conversation.
- security: Moderate to high, must ensure no unauthorized prompting or activation of control.
- depends on: mac-vision context access; dialog system integration; permission state data

### `firmware` — Update pendant firmware to handle encrypted secure storage and user-triggered permission consent state toggling with strict timing and multi-factor physical interaction constraints to ensure no accidental or malicious switches occur.
- **owner gets:** Firmware-level enforcements prevent unauthorized software from toggling critical permissions or control states without explicit, deliberate owner physical intervention on the pendant hardware, increasing trust and security.
- effort: Moderate firmware development with cryptographic key management and physical input logic.  ·  risk: Firmware bugs could lock out permission toggling; requires recovery mode.
- cost: Minimal, impacts pendant flash and RAM usage slightly.  ·  latency: No latency impact during normal operation.
- security: High, critical for secure permission gating.
- depends on: hardware button/switch design; secure key storage in pendant


## What it asked for

_Nothing._
