# Harness derivation — mac-vision — round 96

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a persistent, contextual UI state memory shared between mac-vision, mac-planner, and relay-realtime to track UI changes and ongoing multi-step workflows more effectively over time."
- **useful because:** This capability allows long-running or interrupted workflows to resume smoothly, improve context awareness across devices and sessions, and reduce redundant UI navigation steps.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** sub-second to few seconds for UI state sync
- **cost:** Moderate cost for state storage, sync protocols, and memory retrieval inference across devices.
- **security:** Sensitive UI state data must be encrypted and access controlled to prevent leaks of private information.
- **missing:** Persistent UI state store with synchronization; Cross-agent protocol for UI context exchange; Memory-aware workflow guidance and recovery algorithms

### "Integrate a flexible, high-precision UI element search and manipulation toolkit combining mac-vision's accessibility and pixel data with mac-planner's scripting and relay-realtime's real-time feedback to reliably manipulate any Mac application UI element."
- **useful because:** This enables robust execution of complex UI workflows across diverse applications with high reliability and minimal manual correction, greatly expanding what mac-vision can automate and making interactions more predictable.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** seconds per complex UI action batch
- **cost:** Moderate; dominated by integration complexity and real-time validation feedback loops.
- **security:** Needs strict permission and audit controls to prevent unauthorized UI manipulation.
- **missing:** Unified UI element abstraction layer combining accessibility and pixel data; Real-time UI state validation and feedback loop between agents; Advanced search algorithms leveraging semantic UI properties


## Changes it proposed to its own stack

### `model-routing` — Implement fine-grained typed action classification routing in the computer-use loop model pipeline, differentiating between read-only, reversible local mutations, and high-impact irreversible mutations, with hooks for audit and undo triggers.
- **owner gets:** This ensures the owner can safely benefit from high autonomy in Mac UI operation while minimizing risk of unintended destructive actions, enhancing trust and usability of the mac-vision agent.
- effort: Moderate to high engineering effort to build the classification model, integrate with existing looping and undo architecture, and create audit and prompt systems.  ·  risk: Risk of misclassification leading to accidental high-impact actions; can be mitigated via human-in-the-loop fallback and robust undo infrastructure.
- cost: Increased compute cost for classification inference in real-time loop; small additional storage for audit logs.  ·  latency: Minimal added latency if carefully optimized.
- security: Increased audit and logging improve security but require careful data handling.
- depends on: Enable mac-vision loop and permissions for real-time UI access; Integrate undo and audit hooks with computer-use loop

### `interaction` — Create an extensible, transparent user approval and feedback system integrated with the mac-vision computer-use loop, allowing contextual prompts, confirmations for high-impact actions, reversible actions feedback, and real-time undo options.
- **owner gets:** This empowers the owner to safely delegate UI control while retaining awareness and intervention ability, significantly reducing anxiety about unintended consequences of AI-driven interactions.
- effort: Moderate engineering effort to design UI/UX for approvals and feedback, integrate feedback into loop, and maintain reactivity without excessive user interruption.  ·  risk: Too frequent prompts could annoy owner; balance needed between safety and usability.
- cost: Minor computational cost; mostly UI development effort.  ·  latency: Slight increase in interaction latency due to prompt handling.
- security: Improves security by requiring explicit confirmation on sensitive actions.
- depends on: Enable mac-vision loop and permissions; Typed action classification layer for risk assessment; Undo and audit infrastructure

### `hardware` — Upgrade the Mac pendant hardware with a dedicated secure module that enables encrypted, low-latency local processing of UI snapshots and vision data, reducing reliance on cloud or Mac CPU for real-time vision and action validation.
- **owner gets:** This enhances responsiveness and privacy for mac-vision's UI interaction, enabling offline operation capability and reducing security risks of sensitive screen data transmission.
- effort: High hardware engineering effort to design, prototype, and integrate a secure vision processing unit in the pendant hardware, plus firmware and software support.  ·  risk: Hardware delays or flaws could reduce overall system usability; high development cost and time.
- cost: Significant hardware cost increase for pendant; moderate operational cost savings by offloading from Mac/cloud.  ·  latency: Substantial reductions in processing latency for computer-use loop tasks.
- security: Improves security by localizing sensitive vision data processing on a trusted hardware environment.
- depends on: Current pendant hardware specs and upgrade path approval


## What it asked for

_Nothing._
