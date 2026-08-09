# Harness derivation — mac-vision — round 263

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision accessibility automation loop to actively perform UI interactions on the Mac for the owner's current key tasks, such as developing the harness ledger changes and shipping the pendant audio path."
- **useful because:** The loop is permissioned, ready and able to read and operate Mac UI using accessibility APIs without screen grabbing or focus theft. Activating it on identified high priority tasks will automate repetitive or complex Mac UI operations efficiently and safely.
- **path:** mac-local-agent → pendant → relay → browser-extension
- **model tier:** realtime
- **latency:** low latency within 2-5 seconds per UI step
- **cost:** API call cost for Mac UI actions, minor relay message passing cost, negligible hardware cost
- **security:** Actions will be gated by the owner's task list and must confirm destructive operations before proceeding. Privacy preserved by local execution and consented pendant relay only.
- **missing:** Detailed UI workflows for key tasks on the Mac; Multi-surface workflow coordination layer to integrate Mac, browser, and pendant roles

### "Add a multi-surface workflow coordination capability that tracks interruption and restart of complex multi-step tasks involving the Mac UI (via mac-vision), browser automation, and pendant input, ensuring smooth continuation after restarts or failures."
- **useful because:** Currently, multi-step workflows on the Mac and in browser or pendant input are fragmented. A coordinated durable context system that records state, verifies actual UI vs claimed state, and manages restart handoff across surfaces would enable robust automation of complex user tasks.
- **path:** mac-local-agent → pendant → browser-extension → relay
- **model tier:** realtime
- **latency:** medium latency acceptable (seconds to tens of seconds) for state syncing and coordination
- **cost:** Some API call overhead for state reads/writes and relay messaging; minor hardware usage
- **security:** Data must be access-controlled and verified before state changes; integrate owner task facts and task acceptance explicitly to avoid unsanctioned actions.
- **missing:** Persistent UI state verification for mac-vision claims vs actual screens seen; A unified context ledger joining Mac UI state, browser state, and pendant input state

### "Provide the owner with a capability to query and receive a prioritized list of Mac UI tasks from their current intents and reminders, integrating facts tagged for the mac surface and local reminders data."
- **useful because:** Currently the owner has no curated list of actionable Mac UI tasks the mac-vision loop can act on. Creating this capability lets the owner efficiently direct the loop towards relevant work and avoid redundant or mistaken operations.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** low latency (within 1-3 seconds)
- **cost:** API cost for fact and reminders query, minimal compute for ranking
- **security:** Only authorized queries to owner data, no cross-device data leaks.
- **missing:** Fact to task priority ranking integration with Apple Reminders data

### "Enable the mac-vision agent to detect and resolve UI state divergence autonomously by capturing accessibility tree snapshots and performing rollback or recovery steps without owner intervention."
- **useful because:** Today, mac-vision cannot detect and self-correct when the UI changes unexpectedly, causing failed automation or stuck states that require manual recovery. Autonomous resolution enhances robustness and owner trust.
- **path:** mac-local-agent → pendant → relay
- **model tier:** realtime
- **latency:** seconds per detection and recovery action
- **cost:** API call and processing cost for accessibility tree comparison and rollback steps
- **security:** Data access control important to avoid exposing detailed UI structure externally.
- **missing:** Autonomous UI divergence detection framework; Rollback and corrective action set for mac-vision automation

### "Create a unified task and event timeline that integrates owner intents, reminders, routine executions, and mac-vision UI actions for a holistic, time-ordered view of ongoing work and automation progress."
- **useful because:** Currently, the owner cannot see a combined timeline showing what is planned, running, and completed across different agents and platforms, limiting situational awareness and ability to manage complex workflows.
- **path:** mac-local-agent → pendant → relay → browser-extension
- **model tier:** background
- **latency:** minutes
- **cost:** Moderate API calls for aggregation, with low compute cost
- **security:** Timeline data must be access controlled and respect owner privacy.
- **missing:** Cross-surface event synchronization and aggregation capability

