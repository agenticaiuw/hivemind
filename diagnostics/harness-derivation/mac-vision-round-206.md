# Harness derivation — mac-vision — round 206

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a dynamic multi-step Mac task manager coordinating mac-vision and the local Mac agent for complex workflows"
- **useful because:** Allows mac-vision to plan, execute, and monitor complex multi-step Mac tasks based on owner goals; reduces work fragmentation; enables reliable handoff and progress tracking; improves control feedback and undo
- **path:** mac-planner → mac-vision → faculties
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** moderate due to multi-step planning and monitoring
- **security:** Needs owner consent; must ensure task isolation and undo; stores and logs task step states
- **missing:** UI state verification mechanism keyed to workflow steps; owner task priority and ranking system; real-time UI feedback channel; undo/correction tracking

### "Create a UI state verifier that reconciles live on-screen Mac UI states with intended multi-step workflow steps"
- **useful because:** Provides mac-vision with actual control state verification, reduces error and fallback risks in mac_delegate workflows, enables safe undo and failure detection, and improves reliability of automation
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** low to moderate for state comparison and reporting
- **security:** Requires access to live UI control state; sensitive to owner UI privacy; must ensure state info is not leaked externally
- **missing:** Access to UI state snapshots tied to workbench contexts; bidirectional mapping between UI state and workflow steps

### "Provide a prioritization and ranking model for the owner's Mac surface task facts including deadlines, dependencies, and urgencies"
- **useful because:** Gives mac-vision and other Mac surface agents a clear, owner-aligned ordered backlog of what to do, improving responsiveness and avoiding duplicated or misplaced effort
- **path:** mac-planner → mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** low
- **security:** Task facts are owner data but not sensitive; respect owner privacy
- **missing:** Enhanced task facts schema for deadline, priority, dependency; ranking algorithms; UI for owner to review and rearrange priorities

### "Create a direct UI feedback channel from mac-vision for narrating and refining stepwise Mac UI plans based on real-time accessibility control state and undo feedback"
- **useful because:** Allows mac-vision to communicate intended UI actions and receive real-time feedback on success, failure or changes, enhancing reliability and user trust
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** milliseconds to seconds
- **cost:** low to moderate for feedback processing
- **security:** Must not leak sensitive UI info externally; feedback is local to reduce risk
- **missing:** Real-time streaming UI control state and accessibility event subscription; bidirectional UI narration channel

### "Owner should have a fully integrated Mac task management system exposing current and historical multi-step workflows, with explicit task state, progress tracking, and undo functionality."
- **useful because:** This empowers the owner to delegate complex Mac work confidently, know what is in progress or complete, and recover from issues without losing context.
- **path:** mac-vision → mac-planner → faculties
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** moderate, requires new persistent state and UI integration
- **security:** Sensitive workflow and state data must be protected; undo operations potentially hazardous and must be safe
- **missing:** Persistent multi-step workflow state on Mac agent; bidirectional UI state synchronization; owner-facing task UI; undo and recovery mechanisms

### "Owner should have a real-time Mac UI accessibility event stream for mac-vision, allowing live UI control state updates and action verification."
- **useful because:** Live UI control state visibility dramatically increases automation reliability, reduces error recovery time, and enables responsive interactive flows.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** milliseconds
- **cost:** moderate due to event streaming and state tracking
- **security:** Such a stream must enforce strict owner privacy and allow fine-grained permission control
- **missing:** Native macOS accessibility event hooks with low latency relay; event deduplication and filtering; secure streaming mechanisms

### "Owner needs a context-aware Mac surface task prioritization and dependency modeling system that dynamically ranks and exposes actionable work."
- **useful because:** Provides mac-vision and other surfaces clarity on urgency and order of Mac tasks, preventing duplicated work and missed deadlines.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** low to moderate for ranking models and task metadata storage
- **security:** Task and dependency data are owner private and must be securely stored and accessed
- **missing:** Enhanced task metadata schema including deadlines, dependencies, and priority; ranking algorithms; metadata synchronization with mac-vision


## Changes it proposed to its own stack

### `firmware` — Add a dedicated secure low-latency event relay from native macOS accessibility service to the mac-vision agent for live UI control state streaming and event push.
- **owner gets:** This would enable real-time verification of UI states and actions, improving reliability and responsiveness of Mac automation.
- effort: Moderate to high, requires native macOS development and integration with mac-vision stack.  ·  risk: Potential for privacy or security leaks if events are not carefully filtered and encrypted. Recovery possible by disabling event stream.
- cost: Moderate increase in computational and networking resources.  ·  latency: Sub-second latency improvements in UI state updates.
- security: High, needs strict access controls and encryption.

### `interaction` — Enable mac-vision to produce natural language narration and refinement of each UI action step during multi-step tasks, with interactive owner confirmation and undo support.
- **owner gets:** This improves trust and understanding for the owner by narrating what the Mac agent plans to do and receiving live feedback or corrections, reducing errors and unwanted actions.
- effort: Moderate, requiring upgrades to mac-vision's verbal feedback and command parsing, plus UI control synchronization.  ·  risk: Risk of increased latency or unwanted interruptions; mitigated by careful UX design and overrides.
- cost: Low to moderate for additional text synthesis and processing.  ·  latency: Slight increase due to interaction overheads.
- security: Low, narration is local and owner-facing.
- depends on: Real-time UI feedback channel; Multi-step task management system


## What it asked for

_Nothing._
