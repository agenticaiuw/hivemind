# Harness derivation — mac-vision — round 273

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A prioritized and dynamically updated Mac vision task list that aggregates the owner's goals, memory facts, live workbench contexts, and smart ranking criteria."
- **useful because:** Today the Mac vision agent has no actionable task queue beyond two owner-stated facts; a prioritized list would allow it to truly focus effort where needed and coordinate better with multimodal agents.
- **path:** mac-local-agent → unified
- **model tier:** gpt-5.6-luna
- **latency:** under 2 seconds per update
- **cost:** moderate, dominated by memory and workbench queries and ranking model inference
- **security:** Must respect owner private memory, only surface tasks relevant to Mac agent, and honor owner preferences for what is shown and prioritized.
- **missing:** a richer task ranking model; integration between memory facts and workbench job states; a UI or dialogue for owner to confirm or reprioritize tasks

### "Seamless synchronization between the Mac vision accessibility UI snapshot and workbench contexts, allowing detection of claimed-versus-actual UI state and recovery after run interruptions."
- **useful because:** Currently, workbench contexts report what the system believes was done, but the Mac vision agent sees what is on screen. Syncing these can detect and recover from UI inconsistencies or failures, improving robustness and trust in automation.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** under 2 seconds
- **cost:** low to moderate, mostly I/O and comparison logic
- **security:** Needs to handle sensitive UI content carefully, restricting access to owner only.
- **missing:** API and storage support for claimed-versus-actual UI snapshot diff; Data structures for UI state versioning and recovery logic

### "Integrated feedback loop from Mac vision UI action results back into memory and workbench to confirm success, failure, or partial completion, enabling retry and undo workflows with minimal owner disruption."
- **useful because:** At present, UI automation steps may fail silently or cause disruption. Confirming action outcomes greatly improves reliability and owner confidence in the system.
- **path:** mac-local-agent → unified
- **model tier:** gpt-5.6-luna
- **latency:** few seconds
- **cost:** moderate, requires persistent state and reconciling action receipts
- **security:** Must not leak UI content or action logs beyond owner control, and avoid unsafe recovering actions without owner consent.
- **missing:** mac-vision capability to report fine-grained UI action outcomes; workbench integration to record and track UI action states

### "Real-time hardware telemetry for the pendant, including battery state, microphone usage logs, and button press history, accessible via the Mac to inform situational awareness and diagnostics."
- **useful because:** Currently, the Mac cannot see critical pendant hardware states or user interaction history, limiting proactive monitoring, diagnostics, and contextual responses.
- **path:** mac-local-agent → pendant
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes
- **cost:** low, mostly telemetry pull and caching
- **security:** Sensitive hardware state data must be protected from unauthorized external access and only shown with owner consent.
- **missing:** pendant telemetry API exposing battery, button press logs, and mic status

### "Cross-device coordinated workflow execution involving Mac vision, browser-extension, and ios-control agents to complete complex multi-step tasks that span Mac apps, browser sessions, and the iPhone."
- **useful because:** Many real tasks require interaction on multiple devices and applications; a coordinated workflow system would increase owner productivity and enable seamless task completion.
- **path:** mac-local-agent → browser-extension → ios-control → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes per step
- **cost:** moderate to high, due to multi-device coordination and state management
- **security:** Requires robust authentication and owner confirmation to avoid unwanted cross-device actions.
- **missing:** cross-device workflow orchestration API; shared task state synchronization across surfaces

### "A Mac vision capability to log and manage detailed history of user button presses on the pendant, supporting advanced gesture recognition and context-aware action triggers beyond the current single button press usage."
- **useful because:** The pendant has only one button with limited gesture recognition today. A history log and manager would allow richer, customizable user input signals and confirm or reject gesture interpretations for more reliable control.
- **path:** pendant → mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds
- **cost:** low, mainly data logging and syncing
- **security:** Button press logs are sensitive as they reveal user activity patterns; must be securely stored and accessed only by authorized components.
- **missing:** pendant button press logging and timestamping API; Mac side management and interpretation framework for button press history

### "Robust error recovery and retry mechanism for Mac vision UI automation tasks that preserves owner context and minimizes disruption"
- **useful because:** UI automation can often fail due to unexpected UI states or changes; a structured recovery mechanism would increase automation reliability and preserve user productivity.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds to retry and recover
- **cost:** low to moderate, mostly logic and state management
- **security:** Recovery actions must be safe and reversible, avoiding unintended side effects or data loss.
- **missing:** UI state checkpointing and diffing; Retry policies and recovery strategies in Mac vision


## What it asked for

_Nothing._
## Its own summary

Proposed eight new capabilities beyond the backlog: 1) Prioritized Mac vision task list fused with owner's memory facts and workbench state; 2) Synchronization of Mac vision UI snapshots with workbench contexts for claimed-versus-actual state comparison and recovery; 3) Feedback loop for UI action success/failure into memory and workbench; 4) Real-time hardware telemetry (battery, button logs) from pendant to Mac; 5) Cross-device coordinated workflows across Mac vision, browser extension, and iOS control; 6) Detailed pendant button press history management for richer user input; 7) Robust error recovery and retry for Mac vision UI automation; 8) Context-aware flexible task ranking with owner policy integration. Most require new APIs or data structures but unlock significant reliability, coordination, and productivity improvements for the owner.

**Biggest unknown:** Actual availability or feasibility of system support for claimed-versus-actual UI snapshot diffing and detailed UI action outcome reporting for Mac vision automation feedback.

