# Harness derivation — mac-vision — round 246

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I want a unified Mac task management capability that shows me a ranked list of what I want done on my Mac, mixing Apple Reminders, calendar, and my agent-stated tasks, allowing me to select and confirm work, and lets the mac-vision agent execute those tasks robustly with progress and undo support."
- **useful because:** The owner lacks a unified, prioritized view of their Mac-related work, limiting productivity. This capability integrates scattered sources of tasks and the agent's understanding into one actionable list with confirmations and feedback, improving interaction clarity and effectiveness.
- **path:** mac-local-agent → pendant → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** interactive, seconds-level
- **cost:** moderate, mostly prompt tokens and CLI action cost
- **security:** needs full mac control permissions, careful with destructive commands, owner confirmation required for critical actions
- **missing:** UI integration for presenting and confirming the ranked task list; workbench context and vision-loop integration to track UI vs claimed state; undo and error recovery mechanisms for mac_run_actions and mac_delegate steps

### "I want robust state reconciliation between the accessible UI controls on the Mac (via the accessibility tree) and the claimed multi-step workbench workflow state, so mac-vision can verify what is actually done on screen versus what the system thinks it did, for safe and reliable stepwise execution and resume."
- **useful because:** This prevents repeated or skipped steps in multi-step workflows due to desynchronization between the system's claimed progress and the real UI state on screen. It is critical for safe UI automation with feedback and error handling.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds for state verification
- **cost:** small - mostly prompt tokens and incremental state checks
- **security:** Requires accessibility read permissions, no destructive permissions needed for reading state only.
- **missing:** code to join vision-loop accessibility tree snapshots with workbench context state; APIs to compare UI control states with expected state in workflows; UI or voice feedback to owner when this desynchronization occurs

### "I want a progress and feedback mechanism on the pendant and Mac that narrates what mac-vision is doing during UI tasks, allows the owner to abort or request more detail, and confirms task success or failure with a short spoken update after each step."
- **useful because:** When automated UI actions happen on the Mac, the owner needs real-time feedback to trust the agent, intervene if needed, or know when work completes or errors occur. This improves transparency, control, and safety for the owner.
- **path:** pendant → mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** realtime, sub-second to seconds per update
- **cost:** small, limited mostly to message generation and minimal audio/LED signals
- **security:** Requires permissions to output audio or LED feedback on the pendant, plus agent control of mac-vision to pause/cancel work safely.
- **missing:** audio TTS output integration with pendant speaker; UI for feedback and abort on Mac; Message protocol between mac-vision and pendant feedback agents

### "I want a real-time UI element state monitoring skill living on the pendant firmware that tracks and logs key UI control states on the Mac via accessibility data pushed through the Mac agent, enabling the pendant to signal the owner on local context changes and UI anomalies even if the Mac is unresponsive or disconnected."
- **useful because:** This distributed awareness extends the owner's situational knowledge beyond Mac connectivity and reduces reliance on cloud or Mac being available, improving offline safety and situational awareness.
- **path:** pendant → mac-local-agent
- **model tier:** embedded
- **latency:** milliseconds to seconds
- **cost:** negligible processing on pendant; moderate communication over USB
- **security:** Requires secure channel from Mac to pendant for UI state updates and privacy protections for sensitive UI states.
- **missing:** firmware and protocol code on pendant for receiving and storing UI state changes; mac agent code to push compact accessibility state diffs to the pendant

### "I want a persistent, unified Mac task inbox that intelligently synthesizes owner-stated tasks, Apple Reminders, calendar events, and multi-surface agent intents into a dynamically ranked, context-aware queue that drives mac-vision's workload with owner-adjustable priority and clear status indicators."
- **useful because:** Currently, the system has no centralized task repository or inbox that combines all work items relevant to the owner on their Mac into one actionable list. This unification enables precise prioritization, tracking, and owner control to truly focus mac-vision's automation on what matters most now.
- **path:** mac-local-agent → pendant → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate, mainly prompt engineering and memory fetches
- **security:** Requires careful permission handling for privacy of calendar, reminders, and agent data; owner confirmation gate recommended.
- **missing:** Data fusion engine combining multiple disparate task sources; UI and voice affordances for owner adjustment and progress feedback; Storage and conflict resolution for multi-source task state

### "I want a fluent conversational Mac interaction skill that uses the full accessibility tree and internal state to intelligently parse ambiguous requests, clarify ambiguities interactively, execute multi-step actions or workflows with undo support, and summarize progress in natural language for the owner."
- **useful because:** The owner currently cannot engage in flexible, natural-language conversations to control the Mac UI beyond isolated short actions. A fluent conversation skill enables much richer, more resilient human-computer interaction with robust error handling and transparency.
- **path:** mac-local-agent → pendant
- **model tier:** gpt-5.6-luna
- **latency:** interactive, seconds to low tens of seconds
- **cost:** high, dominated by large memory and context handling
- **security:** Needs very careful control over destructive commands and data privacy; undo and confirm gates mandatory.
- **missing:** Dialogue manager tightly integrated with accessibility state; Deep semantic parsing and reference resolution across UI state; Undo stack and rollback handlers; Natural language progress summarization modules


## Changes it proposed to its own stack

### `hardware` — Design and produce a new wearable pendant device with two physical buttons instead of one, enabling one button strictly as a dedicated physical transaction approval latch separate from conversation controls. Add a small slider or toggle switch for mode selection (e.g., standby, conversation, task confirmation). Increase on-device RAM to at least 512 KB to support local ML and gesture recognition including multiple press types (single, double, long press). Expand storage to include reliable non-volatile memory beyond the microSD for persistent interaction logs and quick local replay or undo buffers.
- **owner gets:** Having a dedicated physical button for approvals separate from conversation starts allows more reliable transaction confirmation gestures without interfering with the main conversation button. The additional mode switch gives better physical UI control for task state. Increased RAM and storage enable richer local intelligence and reliability improvements with less cloud dependence.
- effort: High, involves hardware design, firmware development, and manufacturing revisions.  ·  risk: Potentially delays product delivery, increased device cost and power consumption, may require software and firmware rework.
- cost: Significant hardware component and manufacturing cost increase, slightly higher power draw.  ·  latency: Zero - hardware only.
- security: Improves security by dedicated approval channel; increases attack surface due to more components.

### `model-routing` — Implement a context-aware model routing system that dynamically selects specialized smaller and focused models (e.g., UI state parsing, action planning, dialogue, error recovery) alongside a large generalist for Mac vision tasks, optimizing latency, cost, and reliability.
- **owner gets:** Currently, one large model handles all Mac UI control and conversation tasks, leading to slower responses and higher costs. Specialized model routing improves user experience by delivering faster and more precise responses adapted to task stages.
- effort: Moderate system integration and testing.  ·  risk: Increased complexity could cause routing errors.
- cost: Reduced overall API costs due to tiered model use.  ·  latency: Faster response times in many cases.
- security: No direct impact.
- depends on: mac-vision


## What it asked for

_Nothing._
