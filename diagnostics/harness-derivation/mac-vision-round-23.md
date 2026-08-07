# Harness derivation — mac-vision — round 23

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, fine-grained mac-vision computer interaction with active user intent confirmation."
- **useful because:** Currently, mac-vision is disabled due to lack of vision upload consent and loop enablement. However, the owner needs safe use of AI-guided computer control on their Mac without risking unintended actions or privacy loss. This capability would allow mac-vision to perform complex UI interactions, automate repetitive tasks, and adapt to UI changes with accessibility-based feedback, improving productivity and usability.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini for vision processing and action guidance; gpt-5.6-luna for judgment and planning.
- **latency:** Realtime to sub-second, enabling conversational speed with action feedback.
- **cost:** Moderate API cost dominated by vision understanding and multi-step planning.
- **security:** Requires explicit owner consent before enabling vision upload. Must have strict action classification to prevent harmful or unintended mutations. Sensitive data from screen contents should be transient and never stored persistently without explicit consent.
- **missing:** A fine-grained typed action policy to classify mac vision loop operations by impact and require dynamic owner confirmation on high-risk actions.; A reliable UI accessibility snapshot or live element tree from mac-planner normally available when the loop is disabled.; Context sharing protocols for safe handoff and error recovery between mac-vision and faculty-action/maclanner.; Enhanced optical character recognition and UI element recognition tools to substitute direct screen capture where disallowed.

### "Ask mac-vision to demonstrate and explain proposed UI interactions before performing them."
- **useful because:** This will give the owner confidence in mac-vision's proposed actions by showing a preview or explanation of what it intends to do, enabling a better informed consent process and reducing the risk of unexpected or incorrect actions.
- **path:** mac-vision → mac-planner → faculty-judgement
- **model tier:** gpt-4.1-mini for interaction explanation, gpt-5.6-luna for synthesis and planning.
- **latency:** Seconds allowed for multi-step explanations and previews before action.
- **cost:** Low to moderate for explanation generation and UI demonstration rendering.
- **security:** No direct sensitive data exposed beyond normal vision processing. The preview must not itself cause undesired side effects without explicit go-ahead.
- **missing:** UI simulation frameworks integrated with mac-vision loop; Protocols for requesting and displaying previews before execution


## Changes it proposed to its own stack

### `integration` — Integrate mac-vision loop with an advanced typed action policy broker that intercepts all proposed computer actions, classifies them by scope and risk, and enforces a dynamic confirmation flow before execution.
- **owner gets:** This ensures that even if mac-vision is given control, the owner retains full awareness and consent over every action, preventing harmful mistakes and privacy breaches while enhancing trust and usability of AI-driven computer automation.
- effort: Medium engineering effort involving designing a robust policy schema, enforcement hooks in the action execution pipeline, and UI for owner confirmations.  ·  risk: If misconfigured, could block legitimate automation or overwhelm the owner with confirmations. Recovery through safe rollback and manual override by the owner.
- cost: Adds minimal API overhead mainly in policy check calls and confirmation UI orchestration.  ·  latency: Adds slight latency when confirmation is required but maintains realtime for approved automatic actions.
- security: Improves security posture by enforcing granular human-in-the-loop control.
- depends on: mac-vision loop enabled with controlled access; availability of UI accessibility data to interpret context for risk classification

### `hardware` — Add a dedicated local vision processing accelerator chip on the pendant or Mac hardware to preprocess screenshots and UI images locally, extracting actionable UI metadata without sending raw images to the cloud.
- **owner gets:** This allows mac-vision to enable real-time computer control with strong privacy guarantees since raw screen content never leaves local hardware, alleviating privacy concerns and enabling prompt consent management.
- effort: High engineering effort requiring custom hardware design, firmware integration, and software protocol updates  ·  risk: Hardware added complexity and cost. Software integration risks around compatibility and firmware bugs. Can be mitigated by phased rollout and fallback to cloud processing.
- cost: Significant hardware cost addition, offset by reduced cloud processing and privacy risk.  ·  latency: Lower latency for vision preprocessing enabling faster interactions.
- security: Major improvement in privacy preservation, as sensitive visual data remains local.
- depends on: Development of local vision processing algorithms compatible with the chip; Software support for data exchange protocols and consent management

### `model-routing` — Implement adaptive multi-tier model routing where mac-vision handles lightweight UI inference locally and defers complex semantic reasoning or multi-step planning to mac-planner or faculty-judgement on higher capacity models.
- **owner gets:** This optimizes cost and latency by leveraging the best execution environment for each part of the task, enabling mac-vision to respond quickly to simple visual UI cues while ensuring safer complex decisions are made by powerful, well-informed models.
- effort: Moderate engineering effort to define handoff interfaces and dynamic routing policies.  ·  risk: Potential inconsistencies or coordination overhead between model tiers. Addressed by robust context sharing protocols and fallback fallback mechanisms.
- cost: Reduces cloud compute cost by offloading some inference locally.  ·  latency: Improves perceived responsiveness of visual interactions on the Mac.
- security: Improves safety by isolating critical judgment in higher-tier models.
- depends on: Availability of local lightweight vision models on the Mac or pendant; Reliable context sharing between mac-vision and other model tiers


## What it asked for

_Nothing._
