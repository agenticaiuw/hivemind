# Harness derivation — mac-vision — round 257

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I want a persistent, prioritized task and goal management system specifically for Mac-based computer tasks that mac-vision can read and act on."
- **useful because:** The owner currently has no durable, ranked list of computer tasks for mac-vision. Without this, mac-vision's automation is reactive and lacks context to plan and prioritize actions effectively. A persistent, owner-editable task list with priorities, deadlines, dependencies, and statuses would empower mac-vision to autonomously manage and execute tasks on the Mac within owner preferences.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** real-time interaction with sub-second response times for reading and planning; longer for batch updates
- **cost:** Moderate API usage; mostly local compute with occasional model calls for prioritization and planning
- **security:** Tasks and goals are sensitive as they represent personal work and priorities. Data should never leave owner devices without explicit permission.
- **missing:** A durable task and goal data store integrated with the Mac agent; UI or voice interface for the owner to add, edit, and prioritize tasks; Conflict resolution and dependency tracking on tasks; Integration for mac-vision to poll and read this list efficiently; Notification or briefing integration to surface urgent tasks

### "I want mac-vision to verify and track the real UI state on the Mac to confirm task progress and side effects of actions, and to compare UI state against claimed workflow progress in the workbench context system."
- **useful because:** Currently mac-vision actions and delegated workflows have no reliable check of actual UI changes, leading to potential errors and uncertainty if tasks are truly done or interrupted. Verifying UI state against claimed context would allow safe resumption, error detection, and higher trust in automation outcomes.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** seconds, not real-time for full diff; real-time for spot checks
- **cost:** Low API cost, mostly local state comparisons; model calls for UI state change interpretation as needed
- **security:** UI state may contain sensitive information. Comparisons and telemetry must respect privacy and not send sensitive data externally.
- **missing:** A persistent and queryable store of UI snapshots tagged by workflow context; Mechanisms to diff current UI tree against saved snapshots for changed state; Integration of the workbench context system with UI snapshots for claimed vs actual state comparison

### "I want the mac-vision agent to initiate and coordinate multi-step Mac workflows that may combine mac_run_actions and browser_run_actions based on owner goals, with dynamic branching and error recovery."
- **useful because:** Owners often need complex workflows that span Mac system apps and web browser interactions, requiring flexible orchestration beyond 1-3 actions. Automating this with a single coordinator agent executing controlled, branchable sequences that can handle errors and retry saves time and reduces frustration.
- **path:** mac-local-agent → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** sub-second for action steps, under seconds for workflow state transitions
- **cost:** Medium to high, due to continuous model usage for state tracking and branching logic
- **security:** Must limit and monitor scope of automated workflows to avoid unintended side effects; error recovery must not cause destructive outcomes
- **missing:** A workflow orchestration engine in mac-vision supporting multi-step, conditional action sequences; Mechanisms to integrate and coordinate mac_run_actions and browser_run_actions; Reliable state persistence and rollback for partial workflows

### "I want the mac-vision agent to be able to propose and enforce a fine-grained user action policy with typed action classifications, reversibility checks, and dynamic 'confirm before execute' gating on destructive actions."
- **useful because:** Currently all mac-vision actions have uniform execution with minimal guards. A typed enforcement layer that categorizes actions into read-only, reversible, and destructive classes would increase the owner's safety and confidence in automation. Dynamic gating and confirmation on destructive actions prevents accidental data loss or harm.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** real-time response for gating decisions
- **cost:** Low to moderate, as classification logic and gating are mostly local
- **security:** Policy enforcement is security-critical; must guard against bypass and provide full audit trail
- **missing:** Typed action classification APIs; Reversibility metadata for actions; Dynamic gating UI or voice confirmation integration


## Changes it proposed to its own stack

### `integration` — Add a unified context tracking layer that connects task facts, workbench workflow contexts, and real UI accessibility trees on the Mac. This system would consolidate owner's stated tasks, multi-step delegated workflows, and live UI state for coherent, actionable, and resumable agent-driven automation.
- **owner gets:** Currently these data sources are siloed and disconnected, reducing reliability and usability of computer-use automation. Connecting them creates a full view of what the owner wants, what is in progress, and what the Mac UI actually shows, enabling trusted, proactive help that can resume interrupted work safely.
- effort: Large, requires changes in multiple agent systems and storage layers  ·  risk: Potential data consistency issues; must gracefully handle partial or missing data; increased complexity needs careful error handling
- cost: Medium API overhead and storage cost for synchronization  ·  latency: Some latency on synchronization but asynchronous by design
- security: High, as it aggregates sensitive data from multiple sources; requires strict privacy and access controls
- depends on: persistent task and goal management system; workbench workflow contexts accessible and queryable; UI state persistence and diffing


## What it asked for

_Nothing._
