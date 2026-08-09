# Harness derivation — mac-vision — round 240

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I want the Mac agent to maintain a dynamic prioritized task list reflecting my true current work, integrating both my hand-typed tasks and my live Reminders and calendar deadlines, with topical ranking beyond structural priority."
- **useful because:** Currently, the Mac agent has no integrated, up-to-date task list to prioritize its activities and decide what to do next. A single, dynamic, prioritized queue would ensure the Mac agent always focuses on what matters most to me, improving productivity and trust in autonomous actions.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** background
- **latency:** seconds
- **cost:** low per invocation, mostly minimal compute and memory IO
- **security:** Task content is personal and sensitive; data should remain encrypted and private, exposed only to trusted agents. User must control task editing/removal.
- **missing:** Reliable multi-source task ranking algorithm; Cross-surface task state sync

### "I want the Mac agent to plan and execute multi-step workflows to progress complex tasks like 'derive the next round of agent changes from the harness ledger' or 'ship the 24 kHz audio path' by combining mac_run_actions and mac_delegate with real-time UI accessibility feedback."
- **useful because:** Complex tasks involving multiple apps and steps cannot be handled by atomic actions alone. Coordinating these with real UI state feedback and reversibility would dramatically extend automation potential on the Mac and reduce manual burden.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** hundreds of milliseconds to a few seconds per step
- **cost:** moderate, as interactive UI perception and planning require more compute
- **security:** Automation with UI control must prevent accidental destructive actions and respect user confirmation policies.
- **missing:** Advanced UI accessibility input-output integration; Stateful multi-step planner with recovery; User approval flow for critical steps

### "I want the Mac agent to coordinate with the physical pendant device to provide real-time tactile and LED feedback for task status, progress, and critical alerts, integrating LED signals with voice feedback for multimodal owner awareness."
- **useful because:** The pendant's single button and LED are underused for feedback and control. Tight integration improves owner awareness and control over ongoing Mac automation, enabling instant acknowledgement, gesture confirmations, and error alerts without breaking workflow.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** background
- **latency:** tens to hundreds of milliseconds
- **cost:** low, minimal radio and processing cost
- **security:** Signals must be respectful of privacy and avoid noisy or confusing patterns. Confirmation-sensitive actions require explicit owner consent gestures.
- **missing:** Expanded pendant LED signalling schema; Button press event routing to Mac agent; Voice-pendant feedback coordination

### "I want the Mac agent to automatically confirm non-destructive reminders and note creations without asking, but require explicit confirmation via physical pendant gestures before destructive actions like sending mail, deleting files, or making purchases."
- **useful because:** This matches the owner's preferences for automation where convenience is prioritized for safe actions, but control and safety are enforced for high-risk ones. It prevents accidental destructive tasks while improving trusted automation scope.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** sub-second
- **cost:** low
- **security:** Must securely verify and log all physical confirmations and offer owner override.
- **missing:** Physical pendant confirmation gestures linked to specific task authorization; Fine-grained action classification for destructive vs safe; Audit logging of confirmed/rejected actions

### "I want a capability where the Mac agent visually verifies the actual UI state against what the automation plan expects before and after each step, detecting failures or divergences in real time to trigger retries or corrections."
- **useful because:** This ensures robust, reliable Mac UI automation by detecting and recovering from unexpected UI changes or failures, increasing trust in complex multi-step workflows and preventing unintended consequences.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** tens to hundreds of milliseconds per step
- **cost:** moderate due to real-time screen parsing and analysis
- **security:** Screenshots and UI state data are sensitive; processing must be local and secure. No stable screenshots should be sent off-device without consent.
- **missing:** Real-time UI state capture and comparison; Automation plan integration with visual verification; Step rollback and retry mechanisms

### "I want to audit and log all Mac automation actions, with full traceability of what commands ran, what UI was touched, their success or failure, and results, providing a complete transparent history for review and debugging."
- **useful because:** Owners need accountability and audit trails when agents control their computer, especially for destructive or complex workflows. This builds trust, supports troubleshooting, and ensures responsible automation.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** low additional storage and compute
- **security:** Logs contain sensitive actions and data; must be encrypted and accessible only to trusted owners. Retention policies and redaction should be configurable.
- **missing:** Unified automation audit log across tools and surfaces; Reliable success/failure detection from UI and shell results; Secure storage and access control for logs

### "I want the Mac agent to automatically detect and adjust for context changes such as app or window focus switches, ensuring automation continues seamlessly across multitasking scenarios by dynamically adapting the UI interaction plan."
- **useful because:** Mac users commonly switch between apps and windows. Automation must robustly track these context changes to avoid errors or stalling waiting for UI elements that are no longer visible. Adaptive context sensitivity boosts reliability and usability.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** tens to hundreds of milliseconds
- **cost:** moderate, requires continuous UI state monitoring
- **security:** Context data is sensitive; processing should remain local and secure.
- **missing:** Context-aware adaptive UI automation logic; Continuous app/window focus tracking; Dynamic plan adjustment middleware


## What it asked for

_Nothing._
