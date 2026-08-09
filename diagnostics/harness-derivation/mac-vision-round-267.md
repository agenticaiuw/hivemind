# Harness derivation — mac-vision — round 267

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "How can mac-vision safely resume or continue multi-step UI automation workflows on the Mac after interruptions?"
- **useful because:** Ensures the system can robustly handle longer complex automation without losing progress or repeating work on failure or reboot, essential for practical macOS UI automation.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate - mostly model interaction
- **security:** Must ensure UI state snapshots do not expose sensitive info; resume protocols need to guard against unwanted or unsafe UI actions.
- **missing:** UI snapshot diff storage and reconciliation APIs; enhanced workbench context state to track UI progress

### "How can the mac-vision accessibility automation loop integrate tightly with mac-run-actions and mac-delegate for seamless multi-tier task execution?"
- **useful because:** Combines declarative planning with precise UI control for reliable complex task automation on Mac, avoiding gaps and reducing errors due to context disconnects.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate
- **security:** Integration requires trust boundaries and action confirmation protocols to avoid destructive or unwanted actions.
- **missing:** protocol for stepwise coordination between tools; status reporting for UI automation steps

### "How can mac-vision have a dedicated persistent UI snapshot state to enable visual diffing for error recovery and claimed-vs-actual verification?"
- **useful because:** Critical for robust UI automation on Mac that can detect failed or drifted states, enabling recovery or re-planning by comparing UI accessibility snapshots over time.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate storage and processing costs
- **security:** UI snapshots may contain sensitive UI labels or structure requiring encryption and access control.
- **missing:** disk-backed UI snapshot store and indexing; API for snapshot retrieval and diff computation

### "How can the mac-vision agent surface and prioritize owner-desired Mac-specific tasks more effectively, improving on the current crude task fact store and DayPlan reads?"
- **useful because:** Allows the mac-vision agent to focus on automation tasks that genuinely matter to the owner, improving responsiveness and relevance of Mac UI automation.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low
- **security:** Requires careful handling of private owner data and preferences for task prioritization.
- **missing:** aggregation and extraction of Mac-specific actionable tasks from owner input and memory; prioritization algorithm tuned for Mac automation relevance

### "A trusted, encrypted state sync service between mac-vision on the Mac and the pendant to persist and recover interaction state, including UI snapshot hashes for claimed-vs-actual verification during long workflows."
- **useful because:** Ensures robustness and consistency when resuming interrupted UI automation workflows, across disconnects or device restarts, preventing work duplication or loss of progress.
- **path:** mac-local-agent → pendant
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low to moderate depending on encryption and bandwidth
- **security:** Sensitive UI snapshot hashes and interaction metadata must be encrypted end-to-end. Access control required to prevent interception or misuse.
- **missing:** Encrypted sync protocol between Mac and pendant; Storage and indexing of UI snapshot hashes; Integration with workbench context checkpointing

### "An advanced contextual action recommender that serves mac-vision by suggesting UI automation next steps by reasoning over recent UI state diffs, owner preferences, task priorities, and error conditions."
- **useful because:** Helps mac-vision select meaningful, non-redundant next steps in complex automations by combining UI state awareness with owner context and task urgency, improving efficiency and user satisfaction.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate computational costs
- **security:** Must ensure owner context and preferences are strictly protected. Use access controls and audit logs.
- **missing:** Real-time UI diff computation and contextual embedding; Context-aware action ranking model integration

### "A safety and confirmation management system that dynamically adjusts mac-vision's UI automation permissions and confirmation prompts based on contextual risk assessment and owner preferences, extending into the Mac agent and pendant firmware layers."
- **useful because:** Provides granular, context-aware control and transparency to the owner about which automated UI actions require explicit confirmation, balancing convenience and safety dynamically.
- **path:** mac-local-agent → pendant
- **model tier:** gpt-5.6-luna
- **latency:** real-time to seconds depending on context
- **cost:** moderate
- **security:** Must resist circumvention, securely enforce permission states, and protect privacy.
- **missing:** Dynamic context-aware risk analysis; Cross-surface permission management tooling and protocols


