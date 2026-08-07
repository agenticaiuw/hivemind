# Harness derivation — mac-vision — round 78

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, responsive computer-use loop on MacBook using vision and UI state, with zero latency clicks and keystrokes for complex tasks"
- **useful because:** The owner will be able to delegate ambiguous, multi-step, or UI-only tasks that cannot be done via API or simple shell commands, increasing automation coverage and convenience.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime-gpt-4.1-mini
- **latency:** sub-second to low seconds for responsiveness to owner commands
- **cost:** primarily runtime cost of real-time GPT model plus some minimal screen capture processing
- **security:** Requires owner consent for screen capture and input control; must ensure no accidental destructive actions; permissions gating needed before activation.
- **missing:** a robust gating/consent framework for vision loop activation; a typed action policy layer to classify and block destructive input; real-time monitoring and immediate abort capability during vision loop operation; a safety layer informed by faculty-perception and judgement to confirm vision loop enablement


## Changes it proposed to its own stack

### `hardware` — Enhance MacBook integration with secure, low-latency screen capture and input control hardware hooks directly accessible by the AI system under strict permission control to enable vision-based computer use loop.
- **owner gets:** Allows vision loop to operate with minimal latency, high fidelity, and maximum safety, enabling broader automation and seamless interaction with complex GUI tasks.
- effort: Moderate hardware and driver development plus OS integration and security vetting.  ·  risk: Potential for abuse if security gating fails, mitigated by hardware-level permission enforcement and owner controls.
- cost: One-time hardware development and deployment, minimal runtime power cost impact.  ·  latency: Significantly reduces latency in vision-driven actions versus software-only capture.
- security: Improved security by hardware-enforced gating versus software alone.

### `model-routing` — Implement a layered decision and failover system that routes tasks between mac_run_actions, mac_delegate, and mac-vision based on complexity, UI accessibility, and safety gating, with fallback to human override or pendant interaction.
- **owner gets:** Maximizes automation coverage with minimal risk by using the most appropriate agent for each task and gracefully handling edge cases where vision loop is too risky or ambiguous.
- effort: Requires integration work and policy modeling, plus stable interfaces between layers.  ·  risk: Incorrect routing could lead to task failure or unintended actions, mitigated by strict logging and user override.
- cost: Moderate compute for model management, plus engineering complexity.  ·  latency: Optimizes latency by preferring fast API calls but allows slower vision loop when necessary.
- security: Reduces risk by minimizing vision loop activation, enforcing safe delegation.
- depends on: computerUse.loopEnabled gating; vision action classification policy

### `context` — Establish real-time UI hierarchy and accessibility snapshot context sharing from Mac to mac-vision loop to enhance state understanding without requiring frequent screenshots.
- **owner gets:** Improves mac-vision's ability to operate without costly full screenshots, reducing latency and power, and enabling safer, more targeted UI actions with enriched semantic information.
- effort: Engineering of stable real-time context API and integration with vision agent.  ·  risk: Potential privacy exposure mitigated by permission control and owner consent.
- cost: Low additional compute; saves cost on image processing.  ·  latency: Reduces vision loop latency by avoiding image processing bottlenecks.
- security: Requires strict gating and consent to avoid leaking sensitive UI data.
- depends on: computerUse.loopEnabled permission; accessibility permission

### `interaction` — Create a user feedback and quick abort mechanism on the pendant device to allow the owner to immediately stop mac-vision loop actions if an unintended one is detected or suspected.
- **owner gets:** Gives the owner direct, low-latency control to safely intervene and abort potentially erroneous or destructive automation from mac-vision, increasing trust and safety.
- effort: Requires pendant UI integration to support quick cancel buttons and interrupt signals.  ·  risk: Minimal; mainly UX design to ensure it's easy to reach and understand.
- cost: Minimal hardware and compute overhead on pendant device.  ·  latency: Negligible; improves safety response time.
- security: Improves security and control by providing immediate manual override.
- depends on: mac-vision enabled; pendant UI capability

### `dashboard-ux` — Develop a clear, intuitive dashboard interface to review, monitor, and control mac-vision initiated actions, including action history, approvals, and undo capability.
- **owner gets:** Improves transparency and user confidence by showing what mac-vision has done or plans to do and allowing easy reversals or confirmations of actions.
- effort: Frontend and backend dashboard development and integration with mac-vision and job tracking.  ·  risk: Requires secure authentication and data privacy controls.
- cost: Moderate web UI hosting and maintenance costs.  ·  latency: No impact on real-time loop; helps post-action management.
- security: Enhances security by adding human-in-the-loop control and audit trails.
- depends on: relay job records; mac-vision action receipts


## What it asked for

_Nothing._
