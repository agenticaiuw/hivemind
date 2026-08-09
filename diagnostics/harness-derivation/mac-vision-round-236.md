# Harness derivation — mac-vision — round 236

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision loop to autonomously perform multi-step, reliable, reversible Mac UI workflows based on the owner's current tasks, with full state reconciliation between planned and actual UI states and seamless recovery from failures."
- **useful because:** The owner can delegate complex Mac UI control tasks to the AI Pendant Agent with confidence that actions are accurately completed or undone, reducing manual interference and errors.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** medium per invocation dominated by the loop planning and state reconciliation model usage
- **security:** Requires trusted accessibility permissions; must prevent unintended destructive actions and ensure privacy of screen content.
- **missing:** A low-level, fine-grained UI interaction model in mac-vision to perform actions like clicks, typing, menu navigation, and event observation.; A persistent reconciliation mechanism to compare intended UI changes with actual UI state read via accessibility tree after each step.; A failure detection and rollback system integrated with mac-vision using existing reversible action receipts from mac_run_actions or extended for UI steps.; A secure user approval or override interface on wearable pendant or Mac for confirming high-impact or ambiguous actions.

### "Maintain and prioritize a durable, rankable Mac-specific task list for the owner that drives mac-vision actions and coordination with other agents."
- **useful because:** Currently, there is no system storing prioritised, structured intent for the Mac tasks. A durable, authoritative Mac task list lets the mac-vision focus on what the owner truly wants done, enabling better planning and performance.
- **path:** mac-vision → mac-planner → faculty-judgement
- **model tier:** gpt-5.6-luna
- **latency:** under one second
- **cost:** low (mostly storage and retrieval)
- **security:** Task data may contain private information; needs encryption and access control to the owner only.
- **missing:** A dedicated storage and coordination layer for Mac task facts, updated by owner input and agent discovery.; A ranking and prioritization algorithm tuned to owner preferences and urgency indicators.; Integration hooks so mac-vision queries and consumes this authoritative task list in planning and execution.

### "Provide mac-vision with live verification of UI action results by comparing the intended UI state changes against the actual visible screen and accessibility tree state after each step, with an automated retry or fallback plan if discrepancies are detected."
- **useful because:** Currently, mac-vision and other agents must trust the promised outcome of UI automation steps. Live verification prevents errors, UI drift, or inconsistent states, increasing reliability and owner trust.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** gpt-5.6-luna
- **latency:** 5 seconds
- **cost:** medium, dominated by UI tree reading and diffing plus reasoning model usage
- **security:** Visibility of on-screen content is sensitive. Verification must be local or encrypted and permissioned.
- **missing:** A reconciliation and diffing mechanism for accessibility-tree snapshots vs. intended UI control states.; Integration of state verification into the mac-vision control loop and mac_run_actions receipts.; Fallback planners to recover or retry on detected inconsistencies.

### "Enable collaboration between mac-vision and browser-extension agents to perform mixed UI and web workflows seamlessly, passing partial results, context, and UI state between them for the owner's tasks."
- **useful because:** Many owner tasks span both native Mac apps and web applications. Coordinated multi-agent collaboration allows efficient, robust handling of complex cross-environment flows without duplication or context loss.
- **path:** mac-vision → browser-extension → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds to tens of seconds
- **cost:** medium, dominated by communication and planning model usage
- **security:** Requires synchronized context sharing with encryption and access control; browser content and native UI visibility are privacy sensitive.
- **missing:** Cross-surface communication protocol and context synchronization between mac-vision and browser-extension.; Shared memory or state abstraction for passing partial steps and results between agents.; Planning and execution orchestration robust across heterogeneous UI environments.


## What it asked for

_Nothing._
## Its own summary

Proposed key capabilities the owner lacks today: (1) autonomous, multi-step, reversible Mac UI workflows with full state reconciliation and failure recovery in mac-vision; (2) a durable, rankable, Mac-specific task list driving mac-vision actions; (3) live UI action result verification after each step; (4) deep collaboration between mac-vision and browser-extension for cross-environment workflows; (5) hardware expansion with a dedicated pendant button for interaction confirmation. Achieving these requires new UI interaction models, state reconciliation systems, task storage and ranking layers, cross-agent protocols, and minor hardware additions. This would create a uniquely powerful, reliable, and owner-aligned Mac automation experience not available today.

**Biggest unknown:** The precise design and implementation of a fail-safe, fine-grained UI interaction model and reconciliation mechanism in mac-vision that can operate continuously without focus theft or unintended side effects, and robustly handle macOS accessibility complexities.

