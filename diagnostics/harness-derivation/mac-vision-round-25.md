# Harness derivation — mac-vision — round 25

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, graduated activation of mac-vision for full computer control on the MacBook"
- **useful because:** The owner can have more powerful and reliable AI assistance by allowing screen-based vision and interaction for tasks no API can handle, increasing autonomy and efficiency.
- **path:** mac-vision → faculty-judgement → faculty-perception → relay-realtime
- **model tier:** gpt-4.1-mini for mac-vision, gpt-5.6-luna for judgement and perception
- **latency:** seconds to enable or disable steps, realtime for supervised actions
- **cost:** moderate, mainly for supervision and frequent context exchange
- **security:** Full computer control risks harmful actions; requires layered consent, confirmation, and oversight by judgement and perception faculties; context and command audit logs mandatory
- **missing:** System framework to gradually enable accessibility permissions safely; Owner UI to grant and revoke partial permissions stepwise; Facilities in judgement and perception for robust gating, anomaly detection, and reversibility controls

### "Owner can temporarily enable mac-vision full control for specific trusted applications only"
- **useful because:** Limits the scope of potentially risky screen-based automation to only those apps the owner trusts and uses frequently, reducing risk and increasing safety while allowing power user features.
- **path:** mac-vision → mac-planner → faculty-judgement
- **model tier:** gpt-4.1-mini for mac-vision, gpt-5.6-luna for judgement
- **latency:** Immediate to seconds
- **cost:** Low, mainly configuration management
- **security:** Reduces exposure by applying principle of least privilege but requires careful UI and policy design
- **missing:** Mechanism for app-level permissions enforcement in mac-vision; UI for owner to specify trusted apps for screen control


## Changes it proposed to its own stack

### `hardware` — Add dedicated secure hardware validation and consent button on the pendant for irreversible actions triggered by mac-vision during computer control loop.
- **owner gets:** Ensures owner physical presence and explicit consent for any irreversible or high-impact actions performed by the AI on the MacBook, increasing safety and trust in automation.
- effort: Medium hardware and firmware update, pendant integration work.  ·  risk: Additional hardware complexity; reliance on pendant availability for confirmations.
- cost: Moderate component and power cost on pendant hardware.  ·  latency: Minimal; user physical interaction time only.
- security: Strong improvement, mitigates unauthorized automated actions.
- depends on: firmware support for button use event; integration with mac-vision and faculty-judgement

### `integration` — Integrate mac-vision with faculty-judgement and faculty-perception to create a layered approval and anomaly detection system, ensuring safe, context-aware, and reversible UI actions on the MacBook.
- **owner gets:** Automated computer control is powerful but risky; layered AI oversight ensures actions are appropriate, reversible, and secure, improving owner confidence.
- effort: Medium software engineering effort to build interfaces and coordination.  ·  risk: Complexity in error handling and edge cases; requires robustness.
- cost: Moderate cloud and compute cost due to added AI supervision.  ·  latency: Some added latency in gating actions, acceptable for safety.
- security: Significant improvement, reduces risk of accidental or malicious actions.
- depends on: full mac-vision control permissions; faculty-judgement and faculty-perception equipped for gating

### `memory` — Implement a dynamic state memory for mac-vision agent tracking UI interaction state, previously performed steps, and owner preferences to improve context continuity and reduce errors in multi-step UI tasks.
- **owner gets:** Enables smoother and more reliable multi-step UI automation on the MacBook, preventing repeated mistakes and improving efficiency with longer tasks.
- effort: Medium software development  ·  risk: Memory corruption or desynchronization could lead to wrong actions but mitigated by fallback and correction mechanisms.
- cost: Low to moderate depending on state size and persistence method.  ·  latency: Negligible
- security: Requires good data handling to avoid leakage of private info.
- depends on: mac-vision partial or full control enabled

### `interaction` — Develop a voice-activated real-time override and correction mechanism for mac-vision that allows the owner to immediately stop or adjust any automated screen interaction via voice commands on the pendant.
- **owner gets:** Provides the owner with immediate manual control and safety override on all AI-driven UI automation, improving trust and preventing unwanted actions.
- effort: Medium software and firmware integration  ·  risk: Voice recognition errors could cause accidental stops or overrides; requires robust design.
- cost: Moderate ongoing compute and audio processing cost.  ·  latency: Low latency required for real-time responsive interaction.
- security: Improves safety and user control; needs secure voice authentication.
- depends on: pendant voice command capabilities; mac-vision real-time control enabled

### `dashboard-ux` — Create an intuitive Mac agent dashboard feature for the owner to monitor mac-vision's real-time activity, permission status, recent actions, and logs with easy controls to pause/resume and review automated steps.
- **owner gets:** Increases transparency and trust by giving the owner visibility and control over the AI's screen automation activities on their MacBook.
- effort: Medium UX and backend development  ·  risk: Potential privacy risk if logs are not properly protected; requires UI design carefulness.
- cost: Low to moderate, mainly frontend and logging storage.  ·  latency: Minimal.
- security: Must ensure log and data access is secure and private.
- depends on: mac-vision event logging; control APIs for enable/disable

### `firmware` — Enhance the pendant firmware to provide haptic feedback signals during mac-vision controlled computer actions, confirming the reception and execution of safety-critical commands.
- **owner gets:** Gives the owner tactile awareness of AI-driven UI control on the MacBook, improving user confidence and facilitating immediate reaction if feedback indicates unexpected behavior.
- effort: Medium firmware and integration work.  ·  risk: Additional hardware resource use; must be subtle and not annoying.
- cost: Minor increase in power use and component wear.  ·  latency: Near real-time feedback expected.
- security: Neutral; does not expose additional data.
- depends on: pendant hardware capable of haptics; mac-vision command integration


## What it asked for

_Nothing._
