# Harness derivation — mac-vision — round 46

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full computer-use loop on Mac-vision for safe and effective pixel-level control and interaction"
- **useful because:** Owner can ask the worn pendant AI to interact with any UI elements on the Mac that are not accessible via APIs or delegated actions, including dynamically changing or graphical interfaces, enabling new levels of automation and live help.
- **path:** relay-realtime → mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini (low latency, local computer use loop)
- **latency:** 100-200 ms per action step, real-time interactive
- **cost:** Moderate token cost per step due to image processing, plus possible cloud compute for AI guidance
- **security:** Pixel-level control must be gated by explicit owner consent and real-time monitoring to prevent unintended actions. Vision upload consent required to protect privacy.
- **missing:** computerUse.loopEnabled flag must be true; visionUploadConsented must be set; UI hierarchy snapshot context for better understanding and precision; Typed action gating based on risk profiles and owner approval


## Changes it proposed to its own stack

### `hardware` — Add a secondary low-power camera on the MacBook that can provide real-time, high-resolution screen capture or partial region capture for the mac-vision agent without interfering with normal user interaction or privacy.
- **owner gets:** Facilitates continuous or on-demand pixel-level vision input to mac-vision without requiring the main system screen to be captured or interrupted, improving reliability and plausibility of computer use loop.
- effort: Moderate hardware and firmware development with OS integration.  ·  risk: Potential privacy concerns if camera access is misused; mitigated by physical shutter or LED indicator and owner control.
- cost: Moderate hardware cost; negligible power impact if low power camera used.  ·  latency: Low latency for region capture aiding real-time interaction.
- security: Requires strict access control and permission gating.
- depends on: computerUse.loopEnabled; visionUploadConsented; OS-level support for camera feed to AI agent

### `model-routing` — Introduce a dedicated computer-use vision model pipeline optimized for rapid understanding of Mac UI screenshots and pixel data, integrated with accessibility API data for deeper semantic understanding.
- **owner gets:** Allows mac-vision to interpret complex UIs, including graphical elements and dynamic controls, reliably and efficiently, enabling more effective automated interaction and guidance to the owner.
- effort: Significant AI model research and engineering for training, integration and deployment.  ·  risk: Model errors could cause incorrect UI interpretation leading to erroneous actions; requires fallback on accessibility API and human-in-the-loop corrections.
- cost: Elevated cloud compute cost for model inference; amortized by batching and caching.  ·  latency: Added inference delay; managed by optimized pipeline and caching.
- security: Model handles potentially sensitive screen contents; must adhere to strong data privacy and security policies.
- depends on: computerUse.loopEnabled; visionUploadConsented

### `integration` — Create a new integration layer that synchronizes pixel-level computer vision data from mac-vision with accessibility API insights and context from faculty-perception and faculty-judgement agents, enabling comprehensive UI state understanding and decision-making.
- **owner gets:** This integration empowers the system to jointly leverage different context sources to handle ambiguous or complex UI states, improving accuracy and robustness of automation and live assistance.
- effort: Moderate to high engineering effort to design data fusion protocols, event handling, and cross-agent communication.  ·  risk: Increased system complexity may introduce synchronization bugs or latency; robust testing and fallback modes are necessary.
- cost: Additional compute and network usage for data synchronization and cross-agent messaging.  ·  latency: Slight increase in end-to-end latency but within practical limits.
- security: Cross-layer sensitive data sharing requires strong encryption and authorization controls.
- depends on: computerUse.loopEnabled; visionUploadConsented; Enhanced model routing for computer vision

### `routines` — Develop a routine that empowers the owner to request a contextual screen reading or UI walkthrough from mac-vision, using combined accessibility and pixel vision input, with stepwise live narration and confirmation prompts.
- **owner gets:** This feature helps owners who have trouble navigating complex or unfamiliar apps by providing accessible, real-time UI descriptions and actionable guidance mediated by their pendant assistant.
- effort: Moderate engineering work for routine creation, voice interaction flow, and integration with mac-vision and relay-realtime.  ·  risk: If routing or descriptions are inaccurate, could confuse owner; mitigatable by fallback and owner override options.
- cost: Low to moderate, mainly API call costs, voice synthesis, and computational inference.  ·  latency: Realtime latency required for smooth conversational flow.
- security: Owner UI context data handled securely according to existing policies.
- depends on: computerUse.loopEnabled; visionUploadConsented; Integration of mac-vision data streams

### `memory` — Implement selective encrypted snapshot memory for UI states and actions taken by mac-vision, with owner-controlled retention policy and ability to review and undo recent changes easily across multiple sessions.
- **owner gets:** This memory capability allows the owner to safely track and audit automated or assistant-driven UI interactions, improving trust and error recovery in complex workflows.
- effort: Moderate engineering and security work for encrypted storage, session linkage, and UI undo features.  ·  risk: Memory misuse or leakage risk mitigated by encryption and owner control.
- cost: Storage and compute costs for encrypting and indexing snapshots.  ·  latency: Minimal latency impact on active use; background encrypting and indexing.
- security: Sensitive UI data encrypted at rest and in transit with strict access control.
- depends on: computerUse.loopEnabled; visionUploadConsented; Integration with job receipts and undo system


## What it asked for

_Nothing._
