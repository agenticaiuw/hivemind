# Harness derivation — mac-vision — round 115

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision loop to interact with Mac UI using AI based on screenshots or UI snapshots for seamless, safe, and smart computer control when APIs are insufficient."
- **useful because:** The owner gains hands-free, intelligent computer control even for complex or visually-driven workflows that cannot be automated through APIs alone. This enables real-time assistance, fixing UI issues, automating mouse/keyboard tasks, and screen navigation with context awareness.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for UI decision loop, gpt-5.6-luna for higher judgement and perception integration
- **latency:** Real-time loop under 1.5 seconds per decision required for smooth interaction
- **cost:** Moderate; dominated by recurrent UI snapshot uploads and model computations on the Mac and relay
- **security:** High; requires strict typed action enforcement, user confirmation for destructive actions, no full keyboard or shell access without explicit permission, careful UI snapshot redaction to avoid exposing sensitive data, and failure recovery mechanisms.
- **missing:** Permission for computerUse.loopEnabled and visionUploadConsented; Typed action brokerage with classification of actions by risk; Continuous UI snapshot or pixel capture feed with owner consent and privacy safeguards; Safety and fallback policies; Integrated multi-agent coordination for perception, judgement, and action

### "Enable a continuous, low-latency UI snapshot and pixel capture feed from the Mac to mac-vision with user-controlled privacy filters and selective upload to ensure responsive, context-aware UI automation without exposing sensitive data."
- **useful because:** Allows mac-vision to have timely and relevant visual context for UI decisions to automate complex tasks and recover from UI changes or errors, enhancing productivity and automation power.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception
- **model tier:** gpt-4.1-mini for decision loop, assisted by stronger models for perception
- **latency:** Under 1.5 seconds per update for smooth response
- **cost:** Moderate, major cost in frequent data transfer and image processing
- **security:** Requires strong filtering/redaction, local privacy controls, and strict user consent management to prevent data leaks.
- **missing:** UI snapshot feed with local privacy filters; User control panel for snapshot settings; Integration with typed action broker for safe UI interaction

### "Seamlessly integrate mac-vision with multi-agent perception and judgement (faculty-perception and faculty-judgement) to analyze UI context deeply and decide next best actions that avoid errors and optimize owner workflow."
- **useful because:** This multi-agent approach leverages specialized models to provide accurate UI state understanding and strategic task planning, enabling mac-vision to act with high confidence and reduce mistakes in UI control.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for mac-vision UI loop, gpt-5.6-luna for faculty agents
- **latency:** End-to-end latency under 2 seconds to maintain interactivity
- **cost:** Moderate with distributed model load
- **security:** Requires secure inter-agent communication and audit trails to prevent misuse or data leakage
- **missing:** Inter-agent communication protocols; Shared context formats for UI state; Joint action planning and arbitration modules


## Changes it proposed to its own stack

### `interaction` — Add multi-channel safe control policy and typed action brokerage for mac-vision to ensure that every UI interaction is classified by risk and authorization level, and that destructive or high-impact UI actions require explicit, context-aware confirmation from the owner before execution.
- **owner gets:** Prevents accidental destructive UI interactions, increases trust in mac-vision automation by ensuring clear observability and control of which UI actions are taken and why, enabling safe full computer use loop unlocking.
- effort: Medium - requires integration between mac-vision decision loops, action brokerage, and confirmation UI layers.  ·  risk: Wrong classification could block legitimate actions or allow unsafe actions; thorough testing and fallback required.
- cost: Low to moderate, mostly computational as confirmation UI and action classification are software-only costs.  ·  latency: Minimal if well designed; extra confirmation adds user wait but only for high-risk actions.
- security: Adds significant security by limiting destructive operations and requiring owner authority.
- depends on: computerUse.loopEnabled permission; visionUploadConsented permission

### `hardware` — Equip the pendant with a dedicated local AI accelerator chip and secure UI snapshot redactor that preprocesses screen captures to anonymize sensitive information before sending to mac-vision, reducing privacy risks and latency.
- **owner gets:** Protects owner's sensitive data on screen by redacting it locally and speeds up UI snapshot processing and transmission, enabling more responsive and privacy-conscious AI computer control.
- effort: High, requires hardware design, firmware, and integration work.  ·  risk: Potential hardware delays or bugs, cost increase, complexity in redaction accuracy.
- cost: High, due to hardware addition and development.  ·  latency: Reduced latency from on-device preprocessing.
- security: Greatly improved privacy and security by localizing sensitive data processing.


## What it asked for

_Nothing._
