# Harness derivation — mac-vision — round 109

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable fallback scripted macros for mac-vision when pixel-based vision is unavailable or disabled"
- **useful because:** Owner can still automate repetitive or routine Mac UI workflows through scripted sequences without needing the pixel vision loop enabled, providing a partial capability and fallback for basic automation tasks.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** Seconds, as these are pre-scripted sequences
- **cost:** Low cost, mostly local execution of scripts
- **security:** Scripts must be inspected and confirmed by owner to avoid unsafe automation; limited to allowed commands; no direct pixel input or screen capture.
- **missing:** Dedicated fallback macro executor in mac-vision agent; Owner UI to configure and trigger fallback macros


## Changes it proposed to its own stack

### `hardware` — Integrate a dedicated onboard AI vision co-processor into the pendant or MacBook to accelerate real-time UI scene analysis and pixel-level decision making for mac-vision loop actions.
- **owner gets:** This reduces latency, improves privacy by keeping raw pixel data local, and enables mac-vision to operate efficiently and reliably at scale without burdening cloud or main CPU resources, enabling fast, context-aware visual computer control.
- effort: Moderate hardware design integration and software adaptation over several months.  ·  risk: Potential hardware integration complexity and incremental power draw. Recovery involves fallback to cloud execution if needed.
- cost: High initial component cost but reduced ongoing cloud compute costs and latency penalties.  ·  latency: Significant improvement in UI interaction responsiveness under 1 second.
- security: Improved privacy by local pixel processing, reducing external data exposure.
- depends on: computerUse.loopEnabled permission granted; visionUploadConsented permission granted; Real-time UI hierarchy snapshot access; mac-vision computer-use loop enabled

### `integration` — Create a secure, privacy-preserving consent and gating integration for mac-vision loop actions, allowing the owner to explicitly authorize pixel-based interaction only in allowed contexts, with transparent logs and context-sensitive privacy filters that redact sensitive info before processing or storage.
- **owner gets:** This gives the owner full control and trust over the computer-use AI, preventing accidental or unwanted data exposure while enabling powerful computer automation.
- effort: Medium software engineering effort to integrate consent UI, context recognition, and secure gating policies.  ·  risk: Misconfigured policies could block useful actions or allow overbroad permissions. Recovery via fallback manual intervention and incremental rollout.
- cost: Low software cost; major benefit in trust and safety.  ·  latency: Minimal impact, possibly some prompt delays for consent dialogs.
- security: Critical for privacy and compliance, reducing risk of sensitive data leakage.
- depends on: computerUse.loopEnabled permission granted; visionUploadConsented permission granted; mac-vision computer-use loop enabled

### `interaction` — Develop a cooperative multi-agent coordination protocol between mac-vision, mac-planner, relay-realtime, and faculty-action to enable seamless handoffs, error recovery, and clarification dialogues during complex multi-step Mac UI workflows involving both voice and visual actions.
- **owner gets:** This allows smooth collaboration across the AI's modular components, ensuring the owner can rely on a coherent, responsive assistant that adapts to evolving goals and handles ambiguous or failing steps gracefully.
- effort: Moderate design and implementation effort over months, including protocol design, messaging, and fallback handling.  ·  risk: Possible synchronization bugs or communication overhead, mitigated by robust error detection and retries.
- cost: Moderate due to added message traffic and computations.  ·  latency: Improves overall task completion latency despite minor messaging delays.
- security: Minimal beyond existing communication security.
- depends on: mac-vision computer-use loop enabled; relay-realtime live voice agent enabled; faculty-judgement and faculty-action coordination

### `model-routing` — Optimize routing of real-time UI visual understanding queries to the specialized mac-vision gpt-4.1-mini model while offloading planning, judgement, and action sequencing to the more capable gpt-5.6-luna models on mac-planner and faculty layers to balance response quality and cost.
- **owner gets:** This tailored routing specialization ensures the computer-use loop runs responsively and cost-effectively, providing fast pixel-level action recommendations with deep strategic planning handled upstream.
- effort: Moderate modification of model routing and prompt orchestration layers.  ·  risk: Potential misrouting or latency spikes if misconfigured, mitigated by monitoring and fallback defaults.
- cost: Reduces expensive usage of large models in pixel loop, lowering cost.  ·  latency: Improves UI action readiness latency.
- security: No change beyond existing model routing security.
- depends on: mac-vision computer-use loop enabled; model routing infrastructure

### `memory` — Enhance memory layering for mac-vision to retain recent UI state changes, user preferences, and workflow successes/failures in short-term and medium-term memory store accessible in real time.
- **owner gets:** Improves mac-vision's contextual awareness of ongoing tasks, reducing repeat queries and enabling more anticipatory, adaptive UI interactions.
- effort: Moderate backend work to sync Mac UI state snapshots and user interaction memory efficiently.  ·  risk: Memory inconsistencies or staleness, mitigated by frequent updates and cross-checks.
- cost: Moderate storage and compute usage in background.  ·  latency: Minimal on the real-time loop if well optimized.
- security: Requires secure handling and encryption of private UI data.
- depends on: mac-vision computer-use loop enabled; ui hierarchy snapshot access; memory infrastructure


## What it asked for

_Nothing._
