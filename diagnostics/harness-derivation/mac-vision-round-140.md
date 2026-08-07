# Harness derivation — mac-vision — round 140

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Turn on the mac-vision computer use loop with full accessibility and pixel interaction to automate GUI tasks safely."
- **useful because:** Many tasks require direct interaction with graphical applications and menus not exposed via API; this capability lets mac-vision assist by operating apps and dialogs visually without disrupting owner focus.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** hundreds of milliseconds per action
- **cost:** moderate due to image analysis and interaction steps
- **security:** Potential for unintended destructive UI actions; requires audit logs and possibly owner approval on high-risk actions.
- **missing:** permission for computerUse.loopEnabled; safe interaction policy; UI automation framework with typed actions

### "Allow mac-vision to capture and analyze detailed UI hierarchy snapshots on demand to guide navigating and interacting with the MacBook apps' interfaces."
- **useful because:** Having real-time structured UI data allows mac-vision to understand app windows and controls precisely, enabling accurate automation without guesswork or reliance on pixel coordinates alone.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds
- **cost:** low to moderate, mostly CPU work parsing UI trees
- **security:** UI snapshots may contain sensitive info; must ensure access is owner-approved and protected securely.
- **missing:** granted context access to ui_hierarchy_snapshot; model capability to parse and use UI data

### "Provide macros and typed automation support for mac-vision to execute reversible and auditable GUI operations, with a history log and undo capability."
- **useful because:** This safeguards owner control, builds trust in the mac-vision automation loop, and lets the owner understand and reverse any changes mac-vision makes to their Mac environment.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds per operation
- **cost:** low
- **security:** Logs must be secured against tampering; undo actions must be robust and reliable to avoid damage.
- **missing:** action receipt framework; undo job support; typed GUI actions with revertibility

### "Enable mac-vision to semantically understand UI elements (buttons, menus, dialogs, text fields, notifications) from accessibility data enhanced by pixel data to improve interaction accuracy."
- **useful because:** Semantic understanding drastically reduces errors in automation by recognizing UI element roles and states, allowing mac-vision to pick the right control without guessing by position or text alone.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** sub-second per UI query
- **cost:** moderate due to combined vision and accessibility ML costs
- **security:** Must ensure the semantic models only process local trusted UI data and do not expose sensitive info externally.
- **missing:** combined accessibility-pixel semantic UI model; training data for UI element recognition

### "Allow mac-vision to coordinate complex UI workflows combining Mac app control and browser interactions by integrating mac-planner and browser-extension capabilities."
- **useful because:** Many owner tasks span both native Mac apps and web browser sessions; seamless coordination via mac-vision enables end-to-end automation and reduces manual context switching for the owner.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** seconds per workflow step
- **cost:** moderate
- **security:** Cross-surface coordination requires careful permission handling and audit to prevent accidental data leaks or unintended automation.
- **missing:** cross-surface orchestration protocols; browser session state sharing

### "Allow mac-vision to run an always-on intelligent UI guardian mode that silently watches for UI state anomalies or accessibility breaks and alerts the owner only on real problems."
- **useful because:** This proactive assistant catches software bugs, accessibility regressions, and unusual states in mac apps without interfering unless necessary, maintaining owner awareness and productivity.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds for anomaly detection
- **cost:** low to moderate, depending on monitoring cadence
- **security:** UI state data is sensitive, must be processed locally and only alert owner with minimal data leaks.
- **missing:** continuous UI state monitoring framework; anomaly detection models; alerting system

### "Enable mac-vision to generate step-by-step visual tutorials for owner training by recording UI interactions and annotating them semantically."
- **useful because:** The owner can learn complex or unfamiliar Mac and app workflows interactively, reducing training time and errors by using demonstrations tailored to their actual environment.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds to minutes per tutorial generation
- **cost:** moderate due to video/image processing and semantic annotation
- **security:** Recorded UI interactions may reveal sensitive info; tutorials must be stored and shared securely.
- **missing:** UI interaction recording framework; semantic annotation models; interactive tutorial generation tooling

### "Enable mac-vision to detect and resolve UI dead-ends or traps automatically by trying alternate paths or recovery actions without owner intervention."
- **useful because:** The owner experiences seamless task automation without manual intervention when dialogs freeze, menus fail, or unexpected UI states block progress.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds per recovery trial
- **cost:** moderate due to exploratory and fallback attempts
- **security:** Must avoid accidental destructive actions; ensure recovery actions are conservative and reversible when possible.
- **missing:** UI exploration and recovery logic; state machine modeling of UI workflows

### "Allow mac-vision to provide contextual help and UI explanations in real-time as the owner explores new or complex Mac apps, by analyzing the current UI state and fetching concise guidance."
- **useful because:** The owner gets proactive, context-aware assistance that reduces learning curves and helps avoid common mistakes without leaving the app or searching externally.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** moderate
- **security:** Context data must remain private; explanations should avoid exposing sensitive data externally.
- **missing:** UI context extraction and analysis; dynamic help content generation models

### "Enable mac-vision to simulate touchscreen gestures and pointer multi-touch events on supported Mac applications and external devices for richer interaction possibilities."
- **useful because:** Many modern Mac apps and external devices support multi-touch and gesture controls; enabling mac-vision to simulate these extends its automation reach and accessibility for the owner.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** milliseconds to sub-seconds per gesture
- **cost:** moderate
- **security:** Gesture simulation must be controlled to avoid accidental or malicious interactions; logs and owner control required.
- **missing:** multi-touch event simulation APIs or drivers; gesture sequence planning and execution models


## Changes it proposed to its own stack

### `hardware` — Add a dedicated low-power vision coprocessor on the pendant to assist mac-vision by preprocessing UI screenshots for semantic element recognition and anomaly detection locally, reducing latency and network usage.
- **owner gets:** Faster UI understanding and proactive anomaly detection without wasting Mac or cloud compute and enabling offline operation with privacy preservation.
- effort: High, requires hardware design, integration, firmware, and developer toolchain enhancements.  ·  risk: Delays or bugs in coprocessor hardware or firmware could reduce overall system reliability temporarily.
- cost: Significant hardware and development cost increase.  ·  latency: Significant reduction for UI processing and recognition tasks.
- security: Local processing means less sensitive UI data sent externally, improving data security and privacy.
- depends on: semantic UI element recognition models; UI state anomaly detection framework


## What it asked for

_Nothing._
