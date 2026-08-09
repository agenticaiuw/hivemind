# Harness derivation — mac-vision — round 261

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide mac-vision with a live, prioritized task list directly tied to owner goals and preferences, integrating memory facts and reminders into actionable ranked tasks."
- **useful because:** Currently, mac-vision has no built-in task list or ranking; reading owner intent is manual and indirect. This capability empowers the agent to focus on what the owner actually wants done first, improving efficiency and value.
- **path:** mac-planner → mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** under 2 seconds
- **cost:** low; mostly local database lookup and ranking
- **security:** tasks potentially include sensitive personal goals; data remains local to the owner's systems; read-only to assistant
- **missing:** integration between memory projection, reminders, and local task ranking for mac-vision; UI for owner to curate and confirm priority adjustments

### "Build a combined mac-vision accessibility UI automation loop that runs live accessibility snapshots, validates UI state, and reliably executes multi-step Mac workflows with error recovery and step verification."
- **useful because:** The mac-vision agent currently cannot do robust multi-step Mac UI automation using accessibility APIs. This capability would unlock granular and dependable UI interactions necessary for complex workflows and improve error handling and state reliability.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** few seconds per step
- **cost:** moderate; some CPU for UI observation and LLM planning
- **security:** Accessibility data is sensitive UI structure; must be restricted to local processing and encrypted transit when shared; user consent mandatory.
- **missing:** a true loop capability combining snapshots, state verification, and action sequencing; integration with mac-workbench contexts for UI state reconciliation

### "Provide mac-vision with smart confirmation prompts that intelligently confirm high-impact or destructive Mac UI actions through its accessibility loop to protect the owner from errors without interrupting low-impact work."
- **useful because:** The owner currently risks unintended destructive actions from automated UI control. Intelligent confirmations based on action classification would balance safety and fluidity, allowing mac-vision to automate freely while preventing costly mistakes.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini
- **latency:** sub-second to one second
- **cost:** low; mostly local rules and small LLM checks
- **security:** Local only; no data leaves device for safety; user override controls needed.
- **missing:** a well-defined action classification system with thresholds for confirmation; UI hooks in mac-vision loop for prompts and user interaction

### "Enable mac-vision to coordinate multi-device workflows by sharing UI state and task context with browser-extension and ios-control, allowing seamless handoffs and multi-surface goal tracking."
- **useful because:** Owners use Mac, browser, and iPhone as a combined workspace. Coordinated AI across these devices magnifies productivity by maintaining context and continuity seamlessly across surfaces.
- **path:** mac-vision → browser-extension → ios-control → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** low-latency synchronization required
- **cost:** moderate, network and context sync costs
- **security:** Sensitive data crossing device boundaries; strict encryption and user opt-in required.
- **missing:** cross-surface context sync and UI state sharing protocols; multi-agent goal and task arbitration


## Changes it proposed to its own stack

### `integration` — Implement a durable UI state synchronization mechanism that connects the mac-vision accessibility loop with workbench job contexts and job handoff features, allowing mac-vision to verify on-screen UI state against expected workflow state and resume interrupted or long-running tasks reliably.
- **owner gets:** This change would prevent lost progress in complex multi-step Mac workflows by providing stateful coordination and robust resumption, making the system more reliable and trustworthy for the owner.
- effort: medium; requires integrating multiple APIs, managing persistent UI state, and building verification logic  ·  risk: mid; UI state mismatch could cause automation to fail; recovery options must exist
- cost: low to moderate; mostly software integration costs  ·  latency: none for user interactions; some background sync overhead
- security: moderate; requires handling sensitive UI accessibility data
- depends on: mac-vision_accessibility_automation_loop; mac-vision_workbench_context_integration

### `hardware` — Add a second physical button to the pendant specifically for mac-vision agent secure confirmations, separate from the main action button, to allow fast, robust, and error-proof user approval of high-impact Mac UI actions via the wearable device.
- **owner gets:** The owner can securely confirm critical Mac actions hands-free without disrupting typing or moving the cursor, improving safety and user experience.
- effort: medium hardware design and firmware update  ·  risk: low; additional button introduces minor complexity
- cost: minimal hardware cost increase  ·  latency: none
- security: positive; enables secure, explicit approvals
- depends on: hardware; firmware


## What it asked for

### `t11-zv8k` (tool) — mac-vision_task_priority_list
- why: To enable mac-vision to read and act on the owner's live prioritized task list, which is currently held in memory facts with kind 'task' and task projection. This is necessary for mac-vision to make informed plans and progress on what the owner actually wants done on the Mac.

```json
{
  "type": "object",
  "properties": {},
  "description": "Request the current prioritized task list for the Mac surface."
}
```

### `t12-75c7` (tool) — mac-vision_accessibility_automation_loop
- why: To fully enable mac-vision to read UI state and control the Mac via the accessibility tree automation loop that is now unlocked by permissions. This loop provides detailed UI snapshots and controlled interaction capabilities for robust multi-step UI workflows.

```json
{
  "type": "object",
  "properties": {},
  "description": "The capability to read accessibility tree snapshots iteratively, plan multi-step UI actions, run them stepwise, and verify state changes."
}
```

### `t13-7j39` (tool) — mac-vision_workbench_context_integration
- why: To enable mac-vision to coordinate and resume multi-step Mac workflows robustly by integrating with workbench contexts and job handoff APIs. This adds durable statefulness around workflows, preventing lost progress and enabling handoff between agents or sessions.

```json
{
  "type": "object",
  "properties": {},
  "description": "Capability to sync live UI state in accessibility snapshots with workbench job contexts, track progress, and resume multi-step workflows."
}
```