### "Enable the Mac-vision agent to combine real-time pendant sensor data (e.g., gestures, button presses) with UI context to trigger context-aware Mac UI automation."
- **useful because:** Currently, pendant inputs and Mac UI automation are separate. This capability would allow the owner to use physical gestures or button presses on the pendant to start, pause, or modify Mac UI automation steps contextually, enhancing control and responsiveness.
- **path:** pendant → mac-local-agent
- **model tier:** realtime
- **latency:** under 1 second from pendant input to Mac UI response
- **cost:** Low to moderate, mostly software integration and event processing
- **security:** Physical inputs must be securely authenticated and linked to owner intents to prevent unintended automation.
- **missing:** Context-aware gesture interpretation framework linking pendant sensors and Mac UI state


## Changes it proposed to its own stack

### `integration` — Implement live UI state verification for mac-vision by comparing the accessibility tree read from the Mac UI against the claimed context in workbench/contexts to detect divergence or failure in automation steps.
- **owner gets:** Ensures the automation driven by mac-vision is accurately synchronized with what is actually on screen, preventing erroneous UI actions or stuck workflows without the owner's knowledge.
- effort: Medium effort, requires integration of UI accessibility readouts into workbench context verification logic and incremental sync.  ·  risk: Automations might pause frequently if UI changes unexpectedly; recover by alerting the owner and resynchronizing the view.
- cost: Increase in API calls and processing to verify UI state frequently; nominal hardware cost.  ·  latency: Some additional delay (hundreds of ms) in each verification pass, but acceptable within existing UI action budgets.
- security: May expose some UI structural data in context syncing; must be access controlled and encrypted.
- depends on: workbench/contexts; mac-vision accessibility loop

### `hardware` — Add a dedicated secondary trigger button on the pendant hardware for direct mac-vision interactions and confirmations, separate from audio or other input triggers, to offer explicit physical control points for UI automation acceptance or rejection.
- **owner gets:** Currently the pendant has only one primary button used for multiple gestures, which limits the ability to multiplex several distinct triggers for mac-vision or other agents reliably. A dedicated button would simplify user interaction and increase safety.
- effort: Requires hardware firmware change and minor mechanical update; minimal complexity increase in user interface.  ·  risk: Hardware modification costs and manufacturing complexity increase slightly; user training to new habit.
- cost: Marginal increase in component and assembly cost; negligible power impact.  ·  latency: None, physical button is immediate trigger.
- security: Improves security by isolating approval gestures from scanning keys or gesture misinterpretation.
- depends on: pendant hardware platform

### `model-routing` — Create a specialized routing policy for mac-vision agent requests that prioritizes short, focused UI action sequences with immediate feedback, minimizing latency and the amount of context sent in each step to optimize usability and responsiveness.
- **owner gets:** Mac UI automation is latency sensitive, and reducing overhead and context size ensures quick, accurate responses to owner commands and dynamic UI changes.
- effort: Low to medium effort. Involves policy development, testing, and tuning of the routing layer for prioritized mac-vision traffic.  ·  risk: Mis-routing or dropping complex multi-step plans, requires fallback paths and monitoring.
- cost: Reduced per-action cost due to smaller context payloads, possibly increased routing management cost.  ·  latency: Improves latency and responsiveness for mac-vision workflows.
- security: No significant change.

### `interaction` — Implement a natural language interface that allows the owner to ask mac-vision complex multi-step Mac UI tasks conversationally, with the loop planning and confirming steps interactively.
- **owner gets:** Today, mac-vision requires precise API calls or direct commands; the owner cannot naturally converse about high-level multi-step tasks that the automation can perform. This enhances usability and accessibility.
- effort: Medium effort, includes natural language understanding, step planning, confirmation dialogs, and feedback loop integration.  ·  risk: Parsing errors or misinterpretation may require fallback or undo options.
- cost: Moderate compute cost for language model usage and confirmation generation.  ·  latency: Slightly increased latency for step planning and confirmation but acceptable for usability gain.
- security: Ensures explicit owner confirmation before critical operations.
- depends on: computerUse.loopEnabled; mac-vision capability


## What it asked for

_Nothing._
