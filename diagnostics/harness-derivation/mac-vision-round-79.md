# Harness derivation — mac-vision — round 79

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, consented, and logged mac-vision loop for visual UI interpretation and action on the Mac"
- **useful because:** The owner cannot currently have the AI take visual screen captures and interpret UI elements to make complex decisions and interactions on the Mac beyond basic API actions. Enabling the mac-vision loop with strict owner consent, privacy controls, and active logging would unlock powerful, context-aware computer use that complements typed action tools and multi-step delegation.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** low-latency advanced model for real-time UI understanding and action; background model for logging and consent analysis
- **latency:** sub-second reaction for UI actions in the loop; seconds for logging commits
- **cost:** moderate API cost for visual model inference; minimal for logging; bandwidth for screenshots
- **security:** Visual data includes sensitive UI content; requires explicit owner opt-in; redaction and bounded retention mandatory; audit trail needed;
- **missing:** owner opt-in toggle for eye-safe UI screenshots (visionUploadConsent true); bridge online requirement gating to avoid detached operation; logging/receipt system specifically for mac-vision actions and screenshots; UI snapshot context sharing from faculty-perception for joint multimodal decision

### "Automatically interpret and interact with ephemeral UI elements in Mac applications that do not expose APIs or accessibility labels"
- **useful because:** Many Mac applications use ephemeral UI elements or custom-drawn controls that cannot be accessed by APIs or accessibility frameworks. Automated visual interpretation and interaction with these elements would enable the owner to automate complex workflows and increase productivity in apps that are otherwise black boxes.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Specialized visual model trained on UI element types and gestures, running on local Mac and enhanced with pendant for guidance and confirmation.
- **latency:** Real-time or near real-time interaction, under one second latency per UI cycle.
- **cost:** Higher cost due to complex visual recognition and gesture generation but optimized for local computation and selective cloud enhancement.
- **security:** Access to sensitive UI content mandates strict owner consent and controlled data flow; data minimized and purged after session ends.
- **missing:** Specialized UI element recognition model for Mac apps; Seamless integration layer between computer vision and Mac accessibility APIs; Permission and logging frameworks specific to ephemeral UI interactions


## Changes it proposed to its own stack

### `integration` — Create a secure real-time data pipeline and protocol between the Mac's local UI snapshotting, the mac-vision loop, the AI Pendant, and the relay-realtime agent to enable continuous synchronized multimodal understanding and interaction with the owner's computing environment.
- **owner gets:** This integration enables the owner to have a seamless and deeply context-aware AI assistant that can react in real time to visual UI changes, voice commands, and action status updates across devices, creating a powerful collaborative system for complex and dynamic workflows.
- effort: Medium software engineering effort to define protocols, optimize data flow, and ensure synchronization and low latency.  ·  risk: Network disruptions might cause lag or desynchronization; privacy risks if data is intercepted; requires strong encryption and authentication.
- cost: Additional development and cloud relay bandwidth costs; minor runtime compute costs.  ·  latency: Minimal if optimized; essential for real-time interaction quality.
- security: Requires thorough end-to-end encryption, strict consent management, and data retention policies.
- depends on: mac-vision loop enabled with privacy protections; bridge online and authenticated; logging and data audit systems

### `context` — Enable full UI hierarchy snapshot context sharing from faculty-perception to mac-vision in real time, including metadata about focus, obscured elements, and interaction history, to empower mac-vision to make informed decisions when visual screenshot data is unavailable or limited.
- **owner gets:** This would allow the mac-vision agent to operate in accessibility mode without needing raw screenshots, reducing privacy risks and enabling some automated GUI control even under restricted conditions.
- effort: Low to medium software effort to extend current UI hierarchy snapshot protocols and inject actionable metadata for mac-vision.  ·  risk: Limited risk; more data flow requires robust access control to prevent leaks.
- cost: Minimal.  ·  latency: Low latency; essential for smooth interaction.
- security: Requires access control and auditing to keep UI metadata confidential.
- depends on: enable faculty-perception context sharing; mac-vision loop enabled

### `model-routing` — Implement dynamic model routing to delegate real-time visual UI interpretation tasks to specialized local or cloud AI models depending on availability, latency, cost, and privacy constraints, ensuring optimal performance and security for the mac-vision loop.
- **owner gets:** This will allow the owner to benefit from the most appropriate AI model for their current context, device state, and privacy preferences, balancing responsiveness with cost and data safety during advanced computer use scenarios.
- effort: Medium software engineering effort to build routing logic, model availability checking, and fallback mechanisms.  ·  risk: Incorrect routing decisions could degrade performance or leak data; monitoring and telemetry required.
- cost: Potential higher cloud costs balanced by local model usage savings.  ·  latency: Optimizes latency by selecting the closest or fastest model available.
- security: Requires robust policy enforcement and auditing to secure data flows.
- depends on: mac-vision enabled; cloud/local model availability; privacy and consent configurations


## What it asked for

_Nothing._
