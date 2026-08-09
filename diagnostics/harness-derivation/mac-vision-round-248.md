# Harness derivation — mac-vision — round 248

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Can the system provide me with a live, automatically prioritized, actionable Mac task list synthesizing my Apple Reminders, owner stated task facts, and daily routines, scoped and updated live specifically for the Mac surface?"
- **useful because:** Currently, there is no durable prioritized task list usable by the mac-vision agent to know what the owner wants done on the Mac. Apple Reminders and owner facts hold tasks, but they are disconnected and not synthesized. Such a capability would allow mac-vision to always have a current, ranked task list of real owner intentions for direct execution or delegation, greatly improving usefulness and reducing confusion.
- **path:** mac → pendant → relay
- **model tier:** background
- **latency:** seconds
- **cost:** low per invocation due to caching and incremental updates
- **security:** Task details are owner-private data, so secure local storage and transmission is required. Only owner-authorized surfaces should access the synthesized list.
- **missing:** No existing route or tool explicitly synthesizes and ranks tasks for the mac at present.

### "Enable mac-vision to record reversible progress on multi-step mac_delegate workflows and mac_run_actions, including marking subtasks as completed and undoing actions, with full UI state reconciliation to maintain accurate task status."
- **useful because:** Currently, the system cannot track partial completion or reverse actions robustly for multi-step or single-step computer tasks. This impedes reliable automation and frustrates owner trust when progress is lost or partial work cannot be undone. Tracking and reversible progress markers with UI state checks improve confidence and automation utility.
- **path:** mac
- **model tier:** background
- **latency:** seconds per progress update
- **cost:** moderate due to state persistence and reconciliation checking
- **security:** Progress and reversals involve sensitive task and UI state; careful access control and encryption are needed.
- **missing:** API endpoints or tools to record action progress, mark subtasks done, undo actions, and reconcile UI state during mac_delegate or mac_run_actions.

### "An AI-driven mac-vision task manager that continuously synthesizes, prioritizes, and updates an actionable, owner-specific Mac task list from native Apple Reminders, owner-stated task facts, and daily routines, with seamless integration to mac_run_actions and mac_delegate for direct execution and delegation."
- **useful because:** Currently, no unified Mac task list exists combining all relevant owner tasks and priorities, making mac-vision less effective and forcing manual task curation. This would enable continuous intelligent task prioritization and automated computer action or delegation, reducing owner effort and increasing system relevance.
- **path:** mac → pendant → relay
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** low to moderate, dominated by frequent read of Reminders and owner facts
- **security:** Owner-private task data must be kept secure with strict access controls. Task execution needs explicit owner consent flows for destructive actions.
- **missing:** A live, robust task synthesizer and prioritizer that aggregates and ranks all task sources per owner preference for the Mac.; Seamless, stateful integration between this task list and mac_run_actions/mac_delegate workflows for progress tracking and interruption recovery.

### "Robust mac-vision-driven multi-step task resumption and progress tracking system using workbench contexts and full UI state reconciliation, enabling reliable recovery and continuation of interrupted Mac workflows."
- **useful because:** Current mac-vision workflows often lose progress or have unclear state after interruption, causing rework and errors. Workbench contexts report claimed workflows but lack tight UI state integration or progress tracking. This capability ensures reliable, seamless continuation and reversibility of UI-driven tasks.
- **path:** mac
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** moderate due to state synchronization, reconciliation, and storage
- **security:** Sensitive partial task states and user actions must be secured and access carefully controlled to prevent misuse or data leakage.
- **missing:** API and infrastructure for mac-vision to claim, mark progress, checkpoint, undo, and reconcile UI state for mac_delegate and mac_run_actions workflows.; Real-time UI state capture and comparison to reconcile planned vs actual state during workflows.


## Changes it proposed to its own stack

### `interaction` — Integrate a user-configurable policy engine into mac-vision that decides when to escalate simple actions to multi-step delegated workflows or require explicit owner confirmation, based on action type, risk level, and past user preferences.
- **owner gets:** This empowers the owner with fine-grained control over automation safety and convenience, avoiding over-automation or dangerous actions without consent, while minimizing unnecessary interruptions for safe tasks.
- effort: Moderate complexity requiring changes to mac-vision decision logic and integration with owner preferences storage.  ·  risk: Misconfiguration could cause false positives or negatives in confirmation prompting, mitigated by clear defaults and owner override ability.
- cost: Low, mostly computational for policy evaluation.  ·  latency: Minimal, as decisions happen locally in mac-vision.
- security: Requires secure preference management and prevents unauthorized escalation or bypass of confirmation.
- depends on: current owner preference storage and retrieval capabilities; mac-run-actions and mac_delegate tooling


## What it asked for

### `c24-ym8s` (context) — mac-vision capabilities and best full use cases
- why: To understand the full scope and recommended use cases for the mac-vision agent so I can make effective proposals that leverage its strengths and avoid misusing it.
- would change: I will tailor proposals for mac-vision only to capabilities aligned with its design and limits and propose new integrations and capabilities where gaps exist.

### `c25-b4y8` (context) — mac-vision ui snapshot and workbench contexts
- why: To get live information about the Mac UI structure and ongoing open workflows to enable the mac-vision agent to plan, validate, and track multi-step UI workflows accurately.
- would change: I would plan and execute multi-step mac_delegate workflows with real-time UI state verification and adapt plans based on actual UI context rather than just expected states in workbench contexts.

