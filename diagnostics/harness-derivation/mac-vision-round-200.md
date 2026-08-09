# Harness derivation — mac-vision — round 200

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Maintain an actively updated prioritized Mac task and goal list integrated from the owner's live memory facts and day plan, accessible to all Mac-side agents for task-driven actions and planning."
- **useful because:** The owner currently has no coherent, prioritized task list for Mac work that agents can reliably reference and act upon. This capability would enable agents like mac-vision and mac-delegate to work from a live prioritized queue of the owner’s actual goals and tasks, enhancing relevance, efficiency, and coordination across multi-step workflows.
- **path:** mac-planner → mac-vision → mac-delegate → unified
- **model tier:** background
- **latency:** seconds for updates, near instantaneous for reads
- **cost:** low API cost for reads, medium for updates due to fact sync
- **security:** Strict owner data access control and explicit opt-in required. The list contains potentially sensitive priorities.
- **missing:** An integrated Mac-side durable prioritized task store derived from memory facts and day plan reminders; A live subscription or polling mechanism for agents to get updates in real time; A mapping and ranking algorithm sensitive to deadlines, priorities, and context for meaningful sorting; Basic UI and API surface to query, annotate, and adjust task priorities

### "Add a state verification and UI alignment validation capability for delegated multi-step Mac workflows, enabling confirmation and error detection of each UI interaction step within mac_delegate tasks."
- **useful because:** Delegated multi-step workflows on the Mac currently lack real-time feedback about whether each step was correctly reached and completed on screen. This leads to silent failures and unreliable task completion. A state verification layer comparing expected vs observed UI state enables recovery strategies and increases trust in full mission workflows.
- **path:** mac-vision → mac-delegate → mac-planner
- **model tier:** background
- **latency:** seconds per step validation
- **cost:** medium for UI assessment and state management
- **security:** Requires ongoing UI accessibility data access and storage. Sensitive to visual state and application context, needing encryption and access control.
- **missing:** A state snapshot and diff mechanism for claiming and validating partial UI states from the mac-vision loop; A UI state alignment protocol integrated with mac_delegate execution steps; A way to report, annotate, and act on state discrepancies during workflow execution

### "Provide deep app interaction profiles and shortcut mapping for the owner’s frequently used applications on the Mac, to enable high-confidence UI automation and task-specific prompting."
- **useful because:** Currently, Mac UI automation lacks contextual knowledge about app-specific UI flow, shortcut keys, menu structure, and task-relevant control locations. This knowledge would allow more precise, confident, and efficient automation and multi-step task completion, reducing errors and awkward workarounds.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to fetch or update profiles, milliseconds in action planning
- **cost:** low to medium depending on profile depth
- **security:** Requires storing potentially sensitive usage patterns and app-specific configurations, requiring strict access controls and opt-in.
- **missing:** A system to extract, curate, and maintain deep interaction models for frequently used Mac applications; A structured API to query and update these profiles during task planning and execution; Possibly a crowd-sourced or learning-enhanced approach to build profiles from owner feedback

### "Enable a comprehensive cross-surface confirmation and undo management system combining Mac UI state verification, multi-step delegation receipt tracking, and pendant physical transaction approval gestures."
- **useful because:** The owner can confidently control the Mac through delegated multi-step workflows with guaranteed correctness and easy recovery options, combining software state validation and a physical pendant confirmation to avoid accidental destructive actions or failures.
- **path:** mac-vision → mac-delegate → relay-realtime → pendant
- **model tier:** realtime
- **latency:** instantaneous to seconds depending on step
- **cost:** medium due to combined state verification, ledger, and pendant interaction event coverage.
- **security:** Highly sensitive: requires secure handling of transaction approval and undo records, encrypted transmission between surfaces, and strict confirmation policies.
- **missing:** A unified transaction management layer linking mac_delegate receipts with mac-vision's UI state diffs and pendant button approvals; A persistent multi-surface ledger storing undo checkpoints and approval states; An event-driven workflow for incremental confirmation steps with undo option


## Changes it proposed to its own stack

### `integration` — Integrate the Mac multi-step delegation workflow with the pendant's physical buttons and gesture inputs to allow the owner to start, pause, resume, or abort delegated Mac tasks hands-free, confirmed by pendant feedback.
- **owner gets:** This would allow seamless, low-effort control over complex Mac workflows through the pendant device, enhancing convenience and safety by enabling flow control without switching focus or using a keyboard/mouse.
- effort: medium engineering effort involving Mac-agent, pendant device firmware and the relay integration layer.  ·  risk: Increased surface for mis-triggered commands or state desync if button integration is unreliable; mitigated by confirmation and safety timeouts.
- cost: small additional API calls and pendant firmware logic; negligible hardware cost change.  ·  latency: near instant as button events happen live.
- security: Requires authentication and authorization checks to ensure only owner commands affect workflow state, protects against accidental command triggering.
- depends on: mac_delegate multi-step execution capability; pendant button event handling firmware; relay event routing for commands


## What it asked for

_Nothing._
## Its own summary

Proposed five new capabilities addressing prioritized Mac task list integration, UI state verification for delegation, deep app interaction profiles, pendant-integrated workflow control, and cross-surface confirmation and undo systems.

**Biggest unknown:** How to efficiently and securely build and maintain UI state validation and deep app interaction profiles at scale for reliable multi-step delegation.

