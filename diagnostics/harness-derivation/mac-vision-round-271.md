# Harness derivation — mac-vision — round 271

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A unified prioritized task manager for the Mac that synthesizes owner input, memory facts, reminders, and open workflows into a single ranked actionable list for mac_vision automation and reporting."
- **useful because:** The owner currently has no durable task management for Mac-vision automation, leading to no prioritized work or progress tracking on the Mac. This would provide a single source of truth for what needs done and enable autonomous UI work with justifications.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** under 1s
- **cost:** low per invocation; mostly in memory query and ranking
- **security:** Task priorities may contain sensitive information; respect owner's privacy and allow opt-out.
- **missing:** a mechanism to write, update, and rank tasks atomically within the Mac local agent; integration with memory facts and reminders APIs; priority and urgency metadata with deadlines and dependencies

### "An accessibility loop state tracker that compares expected workflow steps from the Mac agent planner to actual UI state via accessibility tree snapshots, to detect divergence, allow recovery, and keep UI automation reliable."
- **useful because:** Currently, mac_delegate and accessibility automation run blindly on the UI and can get lost or confused. A state tracker monitoring actual UI progress enables more robust, human-like workflow continuation and error recovery.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** milliseconds to 1s per step
- **cost:** medium; requires maintaining UI state and workflow graphs
- **security:** UI state may reveal sensitive data; keep all data local and encrypted.
- **missing:** persistent UI state graph store; linking expected workflow state to accessibility snapshots; mechanisms for recovery prompts or automated corrective actions

### "Voice-activated incremental Mac memo dictation and summary creator integrated with Mac-vision. The owner can speak notes or reminders that are transcribed, stored, refreshed, and summarized on demand by Mac-vision, and optionally linked to tasks or workflows."
- **useful because:** This gives the owner a hands-free way to capture ideas and next actions while working on the Mac, tightly integrated with the automation and task prioritization engine.
- **path:** mac-local-agent → pendant
- **model tier:** realtime
- **latency:** under 2s for transcription and update
- **cost:** moderate; requires audio capture, speech-to-text, and text summarization models
- **security:** Audio transcripts may contain sensitive information. Data must be encrypted and controlled by the owner.
- **missing:** low-latency local speech-to-text model or fast offload to cloud; durable memo store linked to memory facts and task list; integration with voice capture on pendant and mac-vision text summary renderer

### "Context-aware automatic prioritization of Mac UI automation tasks by integrating owner preferences, calendar context, and urgency signals to dynamically adjust the focus of mac_vision's autonomous actions."
- **useful because:** This allows the Mac automation to focus on what matters most in real-time, improving owner productivity and reducing distractions or low-value tasks.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** sub-second update for priority shifts
- **cost:** moderate cost for ranking and inference models
- **security:** Task priority data may reveal sensitive info; ensure privacy and local computation.
- **missing:** dynamic context feeds from calendar and reminders; ranking model tuned to owner preferences; integration with mac_vision task execution loop

### "A seamless, omnipresent UI state snapshot and backup capability that takes rapid accessibility-tree snapshots and selectively pixel screenshots on the Mac. This would support audit, undo, and recovery across all automation steps and prevent workflow loss or damage."
- **useful because:** Because UI automation can fail silently or diverge unnoticed, having a rich context-aware snapshot and undo store enables mac_vision and the owner to diagnose, revert, and continue work reliably and safely.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** milliseconds to seconds per snapshot
- **cost:** medium to high, depending on snapshot frequency and storage
- **security:** Snapshots might contain sensitive user data; must be securely encrypted and accessible only to the owner.
- **missing:** efficient rapid snapshot storage and retrieval system; integration with workflow tracking and undo job mechanisms; selective pixel capture policy to minimize privacy risks


## Changes it proposed to its own stack

### `model-routing` — Introduce a typed UI action classification and policy enforcement broker for mac_run_actions and browser_run_actions. Classify each action as read-only, reversible, or destructive with enforced confirmation or undo options for destructive actions.
- **owner gets:** This mitigates risk of accidental destructive UI automation, enabling safer autonomous computer use without causing data loss or unintended side effects.
- effort: Medium complexity; requires changes in Mac agent action dispatch and integration with undo job routes.  ·  risk: Potential delays or blocking of UI steps if policies are too strict; requires tuning and user feedback to get right.
- cost: Minimal API cost; mostly software change.  ·  latency: Slight increase in action dispatch latency for classification and confirmation.
- security: Improves security by enforcing user consent on risky actions.
- depends on: mac_run_actions; browser_run_actions

### `hardware` — Design a next-generation pendant with additional physical controls (e.g., a second button with distinct functionality) and enhanced sensors (battery gauge, temperature) to support more expressive and safer user gestures, better environmental awareness, and improved power management.
- **owner gets:** Current pendant hardware limits the owner's direct interaction capabilities and power feedback, restricting user experience and feedback on device status.
- effort: High; requires new PCB design, firmware updates, and validation.  ·  risk: Potential delays in production, increased power consumption, and firmware complexity.
- cost: Hardware cost increase due to additional components, moderate development cost.  ·  latency: No latency impact on AI services but better real-time feedback to user.
- security: Improved due to hardware-enforced physical controls preventing mistaken actions.


## What it asked for

_Nothing._
