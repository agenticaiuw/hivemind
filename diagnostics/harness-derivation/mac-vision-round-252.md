# Harness derivation — mac-vision — round 252

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to autonomously manage prioritized Mac tasks including complex multi-step workflows and UI interactions."
- **useful because:** Currently, mac-vision has the accessibility permissions and loop enabled but lacks a durable task list and multi-step workflow coordination. A task management capability that integrates live tasks, a priority queue, and UI control would allow the pendant to effectively delegate and execute complex activities, enhancing the owner's productivity and reducing manual intervention.
- **path:** mac → pendant → relay → browser
- **model tier:** realtime
- **latency:** seconds to act on UI changes and task updates
- **cost:** medium, dominated by state management and UI interaction models
- **security:** Needs to strictly respect user's automation preferences and permissions; only perform actions that are clearly authorized by owner; provide undo and prompts for high-impact actions.
- **missing:** Durable mac task list accessible to mac-vision; Join of task state between UI and execution context; UI state verification against receipts to prevent unwanted or failed actions; Multi-step workflow persistence and resumption

### "Provide seamless integration of the accessibility-based mac-vision UI automation loop with error detection and rollback capabilities."
- **useful because:** Mitigates risks of accidental or failed UI interactions by allowing the system to detect when an action fails or does not have the expected effect, and automatically rollback or notify the owner. Improves trust in full autonomous control of the Mac UI.
- **path:** mac
- **model tier:** realtime
- **latency:** milliseconds to a few seconds per interaction
- **cost:** low to medium, mainly for checks and rollback logic
- **security:** Rollback only authorized actions, never bypass user confirmation on destructive steps, keep audit trail for transparency.
- **missing:** UI state verification combined with action receipts; Rollback mechanism integrated with mac-run actions or equivalent; Undo stack for UI actions

### "Create a dynamic prioritization and notification system that pulls the owner's current active tasks and preferences to present the highest urgency Mac tasks via the pendant."
- **useful because:** The owner can keep focus on the most important work without manually checking multiple task sources. The system actively surfaces what matters right now based on current task facts, calendar/reminder integration, and owner's stated preferences.
- **path:** pendent → mac → relay
- **model tier:** background
- **latency:** seconds to minutes between task updates and notification
- **cost:** low, mainly data aggregation and lightweight model inference
- **security:** Ensure notifications respect owner's privacy and do not leak task info beyond pendant display, avoid flooding with too many alerts.
- **missing:** Task fact prioritization beyond static expiration; Cross-surface data synchronization for tasks and preferences; Smart notification control based on owner's interruption policy

### "Introduce a verification step after each mac-vision UI action where the agent confirms with the owner if the performed action matched their intent before proceeding with any follow-up."
- **useful because:** Reduces the risk of automation errors causing unwanted changes or confusion by ensuring each impactful action is validated by the owner. Improves trust and acceptance of autonomous Mac UI control from the owner’s perspective.
- **path:** mac → pendant
- **model tier:** realtime
- **latency:** seconds per confirmation interaction
- **cost:** low to medium, mainly on interaction and user input model
- **security:** Only display relevant action summaries, ensure confirmations are secure and cannot be spoofed or bypassed, respect owner's final decision strictly.
- **missing:** UI action summaries in natural language; User confirmation interface on pendant or Mac; Integration with mac-vision control loop

### "Create an integrated mac-vision agent capability to maintain a real-time, durable, and owner-modifiable prioritized Mac task queue that dynamically merges owner-stated task facts, reminders, and workflow contexts."
- **useful because:** The owner currently can see tasks from disparate sources but cannot manage or act on a unified, prioritized list that reflects real-time changes and integration with UI automation efforts. This queue would empower mac-vision to autonomously select, act on, and report task progress reliably and transparently.
- **path:** mac → pendant → relay
- **model tier:** realtime
- **latency:** seconds for task selection and update
- **cost:** medium, due to state syncing and task merge models
- **security:** Owner control is paramount: tasks are modifiable only by owner or trusted agents; audit history kept; no action without confirmation on impactful operations.
- **missing:** Durable task queue store accessible to mac-vision; Cross-surface synchronization of task facts; Task merge model combining facts, reminders, and workflows; Owner task modification interfaces

### "Develop a robust UI state verification and rollback subsystem integrated with mac-vision's accessibility-based UI automation loop."
- **useful because:** This capability would automatically detect when a UI action has failed or diverged from expected state, triggering rollback or recovery steps to avoid cascading errors or undesired side-effects, thus making the agent safer and trustworthy for autonomous Mac control.
- **path:** mac
- **model tier:** realtime
- **latency:** milliseconds to seconds per UI action
- **cost:** medium, driven by verification models and rollback logic complexity
- **security:** Rollback restricted to authorized reversible actions only; explicit user confirmation required for destructive or irreversible changes; audit trails maintained.
- **missing:** UI verification algorithms comparing expected vs. actual UI state; Rollback execution path in the mac-vision control loop; Undo stack management for reversible actions; Integration with job receipts and workbench contexts

### "Enable a secure user confirmation interface for mac-vision UI actions involving significant changes, accessible on pendant and Mac, with natural language summaries."
- **useful because:** This provides the owner with control over impactful automated UI actions by requiring explicit confirmation or rejection before proceeding, building trust and preventing unintentional disruptions.
- **path:** mac → pendant
- **model tier:** realtime
- **latency:** seconds per interaction
- **cost:** low to medium, depending on interaction complexity
- **security:** Ensure confirmation requests are accurate and cannot be forged or bypassed; respect owner decisions uncompromisingly; keep interaction logs for audit.
- **missing:** Summarization ability to generate natural language UI action descriptions; User interaction handling on pendant UI and Mac; Integration with mac-vision control loop and dispatcher

### "Implement an advanced multi-step workflow persistence and resumption framework integrated with mac-vision UI automation to allow durable tracking, pausing, and continuation of complex delegated Mac tasks."
- **useful because:** This would let the owner delegate sophisticated workflows that mac-vision can execute step-by-step while preserving state and progress across interruptions or restarts, making autonomous Mac control practical for real-world use.
- **path:** mac → pendant → relay
- **model tier:** realtime
- **latency:** seconds to resume and checkpoint state
- **cost:** medium to high due to state management complexity
- **security:** Workflows must be owner-authorized before execution; sensitive data in workflow context is encrypted and access-controlled; strict audit trail of execution and interruptions.
- **missing:** Persistent workflow context store accessible to mac-vision; State checkpointing and recall in UI automation loop; Interruption detection and automated resumption logic; Integration with user task list and confirmation subsystem


## What it asked for

_Nothing._
