# Harness derivation — mac-vision — round 212

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a live prioritized actionable task list on the Mac that unifies owner-stated goals, reminders, open workflows, and live UI state verification to enable proactive and reliable task progress by mac-vision."
- **useful because:** Currently the Mac surface sees sparse owner task statements and scheduled routines but no prioritized queue that integrates real UI state verification. This capability lets mac-vision reliably advance owner goals, track multi-step workflows, and resume interrupted work with confidence.
- **path:** mac-planner → mac-vision → unified
- **model tier:** realtime
- **latency:** under 1 second
- **cost:** low; mostly local computation with minimal API overhead
- **security:** Needs to handle owner task privacy carefully; UI state verification must not expose sensitive data externally; must respect owner preferences for actions.
- **missing:** Integration of UI state verification before/after actions; State reconciliation APIs for UI versus expected state; Unified task representation combining owner facts, reminders, and open work

### "Enhance coordination between mac_delegate and mac_run_actions/browser_run_actions with UI state reconciliation to ensure reliable multi-step workflow execution on Mac."
- **useful because:** Separating complex multi-step goals and atomic UI actions requires tight coordination. Adding verification of UI state before and after steps reduces failure, drift, and improves resumption after interruption.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 1 second
- **cost:** medium due to verification overhead
- **security:** Requires managing sensitive UI state securely; must avoid leaking private UI content during verification; needs owner consent for deep UI state access.
- **missing:** UI state reconciliation APIs and snapshot comparison; State change detection and error recovery protocols; Unified coordination logic between mac_delegate and atomic action executors

### "Expose automation boundary preferences as explicit surface-scoped settings on Mac, enabling the owner to control confirmations and limits on destructive versus non-destructive actions during automated workflows."
- **useful because:** Owner preferences currently exist but are implicit or scattered. Making them explicit and surface-scoped aids clarity, safety, and owner confidence in complex automation, especially when mac-vision acts proactively.
- **path:** mac-planner → mac-vision
- **model tier:** realtime
- **latency:** under 1 second
- **cost:** low
- **security:** Preferences must be private and only alter automation behavior, not data integrity; clear owner control is needed.
- **missing:** UI for preference capture and adjustment; Surface integration to enforce these preferences during action planning and confirmation

### "Enable mac-vision to verify and reconcile real-time Mac UI state before and after each delegated or direct action, including detecting partial completions, failures, or drift, and notifying the owner or retrying automatically."
- **useful because:** Owners cannot currently trust that multi-step or delegated workflows on the Mac have executed fully or correctly because there is no mechanism to verify UI state changes against expectations. This leads to silent failures, lost progress, or user confusion.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 1 second
- **cost:** medium due to state snapshot comparison and differential checking
- **security:** UI state snapshots may contain private data and must be handled securely and locally. Owner consent is essential. Verification logic must respect data privacy and limit exposure.
- **missing:** APIs for capturing, storing, and comparing UI state snapshots; Protocols for error detection and recovery when UI state deviates; User notification or auto-retry mechanisms

### "Allow the Mac agent to autonomously interpret and execute owner-stated but ambiguous or multi-step goals by dynamically decomposing them into verified atomic UI actions without requiring manual scripting."
- **useful because:** Owners want to delegate complex workflows or abstract goals to the Mac agent without needing to specify exhaustive step details. The agent today cannot reliably interpret and self-structure such goals into atomic UI steps with verification and recovery.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** under 2 seconds due to complex reasoning
- **cost:** high for model inference and verification
- **security:** Such autonomous capability must be tightly controlled with clear owner-provided goals and verification to avoid unintended actions. Sensitive UI content must be protected.
- **missing:** Dynamic goal decomposition and planning algorithms; Verified atomic action execution with UI state reconciliation; User verification and override flow

### "Provide an owner-visible Mac UI state history timeline with timestamps and key UI events, integrated with mac-vision's actions and delegations, enabling review, undo, and recovery of unintended changes or failed steps."
- **useful because:** Owners have no comprehensive view of what UI changes the agent has made over time, making it hard to diagnose issues, undo mistakes, or understand progress in multi-step workflows.
- **path:** mac-vision → mac-planner → dashboard
- **model tier:** background
- **latency:** minutes, not realtime
- **cost:** medium storage and indexing cost, low active compute
- **security:** Must securely store UI state history locally, encrypt if needed, and expose only to authorized user surfaces. Privacy is critical.
- **missing:** UI state event logging and storage; Timeline UI visualization components; Undo and recovery APIs integrated with mac-run-actions and mac_delegate

### "Create a Mac surface contextual memory augmentation that persists key UI element states, user interaction patterns, and workflows to accelerate task recognition, recommendation, and automation over time."
- **useful because:** The Mac agent currently lacks persistent contextual learning from ongoing UI use, missing opportunities to proactively assist or suggest shortcuts based on observed interaction patterns and frequent workflows.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** minutes for learning cycles, realtime for retrieval
- **cost:** moderate storage and compute
- **security:** Must store sensitive UI interaction data locally and securely; respect user privacy and opt-in preferences.
- **missing:** Persistent contextual UI state storage; Interaction pattern recognition algorithms; Integration with task prioritization and recommendation engines


## Changes it proposed to its own stack

### `hardware` — Add a dedicated physical status indicator LED or tactile feedback on the AI Pendant to signal mac-vision activity states such as waiting for owner input, executing a UI action, or error requiring attention.
- **owner gets:** Currently, the owner has no physical or immediate indication from the pendant when the Mac agent is actively processing commands or encountering errors, leading to uncertainty whether their voice or UI requests are being handled.
- effort: low to medium; involves hardware firmware and pendant LED control integration  ·  risk: Minimal hardware risk; potential distraction if feedback is too frequent or intrusive, which can be mitigated by adjustable settings.
- cost: Low hardware cost; negligible power draw increase  ·  latency: None
- security: None

### `model-routing` — Introduce a semi-autonomous model routing tier that dynamically decides whether to handle a Mac task at the atomic UI action level (mac_run_actions/browser_run_actions) or delegate it to a multi-step planner (mac_delegate) based on task complexity, context, and past success rates.
- **owner gets:** Owners get optimal execution tailored to task difficulty and context, improving efficiency and success rates without manual intervention or guesswork from the user about which model or approach handles each request.
- effort: medium to high; involves model orchestration and telemetry integration  ·  risk: If routing chooses incorrectly, it might delay task completion or require retries; thorough testing and fallback needed.
- cost: Moderate compute cost due to additional model inference  ·  latency: Slightly increased latency for routing decision, offset by better execution
- security: Models and routing decisions respect owner data privacy; routing logic is local to owner's environment.
- depends on: metrics on task complexity and outcome; well-logged task history; existing mac_run_actions and mac_delegate capabilities


## What it asked for

_Nothing._
