# Harness derivation — mac-vision — round 224

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a prioritized and live task list specifically for Mac-side work, integrating known owner priorities and task facts."
- **useful because:** The mac-vision agent can then always know what the owner most wants done on the Mac now, to plan or execute UI interactions effectively.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 1 second
- **cost:** Low, mostly model cost
- **security:** Contains owner task priorities; must respect privacy and not leak externally
- **missing:** A store or API to supply and keep updated the prioritized task list with due dates, dependencies, and current status

### "Provide a capability to verify the actual on-screen UI state and control outcome relative to the planned UI steps for Mac automation."
- **useful because:** This lets the mac-vision agent confirm it succeeded or detect divergences or failures in UI workflows, improving robustness.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** 1–2 seconds
- **cost:** Low, mostly model cost plus some I/O
- **security:** Reports internal UI states and automation results; carefully scoped to local use.
- **missing:** An accessible, queryable snapshot or diff of accessibility UI states versus planned steps; A method to integrate this with existing GET /workbench/contexts/:contextId disk-level verification

### "Define an integration and coordination protocol for mac-vision, mac-planner, and mac-terminal agents on the Mac to share context, goals, and task executions cleanly."
- **useful because:** Allows seamless cooperation among Mac-side agents handling UI automation, planning, and shell tasks, maximizing the owner's productivity.
- **path:** mac-vision → mac-planner → mac-terminal
- **model tier:** gpt-5.6-luna
- **latency:** 2 seconds
- **cost:** Low, model interaction cost
- **security:** Coordination involves task and possibly sensitive commands; must keep all local and private.
- **missing:** A defined shared context store or pub-sub mechanism for Mac-side agent coordination

### "Enable the mac-vision agent to monitor and anticipate the owner's app focus changes on the Mac using accessibility events for better task switching and smoother UI automation."
- **useful because:** Knowing when the active app or window changes allows the mac-vision agent to contextually adapt UI automation and pre-prepare likely needed actions, improving responsiveness and relevance.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** 500 ms
- **cost:** Low
- **security:** Only local UI state, no external data exposure.
- **missing:** A live event feed or subscription to macOS accessibility focus change events

### "Develop a demo or training function in mac-vision to record a UI interaction sequence once and then replay it accurately, for common repetitive Mac tasks without manual intervention."
- **useful because:** This would speed up automation for frequent tasks by letting the system learn and reproduce UI workflows reliably, improving owner productivity.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** 2 seconds
- **cost:** Medium, requires storage and replay engine
- **security:** Stored UI interaction sequences should be encrypted and access-controlled locally only.
- **missing:** A local persistence layer for UI action sequences; A deterministic replay engine for accessibility-based UI actions

### "Provide the owner with a unified, proactive Mac-side personal assistant that continuously monitors active apps and windows and predicts next needed actions, using accessibility event hooks and history data."
- **useful because:** This assistant would reduce manual interruptions and wait times by pre-empting the owner's intentions and launching appropriate UIs or actions.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 1 second
- **cost:** Medium, due to continuous monitoring and prediction model
- **security:** Accesses sensitive UI state and owner behavior patterns; data must be kept private and used only locally.
- **missing:** Accessibility event subscriptions for app/window focus changes; A history logging and predictive model trained on owner data

### "Build a local training mode for the mac-vision agent to record UI control interaction sequences and replay them reliably later, enabling DIY macro automation."
- **useful because:** Owners can teach the AI useful repetitive tasks once and have it run them automatically later, reducing friction for automation and increasing productivity without scripting knowledge.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** 2 seconds
- **cost:** Medium due to storage and replay complexity
- **security:** Stored sequences must be encrypted, access-controlled, and remain local only to protect sensitive workflows.
- **missing:** Persistent storage for UI action sequences; A deterministic accessibility action replay engine; UI snapshot comparison for validation during replay

### "Implement an offline Mac vision agent mode that can perform UI automation steps reliably without current network or cloud dependencies, fully on-device."
- **useful because:** Owners can still benefit from UI automation even when offline or the cloud relay is unavailable, improving reliability and autonomy.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini
- **latency:** 1 second
- **cost:** Low; uses existing local resources
- **security:** No data leaves device; full privacy guaranteed.
- **missing:** Full local model and policy stack for mac-vision agent; Offline capable accessibility control libraries


## Changes it proposed to its own stack

### `integration` — Create a robust Mac-side shared context store or pub-sub mechanism for mac-vision, mac-planner, mac-terminal, and other agents to coordinate tasks, share goals, and synchronize state in real-time.
- **owner gets:** The owner benefits by having all Mac-side agents work seamlessly together, avoiding duplicated efforts, conflicts, and enabling complex, fluid workflows across UI, terminal, and browser.
- effort: Medium to large, involving collaborative engineering on shared APIs, data models, and synchronization protocols, plus adapting existing agents.  ·  risk: Potential data race or synchronization bugs; mitigated by careful design and fallback states. Only local data is shared; no external exposure involved.
- cost: Minor runtime cost; mostly development resources.  ·  latency: Minimal, designed for asynchronous updates; no blocking.
- security: All data remains local and private to the owner's Mac.


## What it asked for

_Nothing._
