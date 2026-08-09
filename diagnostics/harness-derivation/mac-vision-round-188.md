# Harness derivation — mac-vision — round 188

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a prioritized, dynamic task list on the Mac that the agent can read and act on automatically."
- **useful because:** The owner currently has no prioritized Mac task list; the agent cannot autonomously know what most needs doing or create an efficient plan. This unlocks full autonomy for the mac-vision agent to serve the owner efficiently by knowing and adjusting to what the owner wants done next.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds to a minute for planning, real-time only for immediate UI actions
- **cost:** Low per invocation, mostly model and context memory cost
- **security:** Tasks may contain sensitive info; requires secure local storage and owner control over what is shared.
- **missing:** A new persistent task store that agents can both write and read; A task prioritization and dependency model; User interfaces to add, modify, prioritize, and confirm tasks

### "Enable mac-vision computer use loop with a safe, user-trusted onboarding flow for macOS Accessibility permission and action confirmation."
- **useful because:** The mac-vision agent's ability to interact autonomously with the Mac UI is blocked without this permission and onboarding flow. This lets the owner enable and trust the agent to operate safely and reversibly, providing real power and convenience.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** sub-second for action recognition, seconds for onboarding completion
- **cost:** Negligible operational cost; development cost for onboarding flow
- **security:** High sensitivity to permissions; must prevent unauthorized use; requires clear owner consent and audit trails.
- **missing:** A designed guided onboarding UX to request and confirm macOS Accessibility permission for the agent process binary; A typed action policy with safeguards and owner confirmation interaction; Enhancements to mac-vision loop to report blocked steps and disallow fallback to screen pixels; Audit and history of all UI manipulations

### "Create a cooperative orchestration layer among mac-vision, browser-extension, and relay-realtime agents for fluid multi-surface workflows."
- **useful because:** Complex owner tasks often span Mac applications, web browsing, and voice interaction. A cooperative orchestration layer enables seamless handoffs, state sharing, and distributed task execution across devices and surfaces, vastly expanding autonomous capabilities.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → faculty-judgement → faculty-perception
- **model tier:** gpt-5.6-luna
- **latency:** variable from milliseconds to minutes depending on workflow stage
- **cost:** Moderate, depends on complexity and interactions; mostly model and relay API calls
- **security:** Requires secure message passing and shared state protection to prevent leak or spoofing; audit trail needed.
- **missing:** Shared state management and handoff protocols; Event and intent routing infrastructure; Multi-agent workflow coordination and conflict resolution strategies

### "A task understanding and prioritization model that fuses owner-stated tasks with contextual urgency from calendar, email, reminders, and external signals."
- **useful because:** The owner can express tasks as vague natural language or pinned reminders, but does not get a fused, prioritized understanding across sources. This model would rank what matters most now, enabling better agent decisions and owner focus.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds for ranking, real time for a brief
- **cost:** Moderate cost for model context and training on owner context data
- **security:** Tasks and context contain private info; the model must run locally or on secure devices with controlled data flows.
- **missing:** Model training data connecting natural language task descriptions to urgency signals; Integration with calendar, email, reminders APIs and owned fact store; Ranking mechanisms based on deadliness, owner preferences, and dependencies

### "A seamless, persistent cross-device undo/rollback system for Mac UI actions performed by mac-vision or delegated agents."
- **useful because:** The owner can experiment with or rely on autonomous Mac control knowing every UI action can be undone across single or multi-step workflows, increasing trust and recoverability.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Real time for immediate undo feedback.
- **cost:** Low to moderate, mostly state management and UI integration.
- **security:** Undo state must be secured against tampering and privacy leaks; actions must be recorded auditable and reversible without data loss.
- **missing:** Undo state capture and propagation mechanism across agent boundaries; UI action rollback handlers in mac-vision and mac_delegate; User interface to view and select undo points or rollback stages


## What it asked for

_Nothing._
