# Harness derivation — mac-vision — round 88

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, transparent, and privacy-protecting visual UI automation on the Mac when APIs and planners cannot complete tasks"
- **useful because:** Many complex or legacy Mac applications and multi-step workflows require pixel-level perception and interaction to automate. This capability closes the automation gap when no suitable API or planner exists, making the system more capable and reliable for the owner.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini on mac-vision for perception and UI click planning; gpt-5.6-luna on faculties and mac-planner for planning and execution
- **latency:** Real-time or near real-time interaction (<1 second response for perception and action decision)
- **cost:** Moderate token usage for screen analysis and click planning; most cost in running mini model locally; minimal additional network cost
- **security:** Requires owner's explicit, revocable consent to capture and analyze screen content; all data encrypted and processed locally where possible; strict audit logs and action receipts to ensure full observability; gating and usage controls to prevent excessive captures or unexpected UI events; no external transmission of screen data without explicit owner initiation.
- **missing:** A strong, transparent consent and gating framework for vision upload and UI control enablement; Fine-grained action classification (read-only, reversible mutations, high-impact mutations) with owner notification; Integrated audit logs and undo for all UI actions initiated by vision loop; Fallback and escalation mechanisms: try API/planner first; only escalate to vision UI loop if necessary; Owner-facing controls to enable, disable, pause, and review pending UI actions and captures; Improved local model performance to handle pixel analysis efficiently and accurately

### "Dynamic context-sharing and task handoff between mac-vision and mac-planner for seamless multi-tiered Mac automation"
- **useful because:** Complex tasks may start with high-level plans or API calls via mac-planner but require visual pixel-level intervention by mac-vision to complete or recover from failures. Automatic, real-time context sharing and task handoff would make the system robust and able to handle any Mac UI automation scenario transparently for the owner.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Combination of gpt-5.6-luna on mac-planner and faculties for planning and judgement, and gpt-4.1-mini on mac-vision for UI perception and pixel-level steps
- **latency:** Under 1 second for handoff and context update between tiers
- **cost:** Moderate token cost mainly for context serialization and model inference to interpret and hand off tasks
- **security:** Context sharing may expose UI states and sensitive content, requiring encrypted context channels and data minimization, plus owner controls for what is shared and when
- **missing:** Standardized schema for representing partial task state and UI context across agents; Reliable synchronization mechanism for UI snapshots and state between mac-vision and mac-planner; Protocols for fallback and escalation: planner tries first, mac-vision steps in only when needed; User controls to govern handoff behavior and consent

### "Automatic visual error detection and recovery capability in mac-vision loop"
- **useful because:** When mac-vision interacts with UI elements, unexpected UI states or errors can occur. An automatic visual error detector trained to recognize common UI failure modes and retry or escalate as needed improves reliability without burdening the owner.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** gpt-4.1-mini for local fast vision error detection; gpt-5.6-luna on faculties for judgement and escalation decisions
- **latency:** Sub-second detection and response time to minimize task disruption
- **cost:** Moderate token and compute cost for continuous local analysis and decision making
- **security:** Requires temporary access to screen captures and UI states but processes locally; owner controls enable disabling this feature at any time.
- **missing:** Training datasets of UI error patterns; Integration with escalation and retry protocols; User controls for error detection aggressiveness and escalation sensitivity


## Changes it proposed to its own stack

### `interaction` — Add explicit owner-facing control surfaces to enable, disable, pause, and audit the mac-vision agent's screen capture and UI interaction capabilities, with clear explanations of privacy, security, and risk tradeoffs.
- **owner gets:** Provides transparency, control, and confidence to the owner about when and how pixel-level UI automation operates, making them more likely to consent and use mac-vision capabilities safely.
- effort: Medium engineering effort to build a secure UI within Mac-planner or pendant interface, plus integration with mac-vision's state and logs.  ·  risk: If controls are confusing or incomplete, owner may misuse or misunderstand the feature, leading to privacy concerns or inadvertent automation; mitigated by clear design and user education.
- cost: Minimal runtime cost, mainly UI development time.  ·  latency: No impact on operational latency.
- security: Improves security posture by increasing user control and auditability.
- depends on: mac-vision UI capture and action capabilities with audit logging

### `hardware` — Upgrade MacBook auxiliary camera and secure local storage to enable encrypted local screenshot capture, temporary caching, and on-device processing required by mac-vision agent for visual UI automation without transmitting raw screen pixels off-device unless owner consents explicitly.
- **owner gets:** Protects sensitive screen content from leakage while enabling advanced visual automation capabilities; improves trust and privacy.
- effort: Medium hardware and driver engineers coordination plus integration with software stack to route screenshots securely.  ·  risk: Hardware/software integration problems could interfere with screen capture quality or delay; mitigated by fallback to accessibility-only automation.
- cost: Add minor hardware cost; slight power draw increases for encryption and storage subsystems.  ·  latency: Local cache speeds up repeated screen analysis, reducing latency.
- security: Significantly enhances security posture for sensitive visual data handling.
- depends on: mac-vision pixel-level UI automation; secure local storage hardware

### `context` — Add a unified, privacy-preserving UI context extraction layer that extracts structured metadata and semantic summaries from the screenshot images and UI accessibility trees before passing them to models, reducing need for raw pixel access and improving interpretability for all agents.
- **owner gets:** Allows agents including mac-vision and mac-planner to share rich task context with minimal privacy risk or data volume, enabling smarter, faster, and safer multi-agent collaboration on UI tasks.
- effort: High engineering effort requiring UI model training, integration with accessibility APIs, and consensus on shared schema.  ·  risk: Incorrect or incomplete context extraction may cause automation errors; mitigated by fallback to full pixel access when necessary.
- cost: Moderate increased processing cost due to advanced UI extraction and modeling.  ·  latency: May add minor processing delay but overall latency improved by reduced data transfer size and clarity.
- security: Improves privacy posture by reducing raw screenshot exposure.
- depends on: ui accessibility APIs; local UI modeling

### `firmware` — Add secure trusted computing features in the MacBook firmware to audit and log all screen captures, UI interactions, and vision agent activity locally with tamper-proof timestamps for owner audits.
- **owner gets:** Ensures that all mac-vision activity is transparently recorded to a secure ledger that can be reviewed by the owner for privacy and security assurance, increasing trust in the system.
- effort: High effort requiring firmware development and integration with OS logging frameworks.  ·  risk: Firmware bugs or integration issues could impact system stability; mitigated by staged rollout and fallback modes.
- cost: Negligible hardware cost, moderate development cost.  ·  latency: No runtime latency impact.
- security: Significantly improves security and auditability of vision automation.
- depends on: mac-vision screen capture and UI action logging


## What it asked for

_Nothing._
