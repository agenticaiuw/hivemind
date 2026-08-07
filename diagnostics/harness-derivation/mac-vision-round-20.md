# Harness derivation — mac-vision — round 20

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the AI Pendant Mac agent's computer vision and control loop for pixel-based and accessibility-driven UI interactions and browser control."
- **useful because:** This would allow the owner to automate complex Mac app interactions, integrate visual and UI context into the AI assistant's actions, and control the browser via the AI Pendant Browser Bridge, enabling seamless cross-device workflows and smarter task automation.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** realtime
- **latency:** sub-second to a few seconds
- **cost:** medium per invocation dominated by vision model and automation action calls
- **security:** Screen recording and accessibility permissions expose sensitive UI data, requiring explicit owner consent and robust permission gating; browser extension online state requires network and extension security; careful limit on what pixel and UI data gets transmitted; requires trust and user control.
- **missing:** Full accessibility permission trust and enablement for AI Pendant Agent on Mac; Screen recording permission granted to the AI Pendant Agent on Mac; Vision upload consent enabled; AI Pendant Browser Bridge extension online and polling to enable browser control

### "A dynamic system to request and manage Mac permissions (Screen Recording, Accessibility, Automation) transparently to the owner, with explanations and options for temporary or context-limited grants."
- **useful because:** Managing sensitive Mac permissions manually is complex, error-prone, and can block full AI pendant capabilities. Automating and streamlining this would improve user experience, increase safe automation scope, and enable full agent capabilities more reliably.
- **path:** mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** background
- **latency:** minutes
- **cost:** low to medium
- **security:** Requires careful handling of sensitive permission requests and validations; must maintain user trust and control without blocking needed capabilities.
- **missing:** New MacOS permission management user interface; Integration with MacOS security APIs and system dialogs; Secure audit logs for permission grant decisions


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure hardware module on the MacBook Air for trusted UI and screen capture streams, isolating screen recording and accessibility data from other applications and user processes, with explicit user enable/disable control via physical switch on the Mac-device.
- **owner gets:** Ensures highly secure and private capture of UI and screen data for AI-powered automation without exposing sensitive data to usual software vulnerabilities or granting broad software permissions.
- effort: High, requires collaboration with Apple and hardware redesign.  ·  risk: Hardware implementation delays, increased device cost, potential user confusion about physical controls.
- cost: High component and manufacturing cost increase, potential power usage increase.  ·  latency: Minimal impact, hardware-level stream access can improve speed.
- security: Greatly improves security and privacy by limiting screen capture access to a dedicated secure path.

### `model-routing` — Implement intelligent context-aware model routing that uses mac-vision for accessibility UI hierarchy actions and fallback to pixel vision only when necessary, balancing privacy, speed, and capability.
- **owner gets:** Allows more efficient AI resource use, reduces need for intrusive screen recording by preferring safe accessibility interfaces, and triggers pixel vision only when essential, enhancing privacy and responsiveness.
- effort: Medium, requires development of model routing logic and usage monitoring.  ·  risk: Potential errors in routing causing action failures or delays.
- cost: Medium, saves some computational cost compared to blanket pixel vision usage.  ·  latency: Improves latency by preferring faster accessibility data access.
- security: Improves security by limiting pixel data transmission and use.
- depends on: Accessibility permission enabled

### `integration` — Create a cross-device synchronization system for suspending and resuming AI Pendant Mac vision tasks on the wearable pendant and cloud relay, ensuring smooth handoff and unified user experience.
- **owner gets:** Enables continuous AI assistant operation across devices, making AI-powered task automation more resilient to device state changes, network issues, or user mobility.
- effort: Medium to high, requires development of sync protocols and session state management.  ·  risk: Sync conflicts or state inconsistencies may disrupt experience; careful design needed to recover.
- cost: Moderate due to data sync storage and communication costs.  ·  latency: Minimal, mostly background sync.
- security: Needs encryption and privacy controls for synced task data.
- depends on: Persistent agent state support in relay; Wearable pendant connectivity

### `interaction` — Develop multimodal user interaction paradigms combining voice commands via wearable pendant and visual context awareness on Mac vision for seamless task initiation, control, and interruption.
- **owner gets:** Provides natural and flexible modes of interacting with AI assistant leveraging the strengths of multiple devices and modalities, making task control intuitive and efficient.
- effort: Medium, requires UX design and multimodal input integration.  ·  risk: User confusion or mode conflicts without careful design.
- cost: Low to medium.  ·  latency: Should improve response time by using the most suitable modality.
- security: Minimal new security concerns but requires robust user intent recognition.
- depends on: Wearable pendant microphone and speech recognition; Mac vision context awareness

### `dashboard-ux` — Add a detailed permission and activity dashboard for the owner showing real-time AI Pendant Mac vision usage, permissions states, screen capture activity logs, and browser extension status with toggle controls and explanations.
- **owner gets:** Builds owner trust and control by making AI agent actions and permissions transparent and modifiable, helping to ensure privacy and security while using powerful automation capabilities.
- effort: Medium, requires UI/UX design and integration with underlying system telemetry.  ·  risk: Overwhelming UI if not designed well; needs to prioritize usability and clarity.
- cost: Low to medium impact.  ·  latency: Negligible.
- security: Improves security awareness and user control.
- depends on: Permission state export; Agent telemetry collection

### `memory` — Enhance memory system to store and recall detailed UI interaction histories and visual states to enable better context-aware automation decisions and repeatable complex task replay.
- **owner gets:** Allows AI assistant to learn from past interactions, anticipate user needs, and execute multi-step workflows with improved accuracy and personalization.
- effort: Medium to high, requires data schema extensions and efficient storage/retrieval mechanisms.  ·  risk: Memory bloat or privacy concerns if sensitive UI data accumulated without proper management.
- cost: Moderate due to storage and retrieval compute costs.  ·  latency: Improves decision latency by leveraging cached context.
- security: Requires secure handling of stored UI and interaction data.
- depends on: Vision and accessibility data ingestion


## What it asked for

_Nothing._
