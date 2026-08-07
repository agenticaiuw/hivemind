# Harness derivation — mac-vision — round 35

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full UI automation loop on Mac using accessibility and optional screen capture for accurate and safe computer control"
- **useful because:** The owner can interact with any Mac application UI directly through the AI Pendant, allowing complex workflows, deep automation and responsive control beyond predefined commands. This is essential for a truly hands-free personal agent on the Mac.
- **path:** mac-vision → relay-realtime → mac-planner → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** sub-second to a few seconds per UI step, batches of up to 25 steps per session
- **cost:** moderate; dominant cost is recurrent model inference for UI analysis and action generation
- **security:** Access to full UI may reveal sensitive information. Must enforce strict access control, consent, and transparent execution logs. Sensitive input fields/capabilities must be carefully guarded.
- **missing:** Enable computerUse.loopEnabled permission in OS agent; Grant accessibility permissions for AI Pendant Agent; Screen recording permission or equivalent visual context capability; Implement ui_hierarchy_snapshot context for accessibility tree snapshots; Model & harness update to utilize these snapshots in the mac-vision loop; A multi-layer consent and control UI flow surfaced mainly on the pendant and mac-planner; Fallback pixel-screenshot mode with strong owner control and safeguards


## Changes it proposed to its own stack

### `hardware` — Add a low-power dedicated visual sensing chip in the pendant to capture simplified UI accessibility snapshot data locally, reducing need for full screen recording consent and protecting privacy by local processing and masking sensitive info.
- **owner gets:** Owners get responsive, privacy conscious UI automation without needing full macOS screen recording permission, enhancing trust and security.
- effort: Significant hardware and firmware design, including custom sensor processing and local AI edge inference development.  ·  risk: Technology maturity risk; potential delays and cost overrun; mitigated by staged prototyping and fallback to traditional methods.
- cost: Estimated additional $20 component cost; low additional power consumption under 100mW; increased device BOM cost but moderate overall.  ·  latency: Reduced latency for UI context updates as data is locally pre-processed before relay transmission.
- security: Improved security by limiting raw screen data exposure; reduces attack surface for sensitive data leaks.
- depends on: Enable computerUse.loopEnabled permission in OS agent; Grant accessibility permissions for AI Pendant Agent; Implement ui_hierarchy_snapshot context ; Model & harness update to utilize ui_hierarchy_snapshot

### `relay` — Implement a consent and permissions UI workflow on the pendant device and relay service to guide the owner through granting and managing accessibility, screen recording, and computer control permissions safely and transparently.
- **owner gets:** Makes permission grants explicit, user-controlled, and reversible, building trust and safety while enabling powerful Mac UI control features on demand.
- effort: Medium software effort in relay and pendant UI design and implementation, plus user experience testing.  ·  risk: UI complexity might overwhelm some users; mitigated by clear, simple language and staged disclosures.
- cost: Minimal to moderate cloud compute cost for relay UI workflows.  ·  latency: Negligible.
- security: Must ensure secure communication and robust consent logging to prevent misuse or unauthorized escalation of privileges.
- depends on: Enable computerUse.loopEnabled permission in OS agent; Grant accessibility permissions for AI Pendant Agent

### `model-routing` — Develop specialized AI models trained on macOS accessibility tree data to generate precise, context-aware UI automation instructions from ui_hierarchy_snapshot and limited pixel data.
- **owner gets:** Allows the AI Pendant to perform safe, reliable, and flexible UI interactions across any Mac application, enabling complex tasks beyond scripted commands.
- effort: Significant data collection, model training, and integration effort across mac-vision and unified surfaces.  ·  risk: Model accuracy and robustness risk; mitigated by extensive testing and fallback modes.
- cost: Moderate to high model inference cost during active UI automation sessions.  ·  latency: Model inference time fits within the 25-step command latency budget.
- security: Models only trained on consented data and used within strict context boundaries to prevent unintended data exposure.
- depends on: Implement ui_hierarchy_snapshot context; Enable computerUse.loopEnabled permission; Grant accessibility permissions for AI Pendant Agent

### `mac-harness` — Integrate UI hierarchy snapshot acquisition and accessibility-driven interaction commands into the mac-vision local agent harness, enabling non-pixel-based interaction loops.
- **owner gets:** Enables mac-vision to perform non-invasive, precise UI automation on the Mac without screen capture, preserving privacy and user experience.
- effort: Moderate software development within the mac-vision agent harness to support snapshot parsing, command generation, and loop state management.  ·  risk: Integration complexity; mitigated by incremental rollout and testing phases.
- cost: Low additional CPU and memory usage on the Mac during UI automation.  ·  latency: Minimal impact; improvements in responsiveness by avoiding full screen grabbing.
- security: Increased security by avoiding pixel data; must ensure secure handling of snapshot data.
- depends on: Implement ui_hierarchy_snapshot context; Enable computerUse.loopEnabled permission; Grant accessibility permissions for AI Pendant Agent

### `dashboard-ux` — Create a dashboard interface for the owner to monitor, control, and audit AI Pendant's Mac UI automation activities, permissions status, and active loops.
- **owner gets:** Increases owner trust and control by providing transparency into the AI's activities, letting them pause, stop or adjust permissions and see logs of UI interactions.
- effort: Moderate UI/UX development effort, linking to mac-vision and relay state and permissions data.  ·  risk: Complexity may intimidate some users; UI must be clear and simple.
- cost: Low cloud and local compute cost for dashboard data aggregation and serving.  ·  latency: Negligible latency impact
- security: Sensitive information displayed; must ensure dashboard access controls and encryption.
- depends on: Enable computerUse.loopEnabled permission; Grant accessibility permissions; Relay consent UI workflow

### `interaction` — Implement natural language fallback and error recovery strategies in the mac-vision loop to safely handle unexpected UI states and ambiguities in automation steps, prompting the owner on the pendant when manual intervention or confirmation is needed.
- **owner gets:** Improves robustness and user experience of UI automation by gracefully handling edge cases and involving the owner only when necessary, maintaining control and transparency.
- effort: Moderate development and design effort in AI interaction and fallback logic on relay and mac-vision surfaces.  ·  risk: Potential misinterpretations mitigated by careful prompt design and testing.
- cost: Moderate due to additional natural language polling and interactions.  ·  latency: Additional user interaction latency but only when needed.
- security: Careful data handling required to avoid exposure of UI state or owner data in prompts.
- depends on: Enable computerUse.loopEnabled permission; Grant accessibility permissions; Relay consent UI workflow

### `memory` — Augment the system memory to retain recent UI snapshot states and user confirmations to allow smooth continuation of mac-vision UI automation loops across sessions and transient interruptions.
- **owner gets:** Provides seamless, uninterrupted automation experiences even if the Mac enters sleep or the AI Pendant temporarily loses connection, improving reliability and continuity.
- effort: Moderate model and infrastructure changes to persist loop states securely and efficiently.  ·  risk: Data synchronization and stale state risk; mitigated by checks and state validation logic.
- cost: Increased storage and retrieval cost proportional to snapshot size and frequency.  ·  latency: Minimal impact on real-time latency due to asynchronous state syncing.
- security: Stored data must be encrypted and access-controlled due to potential sensitivity.
- depends on: Enable computerUse.loopEnabled permission; Implement ui_hierarchy_snapshot context


## What it asked for

_Nothing._
