# Harness derivation — mac-vision — round 38

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable continuous AI visual computer use loop on Mac with safe permissions and user control"
- **useful because:** The owner could have a real-time AI assistant that visually understands their Mac screen, reads UI contexts, and proactively performs complex multi-step workflows that cannot be done through APIs. This enables the AI to help more effectively with any task, especially those requiring rich visual feedback and interaction with apps without public APIs.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for vision, gpt-5.6-luna for planning and judgment
- **latency:** Low latency visual loop for UI reading, moderate latency for planning and action
- **cost:** Moderate, mainly for frequent vision model inferences and actions triggered by the AI Pendant real-time relay
- **security:** Requires trusted Accessibility and Screen Recording permissions enabled on macOS; must respect user privacy with strict gating around vision upload consent. Any destructive actions require explicit confirmation from the user.
- **missing:** macOS Accessibility permission granted and signals to AI Pendant Agent; macOS Screen Recording permission granted for continuous screenshots; User consent for vision data upload and analysis; Robust UI hierarchy snapshot and incremental update APIs exposed through the Mac agent; Integration with voice conversation through relay-realtime for context and safety confirmation; Typed action gating and undo/receipt mechanisms fully integrated for reversible control

### "Provide safe, explainable undo and action receipt mechanism for all computerUse loop actions on Mac"
- **useful because:** The owner can undo any automated or AI-driven computer actions reliably, increasing trust and safety in AI control, especially when using the vision-based computer use loop.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** Moderate response time to confirm and revert actions
- **cost:** Low to moderate, mainly bookkeeping and state tracking
- **security:** Requires secure action logging, confirmation workflows, and must prevent unauthorized or unintended undo actions
- **missing:** Universal, typed action receipts and undo APIs across all Mac agent control surfaces; Integration of receipts with voice and visual feedback mechanisms


## Changes it proposed to its own stack

### `hardware` — Add a dedicated local AI vision co-processor or neural engine on the MacBook or pendant to offload computer vision tasks, reducing latency and privacy exposure.
- **owner gets:** This hardware addition would allow the AI vision loop to run more efficiently and privately, processing screenshots and UI state locally without needing cloud resources or broad permission to upload data externally.
- effort: High, requires hardware design and integration.  ·  risk: Delays in hardware development and integration; fallback to software vision if not ready.
- cost: High component cost, moderate increased power draw on device.  ·  latency: Significant reduction in latency for vision model inference.
- security: Improves privacy by limiting data upload.
- depends on: enable accessibility and screen recording permissions; enable vision upload consent

### `interaction` — Design a user interface and voice interaction protocol that continuously informs and obtains explicit owner consent for any potentially invasive visual analysis or control actions on the Mac. Provide easy opt-in and opt-out controls accessible via the pendant and Mac interface.
- **owner gets:** The owner remains in control and confident about when and how visual data is accessed by the AI. This transparency builds trust and allows safe enabling of the computer use loop.
- effort: Moderate UX and voice/dialog development.  ·  risk: Poorly designed interactions could annoy or confuse the owner; must balance usefulness and control.
- cost: Low software cost.  ·  latency: Minimal impact.
- security: Improves user consent and control workflows.
- depends on: enable vision upload consent; enable accessibility and screen recording permissions

### `integration` — Integrate mac-vision and mac-planner with faculty-judgement and relay-realtime to form a shared, multimodal continuous context, allowing visual, voice, and action cues to reinforce each other and improve safe, context-aware automation on the Mac.
- **owner gets:** This creates a unified intelligent assistant that understands visual UI state, voice commands, and task context simultaneously, enabling complex and safe automation workflows on the Mac beyond what a single modality can provide.
- effort: High engineering effort for synchronization and data sharing between surfaces and faculties.  ·  risk: Complexity could introduce synchronization bugs and user confusion if not done carefully.
- cost: Moderate ongoing API cost due to increased communication and computation.  ·  latency: Potential slight increase due to communication overhead, but overall responsiveness improved.
- security: Must ensure secure communication and consent management across surfaces and faculties.
- depends on: enable computerUse loop and vision upload consent; permissions for voice and action surfaces

### `memory` — Implement a secure, privacy-preserving contextual memory caching system for mac-vision that retains recent UI states and user interaction logs locally, enabling faster recovery and continuity after interruptions without exposing sensitive data externally.
- **owner gets:** Improves the assistant's efficiency and user experience by remembering the UI context and prior actions locally, reducing redundant UI exploration and improving responsiveness for recurring tasks.
- effort: Moderate development effort for data encryption and caching logic.  ·  risk: Incorrect caching or stale state could cause confusion; must have transparent invalidation policies.
- cost: Low to moderate storage and processing cost locally.  ·  latency: Reduces latency in repeated interactions.
- security: Needs strong encryption and access controls to protect sensitive UI and interaction data.
- depends on: computerUse loop enabled; local storage access

### `model-routing` — Route high-frequency, low-latency vision tasks to a smaller, optimized on-device model and route complex planning and language understanding tasks to a more capable cloud model, balancing privacy, latency, and cost.
- **owner gets:** Enables real-time UI understanding and interaction with low delay and privacy-preserving local processing, while still leveraging powerful cloud models for complex reasoning and coordination.
- effort: Moderate model engineering and infrastructure changes.  ·  risk: Model routing mistakes could degrade user experience if latency or accuracy suffers.
- cost: Optimizes cost by offloading simple tasks locally.  ·  latency: Improves real-time responsiveness for vision tasks.
- security: Limits raw vision data exposure by processing locally first.
- depends on: hardware support for local model inference; enabled computerUse loop

### `dashboard-ux` — Design and build a dashboard view on the Mac and pendant that visualizes the AI's current visual understanding of the screen, planned actions, and permission states, offering manual control and override capability.
- **owner gets:** Gives the owner transparency into what the AI sees and plans, making the vision-based computer use loop more trustworthy, easier to audit, and controlled directly by the user.
- effort: Moderate UI design and development effort.  ·  risk: Complex UI could overwhelm the owner if not designed well.
- cost: Low to moderate software cost.  ·  latency: Minimal.
- security: Improves user trust and control.
- depends on: computerUse loop enabled; vision upload consent


## What it asked for

_Nothing._
