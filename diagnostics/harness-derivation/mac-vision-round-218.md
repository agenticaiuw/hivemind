# Harness derivation — mac-vision — round 218

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I want a fully autonomous mac-vision agent that reads the owner's prioritized task facts and day plan, derives detailed multi-step GUI workflows, and performs them via the accessibility tree without owner intervention."
- **useful because:** This enables true autonomous Mac UI control for complex, ongoing tasks aligned with owner's priorities and preferences, fulfilling the promise of hands-free Mac automation.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** minutes to hours for complex workflows, subsecond to seconds per UI step
- **cost:** primarily model inference in the cloud plus local validation, negligible local compute
- **security:** Full trusted control of Mac UI requires strict owner consent and visibility; must ensure undo and failure recovery, with logging and owner's manual override.
- **missing:** task prioritization and ranking that integrates owner facts and reminders into actionable UI tasks; accessibility tree integration into workbench context state for state reconciliation; automatic multi-step UI plan generation and execution based on task facts

### "I want a reconciliation system that compares claimed Mac UI state in workbench contexts with the live accessibility tree snapshot to detect and recover from workflow failures automatically."
- **useful because:** This allows resilient autonomous Mac UI workflows that can detect if UI is out of sync and auto-recover or retry steps without owner intervention, improving trust and reliability.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes per reconciliation cycle
- **cost:** local and cloud model costs plus access to accessibility snapshots
- **security:** Needs secure handling of live UI data; reconciling claimed vs actual state requires careful state management and possible owner override.
- **missing:** API or mechanism to attach accessibility tree snapshots into workbench context state; UI state diff and reconciliation logic

### "I want a new prioritized task creation and ranking interface where the owner can input, rank, and modify Mac UI automation tasks that mac-vision will act on."
- **useful because:** This gives the owner direct control over what mac-vision does on their Mac, letting them create prioritized actionable tasks and enabling more useful autonomous automation.
- **path:** mac-planner → mac-vision → unified
- **model tier:** gpt-5.6-luna
- **latency:** interactive latency for task updates and ranking
- **cost:** small relative to normal usage; mainly local storage and model calls
- **security:** Owner input and task data must be private and editable only by owner, with full audit trail.
- **missing:** owner-friendly UI for task creation and ranking; memory store support for expressing task priorities and dependencies; integration with mac-vision's accessibility loop


## Changes it proposed to its own stack

### `integration` — Add integration glue that converts kind:task facts and day-plan reminders into a mac-vision task queue that the mac-vision accessibility loop consumes as actionable prioritized UI workflows.
- **owner gets:** This enables the new autonomous mac-vision UI control loop to get real owner-defined prioritized work from the existing memory facts and reminders, turning passive data into actionable tasks.
- effort: medium complexity software integration requiring scheme design, API design, and UI flow coordination.  ·  risk: moderate risk of mismatch between abstract tasks and concrete UI steps; requires extensive testing and fallback.
- cost: software engineering effort mostly; negligible hardware or runtime cost.  ·  latency: adds processing time in the mac-vision orchestration stage, expected subsecond to seconds.
- security: requires careful permission and privacy handling but uses existing permissions and data.
- depends on: mac-vision loop enabled; mac planning surface able to read facts and day plan

### `integration` — Create a reconciliation and validation layer that ingests live accessibility tree snapshots alongside workbench context state to detect desyncs and recovery failures in multi-agent Mac UI workflows, signaling faults and auto-initiating retries or rollbacks.
- **owner gets:** This improvement makes autonomous Mac UI workflows more robust and transparent, reducing frustration from failed or stuck states and increasing trust in automation.
- effort: non-trivial, requires state diff tooling, error handling, retry logic, and UI state storage extension.  ·  risk: possible false positives or misdetections; requires owner override path.
- cost: software engineering effort; minimal runtime impact; cloud model inference cost for decision logic.  ·  latency: seconds to minutes per reconciliation cycle, depending on complexity.
- security: sensitive UI state data handling requires strict access control and audit trail.
- depends on: accessibility snapshots persistently stored; workbench context APIs with state extension

### `interaction` — Build an owner-facing UI on mac-planner surface that enables creation, ranking, and management of mac-vision actionable UI tasks derived from task facts and reminders, with real-time syncing and status updates from the vision loop execution.
- **owner gets:** Owners can directly specify what mac-vision should do on their Mac, control priorities, and monitor progress, making autonomous Mac UI control transparent, manageable, and trustable.
- effort: medium, involves UI/UX design, backend integration, and real-time state sync with mac-vision loop.  ·  risk: UI complexity risks usability issues; data sync issues can cause misinformation.
- cost: mainly developer time and runtime communication costs.  ·  latency: interactive latency expected under 1 second.
- security: owner task privacy, authentication, and audit logging needed.
- depends on: memory facts API; day plan API; mac-vision loop status APIs


## What it asked for

_Nothing._
