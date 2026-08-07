# Harness derivation — mac-vision — round 37

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable proactive visual loop control on the MacBook for complex multi-app workflows and ambiguous computer tasks using direct UI interaction and typed actions."
- **useful because:** The owner can delegate complex long-running tasks or navigate graphical workflows that cannot be fully handled by individual discrete actions or APIs alone. This would unlock seamless multi-app control, visual debugging, and step-by-step UI guidance, dramatically improving productivity and reducing owner effort.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini (mac-vision) plus gpt-5.6-luna for planning and judgement
- **latency:** Real-time UI responsiveness under 1 second for each step; complex workflows may take minutes total but with live progress updates.
- **cost:** Moderate due to high use of UI snapshot analysis and planning plus multi-agent coordination; major cost driver is screenshot uploads and UI parsing.
- **security:** Vision data and UI interactions are highly sensitive; requires strong owner consent and secure data handling policies. Local execution preferred to reduce data exposure. Permissions gating essential for full control.
- **missing:** computerUse.loopEnabled permission granted; visionUploadConsented permission granted; UI hierarchy snapshot context access; Enhanced multi-agent workflow coordination protocols


## Changes it proposed to its own stack

### `model-routing` — Add dynamic multimodal coordination between mac-vision and mac-planner based on UI state and owner voice commands, enabling the mac-vision agent to escalate complex UI tasks to mac-planner with human approval flow.
- **owner gets:** This routing allows the owner to delegate UI-heavy tasks visually to the mac-vision agent while complex planning and judgment stays with mac-planner, providing the best tool for each aspect of the job.
- effort: Medium effort to develop real-time routing logic, define escalation protocols, and implement approval prompts on the wearable pendant.  ·  risk: The routing must strictly respect owner privacy and consent; implementation errors could cause unauthorized control attempts. Requires robust fail-safe modes to revert to manual control.
- cost: Additional small computation overhead on routing server and pendant; no major hardware cost impact.  ·  latency: Minor increase in routing latency, under 100ms per escalation decision.
- security: Must ensure routing respects the same security and privacy constraints as current permissions.
- depends on: computerUse.loopEnabled; visionUploadConsented; UI hierarchy snapshot context access

### `hardware` — Add a dedicated low-power vision co-processor on the pendant to locally preprocess Mac screen captures, run simple UI element recognition, and send structured UI insights instead of raw screenshots to the Mac-planner and mac-vision agents.
- **owner gets:** This allows vision data to be processed and minimized locally on the pendant, reducing privacy risks, lowering latency for UI understanding, and enabling partial offline operation or operation on limited bandwidth.
- effort: High effort to design, integrate, and validate a new chip with appropriate software.  ·  risk: Design and firmware bugs could reduce effectiveness or cause data leaks. Hardware manufacturing delays and integration complexity.
- cost: Moderate hardware cost increase to the pendant; minimal power draw increase with optimized chip design.  ·  latency: Improved latency on vision processing compared to raw image upload.
- security: Improves security by limiting raw image data exported; local processing limits attack surface.
- depends on: computerUse.loopEnabled; visionUploadConsented

### `interaction` — Implement an interactive visual task guidance interface on the pendant that provides step-by-step prompts, highlights UI elements on the Mac screen using visual landmarks, and allows the owner to approve, pause, or correct each step with voice or button input.
- **owner gets:** This interface aids the owner in training and supervising the mac-vision loop for complex or critical workflows, ensuring a safe, transparent, and controllable execution of tasks that rely on UI interaction.
- effort: Medium development effort to integrate UI control, voice recognition, and visual highlighting together with the mac-vision and relay-realtime surfaces.  ·  risk: If prompts are misaligned or delayed, owner may lose trust; interface must allow quick abort or rewind and fallback to manual control.
- cost: Minimal hardware impact; mostly software complexity and integration.  ·  latency: Low latency required for smooth interaction, under 500ms for prompts and responses.
- security: Requires strict authorization for control commands; data shared must be limited to relevant UI context.
- depends on: computerUse.loopEnabled; visionUploadConsented; relay-realtime surface improvements

### `context` — Enhance shared context graph to integrate real-time UI state from mac-vision with owner voice intents from relay-realtime, enabling seamless, contextual decisions about when to trigger direct UI interaction versus typed actions or delegation.
- **owner gets:** Gives the system a holistic, up-to-date understanding of what the owner is trying to achieve, the current UI state, and the best mode of action, thereby improving responsiveness and success rates of computer tasks.
- effort: Medium effort to augment context graph schema, synchronize data streams from multiple agents, and build decision logic in faculty-judgement.  ·  risk: Context synchronization errors may cause incorrect actions. Needs robust error detection and recovery mechanisms.
- cost: Small computation cost increase on context processing servers.  ·  latency: Minimal impact; decisions must remain responsive within 1 second.
- security: Context data is sensitive and requires encryption and access controls to maintain owner privacy.
- depends on: computerUse.loopEnabled; visionUploadConsented; relay-realtime; faculty-judgement; faculty-perception

### `firmware` — Update mac-vision firmware to support layered permission checks for UI interaction, ensuring actions that change state are logged, reversible where possible, and require owner confirmation on first use or for high-impact changes.
- **owner gets:** Provides a safety net that maintains owner control and trust when visual UI control is enabled, preventing accidental destructive operations and facilitating undo.
- effort: Medium effort to implement layered permission model, UI prompts, and action receipts integrated with mac-run-actions and mac-delegate.  ·  risk: Complex permission logic could cause false blocks or delays; must be thoroughly tested and easily overridable by owner.
- cost: No hardware cost; mostly software complexity.  ·  latency: Negligible latency increase for action authorization.
- security: Strengthens security and auditability of potentially sensitive UI control operations.
- depends on: computerUse.loopEnabled

### `dashboard-ux` — Add a dashboard interface on Mac and pendant to display real-time visual loop status, recent actions taken by mac-vision, pending approvals, and allow manual intervention such as pause, undo, or re-run steps.
- **owner gets:** Increases transparency and control for the owner over the visual interaction agent, allowing them to monitor system behavior, regain control easily, and build trust in expanded autonomy.
- effort: Medium development effort for real-time UI, synchronization across devices, and integration with mac-vision logs and approval APIs.  ·  risk: If dashboard data is stale or misleading, owner trust may be damaged. Requires robust sync and clear UI design.
- cost: Moderate software complexity, no hardware impact.  ·  latency: Needs sub-second update frequency for live feedback.
- security: Dashboard requires secure authentication and encrypted communication channels.
- depends on: computerUse.loopEnabled; visionUploadConsented


## What it asked for

_Nothing._
