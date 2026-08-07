# Harness derivation — mac-vision — round 118

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Cross-device workflow orchestration that uses the Mac's UI vision/input capabilities combined with the browser extension and wearable pendant for an integrated multimodal assistant experience."
- **useful because:** Many tasks require coordinated action across apps, devices, and interfaces — for example, researching a topic in the browser, taking notes in a Mac app, and receiving voice summaries via the pendant. Centralizing orchestration across these substrates would enable smoother, context-aware task execution not achievable by any single device alone.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for orchestration, with gpt-4.1-mini assisting mac-vision locally
- **latency:** Seconds to minutes, depending on task length; low latency needed for multi-turn interactions
- **cost:** Moderate, depends on complexity and task volume; mostly server-side orchestration and cross-device communications
- **security:** Requires end-to-end encryption of context and task state, strict access control and user confirmation to avoid unintended cross-device actions
- **missing:** Unified task context and session state sharing across devices; Multimodal input fusion from vision, voice, keyboard, and UI events; Cross-device action delegation and reliable state reconciliation mechanisms

### "Give the owner real-time alerts on their Mac vision agent of critical UI changes or states requiring immediate attention, with selective screen capture summaries pushed to their wearable pendant."
- **useful because:** Many crucial tasks or errors appear visually on the Mac screen but may go unnoticed if the owner is focused elsewhere. Real-time visual alerts and summaries delivered to the pendant keep the owner informed and able to act promptly without constantly monitoring the Mac screen.
- **path:** mac-vision → relay-realtime
- **model tier:** gpt-4.1-mini local vision processing with lightweight relay summarization
- **latency:** Under 5 seconds for alerts and summary delivery
- **cost:** Low to moderate, mostly local processing and minimal cloud relay use
- **security:** Must carefully filter and redact private data in screen captures, owner consent required for monitoring and alerts.
- **missing:** Real-time visual change detection tuned for actionable UI states; Efficient, privacy-aware screen capture throttling and summarization; Integration between Mac vision alerts and pendant notification system

### "Enable owner-driven visual scripting on Mac that lets the owner teach the system UI interactions by example through direct manipulation, recorded clicks, and annotated screenshots."
- **useful because:** This lowers the barrier for automation by letting the owner easily create custom workflows based on their actual screen interactions without needing to write code or understand system internals. It empowers less technical users and speeds up task automation.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini for real-time interaction processing and scripting guidance
- **latency:** Interactive, within seconds of user input for feedback and script generation
- **cost:** Moderate due to continuous interaction monitoring and script synthesis
- **security:** Scripts must run with strict sandboxing to avoid unintended destructive actions; owner must confirm before running new scripts.
- **missing:** UI interaction recording and replay framework; Visual annotation and script generation interface; Integration with Mac automation and action execution tools

### "Allow the mac-vision agent to proactively learn and adapt UI interaction patterns based on owner habits and preferences, improving prediction accuracy and reducing manual corrections over time."
- **useful because:** By adapting to the owner's frequent UI tasks and preferred workflows, the system becomes more efficient, requiring fewer user interventions and making the interactions smoother, faster, and more personalized.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** gpt-4.1-mini locally for immediate adaptation and gpt-5.6-luna for aggregated learning and refinement
- **latency:** Real-time or near real-time adaptation within seconds
- **cost:** Moderate due to ongoing learning and model refinement
- **security:** Requires local data storage and analysis with owner control over what is learned and how data is used.
- **missing:** Continuous behavior tracking for UI interaction patterns; Model training infrastructure for incremental personalized learning; Mechanisms for user feedback to reinforce or correct learned patterns


## Changes it proposed to its own stack

### `integration` — Create a visual scripting integration layer that enables mac-vision to record on-screen actions, annotate UI elements, and generate executable automation scripts that run via mac_run_actions and mac_delegate, with user confirmation flows.
- **owner gets:** This would let the owner teach the AI how to interact with complex or custom UIs by showing it rather than explaining or coding, making automation accessible and practical for daily use.
- effort: Medium to high, involving UI event capture, annotation UX, script synthesis, and secure execution environment development.  ·  risk: Risk of incorrect or destructive automation if scripts aren't verified; can be mitigated by mandatory user approvals and sandboxing.
- cost: Moderate, requiring real-time recording and script generation infrastructure.  ·  latency: Low latency needed for interactive feedback.
- security: Requires strict sandboxing of generated scripts and user consent for execution.
- depends on: Enable the Mac vision loop for pixel-level UI data; Permission for vision data uploads for processing


## What it asked for

### `c12-fxym` (context) — ui_hierarchy_snapshot
- why: To understand current UI structure and elements on Mac for next computer use step.
- would change: I will be able to identify actionable UI elements and plan interaction steps precisely.

### `p6-m3fd` (permission) — computerUse.loopEnabled
- why: To enable the vision/computer use loop so I can capture screenshots and do pixel-based UI reasoning for tasks that need visual confirmation or layout understanding.
- risk it sees: Screenshots may expose sensitive screen contents; needs strong user consent and strict access control.

### `p7-41bt` (permission) — visionUploadConsented
- why: To upload captured images for cloud vision processing or sharing with other agents for better task understanding and assistance.
- risk it sees: Uploading images may expose private screen content to external services; requires owner consent.

