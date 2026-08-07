# Harness derivation — mac-vision — round 32

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision loop for safe, fully accessible computer UI interaction"
- **useful because:** The owner wants a trusted computer-use loop on their Mac that can perceive app UI hierarchies via accessibility, plan and execute precise UI actions (clicks, typing) non-intrusively, and perform multi-step complex workflows that cannot be done through API calls. This would let the AI control the Mac at a deep level with minimal owner disruption.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for UI loop, gpt-5.6-luna for planning and judgement
- **latency:** Real-time for UI perception and click sequencing; millisecond-scale action response to maintain fluid user experience.
- **cost:** Moderate to high due to continuous UI snapshot processing and low-latency action execution. Model costs dominated by frequent context evaluation and validation steps.
- **security:** Need strict policy control on UI actions to avoid destructive outputs. Prefer layered permission gating from owner with real-time observability and undo support. Protect privacy from UI content exposure during snapshot upload.
- **missing:** System-wide, trusted accessibility UI snapshot permission granting for mac-vision, ideally without stealing focus or disrupting input.; A verification and gating framework for UI actions enabling undo or safe fallback when a planned action sequence is risky or ambiguous.; Integration enhancements between faculty-perception for UI state capture and mac-vision for action planning and safe execution.; Extended modeling capacity to handle multi-step UI workflows with error handling and adaptive recovery.


## Changes it proposed to its own stack

### `hardware` — Add hardware support on the pendant for secure real-time UI snapshot streaming with privacy-preserving encryption and local preprocessing to reduce data sent to cloud services.
- **owner gets:** It allows the owner to maintain privacy and security when mac-vision needs to see Mac UI state; reduces latency and bandwidth usage, enabling richer UI perception and interaction without leaking sensitive data.
- effort: Medium, requires developing and integrating specialized hardware and firmware on the pendant, plus software changes on Mac and relay sides.  ·  risk: Potential bugs in encryption or data handling could expose sensitive UI data. Mitigated by software verification and fallback modes.
- cost: Moderate hardware cost increase for chips and radios, plus increased power use during UI snapshot streaming bursts.  ·  latency: Improves latency for UI data delivery compared to raw screen capture over standard links.
- security: Significantly enhances security and privacy by encrypting UI snapshots before transmission.
- depends on: Software protocols for UI snapshot capture and packaging on the Mac; Relay and pendant software updates to handle new encrypted UI data streams

### `model-routing` — Implement a dedicated routing path for mac-vision that prioritizes low-latency and context-rich interaction, combining live UI hierarchy data, owner's intent signals, and proactive multi-step action generation with continuous feedback from faculty-judgement and faculty-action.
- **owner gets:** Ensures that mac-vision receives the most relevant and complete information to make accurate and safe decisions on complex UI tasks, improving reliability and responsiveness.
- effort: High, requires modifications to the input-output routing infrastructure, real-time prioritization logic, and context blending pipelines.  ·  risk: Correctness of routing decisions is critical; errors could cause stale or insufficient context leading to wrong actions. Mitigated by extensive testing and fallback to safe defaults.
- cost: Moderate API usage increase due to more frequent context updates and confirmations.  ·  latency: Improves perceived latency by reducing waiting times for context updates before action decisions.
- security: Minimal direct security impact, but must ensure no sensitive context leaks to other agents.
- depends on: Reliable access to live UI hierarchy data; Inter-agent communication integrations for context and intent synthesis

### `integration` — Create a coordinated multi-agent workflow protocol that orchestrates mac-vision, mac-planner, faculty-judgement, and faculty-action to handle complex multi-step computer tasks with checkpoints and owner-aware confirmations. Include fallbacks and safe undo steps to maintain owner trust and minimize disruption.
- **owner gets:** This would allow the owner to delegate complex workflows to the AI system with confidence, knowing there are checks, balances, and the ability to revert actions if something goes wrong or is unexpected.
- effort: Medium to high, requires protocol design, implementation of state checkpoints, communication channels, and user interaction models.  ·  risk: Coordination bugs could cause lost context or inconsistent state. Fallbacks and logging would mitigate this.
- cost: Moderate increase due to added communication and checkpoint storage.  ·  latency: Slight additional overhead due to checkpointing but overall improves trust and reduces errors.
- security: Improves security by enforcing owner confirmations and recoverability.
- depends on: Reliable, low-latency communication between agents; Context-rich environment data available to all participating agents

### `dashboard-ux` — Build a real-time visibility dashboard for the owner to monitor mac-vision's UI actions, live UI snapshot previews, pending multi-step tasks, and undo options. Provide simple controls to pause, rewind, or escalate interventions to a human if concerns arise.
- **owner gets:** Allows the owner to maintain confidence and oversight of mac-vision's autonomous UI operations, reducing anxiety about unexpected changes, and enabling easy correction or intervention.
- effort: Medium, requires UI/UX design and integration with mac-vision's action and state streams.  ·  risk: UI must be clear but not distracting; mishandling of undo or escalation could cause confusion.
- cost: Moderate, due to continuous UI state streaming and dashboard updates.  ·  latency: Dashboard updates in near real-time for user assurance.
- security: Must securely authenticate owner and protect sensitive UI data displayed.
- depends on: Low-latency UI data access from mac-vision; Integration with agent command and state logging systems


## What it asked for

_Nothing._
