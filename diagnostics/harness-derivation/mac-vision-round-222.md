# Harness derivation — mac-vision — round 222

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to execute multi-step macOS UI interaction plans using the accessibility tree without taking screen captures, fully controlling the Mac interface safely and efficiently."
- **useful because:** This would allow fully automatic, complex task completion on the Mac that respects the owner's privacy and control preferences, moving beyond simple clicks or superficial control.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** seconds per interaction sequence
- **cost:** moderate API usage due to multi-step planning and execution
- **security:** Requires strict permission and trust controls to avoid unintended destructive actions.
- **missing:** A robust accessibility interaction execution framework beyond current limited actions.; A way to map owner tasks to UI workflows.; More detailed state verification before and after steps.

### "Create an owner-intent-driven dynamic task manager that interprets the owner's priority facts, combined with macOS UI status, to generate a ranked queue of actionable tasks for mac-vision to pursue."
- **useful because:** It closes the gap between what the owner wants done and what is actually actionable on the Mac, enabling more proactive and prioritized automation.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** sub-minute for task refresh and ranking
- **cost:** API usage focused on reading owner facts and state
- **security:** Must guard against unauthorized task manipulation and respect privacy.
- **missing:** A priority-driven task interpretation engine.; Task queue storage and interface.; Integration with memory facts and workbench contexts.

### "Add a robust verification and state-delta reporting system for mac-vision's UI actions, comparing expected versus actual macOS UI state before and after each step to detect discrepancies and recover gracefully."
- **useful because:** This would increase reliability and trust in automated UI control by preventing or mitigating errors from UI changes or unexpected states.
- **path:** mac-planner → mac-vision
- **model tier:** realtime
- **latency:** seconds per step verification
- **cost:** Higher due to state comparison and error handling.
- **security:** Must securely handle sensitive UI state and avoid leaking private UI content.
- **missing:** State snapshot and diff capabilities integrated with accessibility tree; Error recovery and retry workflows; Reliable state-change detection mechanisms

### "Implement a background assistant on the Mac that continuously monitors owner priority tasks and suggests or auto-triggers mac-vision UI workflows to progress or complete those tasks, with owner override ability."
- **useful because:** Enables seamless, proactive task management and completion on the Mac without requiring owner initiation, reducing manual effort and cognitive load.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** minutes for monitoring and activation cycle
- **cost:** Moderate API and compute cost for continuous monitoring and workflow planning.
- **security:** Must ensure owner privacy and maintain explicit override and audit controls.
- **missing:** Long-running background workflow coordinator.; Integration with live owner priority and memory facts.; Automated Mac UI workflow triggering APIs.


## Changes it proposed to its own stack

### `integration` — Add a typed and well-documented macOS accessibility action execution API distinct from pixel-based UI control, supporting batched and reversible UI steps to underpin mac-vision's control capabilities.
- **owner gets:** This change empowers automatic, detailed UI control on the Mac while preserving safety and auditability, enabling truly hands-free task completion via mac-vision.
- effort: Medium-large engineering effort including API design, implementation, testing, and packaging.  ·  risk: Misuse could cause unintended destructive UI actions; needs strict user consent and rollback mechanisms.
- cost: Moderate increased API complexity; no major hardware cost.  ·  latency: Adds milliseconds to step execution for safety and correctness.
- security: Requires robust permission and confirmation layers.
- depends on: computerUse.loopEnabled; Accessibility permission granted to the running binary

### `hardware` — Add a dedicated hardware button on the pendant for mac-vision interaction approval and context bookmarking, separate from existing buttons to prevent gesture conflicts and enable explicit owner approval.
- **owner gets:** Facilitates quick owner approval of automated Mac UI actions and reliable context marking without interfering with other hardware controls.
- effort: Low, hardware button integration and event routing.  ·  risk: Minimal, new input event may be accidentally pressed but does not trigger destructive action alone.
- cost: Low hardware cost increase, negligible power usage.  ·  latency: None.
- security: Improves security by enabling explicit owner confirmation.

### `model-routing` — Integrate an advanced reasoning model that combines owner priority tasks, live Mac UI accessibility state, and task history to plan and adapt multi-step UI interaction plans dynamically.
- **owner gets:** Enables smarter, adaptive mac-vision behavior that can adjust plans in real time to unexpected UI changes or task priority shifts, improving success rates and responsiveness.
- effort: Large effort to build and test complex multi-source planning and routing logic.  ·  risk: New model complexity might introduce planning errors; requires extensive validation.
- cost: Moderate increase in model inference costs.  ·  latency: Longer planning time but within acceptable limits for interactive use.
- security: Requires strict access controls to sensitive owner task data and UI state.
- depends on: computerUse.loopEnabled; accessibility permission; owner priority task access; UI state accessibility


## What it asked for

_Nothing._
