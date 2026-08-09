# Harness derivation — mac-vision — round 245

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Build a prioritized actionable Mac UI task queue integrated with owner tasks, facts, and routines."
- **useful because:** The mac-vision agent needs a durable, ranked to-do list of concrete UI steps to make progress on the owner's goals with measurable progress and recovery.
- **path:** mac-local-agent → relay → pendant
- **model tier:** gpt-4o-mini
- **latency:** seconds to a minute
- **cost:** Moderate API usage; mostly local processing
- **security:** Task data remains private and only accessible on the owner's devices; no external sharing without explicit consent.
- **missing:** UI state snapshots for state reconciliation; Multi-step workflow management linking tasks to UI states; Automatic task ranking based on owner preferences and facts

### "Add a visible state reconciliation capability for multi-step Mac workflows in mac_delegate to verify UI state changes post-action using accessibility snapshots."
- **useful because:** This allows robust recovery and correctness checking for long-running or multi-step workflows that depend on UI changes, increasing reliability and trust.
- **path:** mac-local-agent → relay
- **model tier:** gpt-4o-mini
- **latency:** seconds
- **cost:** Low to moderate; mostly local processing and snapshot comparison
- **security:** Snapshot UI data is sensitive; handle carefully and keep local or encrypted
- **missing:** Incremental UI snapshot fetch and diff capability; Workflow state visual state binding

### "Enable mac-vision agent to perform live incremental UI snapshot fetches to optimize multi-step Mac action planning and reduce latency."
- **useful because:** Fetching full UI snapshots each step is expensive and slow; incremental snapshots reduce API overhead and accelerate action sequencing.
- **path:** mac-local-agent
- **model tier:** gpt-4o-mini
- **latency:** seconds per step
- **cost:** Low to moderate; improved efficiency in usage of accessibility APIs
- **security:** UI snapshot data is sensitive; ensure local retention and encryption in transit to relay if needed.
- **missing:** Incremental snapshot APIs in vision loop; Snapshot diffing tools

### "A smart, dynamic Mac UI assistant that can visually and algorithmically break down arbitrary app interfaces into actionable segments and suggest context-aware next steps to the owner for approval."
- **useful because:** Currently the owner lacks proactive, intelligent UI navigation support for ambiguous or unfamiliar Mac app interfaces. This would empower rapid, confident multi-step workflows regardless of app complexity.
- **path:** mac-local-agent → pendant → relay
- **model tier:** gpt-4o-mini
- **latency:** up to a minute for complex breakdowns
- **cost:** Moderate due to heavy UI state interpretation and model usage.
- **security:** Highly sensitive UI data analyzed; must stay encrypted and local where possible.
- **missing:** Advanced UI semantic segmentation and understanding beyond current accessibility tree; Natural language, visually grounded UI step suggestion generation; Interactive owner approval loop on pendant or Mac; Deep integration between UI state, delegations, and task priority for workflow orchestration

### "Unified cross-device user intent and task management system that aggregates spoken commands, reminders, system events, and manual task inputs into a shared, owner-curated goal hierarchy with deadlines, dependencies, and priorities."
- **useful because:** Currently, the owner has no single accessible repository or UI for all active intents and tasks; tasks live in disparate systems and manual mappings are required. This system offers holistic, edge AI-driven management and situational awareness.
- **path:** pendant → mac-local-agent → ios-control → relay → dashboard
- **model tier:** gpt-4o-mini
- **latency:** seconds to minutes for updates, near-instant intent recognition
- **cost:** Moderate to high due to model orchestration and cross-surface syncing.
- **security:** Highly sensitive user intent and schedule data; must enforce strict data minimization, encryption, and owner control.
- **missing:** Cross-surface synchronization and consensus mechanisms; Flexible, user-friendly task hierarchy editor UI; Automated dependency, priority inference and conflict resolution; Low-latency intent recognition across devices


## Changes it proposed to its own stack

### `hardware` — Add a dedicated physical confirmation button to the pendant distinct from the existing conversation start/stop button, to safely confirm high-risk Mac UI actions without toggle conflict.
- **owner gets:** Reduces risk of accidental commands and dangerous fallback mouse clicks during Mac control interactions, improving safety and confidence in voice/Mac control workflows.
- effort: Moderate hardware redesign with minor firmware updates to integrate the new button.  ·  risk: Possible manufacturing delays; firmware bugs could cause missed confirmations, mitigated by testing and rollback.
- cost: Minimal increase due to a single extra button; no significant power increase.  ·  latency: None, hardware event is immediate.
- security: Improves security by requiring explicit physical confirmation for critical actions.
- depends on: pendant hardware design and firmware source code

### `model-routing` — Implement adaptive model selection and routing logic that dynamically balances latency, model power, cost, and context relevance across surfaces and tiers for Mac UI vision tasks and cross-surface coordination.
- **owner gets:** Optimizes responsiveness and cost-efficiency of the AI assistant during complex UI understanding and cross-device task coordination, improving owner experience and system sustainability.
- effort: Moderate to high, requiring infrastructure and software changes to implement telemetry, decision trees, and fallback strategies.  ·  risk: Model misrouting might degrade user experience temporarily; recoverable by retraining and tuning.
- cost: Potential cost savings by preventing overuse of most powerful models on every request.  ·  latency: Reduces average latency by routing to faster models when appropriate.
- security: Routing decisions could expose minimal metadata; design must ensure privacy.
- depends on: Extensive telemetry collection; Model performance profiling; Cross-surface capability awareness


## What it asked for

### `c23-wbv5` (context) — mac-vision ui snapshot and workbench contexts
- why: To plan precise Mac UI interactions and resume multi-step workflows accurately
- would change: Allow the mac-vision agent to see the current UI state on the Mac and any open delegated workflows to pick the next best UI action accurately

