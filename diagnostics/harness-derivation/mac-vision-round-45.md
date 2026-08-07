# Harness derivation — mac-vision — round 45

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a fully interactive multi-modal Mac control loop with safe pixel and UI access"
- **useful because:** The owner can then have a truly autonomous assistant on their Mac, able to integrate pixel-level vision, accessibility UI structure, typed actions, and multi-step planning. This enables much broader control, context-aware actions, and more intuitive interactions that respond to what is actually visible on screen and in the app UI. It also opens the path to more advanced workflows where pixel and UI together provide reliability and possibilities no single method alone can deliver.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** high-capacity, low-latency model for real-time vision and planning on Mac
- **latency:** sub-second to a few seconds per interaction to feel responsive and interactive
- **cost:** moderate due to pixel processing, vision models, and complex planning logits
- **security:** Strict policy control for enabling pixel vision and action authorization to prevent unintended destructive or privacy-invasive steps; ensure transparency with logging and optional owner approval for dangerous commands
- **missing:** Permission to enable computerUse.loopEnabled and visionUploadConsented; Typed action broker API that can coordinate mac_run_actions, browser_run_actions, and mac_delegate with observability and gating; UI hierarchy snapshot context that integrates with pixel vision for robust scene understanding; Policy mechanism for automatic or semi-automatic approval of high-impact or destructive Mac actions

### "Enable seamless cross-device handoff for complex Mac workflows between mac-vision, mac-planner, browser-extension, and relay-realtime."
- **useful because:** Owner can start complex multi-app workflows on one device or surface and seamlessly continue on another without losing context or requiring manual intervention. This enhances productivity and flexibility, especially when moving between Mac, browser, and wearable pendant.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** multi-tier distributed intelligence with synchronized context storage and message passing.
- **latency:** sub-second state sync; minutes for longer multi-step workflows
- **cost:** Moderate depending on sync frequency and data size; mostly messaging and context storage
- **security:** Requires secure, authenticated synchronization of personal context and task state. Strong access controls and audit trails to prevent leakage or loss.
- **missing:** Context synchronization and cross-surface message passing infrastructure; Unified context representation format for Mac, browser, and pendant surfaces; Protocols for graceful handoff and resumption of workflows


## Changes it proposed to its own stack

### `model-routing` — Implement dedicated model routing logic to direct complex Mac desktop control tasks to real-time mac-vision and mac-planner collaboration while delegating one-shot or simple typed actions to mac_run_actions or browser_run_actions. This prioritizes appropriate model tier usage, minimizing latency and cost while maximizing precision and safety.
- **owner gets:** Optimizes the use of computational resources and improves the owner's experience by matching the right models and surfaces to the complexity of the Mac task, reducing slow or costly actions and improving reliability of complex workflows.
- effort: Moderate engineering to build and integrate routing logic between existing tools and models, along with policy definitions on task complexity thresholds.  ·  risk: Misclassification of tasks could cause actions to be routed suboptimally, leading to delays or insufficient action detail. Monitoring and fallback for rerouting would be necessary to recover.
- cost: Reduces overall API costs by avoiding overuse of high-cost real-time models for simple actions; some development cost to implement routing logic.  ·  latency: Improves latency by avoiding unnecessary heavy model use for simple tasks.
- security: Requires secure and auditable decision-making for routing to prevent misuse or errors.
- depends on: Permission for computerUse.loopEnabled; Typed action broker to support multi-model orchestration

### `hardware` — Add a dedicated low-power secure coprocessor on the MacBook to handle vision input locally with privacy and security safeguards, enabling pixel-level processing without excessive energy or privacy risks. This coprocessor would perform preprocessing of vision data before passing summaries or events to the main system and AI models.
- **owner gets:** Allows continuous or on-demand vision capabilities with minimal impact on battery life and significantly stronger privacy guarantees, as raw pixel data never leaves the secure coprocessor and only processed insights are shared.
- effort: High hardware design and integration effort, plus software drivers and secure APIs.  ·  risk: Hardware design flaws or integration bugs could impact security or system stability. Initial cost and production overheads may be high.
- cost: Increased hardware cost and R&D expenses, but reduces operational energy costs and cloud data transfer costs long term.  ·  latency: Reduces latency for vision preprocessing steps, enabling more real-time interactions.
- security: Greatly enhances security and privacy of vision data, limiting exposure of raw images.
- depends on: Integration with mac-vision software stack; Corresponding firmware and driver support

### `interaction` — Develop an owner-configurable policy and confirmation interface for real-time control decisions in mac-vision and mac-run_actions. This would allow the owner to specify which actions require approval, minimize accidental destructive commands, and provide clear, non-intrusive notifications of assistant actions.
- **owner gets:** Improves trust and transparency in assistant control of the Mac, reducing risk of unintended consequences and tailoring control granularity to the owner's preferences and risk tolerance.
- effort: Moderate front-end and back-end development to support dynamic policy rules and UI for confirmations and notifications.  ·  risk: Complexity in policy management could confuse owners; needs excellent UI/UX design and sensible defaults.
- cost: Minimal increase in computational cost, mostly development time.  ·  latency: May add slight delays if confirmations are needed but can be optimized for minimal disruption.
- security: Increases security by adding user approval layers for sensitive operations.
- depends on: mac_run_actions with typed action observability; User interface surfaces for owner feedback

### `dashboard-ux` — Create a comprehensive Mac activity dashboard on the owner's Mac and pendant that visualizes ongoing assistant tasks, queued actions, recent activity logs, and permission requests. This dashboard integrates data from mac-vision, mac-run_actions, mac_delegate, and browser-run_actions for single-pane-of-glass monitoring and control.
- **owner gets:** Provides the owner with clear, real-time visibility into what their AI assistant is doing on their Mac and browser, improving trust, control, and debugging capabilities. It also surfaces permission requests and action feedback in one place.
- effort: Moderate to high UI/UX design and implementation effort, plus backend integration from multiple agents and subsystems.  ·  risk: Possible information overload if not well designed; must prioritize clarity and simplicity.
- cost: Some additional resource and bandwidth usage for real-time updates and state aggregation.  ·  latency: Real-time or near-real-time updates needed for good user experience but can be optimized with efficient data handling.
- security: Requires secure handling of sensitive activity logs and permission data.
- depends on: Integration with all relevant Mac and browser agent action logging; Owner device UI surfaces and pendant capabilities

### `memory` — Enhance short-term contextual memory on the Mac surface to include visual state from the mac-vision pixel input combined with UI hierarchy snapshots, enabling the Mac AI to remember more detailed situational context over multiple interactions for better continuity and less repetition.
- **owner gets:** Owner benefits from more coherent and context-aware assistant behavior on the Mac, with less need to repeat instructions or re-establish state across sessions or tasks involving visual and UI elements.
- effort: Medium, involves integration of vision and UI data into the Mac's memory subsystem with efficient indexing and retrieval.  ·  risk: Larger memory footprint and complexity may slow down real-time performance if not optimized.
- cost: Moderate increase in storage and compute usage for memory indexing and lookup.  ·  latency: Negligible if done asynchronously or with efficient caching.
- security: Requires secure storage policies to protect sensitive visual and contextual memory.
- depends on: Vision-enabled computer use loop; UI hierarchy snapshot context


## What it asked for

_Nothing._
