# Harness derivation — mac-vision — round 90

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision computer use loop with safe, policy-aligned access to screenshots, UI snapshots, and pixel-level actions to perform precise UI interactions on the Mac that cannot be done via API alone."
- **useful because:** This would allow seamless multi-modal automation on the Mac by bridging low-level UI manipulations (pixel and accessibility level) with higher-level API-based control. It would enable resolving ambiguous or complex workflows the owner cannot express as short command sequences. It also provides fallback when direct API controls do not exist or fail, improving reliability and reach of automation.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini specialized with real-time pixel and UI context understanding
- **latency:** Low latency (sub-second) per interaction step to allow fluid UI navigation and reaction to owner prompts
- **cost:** Moderate API cost per invocation dominated by vision model compute and potentially additional snapshot/context uploads
- **security:** This capability requires granting the mac-vision loop permission to capture screen content, interpret UI with pixel context, and perform click/type actions. Policies and explicit owner consent must prevent accidental destructive actions. Visibility into all actions is mandatory.
- **missing:** Enable computerUse.loopEnabled; Enable visionUploadConsented for screen capture; Implement robust typed action policies to prevent destructive commands without confirmation; Add dedicated context permissions such as ui_hierarchy_snapshot; Policy/UX for owner approval and audit of actions

### "Unified multimodal task orchestration that seamlessly combines visual UI control (mac-vision), high-level planning (mac-planner), voice interaction (relay-realtime), and browser automation (browser-extension) into a single continuous workflow for the owner."
- **useful because:** This integration would allow the owner to interact naturally, issuing commands verbally, visually, or by planning, with the system dynamically deciding the best surface to act on for each step. Complex tasks involving multiple applications or modalities would be solved fluidly without manual handoff or context switching.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna coordinating multiple specialized subsystems
- **latency:** Moderate latency (seconds) allowing smooth transitions and updates between surfaces but prioritizing interactive feel
- **cost:** Relatively high due to cross-surface coordination and multi-model calls per task step
- **security:** Requires tight authorization and auditing across all surfaces, since multi-surface actions can have broad impact. Context sharing policies must protect the owner's privacy and control.
- **missing:** Cross-surface communication protocols for task handoff and status updates; Unified state model with shared context and history; Advanced model routing for specialization and fallback; User experience for error recovery and clarification

### "A proactive assistant feature on mac-vision that automatically observes the Mac's UI state and detects when complex or ambiguous user tasks arise that need multi-step plans, then prompts the owner or escalates to mac-planner or mac-delegate automatically."
- **useful because:** This would reduce the owner's need to explicitly ask for help with complex tasks, enabling anticipatory assistance and more natural interaction flows. It helps surface important tasks or problems that the owner might overlook, increasing productivity.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → relay-realtime
- **model tier:** gpt-4.1-mini with event detection and task understanding modules
- **latency:** Low latency for UI observation events, moderate for task escalation steps.
- **cost:** Moderate due to continuous observation and model inference for event detection and goal identification.
- **security:** Needs privacy-preserving observation limits and strict data retention policies to avoid misuse of UI state monitoring.
- **missing:** Event detection mechanisms within mac-vision agent; Automatic goal formulation and escalation pipelines; Consent and control interface for proactive interventions


## What it asked for

_Nothing._
