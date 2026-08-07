# Harness derivation — mac-vision — round 84

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Interactive visual debugging assistant on the Mac to help the owner understand and fix UI problems"
- **useful because:** Owners often face obscure UI or app issues that are hard to diagnose and fix remotely. A visual debugging assistant could inspect screen elements, UI trees, logs, and application state, then provide a clear, interactive diagnostic with suggestions and actionable steps.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** gpt-5.6-luna for deep context analysis and interactive guidance
- **latency:** Minutes for deep diagnosis, seconds for concise replies
- **cost:** Moderate to high due to multi-modal analysis and human-like interaction
- **security:** Needs read-only access with owner confirmation for any remote or local diagnostic commands; privacy careful with screenshots or logs; interaction logged for transparency
- **missing:** Robust UI and log data integration streams from Mac apps; Interactive stepwise guidance and state monitoring; Safe toggles for read-only vs. actionable modes controlled by owner; Integration with knowledge bases of common Mac UI issues and fixes

### "Cross-surface AI orchestration for seamless delegation of complex multi-step tasks involving Mac apps, browser sessions, and voice commands"
- **useful because:** Currently, AI agents operate mostly in isolation on Mac, browser, or voice surfaces. Orchestrating their capabilities in a coordinated workflow would enable the owner to request complex tasks (such as preparing a report from browser research, file management, and calendar scheduling) in one command with seamless handoffs.
- **path:** mac-planner → browser-extension → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for planning and orchestration with fallback AI tiers for specialized tasks
- **latency:** Seconds to few minutes depending on task complexity
- **cost:** Moderate due to orchestration overhead and multistep task planning
- **security:** Requires robust context sharing protocols across surfaces with strong access control and audit logging; owner approval required for sensitive workflow triggers; careful failure recovery mechanisms
- **missing:** Unified cross-surface task state representation and goal passing; Inter-surface context sharing and memory synchronization; Protocols for human-in-the-loop approval at sensitive steps; Error and conflict detection/reconciliation across agents

### "AI assistant that proactively detects UI anomalies or stuck states on the Mac and suggests recovery actions"
- **useful because:** Users sometimes encounter UI freezes, dialog jams, or unexpected behavior that they do not notice immediately. An AI monitoring assistant that watches the UI state (via accessibility snapshots or screenshots once enabled) can detect these anomalies, alert the owner, and propose or automatically perform recovery actions like killing a hung app or closing modals.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement
- **model tier:** gpt-5.6-luna for anomaly detection and recovery planning
- **latency:** Seconds to notify, with background execution for recovery steps
- **cost:** Moderate for continuous UI monitoring and anomaly detection models
- **security:** Requires careful owner-configured permissions for automatic actions; logs and alerts must respect privacy; emergency shutoff features mandatory to prevent annoying false alarms or dangerous actions.
- **missing:** Continuous UI state streaming and anomaly detection integration; Safe automated action triggers with owner-configured policies and fail-safe mechanisms


## Changes it proposed to its own stack

### `hardware` — Implement a low-power local vision processing chip on the pendant hardware to preprocess and classify UI elements visually in real time, enabling context-aware actions without exposing raw screenshots externally.
- **owner gets:** This would allow extremely low-latency and privacy-preserving visual UI understanding to support the mac-vision loop's real-time interaction without needing constant high-bandwidth screenshot uploads to the cloud, protecting owner's data and enabling offline use.
- effort: Significant hardware design and firmware development plus integration with cloud AI interfaces and local AI runtimes.  ·  risk: Hardware complexity could increase cost and power draw; could fail to meet accuracy targets requiring fallback to cloud processing; recovery by software update and graceful degradation to limited functionality.
- cost: High initial hardware design and unit cost increment; power draw increase but managed by low-power chip choice.  ·  latency: Greatly reduced latency for UI recognition tasks compared to full screenshot upload and processing.
- security: Improves security by limiting raw data exposure; requires secure firmware and trusted computing to prevent tampering.
- depends on: mac-vision enabled visionUploadConsented loop; software integration for local AI preprocessing on pendant

### `interaction` — Create an interactive guided UI exploration mode that lets the owner visually showcase an app or screen area to the mac-vision agent for teaching or problem diagnosis.
- **owner gets:** Owners often need to demonstrate a problem or task visually in a flexible way. An interactive teach-back mode allows them to highlight areas, explain issues via voice or text, and get guided AI assistance or diagnostics that adapt dynamically to the owner's explanations and input.
- effort: Medium to high, involving UI tooling for interactive region selection, audio input integration, dynamic AI feedback loop, and state capture from the visual environment.  ·  risk: Interaction complexity risks user confusion; mitigated by clear UI design and fallback modes. Privacy concerns managed by explicit user start/stop control and no data retention without consent.
- cost: Moderate due to multi-modal AI processing and context memory usage.  ·  latency: Interactive but with a few seconds response time, suitable for a conversation or teaching session.
- security: Requires explicit owner consent and secure handling of visual and audio data. Logs and data retention must be transparent to owner.
- depends on: mac-vision loop enabled with screenshot and audio input capture; dialog and context memory management; voice recognition and transcription


## What it asked for

_Nothing._
