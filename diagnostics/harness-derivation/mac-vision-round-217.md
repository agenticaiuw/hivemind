# Harness derivation — mac-vision — round 217

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision agent's accessibility-based computer use loop to interact with the Mac UI safely and effectively."
- **useful because:** This capability allows the mac-vision agent to read and interact with Mac applications via the accessibility API without requiring screen recording, enabling automation and assistance around computer use tasks, improving productivity and user experience.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** low-latency response under 1 second
- **cost:** Low per call, mostly CPU for planning and validation; no additional API calls triggered
- **security:** Requires accessibility permission for the AI Pendant Agent binary; control actions must be reversible or confirmed by the owner on destructive commands; no screen recording to protect privacy.
- **missing:** 

### "Provide mac-vision with verified state of the Mac UI during multi-step workflows by comparing claimed work state to actual on-screen UI state."
- **useful because:** Currently, mac-delegate provides claimed versus actual state for file outputs in workflows, but there is no similar verification for GUI state. This capability would allow mac-vision to detect divergences between intended and actual UI progress, allowing smarter error recovery and more reliable multi-step automation.
- **path:** mac-vision → mac-delegate → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** moderate, about 2-3 seconds
- **cost:** Moderate, requires querying workbench contexts and accessibility tree snapshots and comparing them.
- **security:** Requires careful handling of UI state to avoid leaking sensitive screen data off the device; all processing should be local.
- **missing:** Automated comparison of GUI accessibility snapshots against workbench contexts; Data model to represent GUI state claims and actuals; APIs to link workflow step state to GUI elements

### "Provide a summary and actionable next steps for notes created today in the mac-vision agent environment."
- **useful because:** This capability enables the mac-vision agent to automatically process notes created throughout the day, summarizing key points and suggesting concrete next actions to the owner, improving task follow-up and personal productivity.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** a few seconds
- **cost:** Moderate, involves NLP summarization and action extraction from text notes.
- **security:** Notes may contain sensitive information; processing should be local or within secure environment with owner consent.
- **missing:** Integration with notes storage and retrieval APIs; NLP pipelines for summarization and action extraction

### "Enable mac-vision to coordinate with the voice assistant and wearable pendant for multimodal task handling, combining voice, UI interaction, and physical device input/output."
- **useful because:** Leveraging the wearable pendant for physical presence, voice assistant for commands, and mac-vision for GUI interaction enables rich multimodal task handling that no single device or surface can match alone. This greatly expands the owner's ability to command, monitor, and adjust complex workflows.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** low-latency under 1 second for voice/UI actions, moderate background for cross-device sync
- **cost:** Complex, involving cross-surface coordination and real-time state management.
- **security:** Requires secure coordination to prevent unauthorized control and leaks, especially given multiple physical and networked components.
- **missing:** Multimodal synchronization protocols and context-sharing APIs; Cross-device event and state coordination frameworks

### "Provide divergence detection for mac-vision interaction loops, comparing expected UI goal states to actual discovered UI states during execution to detect errors or unexpected changes."
- **useful because:** Without detecting when the UI drifts or changes unexpectedly during an automation sequence, the mac-vision agent risks taking incorrect actions or failing silently. Divergence detection improves robustness and supports recovery by alerting when UI states do not match expectations.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini
- **latency:** low-latency, realtime to next step decision
- **cost:** Low per-step computational cost, but requires storage of expected UI snapshots or models and comparison algorithms.
- **security:** UI state is sensitive and may include private content; divergence detection must keep data local and secure.
- **missing:** Formal models or summaries of expected UI states or control trees per step; Algorithms to compare observed UI to expected UI states; Capability to store and retrieve historical UI state snapshots

### "Enable mac-vision to register physical button presses from the pendant to trigger specific Mac UI automation sequences or approvals."
- **useful because:** The pendant's physical buttons provide a secure and convenient way for the owner to trigger or approve actions on their Mac via mac-vision. Leveraging this direct hardware interaction improves safety, responsiveness, and usability of Mac automation workflows.
- **path:** mac-vision → pendant
- **model tier:** gpt-5.6-luna
- **latency:** low-latency, sub-second response
- **cost:** Low cost - the pendant hardware already supports button detection; the work is on event handling and mac-vision binding.
- **security:** Must ensure physical button events are securely authenticated and cannot be spoofed or misused. Approval actions must be clear and unambiguous.
- **missing:** Event relay system from pendant button presses to mac-vision agent; Mapping between button events and mac-vision automation sequences

### "Real-time adaptive Mac UI assistant that detects and recovers from unexpected changes or prompts during workflows, with user feedback loop via the pendant."
- **useful because:** Users often encounter unexpected dialogs, errors, or changes in app state during Mac workflows that break automation. An assistant that detects these in real-time via mac-vision, proposes recovery actions, and requests quick user approval or guidance via the pendant would create a reliable, interactive automation experience that adapts dynamically to conditions unseen in advance.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** sub-second for detection, 1-3 seconds for user feedback and recovery
- **cost:** Moderate to high due to continuous monitoring, AI interaction, and cross-device communication
- **security:** Requires secure, owner-controlled permissions for UI monitoring and device interaction; careful data privacy design.
- **missing:** Real-time UI anomaly detection models; Fast user feedback channel via pendant; Integration of AI reasoning for adaptive recovery steps

### "A comprehensive GUI automation scripting language or DSL integrated with mac-vision that supports conditional logic, error handling, and context awareness, plus integration points for voice and pendant input triggers."
- **useful because:** Current automation through mac-vision is step-by-step and reactive. A rich scripting or DSL layer would enable the owner and the system to create, reuse, and share complex, robust automation flows that dynamically adapt to UI state, errors, and multimodal triggers, vastly expanding power and flexibility.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** Design time scripting can be slow; runtime reaction should be low-latency for UI steps
- **cost:** High development and compute cost initially; runtime cost moderate
- **security:** Complex scripts increase risk of unintended actions; must have strong owner controls, safeguards, and transparency.
- **missing:** Formal DSL design and interpreter; DBG and editor support in mac-planner; Integration of voice and pendant triggers for dynamic flow control

### "Mac-vision enabled with predictive UI interaction: using AI to forecast next logical UI controls or dialogs to appear in currently running apps and preemptively preparing automation steps or user prompts."
- **useful because:** Predictive interaction reduces latency and error by anticipating UI changes before they happen, smoothing automation flow and improving user experience. This capability could also warn the owner of likely modal dialogs or errors ahead of time.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** Low latency for predictions as UI state is refreshed
- **cost:** Moderate, due to running prediction models continuously
- **security:** Predictions require UI state monitoring; data privacy and secure local processing are needed.
- **missing:** AI models trained on UI state sequences; Fast integration with mac-vision's accessibility tree polling

### "Allow mac-vision to autonomously test, learn, and improve its UI interaction sequences by recording failed attempts, exploring alternative paths, and updating workflows accordingly."
- **useful because:** Automation often breaks due to UI changes or unexpected states. By recording failures, exploring alternatives, and learning from experience, mac-vision can self-heal automation scripts, reducing owner intervention and improving reliability over time.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** Background learning with real-time fallback
- **cost:** Potentially high due to exploration, recording, and retraining
- **security:** Requires logging UI states and automation actions securely; must avoid leaking sensitive info; clear owner control needed.
- **missing:** Self-learning algorithms for UI automation; Storage for histories and alternative interaction paths; Integration with accessible workflow editors


## What it asked for

_Nothing._
