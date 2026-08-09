# Harness derivation — mac-vision — round 242

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to manage an integrated Mac task prioritization and interaction queue within mac-vision, combining memory facts tasks and Reminders tasks, with natural language commands to start, pause, complete, and reorder tasks on the Mac interface."
- **useful because:** Today the owner has no consolidated Mac task manager accessible through AI that actively prioritizes and manages tasks, leading to disconnected workflows and manual juggling between reminders and task lists.
- **path:** mac-vision → mac-planner → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** real-time interaction under 3 seconds
- **cost:** moderate LLM usage for prioritization and status updates per interaction
- **security:** Requires access to Apple Reminders data and memory facts; needs owner consent and secure handling of private task data.
- **missing:** A consolidated task state store unifying memory facts and reminders with prioritization metadata; UI elements or voice interaction flows in mac-vision and relay to allow task management; APIs allowing reorder and status update of tasks with confirmation dialogs

### "Enable a contextual assistant that can monitor live Mac UI state via accessibility (mac-vision) and proactively suggest or perform follow-ups for multi-step workflows, including error recovery, confirmations, and optimizations of repetitive workflows."
- **useful because:** Currently, the system lacks a proactive assistant aware of live UI state and step progress, which hampers automation robustness and smooth workflow completion. A live contextual assistant can improve efficiency and reduce owner intervention or frustration.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to few seconds for suggestions and follow-ups
- **cost:** Moderate due to continuous UI analysis and LLM guidance
- **security:** Requires extensive access to live accessibility data and workflow state; data privacy controls essential.
- **missing:** Robust real-time UI state introspection usable by the assistant; Event and context listeners for workflow step transitions; Proactive action suggestion and confirmation UI/voice interfaces

### "Implement a continuous learning capability where mac-vision observes the owner's manual corrections and input during Mac workflows to improve future automation and error recovery."
- **useful because:** Automation often fails due to unexpected UI changes or context slips; learning from manual corrections helps tailor the automation to the owner's actual habits and environment, improving efficiency and trust.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** Background or batch processing with asynchronous updates
- **cost:** Low to moderate cost in model training and data handling, mostly offline.
- **security:** Requires recording some user interactions and corrections while respecting privacy and consent; secure storage and processing mandatory.
- **missing:** Mechanisms to record and interpret manual corrections; Data pipelines for incremental model improvement; UI to review and approve learned automations

### "Create a unified history and undo system for all Mac UI interactions performed by mac-vision, including reversible actions from mac_run_actions and delegated steps from mac_delegate, with user-accessible control to review and rollback."
- **useful because:** Currently, there is limited visibility and control over what the AI has done on the Mac and no systematic way to undo multi-step workflows. A unified undo/history improves trust, safety, and user control over automated Mac interactions.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** Sub-second to interactive for undo commands
- **cost:** Low to moderate storage and compute for state snapshots and action logging
- **security:** Requires secure storage of action logs and state snapshots; user authentication for undo commands.
- **missing:** Comprehensive action logging and snapshotting APIs; UI and API for listing, reviewing, and undoing actions; Integration with job receipts and execution records

### "Enable the AI system to proactively monitor and handle Mac OS notifications and dialogs, especially error or confirmation dialogs, during mac-vision workflows, automatically or with owner confirmation."
- **useful because:** Dialog pop-ups and system notifications often interrupt automation and require manual clearance. Handling them proactively reduces interruptions, improving workflow reliability and user experience.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** Seconds for dialog detection and response
- **cost:** Low to moderate compute for observation and classification
- **security:** Needs monitoring of system dialogs, which may contain sensitive info; privacy must be assured.
- **missing:** Dialog detection and classification mechanisms; UI automation hooks for dialog dismissal or interaction; Owner confirmation interfaces for sensitive dialogs


## Changes it proposed to its own stack

### `integration` — Define and implement a system-wide dynamic prioritization and task handoff policy that actively interprets owner context, urgency, and task interdependencies to guide mac-vision and other agents in what to work on next and when to delegate.
- **owner gets:** Without a real prioritization and handoff system, the owner faces fragmented and inefficient task management. This system enables smooth focus shifts across devices and agents, optimizing time and cognitive load.
- effort: Major design and development effort involving multi-agent coordination and UI/UX work in mac-vision and other surfaces.  ·  risk: Misinterpretation of owner urgency or context leading to prioritization errors; fallback to manual override possible.
- cost: High due to continuous context tracking and computation plus possible UI enhancements.  ·  latency: Real-time prioritization with slight latency added to interaction response times.
- security: Requires secure handling of personal context and task data, with owner control over sharing scopes.
- depends on: capability to read and write owner goals and task metadata; integration with mac-vision UI and mac_delegate workflows

### `hardware` — Add a dedicated secondary physical input device or gesture sensor on the Mac or pendant to provide non-conflicting explicit user commands and confirmation, freeing mac-vision from relying solely on ambiguous or limited UI triggers or voice commands.
- **owner gets:** The owner's current input device for state changes and confirmations is limited to very few buttons with constrained gestures, leading to ambiguity and limited control. A dedicated user input device would provide safer, more reliable manual intervention and control in complex workflows.
- effort: Moderate hardware design and integration effort, plus driver and software integration.  ·  risk: Hardware cost and potential user inconvenience; integration errors.
- cost: Material and development costs for hardware and firmware changes, plus slight power and latency overhead.  ·  latency: Minimal; input device is physical and direct.
- security: Additional hardware input must be secured from spoofing and accidental triggers.

### `model-routing` — Integrate a dedicated command and control LLM model tier for low-latency prioritisation, task management, and UI interaction planning distinct from the main reasoning models, optimizing responsiveness and reducing cost.
- **owner gets:** The owner benefits from a system that feels instant and responsive for UI tasks and decisions, without waiting for full large model runs each time, making Mac interactions smoother and more natural.
- effort: Moderate to major engineering effort for model pipeline design and changes to agent architecture.  ·  risk: Possible context mismatch or loss of nuance in priority decisions if tiering is imperfect; fallback to full model preserves safety.
- cost: Reduced compute cost on average but some infrastructure overhead.  ·  latency: Significantly faster response times for UI decisions and task prioritisation.
- security: Additional model endpoint needing secure isolation; sensitive context handling remains.
- depends on: Clear interface definitions between tiers; Availability of specialized lower-tokens models for control

### `dashboard-ux` — Build a unified task and workflow dashboard integrating real-time Mac tasks from memory facts and Reminders, current mac-vision workflow state, undo history, and proactive AI suggestions, accessible from Mac and pendant.
- **owner gets:** Currently, task, workflow, and action history visibility is fragmented across systems. This dashboard gives the owner a single place to understand, control, and interact with AI-driven Mac tasks and automations, boosting productivity and trust.
- effort: Moderate to major UI/UX and integration engineering effort.  ·  risk: Potential overload of information or distraction if not designed well; requires ongoing maintenance.
- cost: Moderate bandwidth and compute cost for live dashboard updates and integrations.  ·  latency: Sub-second to a couple seconds for UI responsiveness.
- security: Must securely aggregate sensitive task, workflow, and UI interaction data; robust authentication needed.
- depends on: Access to all Mac tasks and contexts; Undo and history data; Integration with AI proactive suggestion pipelines


## What it asked for

_Nothing._
