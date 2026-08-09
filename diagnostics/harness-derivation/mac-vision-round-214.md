# Harness derivation — mac-vision — round 214

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a verified UI state validation feature that compares claimed workbench contexts with the actual current accessibility UI tree state on the Mac. This would uniquely ensure that delegated multi-step Mac workflows are tracked with real UI control presence, reducing errors and drift in automation."
- **useful because:** Currently, the system only knows what it claims to have done or what files it wrote, but not whether the expected UI controls remain on screen as claimed before the next step. This would drastically reduce failure due to UI desynchronization in multi-step delegated tasks, improve reliability and owner trust, and enable higher-confidence automation.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to a few seconds per verification
- **cost:** Low to moderate API cost, dominated by accessibility tree reads; no heavy model cost.
- **security:** Requires ongoing accessibility permission and careful handling of UI state data to avoid leaking sensitive UI content outside the owner’s devices. Does not require screen pixels, only accessibility tree data.
- **missing:** A persistent UI state diff store tied to workbench contexts; Protocols for UI state claim validation and correction feedback loops; Owner UI to view verification reports and intervene

### "Enable full accessibility-driven Mac UI automation loops that run exclusively on accessibility tree data without capturing screen pixels, enabling privacy-preserving, stable, focus-safe, and reliable multi-step Mac workflows that the owner can trust and control."
- **useful because:** Allowing mac-vision full control with accessibility-only feedback means no screen recording is needed, respecting privacy and permissions while enabling powerful automation that integrates with complex Mac apps and systems. It also avoids interference with the user experience by avoiding focus stealing or unexpected clicks.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** milliseconds to seconds per action
- **cost:** Moderate API and compute cost due to complex UI tree analysis and planning
- **security:** Needs very careful permission checks and sandboxing of actions to avoid accidental destructive operations. The owner must grant and optionally revoke accessibility permissions per app or globally to control risk.
- **missing:** Enhanced accessibility event hooks and preflight checks; Policy system for granular consent and safe fallback; Owner override and abort interfaces

### "Create an intelligent Mac surface-only task manager that reads the actual live UI state, macOS Reminders and Calendar, and owner preferences to build a dynamic prioritized task list tailored to what the owner can act on at their Mac right now."
- **useful because:** The owner lacks a reliable, dynamic, machine-read task list specialized for the Mac surface that integrates real UI state with priority and due data. This would improve focus, reduce overwhelm, and increase productivity by presenting only actionable and context-aware tasks. It avoids reliance on incomplete or out-of-sync stores and enhances decision-making.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** up to a few seconds for data aggregation and ranking
- **cost:** Moderate API cost; querying multiple local data sources and scoring tasks; occasional model use for prioritization
- **security:** Sensitive task and calendar data must stay private and encrypted; read-only for non-owner agents unless explicitly permitted
- **missing:** Unified aggregation protocol for task and UI state; Dynamic priority ranking algorithms that include owner preferences; Owner dashboard or voice query interface for task presentation

### "Implement a seamless integration between the pendant button triggers and mac-vision for context-aware moment bookmarking and computer interaction confirmation, enabling the owner to physically signal task states or approvals to the Mac agent with minimal latency."
- **useful because:** Currently, the pendant button has limited use and is mostly associated with audio conversations. Extending it to a robust physical interface for directing mac-vision expands natural owner interaction modes, mitigates accidental or unclear commands, and enables quick context capture or approvals without interrupting the workflow.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** milliseconds to under 1 second for trigger to action handoff
- **cost:** Low API cost; mostly event-driven with occasional short interactions
- **security:** Physical button use must be carefully mapped to prevent accidental destructive actions; edge cases like long presses vs tap must be explicitly managed to avoid confusion or accidental control.
- **missing:** Standardized event protocol for pendant button presses integrated with mac-vision context; Configurable mappings for triggers to precise computer control actions; Owner interface to configure button behavior and confirm actions

### "Develop a multi-tiered Mac UI interaction planner that leverages mac-vision for accessibility-driven real UI control state, mac-planner for workflow planning, and unified for cross-device context, enabling dynamic fallback between accessibility tree and pixel-based control if permissions change or fail."
- **useful because:** This would enable resilient automation that does not break if mac-vision accessibility permission is unavailable, but prioritizes accessibility-first control for privacy and stability when available. It bridges current gaps in capability fallback to maximize up-time for Mac automation.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** sub-second to seconds depending on fallback complexity
- **cost:** Moderate; requires orchestration across surfaces and layered planners.
- **security:** Fallback to pixel-based control potentially leaks screen content and must require explicit owner approval or be heavily sandboxed.
- **missing:** Capability to detect accessibility permission state in real time; Seamless switch-over architecture between control tiers; Fallback pixel-based control capabilities and safeguards


## Changes it proposed to its own stack

### `hardware` — Add a second programmable user button and an additional LED indicator to the pendant hardware to increase physical interaction bandwidth and enable user-configurable quick actions with visual feedback, independent of the existing mic activation button.
- **owner gets:** This would allow richer use of physical triggers for different contexts, approvals, or quick commands to mac-vision and other agents, reducing reliance on ambiguous gestures and enabling more precise and responsive user control.
- effort: Medium hardware redesign, minor firmware updates, and corresponding software changes on Mac and relay to interpret new button/LED states.  ·  risk: Medium; requires hardware production changes and user adaptation. Faulty firmware could cause misinterpretation of triggers, but fallback to existing button preserved.
- cost: Moderate increase in hardware cost and power consumption, roughly 5% additional cost per pendant unit, negligible latency impact.  ·  latency: None; hardware button events are instantaneous.
- security: No direct security impact but increased data flow may require careful permission handling.


## What it asked for

### `c22-f2dy` (context) — mac-vision capabilities and best full use cases
- why: To understand all possible capabilities and best-case scenarios for mac-vision to propose the most useful new features
- would change: It will inform what is genuinely new and uniquely useful that mac-vision can deliver, leading to more impactful proposals.

