# Harness derivation — mac-vision — round 266

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A seamless, real-time Mac task manager interface that links owner's multitasking goals and reminders to live accessibility-driven UI recognition for instant next-step execution."
- **useful because:** Currently, the owner has no persistent, priority-ranked task list integrated with visible Mac UI state enabling instant task resumption or completion. This would increase productivity by smartly bridging cognition, task tracking, and automated UI control.
- **path:** mac-local-agent → pendant → relay → browser → dashboard
- **model tier:** realtime
- **latency:** under 2 seconds for step planning and actuation
- **cost:** moderate API usage for accessibility snapshots and Mac delegate tasks
- **security:** Requires trusted accessibility permissions and secure handling of personal task and UI data, with user control of automation thresholds.
- **missing:** durable prioritized task store with owner input interface; continuous accessibility tree snapshots linked to workbench context; UI-driven task progress recognition; dynamic plan synthesis merging owner goals with live UI state; integration of mac_delegate with UI state to guide action steps

### "Dynamic multi-step workflow resume and recovery across multiple apps on the Mac, bound tightly to visible UI state and with confirmation steps on the pendant."
- **useful because:** Interrupted or long workflows today have no automated resumption or verification combining what is on screen with what work was claimed. This reduces wasted effort, errors, and cognitive load.
- **path:** mac-local-agent → pendant → relay
- **model tier:** realtime
- **latency:** under 3 seconds to resume workflow and update from UI state
- **cost:** API usage moderate with integration complexity
- **security:** Requires fine-grained control to avoid unwanted automation; user confirmation needed for risky actions.
- **missing:** deep integration between UI snapshot state and workbench job claims; ability to verify UI state matches job claims before continuing; operator-facing pendant UI for confirmation and error handling; middleware to correlate workbench data with live UI accessibility tree


## Changes it proposed to its own stack

### `interaction` — Implement a typed, event-driven action broker in the mac-vision loop that mediates between typed Mac UI actions, browser interactions, and the workbench job system to allow fine-grained control, observability, and orderly multi-agent coordination.
- **owner gets:** Currently, the system risks conflicting or redundant UI actions without a broker that can classify and sequence each step by intent, type (read/write), and side effects. This would enable safer, more responsive and transparent automation.
- effort: moderate; involves refactoring the mac-vision loop and core action dispatch with typed classification and observability hooks.  ·  risk: Potential introduction of latency or race conditions; mitigated by thorough testing and staged rollout with fallbacks.
- cost: Negligible to moderate, mostly engineering time.  ·  latency: Minor increase in action dispatch latency acceptable for safer operation.
- security: Improved by explicit classification of user-impactful steps enabling potential future gating or user consent prompts.
- depends on: mac-vision ui snapshot and workbench context integration; mac_delegate; relay_job_status


## What it asked for

### `c32-6txj` (context) — mac-vision capabilities and best full use cases
- why: To use the correct Mac UI interaction patterns and prioritize effectively on the Mac.
- would change: I will know the ideal scenarios and use cases for mac-vision to focus on what is most valuable to the owner.

### `c33-by67` (context) — mac-vision ui snapshot and workbench contexts
- why: To know the current on-screen UI structure and relate it to ongoing work.
- would change: I will be able to see the accessibility tree and coordinate with job/workbench state to decide precise UI actions.

### `c34-5kva` (context) — workbench contexts
- why: To see the current tracked work claims and coordination signals for multi-step tasks on the Mac.
- would change: This helps me integrate UI perception with actual work in progress state and avoid redundant or conflicting actions.

### `c35-wt3g` (context) — mac-vision agent current task list
- why: To understand the highest priority work the owner wants me to do on the Mac.
- would change: I will pick and sequence my actions based on the owner's stated current tasks, avoiding idle or unnecessary work.

