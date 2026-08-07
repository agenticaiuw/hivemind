# Harness derivation — mac-vision — round 89

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the MacVision computer-use loop with safe, privacy-respecting screenshot and UI control to automate complex Mac workflows seamlessly."
- **useful because:** The owner wants true AI-driven Mac interaction that can read the screen and UI context fully, perform multi-step complex tasks that no single API can handle, and safely execute reversible commands without interrupting the owner unless necessary.
- **path:** mac-vision → mac-planner → relay-realtime → pendant → browser-extension
- **model tier:** gpt-4.1-mini for vision actions, gpt-5.6-luna for planning and orchestration
- **latency:** Interactive responsiveness expected within 1-2 seconds for reading UI and responding; longer multi-step workflows allowed to take minutes if progress reporting is available.
- **cost:** Higher cost due to vision model usage, screen capture, and multi-step execution; dominated by model inference and data transmission costs.
- **security:** Screenshots and UI data are sensitive; must have strict privacy consent and storage controls. All mutating actions require reversible design and user confirmation for destructive changes.
- **missing:** Owner consent for vision data upload and usage; Secure, granular action confirmation framework; UI hierarchy snapshot and accessibility event streaming; Local caching of sensitive data to minimize upload; Multi-step workflow control with progress tracking

### "Enable a hybrid AI assistant mode that leverages the MacVision loop's UI understanding combined with the mac-planner's long-term multi-app workflows and the relay-realtime's voice interface for hands-free, eyes-free Mac control."
- **useful because:** This combines strengths of multiple surfaces to allow the owner to initiate, monitor, and adjust complex Mac workflows by voice command in real time, without needing to manually interact with the Mac's UI or focus the screen.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-4.1-mini for UI understanding, gpt-5.6-luna for planning, gpt-realtime-2.1 for voice interface
- **latency:** Sub-second to 1-2 second responses for voice commands, longer for workflow execution.
- **cost:** Moderate to high due to multi-surface coordination and voice processing costs.
- **security:** Voice commands must be securely processed; UI data privacy must be enforced; workflow control must respect owner consent and allow overriding or halting.
- **missing:** Cross-surface workflow orchestration protocols; Voice-to-UI action translation with fallback and recovery; Real-time status feedback via pendant voice; Context sharing between surfaces maintaining privacy


## Changes it proposed to its own stack

### `integration` — Create a privacy-first, real-time UI hierarchy snapshot and event streaming system combined with a local reversible action log, to allow the MacVision loop to operate continuously without visual screenshots and with strict user control over mutating actions.
- **owner gets:** This will enable the MacVision loop to safely and effectively perceive the Mac UI and perform complex workflows without invading privacy or interrupting the owner's work, making AI interaction seamless and trusted.
- effort: Moderate to high engineering effort due to building a new event streaming system integrated with local reversible logging and explicit user consent flows.  ·  risk: If privacy controls are weak, sensitive screen and UI data could leak. Careful design and user controls must prevent unwanted data exposure or destructive actions without confirmation.
- cost: This will increase local resource usage for logging and event capture, and some cloud cost for event streaming and logging storage. It reduces expensive full screenshot uploads, balancing cost.  ·  latency: Event streaming and local logs are designed for very low latency to allow responsive AI action planning and execution.
- security: High security impact requiring encryption, local control, and user permission management.
- depends on: permission:computerUse.loopEnabled; permission:visionUploadConsented

### `model-routing` — Implement enhanced context routing and sharing protocols that preserve privacy but allow mac-vision, mac-planner, relay-realtime, and the pendant to coordinate in real time on multi-step workflows with voice and UI interaction combined.
- **owner gets:** The owner can seamlessly control their Mac through voice and UI with AI that appears coherent and unified despite involving different model tiers and physical devices.
- effort: Moderate engineering to design and implement secure, low-latency context routing and sharing protocols with privacy controls.  ·  risk: Improper routing could lead to data leakage or timing issues causing confusing user experience. Need robust privacy and failure recovery.
- cost: Increased bandwidth and compute cost from context sharing but optimized for minimal necessary data exchange.  ·  latency: Designed for real-time to near real-time coordination with minimal delay for user commands and AI responses.
- security: Requires strict encryption, access controls, and audit trails to protect owner data and command integrity.
- depends on: permission:computerUse.loopEnabled; permission:visionUploadConsented


## What it asked for

_Nothing._
