# Harness derivation — mac-vision — round 238

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have mac-vision automatically detect and reconcile on-screen UI state with claimed work contexts to ensure seamless continuation of interrupted complex workflows and prevent duplicated or lost effort."
- **useful because:** Currently, the system tracks what work is claimed and what is completed on disk, but there is no mechanism to compare that with the actual UI state the owner sees. This leads to uncertainty about whether the workflow is consistent with reality, causing repeated or forgotten steps and broken automation continuity. This proposal bridges that gap by making mac-vision visually validate and sync UI state with claimed progress.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** real-time to a few seconds
- **cost:** Moderate, due to UI state analysis and context syncing
- **security:** Requires deep access to UI and workflow data. Must be strongly access-controlled and auditable to prevent misuse or accidental state corruption.
- **missing:** API to snapshot UI state on demand and compare it to workbench/contexts state; Extended mac-vision loop integration with workflow reconciliation logic; Cross-surface context sync mechanism for state agreement

### "Create a priority-driven agent controller on the Mac that dynamically schedules and executes mac_run_actions or mac_delegate tasks based on the owner's current explicit task list and environment status."
- **useful because:** There is no current autonomous Mac-side agent that dynamically picks from the owner's prioritized tasks and runs optimized UI interactions or delegations proactively without waiting for explicit commands. Such a controller would reduce friction, anticipate needs, and keep workflows flowing smoothly based on context and real priorities.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** a few seconds to minutes, depending on task complexity
- **cost:** Moderate to high depending on task frequency and complexity
- **security:** Needs permission for autonomous UI control; potential risk if errors or runaway actions occur. Must include careful fail safes and reversible actions.
- **missing:** Task prioritization integration beyond current static facts; Reactive environment sensing and decision-making logic; Robust error recovery and undo workflows; Expanded use of mac_delegate for complex workflows

### "Enable mac-vision to propose and execute context-aware remediation steps automatically when UI inconsistencies or blockages occur during task execution, improving robustness of automation."
- **useful because:** During complex workflows, UI states can be inconsistent or block the planned automation steps, causing failures or requiring manual intervention. Automating corrective actions such as closing interfering dialogs, refreshing views, or repeating steps can improve reliability and reduce owner frustration.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** Low to moderate, mostly execution on the Mac
- **security:** Automated UI changes require trusted permission and careful safeguards to avoid inadvertent undesired outcomes.
- **missing:** Access to real-time UI failure detection and recovery action library; Integration with existing mac_run_actions and mac_delegate for retry logic

### "Implement a rich UI context memory in mac-vision that tracks recent screen states, user inputs, and automation actions to enable undo, rollback, and advanced context-aware task planning."
- **useful because:** Having a detailed, indexed memory of UI states and actions enables the system to provide powerful undo features, detect patterns in automation failures, and plan next steps more intelligently by recalling past context beyond static reminders or tasks.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes for state recall
- **cost:** Moderate storage and compute on the Mac
- **security:** Requires careful data protection since detailed UI state may include sensitive information.
- **missing:** Capability to persist and index detailed UI snapshots; Integration with action logging and recovery mechanisms


## Changes it proposed to its own stack

### `interaction` — Build a unified multi-surface interaction policy that lets the Mac-vision agent coordinate with browser-extension, mac-terminal, and relay-realtime to manage work distribution seamlessly as the owner's context switches between these.
- **owner gets:** The owner shifts frequently between Mac GUI, browser, terminal, and voice via pendant. Without coordinated control, there is risk of duplicated efforts, lost state, or conflicting commands. A unified policy would enable seamless workflow transition, appropriate task routing, and better resource use across surfaces.
- effort: Moderate to high engineering effort for cross-surface communication, policy enforcement, and context sharing.  ·  risk: Potential complexity might cause bugs or state desync initially but can be mitigated with layered rollout and logging.
- cost: Mostly engineering time; minor runtime overhead for communication.  ·  latency: Minimal; design for async cross-surface update flows.
- security: Requires secure channels and strong permission checks to avoid hijacking or data leaks.
- depends on: Cross-surface context sync mechanism; Improved multi-agent communication architecture


## What it asked for

_Nothing._
