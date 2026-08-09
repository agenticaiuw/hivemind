# Harness derivation — mac-vision — round 258

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide the mac-vision agent a reliable route to fetch the Mac UI accessibility tree or control snapshot, accessible by HTTP, which can be used to plan and execute UI steps in any macOS application."
- **useful because:** Mac-vision needs structured UI state beyond fixed actions or unreadable pixels to safely navigate and automate complex app workflows via accessibility APIs. This allows precise control and feedback without focus theft or blind clicks.
- **path:** mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 200ms
- **cost:** Low API call cost, no external API usage
- **security:** Requires careful authorization to prevent unwanted automation or reading of sensitive UI elements.
- **missing:** A named and stable HTTP API to access this accessibility data on the Mac agent

### "Create a persistent context and checkpoint store for mac-vision to record and resume in-progress UI automation workflows, storing UI state snapshots, pending steps, claimed tasks, and results to handle interruptions and enable safe retries."
- **useful because:** This lets mac-vision break down and track complex multi-step UI workflows, recover from interruptions, and avoid redundant or unsafe actions. It extends the existing workbench context system with UI-specific state and checkpoints.
- **path:** mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 500ms
- **cost:** Moderate API cost for state storage and retrieval, no external API.
- **security:** Storing UI state may expose sensitive information; needs encryption, access controls, and auditing.
- **missing:** UI-aware context and checkpoint schema; Stateful route endpoints on the Mac agent

### "Integrate the owner's stated prioritized tasks and mac-vision context into a single daily dashboard or task list surface that updates in real time and guides the mac-vision agent on what to work on next, with task details, context, preferences, and progress."
- **useful because:** This would give the owner and mac-vision a clear prioritized work plan explicitly linked to UI actions needed on the Mac. It enables effective focus, interruption handling, and status reporting. Without it, mac-vision acts blind to true current priorities beyond raw task facts.
- **path:** mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 300ms
- **cost:** Low to moderate API cost, mainly local agents and state fetching.
- **security:** Needs access control to task and context data, and secure update methods to prevent injection or corruption.
- **missing:** Joined view and update API on task facts and workbench contexts

### "Enable mac-vision to break down the task 'derive the next round of agent changes from the harness ledger' into concrete UI and shell actions that it can run or propose, including opening code editors, running shell scripts, navigating files, and editing text based on preferences such as using VS Code and zsh shell."
- **useful because:** This task is current and critical for owner workflows. Automating or assisting it via mac-vision maximizes owner productivity and leverages existing capabilities and environment.
- **path:** mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 800ms
- **cost:** Moderate to high depending on shell/script complexity, no external API calls.
- **security:** Executing shell or editor commands requires caution to avoid data loss or harmful mutations; confirmation policies are essential.
- **missing:** Task-specific UI and shell action schemas and orchestrations

### "Enable mac-vision to break down the task 'ship the 24 kHz superwideband audio path end to end on the pendant' into concrete UI actions or shell commands to validate, configure, test, and deploy the audio path using local tools and the pendant interface, following owner preferences and existing device capabilities."
- **useful because:** This task is a top priority explicit owner goal. Automating key steps or assisting via mac-vision would greatly accelerate development, testing, and deployment workflows for the pendant audio path.
- **path:** mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 800ms
- **cost:** Moderate to high depending on interaction complexity.
- **security:** Interactions with device interfaces and shell commands may require confirmations to avoid unintended changes.
- **missing:** Detailed device APIs and UI workflows for audio path and pendant interaction

### "Enable the owner to have a fully visual and interactive Mac UI agent that can operate seamlessly with zero focus theft, reading all control states and invoking any Mac app UI function via accessibility APIs with instant undo and recovery from interruptions."
- **useful because:** The owner currently cannot have an agent that fluidly drives the Mac UI with full fidelity and reliability. This would let the owner delegate complex computer tasks to an AI that works visibly and safely in the foreground or background, maximizing productivity and reducing manual errors.
- **path:** mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 500ms
- **cost:** Moderate API and compute cost for live UI tree processing and action orchestration.
- **security:** Needs fine-grained accessibility permission and undo safeguards to avoid unintended changes or data loss.
- **missing:** A dedicated mac-vision UI accessibility tree API with read/write action support and undo framework.; Persistent local checkpointing of UI workflows with versioning and rollback.; Real-time focus theft avoidance and event injection validation mechanisms.

### "Allow the owner to define, prioritize, and adjust a live task queue that integrates multi-surface agent capabilities (Mac, browser, iPhone, pendant) with explicit owner input and automated policy-driven re-prioritizations, visible to all agents and synchronizing state in real time."
- **useful because:** Currently, task tracking is fragmented or non-existent. This capability would let the owner manage a coherent, integrated task list that all agents understand and act on, making delegation, automation, and feedback consistent and predictable.
- **path:** mac-planner → browser-extension → ios-control → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** 400ms
- **cost:** Moderate API cost for state synchronization, multi-surface awareness, and UI integration.
- **security:** Needs mediation on multi-agent updates and tight access control to prevent conflicting commands or information leakage.
- **missing:** A real-time shared task queue manager with authorization and conflict resolution.; UI surfaces for owner review and manual task adjustments.; Cross-agent protocols for task priority and progress broadcasting.


## Changes it proposed to its own stack

### `hardware` — Add a dedicated hardware button or gesture sensor on the pendant for quick explicit task approval, cancellation, or escalation signals to the Mac or relay agents.
- **owner gets:** This would give the owner tactile, fast, low-latency control to approve or veto task executions without relying on voice or UI interactions, improving safety and responsiveness.
- effort: Medium - hardware design and firmware integration required.  ·  risk: User inconvenience if poorly designed; recovery by fallback to software confirmations.
- cost: Low to moderate hardware component and power consumption costs.  ·  latency: Negligible.
- security: Physical control reduces risk of unintended commands.

### `model-routing` — Implement a priority-based multi-agent orchestration layer that dynamically assigns subtasks to the best agent (Mac, browser, iPhone, pendant) based on current capabilities, context, and owner preferences, with fallback and retry logic.
- **owner gets:** The owner cannot currently leverage all agents coherently; a dynamic orchestration layer would unify multi-surface AI capabilities and maximize efficiency, even as context and connectivity change.
- effort: High - significant integration and testing needed across agents and routing layers.  ·  risk: Increased system complexity may introduce bugs; fallback and monitoring required.
- cost: Moderate compute cost for routing and state management.  ·  latency: Adds minor latency to decision making but reduces total work time.
- security: Requires robust authorization and auditing.
- depends on: real-time task queue; multi-surface context aggregation


## What it asked for

_Nothing._
## Its own summary

Discovered mac-vision tool capabilities and Mac agent routes. Confirmed mac-vision loop enabled with accessibility permission. Read owner’s current tasks and preferences from memory projection. Discovered no existing UI snapshot route for mac-vision; proposed new capability to provide structured accessibility tree for UI automation. Proposed checkpoint store for mac-vision to track multi-step UI workflows. Proposed daily task dashboard, and concrete task decompositions for owner’s current priorities. Next needed are detailed UI snapshot API, partial workflow state access, and cross-agent coordination for multi-surface task handling.

**Biggest unknown:** Exact API or mechanism mac-vision should use to fetch the accessibility tree snapshot for UI automation steps is missing. No existing route documented to expose this currently.

