# Harness derivation — mac-vision — round 198

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have the pendant and Mac agent maintain a synchronized UI state ledger that records every meaningful accessibility tree snapshot and UI action completion on the Mac, with rollback and gap-detection for resumed multi-step workflows."
- **useful because:** This lets the owner confidently resume interrupted multi-step UI workflows, with verification of actual Mac UI state against expected state, avoiding UI loss or errors.
- **path:** mac-planner → mac-vision → pendant
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** low model cost, moderate server storage
- **security:** This replicates some UI state logs off-device; requires strong encryption and owner control.
- **missing:** backend ledger to record UI state snapshots and reconcile against workbench job state; firmware signal pass-through to pendant for UI state confirmations; integration with mac_run_actions and mac_delegate for expanded state validation

### "An owner-facing Mac task prioritization and actionable briefing system that merges live reminders, owner facts, routines, and active jobs into a ranked actionable list guiding both manual and automated Mac work."
- **useful because:** Currently the owner task list is fragmented; such a system provides a single reliable prioritized queue of what the owner wants done on the Mac, improving productivity and focus.
- **path:** mac-planner → mac-vision → pendant
- **model tier:** background
- **latency:** under a second to update briefing
- **cost:** very low model cost
- **security:** All data remains local to owner; no external data exposure needed.
- **missing:** aggregator service to combine Apple Reminders, facts store, and routines; UI and voice briefing integration; task ranking algorithms and feedback from owner

### "Enable smart UI error recovery for multi-step Mac workflows by detecting UI state mismatches through accessibility tree comparisons and triggering corrective navigation or restoration actions dynamically."
- **useful because:** This allows the mac-vision agent to recover reliably from UI desynchronization or unexpected changes during automation, reducing failed task runs and improving robustness.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** moderate model cost for state analysis
- **security:** Local UI state only, no external data exposure. Must safeguard against state spoofing.
- **missing:** UX pattern library for error corrections; access to historical UI snapshots for state diffing; integration with mac_run_actions and mac_delegate for recovery invocation

### "Provide a persistent, encrypted local log on the Mac that tracks every UI interaction initiated by mac-vision or mac-delegate with timestamps, parameters, and success/failure status, accessible by the owner for audit and manual replay."
- **useful because:** Increases transparency and trust for the owner in automated Mac control by enabling post-mortem review and manual intervention to retry or undo UI actions.
- **path:** mac-planner → mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** low storage and compute cost
- **security:** Log data contains UI operation details; must be encrypted and access-controlled.
- **missing:** UI action interception and logging hooks; encrypted local storage for logs; UI action replay mechanisms

### "A capability for mac-vision to intelligently compose and send emails by combining lightweight UI automation with context-aware draft generation, respecting the owner's preference for confirmation before sending."
- **useful because:** Email is a common task but requires confirmation to avoid mistakes. This would automate composing emails based on context but require owner approval before final sending, improving productivity safely.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate model cost
- **security:** Email content could be sensitive; requires strict privacy and confirmed sending.
- **missing:** context-aware draft generation model; UI automation integration with mail client; confirmation workflow integrated with pendant or voice


## Changes it proposed to its own stack

### `integration` — Add a reusable typed confirmation broker that integrates with mac_run_actions and mac_delegate to require owner approval via pendant button or voice before executing destructive or ambiguous UI automation steps.
- **owner gets:** Increases safety and trust in automation on the Mac by preventing unwanted destructive actions without explicit owner approval.
- effort: Medium  ·  risk: Low to medium; could delay actions if owner unavailable; mitigated by configurable timeouts.
- cost: Low for compute and negligible hardware cost  ·  latency: Introduces minor delay awaiting confirmation
- security: Handles physical button signals and voice confirmation securely to avoid spoofing.
- depends on: pendant button input; voice input and recognition; mac_run_actions and mac_delegate integration


## What it asked for

_Nothing._