## Changes it proposed to its own stack

### `integration` — Add an integration module that coordinates mac-delegate, mac-run-actions, and mac-vision UI automation. This module acts as an orchestration layer that transforms high-level goals into UI accessibility steps, manages their execution, and reports progress to the workbench context. It handles error recovery using UI snapshot diffs and manages task claiming, checkpointing, and resume on interruptions.
- **owner gets:** This integration enables robust automation of complex multi-step Mac tasks by combining planning, direct system commands, and fine-grained UI automation. It prevents task duplication, lost progress, and reduces errors, making automation trustworthy and usable for real work.
- effort: Medium engineering effort to build the protocol, data model, and API surface for coordination. Requires extension of existing tools and workbench integration.  ·  risk: Bugs or race conditions could cause inconsistent state or unwanted UI interaction. Can be mitigated by staged rollout and extensive testing.
- cost: Mostly server-side compute and state storage affordable within the current system budget.  ·  latency: Adds minor orchestration latency but operates within acceptable real-time bounds for user interaction.
- security: Requires strict action confirmation and audit logging to ensure safety.
- depends on: workbench context APIs; UI snapshot store; mac-vision enabled automation

### `memory` — Introduce a Mac-focused task memory projection that aggregates owner-stated tasks, reminders, and current workbench contexts prioritized for automation by mac-vision. This projection enriches the existing task facts and DayPlan with explicit Mac automation intent, deadlines, and priority scores, surfaced to mac-vision for planning and execution.
- **owner gets:** Enables mac-vision to focus on owner-important Mac tasks rather than generic or unrelated tasks. Helps the owner feel automation is responsive and relevant to their actual work goals on the Mac.
- effort: Low-to-medium engineering effort to aggregate and prioritize existing inputs, add Mac-specific filters, and surface the projection via a dedicated API endpoint.  ·  risk: Incorrect prioritization could cause suboptimal task ordering, mitigated by owner feedback and preference adjustments.
- cost: Low storage and query cost, mostly software processing.  ·  latency: Negligible latency impact.
- security: Requires care to protect private task data and not expose sensitive task details.
- depends on: memory/facts; day-plan; workbench contexts

### `hardware` — Design next-generation pendant hardware with two physical buttons instead of one, giving physical transaction approval (confirmation) separate from conversation start/end. Include a small e-ink display for moment markers and status indication to reduce audio and visual distractions.
- **owner gets:** Physical separation of confirmation button reduces risk of accidental commands; e-ink display provides quiet feedback and richer interaction without waking Mac or using audio. Improves owner control and trust in the system.
- effort: Hardware redesign and firmware updates; medium-long engineering cycle.  ·  risk: Hardware delays and potential increase in device size or power usage; risk mitigated by prototyping and power budgeting.
- cost: Higher hardware cost but justified by improved UX and safety.  ·  latency: No additional latency expected.
- security: Allows more reliable user approval, reducing accidental commands.

### `firmware` — Implement a minimal local state machine in the pendant firmware that tracks interaction phases and confirms physical transaction approvals before forwarding commands to the Mac. This acts as a hardware safety net for critical operations triggered by the AI pendant.
- **owner gets:** Provides a fail-safe physical gate for transaction approval, reducing accidental or unsafe UI interactions triggered by software automation, increasing owner trust and control.
- effort: Moderate firmware development and testing.  ·  risk: Firmware bugs could block or misinterpret approvals; recovery needed via safe fallback.
- cost: Negligible.  ·  latency: Minimal additional latency on command transmission.
- security: Improves security by enforcing physical consent before sensitive actions.
- depends on: pendant hardware with at least one button; mac-vision enabled automation loop


## What it asked for

_Nothing._
