# Harness derivation — mac-vision — round 119

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the Mac to autonomously interact with any app UI using accessibility and pixel-based vision, for complex multi-step workflows and seamless cross-app automation."
- **useful because:** The owner could delegate any ambiguous or multi-step task that involves GUI manipulation, not just single app commands. This opens up true hands-off automation, including filling forms, clicking buttons, dragging, menu navigation, and more, that current tools cannot do due to lack of full UI interaction permissions and vision capabilities.
- **path:** mac-vision → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** large language model with vision and context awareness, running on the Mac for low-latency, with centralized coordination in relay-realtime for orchestration and state continuity.
- **latency:** Interactive, under 1 second per action for simple steps, up to a few seconds for complex multi-step tasks.
- **cost:** Moderate API calls for planning and verification per step; local compute for real-time vision processing.
- **security:** Requires explicit owner consent to enable full screen capture and UI interaction. Needs robust gating to avoid unintended destructive actions. Vision data must be handled with privacy controls and locally as much as possible.
- **missing:** Permission for mac-vision loop to enable screen capture and interaction; Vision upload consent for privacy and security; Integrated typed action policy for classification and safety gating of actions; Robust UI snapshot and pixel-based interaction tooling

### "Enable safe undo and confirmation mechanisms for all mac_run_actions and mac_delegate commands, with a transparent transcript system for the owner to review recent changes and revoke unintended effects."
- **useful because:** Owners gain trust in autonomous control by being able to easily see what actions were done, confirm or revoke them, and understand the AI's decision process. This is critical for high-impact or irreversible actions, reducing fear and errors, thus allowing broader autonomous operation.
- **path:** mac-planner → mac-vision → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Medium latency LLM generating receipts and confirmations with high reliability, integrated tightly with mac_run_actions and mac_delegate.
- **latency:** Milliseconds to seconds for receipts generation; confirmation on demand.
- **cost:** Minimal extra cost mostly from metadata tracking and simple UI overhead.
- **security:** Transcript data must be securely stored and protected to prevent misuse or privacy leaks.
- **missing:** Undo API for mac_run_actions and mac_delegate; Change tracking and action receipt generation; UI components for playback and confirmation


## Changes it proposed to its own stack

### `integration` — Implement a typed action classification and policy enforcement layer that automatically categorizes Mac UI interactions and commands into read-only, reversible, or destructive, and enforces owner-set policies and confirmations accordingly.
- **owner gets:** This ensures safe autonomous operation by limiting unintended destructive actions, allowing the owner to trust autonomous workflows to act within defined boundaries.
- effort: Moderate software development effort and integration testing.  ·  risk: Incorrect classification could lead to inappropriate blocking or allowing of actions; requires careful tuning and owner feedback.
- cost: Minimal additional compute cost for classification and policy checking.  ·  latency: Negligible impact due to lightweight classification.
- security: Enhances security by enforcing safe action boundaries.
- depends on: mac_run_actions; mac_delegate; relay_job_status

### `memory` — Create a persistent task and intent memory across all Mac surface agents that stores owner preferences, task outcomes, and rationale for actions taken, for personalized adaptation and auditability of autonomous Mac control.
- **owner gets:** Gives the owner confidence in the AI's ongoing behavior by remembering their preferences and previous decisions, enabling learning over time and reducing repetitive confirmations.
- effort: Moderate backend and local storage integration effort, plus extension to all Mac agents.  ·  risk: Data privacy and security must be carefully handled; data loss or corruption could degrade reliability.
- cost: Increased storage and retrieval costs, but manageable.  ·  latency: Slight delay added to integration steps when recalling context.
- security: Sensitive personal data requires strong encryption and access controls.
- depends on: mac_delegate; mac_run_actions; relay_job_status

### `context` — Establish a real-time unified UI and context telemetry stream from the Mac to all cooperative agents in the system, allowing synchronized awareness of app state, UI changes, notifications, and user behavior for enhanced coordination.
- **owner gets:** Sharing live UI and context state across mac-vision, mac-planner, relay-realtime, and the AI Pendant enables smarter, context-aware task execution and reduces redundant checks or actions, improving responsiveness and accuracy.
- effort: Moderate integration work across surfaces and agents, plus a low-latency communication protocol.  ·  risk: Privacy concerns with live streaming UI state; requires encryption and owner controls to disable or limit sharing.
- cost: Medium network and processing overhead due to continuous state streaming.  ·  latency: Designed for minimal latency but network conditions may affect timely updates.
- security: Sensitive UI context data requires strong encryption and strict access policies.
- depends on: mac-vision; mac-planner; relay-realtime; unified

### `interaction` — Develop a multi-modal natural language and gesture interface system that allows the owner to interact with Mac-based agents via speech, pen, touch, and eye tracking for intuitive and flexible control.
- **owner gets:** This provides the owner with more natural, accessible, and flexible ways to command and correct the AI agents, improving usability and reducing reliance on keyboard/mouse alone.
- effort: Significant software development including gesture recognition, speech processing, and cross-device integration.  ·  risk: Complexity of recognition could lead to errors or frustration if not highly accurate.
- cost: Increased compute costs for processing multi-modal inputs.  ·  latency: Needs to be low-latency for responsiveness, requiring optimization.
- security: Audio and sensor data privacy must be safeguarded.
- depends on: relay-realtime; mac-vision; mac-planner; unified


## What it asked for

_Nothing._
