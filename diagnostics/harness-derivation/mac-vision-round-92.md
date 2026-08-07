# Harness derivation — mac-vision — round 92

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe and privacy-respecting computer use loop on the MacBook to directly interpret UI and control apps interactively"
- **useful because:** The owner could delegate complex and precise computer tasks involving multiple apps and UI elements that no API or single mac_run_actions call can handle. It allows incremental, visual, and reactive control tied to live UI state without stealing focus or disrupting user flow.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini
- **latency:** within a few seconds for UI read, low latency for small clicks or typing
- **cost:** moderate model inference and UI state polling, occasional screenshot uploads when permitted
- **security:** must ensure privacy by never uploading screenshots or UI state without owner opt-in, must apply fine-grained action policy before any mutation, avoid destructive actions without explicit confirmation
- **missing:** Permission to enable computerUse.loopEnabled without owner-facing gating; Permission for visionUploadConsented to allow controlled screenshot upload; Context data about current UI hierarchy snapshot suitable for accessibility-level navigation

### "Owner wants an integrated multi-agent workflow to interpret screen contents and context from other devices for disambiguation and adaptive step-by-step Mac control"
- **useful because:** This would enable the owner's Mac agent to receive context and additional sensory input (like voice commands, wearable pendant state, browser extension insights) to plan and execute steps more flexibly, handling ambiguous tasks and adjusting dynamically without requiring many approvals or workflow restarts.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds for context exchange, under 5 seconds for planning next step
- **cost:** higher inference and communication cost given multi-agent orchestration and context sharing
- **security:** data sharing confined within trusted devices; explicit opt-in to share context; audit logs for actions executed; no external data leakage without confirmation
- **missing:** API or protocol to merge multi-agent context streams in real time for Mac task planning; User interface for the owner to clarify ambiguous or multi-step workflows when computer loop is active


## Changes it proposed to its own stack

### `hardware` — Add a low-power, high-resolution front-facing camera and proximity sensor to the MacBook for continuous contextual environmental capture to assist AI in better interpreting user intent and providing context-aware assistance.
- **owner gets:** It would enable richer context for AI agents to understand the owner's environment and actions beyond the screen, improving task execution accuracy and situational awareness.
- effort: Requires hardware design update, driver development, and software integration; moderate effort over several months.  ·  risk: Privacy concerns if camera data is mishandled; mitigate with strict local processing and opt-in policies.
- cost: Additional hardware cost and slight increase in power consumption, minor impact on battery life.  ·  latency: Minimal latency impact, data processed locally before any cloud transmission.
- security: High security impact requiring encryption and strict access controls to camera data.

### `integration` — Develop a real-time multi-agent context sharing protocol that synchronizes UI state, voice commands, browser state, and wearable sensor inputs, enabling a unified decision-making framework for the owner's AI hive mind.
- **owner gets:** This would allow seamless collaboration between the Mac-vision, relay-realtime, mac-planner, and other agents to dynamically adjust computer control actions based on the full range of user context and input modalities.
- effort: Requires protocol design, implementation across multiple agents, and robust testing; moderate to high effort over months.  ·  risk: Complexity could introduce synchronization bugs or delays; requires careful fallback mechanisms.
- cost: Higher compute and communication overhead due to continuous synchronization and context merging.  ·  latency: Potentially increases latency if not optimized; needs prioritization of critical context updates.
- security: Sensitive user context shared among devices must be encrypted and access controlled to prevent leaks.
- depends on: hardware change for sensors and cameras; permissions for data sharing and vision upload

### `firmware` — Implement a local hardware-accelerated privacy filter and encryption module on the MacBook that controls camera, microphone, and screen capture data streams before they leave the device for AI processing, ensuring user data never leaves in unencrypted or unanonymized form.
- **owner gets:** Owner's privacy is safeguarded by hardware-level controls, allowing full AI assistance without risk of unintentional data exposure.
- effort: Firmware development and hardware interface work; medium effort over several months.  ·  risk: Firmware bugs could impair AI functionality or user experience; requires rigorous QA and update mechanisms.
- cost: Minimal additional hardware cost, some power consumption increase during active filtering.  ·  latency: Minimal latency increase due to accelerated filtering processes.
- security: Greatly improves security posture by enforcing privacy policies at hardware level.
- depends on: hardware changes for sensors and camera; integration changes for data handling

### `interaction` — Design and implement an AI-powered augmented reality interface accessible via the wearable pendant to visually guide the owner through complex computer and multi-device tasks, with touch or voice interaction.
- **owner gets:** Allows the owner to control and understand complex workflows with intuitive, context-sensitive visual aids without switching focus away from their primary work or devices.
- effort: Requires UI/UX design, AR software development, integration with AI agents and device sensors; high effort over many months.  ·  risk: User distraction or cognitive overload if not designed well; depends on pendant hardware capabilities and battery life.
- cost: Increases computing and possibly hardware costs for the pendant device.  ·  latency: Needs low latency for smooth and responsive interaction.
- security: Sensitive task data displayed on AR interface must be protected from unauthorized viewing.
- depends on: hardware upgrade to pendant; integration of multi-agent context; visionUploadConsented permission


## What it asked for

_Nothing._
