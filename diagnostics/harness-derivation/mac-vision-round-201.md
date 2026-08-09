# Harness derivation — mac-vision — round 201

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Give me a fully integrated, safe, multi-step Mac UI control capability that uses the accessibility API driven vision loop, linked to my live task management and multi-device workflows."
- **useful because:** Today I have no safe, traceable, undoable way to plan and execute multi-step UI interactions on my Mac via accessibility. This capability would allow me to automate complex workflows safely without focus theft or screen recording, seamlessly integrated with my tasks and coordination with other devices in my AI hive mind.
- **path:** mac-vision → unified → relay-realtime → pendant
- **model tier:** background
- **latency:** completion and validation within a few seconds but multi-step runs can take longer with interactive waits
- **cost:** API cost dominated by plan validation and execution steps; model calls for step planning and context reasoning; minimal HTTP overhead for coordination
- **security:** Accessibility API control is powerful and potentially destructive; requires owner consent and well-verified undo and confirmation flows; task routing must respect owner's destructive action preferences.
- **missing:** A fully specified vision loop planning and control API with step validation and safe execution.; A task intake and routing system for the Mac-vision agent that reliably routes owner intentions to this loop or other tools.; A multi-surface coordination API that supports workflow handoff, state persistence, and restartability.

### "A context-aware, prioritized Mac task list that automatically updates based on my live reminders, scheduled routines, and owner-stated task facts, presented to mac-vision for continuous workflow automation."
- **useful because:** Today, mac-vision has no direct input task list and cannot autonomously determine the highest priority or next action to take on the Mac. This capability would allow seamless, adaptive automation driven by actual owner priorities and schedules, reducing manual direction and enabling proactive support.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** Updated every few minutes or on demand; real-time responsiveness not required.
- **cost:** Minimal API cost, mostly local filtering and some reasoning calls to maintain priority rank.
- **security:** Maintains owner privacy by consolidating task preferences and facts locally; no external sharing without owner consent.
- **missing:** A joined system that continually aggregates reminders, routines, and owner facts into a dynamically ranked prioritized list viewable by mac-vision.; APIs for mac-vision to consume this prioritized task list.; Possibly UI or voice interfaces for owner to adjust priority or add emergency tasks.

### "A multi-device workflow coordination capability that allows a seamless handoff of interrupted or long-running workflows across Mac, pendant, and relay, with state persistence, restartability, and joint progress visibility."
- **useful because:** Currently, workflows spanning multiple devices in the AI hive mind cannot be reliably paused, handed off, or resumed by another device or agent. This capability would enable continuous, smooth multi-surface automation, leveraging each device's unique strengths without work loss or duplication.
- **path:** mac-vision → pendant → relay-realtime → unified
- **model tier:** background
- **latency:** Supports asynchronous, durable state saving and progress reporting; no strict low-latency requirement.
- **cost:** Moderate API cost for state serialization, storage, retrieval, and reasoning about workflow progress and handoff logic.
- **security:** Requires careful control over workflow state to avoid data leakage or unauthorized access; owner consent and encryption of persisted state recommended.
- **missing:** A shared durable workflow/workbench context API accessible by all surfaces.; Resume and handoff mechanisms to continue interrupted workflows on different devices.; Unified progress and state views across all agents in the hive mind.

### "A logging and monitoring system for Mac-vision that records all UI interaction plans, their validation results, execution outcomes, and provides owner-accessible history with undo and forensics capabilities."
- **useful because:** Owners have no visibility into what Mac-vision did on their Mac or any way to audit or undo multi-step UI workflows. This system would increase transparency, trust, and provide safety nets for recovery from errors or undesired actions.
- **path:** mac-vision → unified → mac-planner
- **model tier:** background
- **latency:** Logs and history queries updated asynchronously; no latency constraints.
- **cost:** Low to moderate storage and processing costs for logs; minor API overhead.
- **security:** Logs contain sensitive control data; encryption and access control are essential. Owner must explicitly authorize any sharing of logs.
- **missing:** A dedicated logging store for UI interaction plans, validation, and execution.; UI or voice interfaces for owner to view and manage undo history.; Integration hooks from the vision loop and mac_run_actions to report outcomes.


## Changes it proposed to its own stack

### `interaction` — Implement a formal typed action broker and policy layer between Mac-vision and the underlying mac_run_actions, mac_delegate, and browser_run_actions. This would classify actions as readonly, reversible, or destructive and enable safety gating, logging, and confirmation on mutations.
- **owner gets:** Currently Mac-vision runs actions with minimal gating or classification. A typed broker would prevent accidental destructive actions, enable safer undo, and improve trustworthiness and observability for Mac control.
- effort: Medium development and integration work, including defining action types, gating rules, and UI/voice confirmation flows.  ·  risk: Incorrect classification could block needed actions or allow unsafe ones. Mitigation via thorough testing and owner override.
- cost: Low; mostly local logic and some user prompt costs for confirmations.  ·  latency: Minimal impact on command execution latency.
- security: Improves security posture by enforcing intent on mutations.
- depends on: Capability for full reversible mac-vision loop; Task intake and routing system for Mac-vision


## What it asked for

_Nothing._
