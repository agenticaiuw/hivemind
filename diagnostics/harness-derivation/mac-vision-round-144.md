# Harness derivation — mac-vision — round 144

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to autonomously and safely direct multi-step, multi-app workflows on the Mac using natural language, with explicit UI control and undo support."
- **useful because:** Today the owner cannot get true autonomous computer use on their Mac without visual UI capture and unsafe focus stealing. This would let the system do complex tasks across apps reliably and safely.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** sub-second for UI steps, minutes for multi-step workflows
- **cost:** moderate CPU and API calls
- **security:** Requires explicit owner consent and fine-grained permission gating to prevent unwanted destructive actions; safety features to undo and confirm high-impact steps.
- **missing:** macOS Accessibility permission grant for AI Pendant Agent binary; typed policy enforcement for UI action gating; undo telemetry and recovery; owner UI for consent and review

### "Create a unified durable task/goals manager that lets the owner and agents set, rank, and reprioritize what work the AI system should do next, including dependencies and deadlines."
- **useful because:** Currently, task facts and routines are disjoint with minimal structure; this would let the owner explicitly state priorities and dependencies for more effective AI planning and execution.
- **path:** memory → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds for ranking and update operations
- **cost:** low storage and compute cost
- **security:** Task and goal data includes personal priorities and deadlines and must be guarded accordingly.
- **missing:** writable integrated goal/task store; priority and dependency modeling; owner UI for task management

### "Enable natural language voice commands that let the owner edit, prioritize, and delegate tasks to the AI system while away from the Mac, syncing changes back to the Mac when connected."
- **useful because:** Currently, task management is only usable from the Mac UI or by separate routine schedules. Voice-based task management on the go would increase owner productivity and AI responsiveness.
- **path:** relay-realtime → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds end-to-end
- **cost:** low to moderate API call cost
- **security:** Voice commands must be authenticated and validated to avoid incorrect task state changes.
- **missing:** voice task management UI; sync protocol to Mac task store; voice recognition and understanding tuned for task edits


## Changes it proposed to its own stack

### `integration` — Integrate the pendant hardware's moment bookmark (existing physical button press) with the Mac agent's task manager and UI action system so the owner can physically signal task boundaries or confirm critical actions seamlessly.
- **owner gets:** Physical interaction to trigger AI task state changes or approve pending computer-use actions would increase trust and control without requiring visual UI focus or modal dialogs.
- effort: Medium implementation effort on firmware, Mac agent, and UI sides.  ·  risk: Potential for accidental triggers mitigated by explicit gesture design and confirmation on the Mac agent.
- cost: Low CPU and power on the pendant; moderate code integration on Mac side.  ·  latency: Near real-time reaction to physical input improves responsiveness.
- security: Requires secure linking of button press events to agent task state and user identity.
- depends on: mac-vision computer-use loop enabled; durable task/goals manager proposed above; macOS Accessibility permission granted

### `firmware` — Add a second physical button to the pendant dedicated solely to allowing discrete in-band signaling for approval/confirmation gestures distinct from the main microphone button press.
- **owner gets:** Currently, the pendant's single button is heavily constrained, limiting gesture differentiation. A second button would enable reliable multi-command gesture input and better explicit user confirmations without impacting the primary audio flow.
- effort: Medium hardware and firmware effort, including board redesign and software update.  ·  risk: Hardware redesign requires production iteration; user needs to learn the new gesture.
- cost: Small hardware cost impact; minor increase in power usage.  ·  latency: No latency increase; possibly reduced gesture decoding latency due to less ambiguity.
- security: Improves security by allowing a dedicated confirmation channel separated from primary microphone button.

### `memory` — Implement an automatic task extraction and ranking system that parses owner communications, reminders, and daily routine commands into a prioritized, actionable task list for all agents.
- **owner gets:** Currently tasks must be entered manually or exist as scattered facts with little ranking. Automation would reduce owner burden and increase AI responsiveness to real priorities.
- effort: High effort in NLP pipeline, storage integration, and ranking logic.  ·  risk: Potential for incorrect task extraction or over-prioritization; needs override UI.
- cost: Moderate compute and storage cost.  ·  latency: Minutes for batch processing; near real-time possible with incremental update.
- security: Sensitive task data must be carefully protected.
- depends on: memoryService writable store; natural language processing model integration


## What it asked for

_Nothing._
