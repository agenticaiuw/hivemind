# Harness derivation — mac-vision — round 232

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a task queue and prioritization system dedicated to mac-vision for handling multi-step Mac UI interaction tasks"
- **useful because:** Currently mac-vision has no structured, durable backlog or priority queue of UI tasks it can consume. This blocks effective autonomous operation and proper work management.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low per invocation, as it mainly manages task metadata and priority calculations
- **security:** Task inputs must be owner-approved to avoid unsafe automation; strict separation from other task lists to avoid confusion.
- **missing:** A dedicated persistent task queue store for mac-vision; Integration with existing memory facts and day plan; User interfaces to add, view, and prioritize tasks for mac-vision

### "Implement safe rollback and recovery mechanisms for mac-vision UI automation failures"
- **useful because:** UI automation via mac-vision can cause unintended side effects or partial completions. Rollback and recovery are required to maintain system integrity and user trust.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes for recovery
- **cost:** moderate due to state capture, verification, and rollback complexity
- **security:** Rollback must be secure and not allow execution of arbitrary code or unsafe states.
- **missing:** State snapshot and diff tools for Mac UI state; Replay capabilities for reversing automation steps; Verification and confirmation steps for rollback triggers

### "Create a user confirmation and override interface for mac-vision automation sequences"
- **useful because:** To prevent disruptive or unsafe UI actions, the owner must have real-time control to approve or stop automation mid-sequence.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds interaction time
- **cost:** low, mostly messaging and UI management
- **security:** Interface must be secure from spoofing and unauthorized access.
- **missing:** Real-time messaging and notification system; User interface components on multiple surfaces; Integration with mac-vision state and automation control


## What it asked for

_Nothing._
