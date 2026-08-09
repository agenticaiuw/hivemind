# Harness derivation — mac-vision — round 243

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Create a unified, prioritized task queue on the Mac that merges owner task facts, calendar/reminders, active workbench contexts, open browser workflows, and editor state into a live actionable list for mac-vision to consume and act on."
- **useful because:** This single capability would turn the mac-vision loop from idle to fully active, by giving it the actual current owner priorities and deadlines across all work contexts on the Mac, including browser and editor. It enables precise autonomous UI actions aligned with what the owner truly wants done.
- **path:** mac-planner → mac-vision → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** 1-3 seconds
- **cost:** Moderate CPU and memory to integrate multiple sources, low network cost as all on Mac or local extension.
- **security:** Aggregating user data from multiple apps requires care; no data leaves user's devices without explicit owner command. Written to local memory controlled by owner.
- **missing:** Dedicated API to read live editor state (e.g. VS Code open file/workflow info); Better workbench context schema for live work claims and progress; Browser extension APIs to actively read open workflows and tab state; Unified ranking and dependency logic for tasks across sources

### "Provide a robust resume and retry protocol for Mac UI workflows, combining claimed vs actual disk state from workbench/contexts with mac-vision hierarchical UI state to enable resumption and verification of interrupted workflows."
- **useful because:** This would close a major gap for long multi-step UI operations on the Mac that might fail or pause. It ensures reliable restart and retry of tasks the mac-vision loop undertakes, improving user trust and automation robustness.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** 3-5 seconds
- **cost:** Moderate CPU and disk state reads, minimal network cost as mostly local state.
- **security:** State data is user local and ephemeral; resuming automated UI input requires trusted execution environment to prevent misuse.
- **missing:** Standardized schema for workbench/contexts progress states; Integration hook between mac-vision UI snapshot and workbench context state; Consistent retry/undo command routing for mac-vision loop

### "Define a protocol for the pendant's single physical button moment marker to send timestamped events with custom payloads to the Mac side, enabling mac-vision to trigger context-aware actions reliably without gesture ambiguity."
- **useful because:** This would optimize the limited physical input interface for the owner, enabling low-latency, reliable, and extensible reaction to button presses on the pendant from mac-vision. It avoids fallback on fragile gesture detection and extends input possibilities without new hardware.
- **path:** pendant → mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** sub-second
- **cost:** Very low CPU and network use, small writes to pendant storage; uses existing button hardware and low-bandwidth radio events.
- **security:** Payloads must be authenticated and validated; button presses are user-intended explicit inputs, minimizing accidental activations; data handling stays local unless owner consents to relay.
- **missing:** Payload format and size limits on s10-l3xe storage; Transport protocol refinement from pendant to Mac; Event dispatch API for mac-vision to subscribe and trigger on marker

### "Enable mac-vision to delegate complex multi-step or ambiguous Mac UI tasks via a mac_delegate API, providing clear progress reporting, undo support, and collaboration with voice and browser extensions for multi-app workflows."
- **useful because:** Many real-world tasks are too complex for short action lists. Delegation to a local planning/execution agent allows robust multi-step workflows with owner review and escape hatches, improving reliability and user trust.
- **path:** mac-vision → mac-planner → unified → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** 5-10 seconds
- **cost:** Moderate CPU and memory on Mac to manage delegation contexts and state; minimal network cost.
- **security:** Multi-app control requires trusted execution; undo and rollback must be robust to avoid disruptive errors; progress reports may expose sensitive state locally but not externally.
- **missing:** mac_delegate API endpoints for delegation lifecycle; Progress and undo state schema for delegated tasks; Cross-surface coordination protocols for voice, browser, and Mac-vision collaboration

### "Create a truly autonomous Mac UI agent workflow system that can plan, execute, verify, recover, and retry any multi-app user workflow on the owner's Mac, including error detection, context recovery from UI and disk state, and user-driven undo/escape hatches."
- **useful because:** The owner currently cannot rely on fully autonomous Mac UI workflows that seamlessly recover from errors and pauses, leaving manual intervention necessary. A robust autonomous workflow system would greatly improve productivity and trust in the AI as a helper.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** 5-10 seconds
- **cost:** Moderate to high CPU and state management on Mac. Mostly local computation.
- **security:** Highly trusted local execution required; UI automation must be safe and reversible. User data stays local unless explicitly shared.
- **missing:** Standardized unified UI and disk state recovery schema; Full mac-vision to Mac task and undo state reconciliation; User-driven interrupt and rollback controls in the UI loop

### "Build a context-aware, event-driven multi-surface task orchestration layer that integrates pendant physical events, Mac UI state, browser sessions, and voice inputs for seamless autonomous task transition and execution."
- **useful because:** The owner cannot currently trigger or transition tasks seamlessly across devices and surfaces using the pendant or voice, resulting in fragmented workflows. This would unify input triggers and task orchestration, enabling fluid transitions and continuity.
- **path:** pendant → mac-vision → browser-extension → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** 1-3 seconds
- **cost:** Moderate CPU and network overhead due to cross-surface event routing.
- **security:** Event stream integrity and authentication is critical. Payloads must be validated and actions authorized. User data stays local unless consented.
- **missing:** Reliable cross-surface event routing and identity federation; Rich event payload formats for pendant button presses; Multi-surface task handoff protocols


## Changes it proposed to its own stack

### `integration` — Create a unified live owner intent and task state API combining memory facts, reminders, active workflows, editor state, and browser workflows into a ranked, prioritized task queue consumable by all surface agents.
- **owner gets:** Currently, task state is fragmented and partial across multiple isolated stores and surfaces, limiting autonomous or assisted task execution by agents. A unified API would enable seamless cross-surface coordination and prioritization aligned to real owner intent.
- effort: High engineering effort to design and implement new data federations and real-time syncing across surfaces.  ·  risk: Data consistency and sync issues, potential privacy concerns requiring owner control and auditability.
- cost: Moderate CPU and memory usage, low network overhead.  ·  latency: Real-time or near real-time updates expected.
- security: High importance on data protection and explicit user consent for sharing across surfaces.


## What it asked for

_Nothing._
