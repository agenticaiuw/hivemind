# Harness derivation — mac-vision — round 241

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide me with a continuous, ranked, priority-driven list of Mac tasks that I want done right now, and execute them safely and with confirmation as needed."
- **useful because:** The owner has no current mechanism that prioritizes Mac tasks by urgency or importance, or integrates multi-step workflows. This tool would make the Mac-vision agent genuinely proactive and able to complete useful work efficiently.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** seconds per decision; realtime for immediate actions
- **cost:** Moderate; mostly model runtime for prioritization and planning, plus cost of running short Mac actions
- **security:** Needs privileged access and input event trust; confirmation required for destructive or high-risk actions; respects owner's stated preferences and permissions
- **missing:** More structured signals about active task priority and deadlines from owner or integrated apps; Better context persistence on multi-step workflow state and UI verification post-execution; Robust error detection and recovery for failed UI interactions; Enhanced coordination protocol between voice, browser, and Mac control surfaces

### "Capture actual Mac UI states after multi-step delegated workflows to confirm task completion or identify deviation."
- **useful because:** Currently the system knows only the declared result of a multi-step workflow but cannot verify if the UI state on screen matches the intended outcome. Capturing this enables robust error detection and manual followup.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes depending on complexity
- **cost:** Low to moderate, mostly model runtime and accessibility API use
- **security:** Requires full accessibility access and trust; UI snapshots stored securely; no personal data leaves device without owner consent
- **missing:** UI state capture and diff capability after workflow execution; Analysis tools for matching intended vs actual UI state; Visual verification user interface

### "Seamless integration of voice commands, Mac UI control, and browser web sessions for multi-modal task execution and context sharing."
- **useful because:** The owner uses voice via pendant, Mac UI controls, and browser logged-in sessions together. Coordinated execution across these surfaces would allow flawless task flows, reducing friction and duplicated effort.
- **path:** relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** milliseconds to seconds for integration steps
- **cost:** Moderate; model cost and relay infrastructure usage
- **security:** Requires cross-device context sharing with strong encryption and ACLs; voice commands need robust recognition and confirmation; no sensitive data leaks between surfaces
- **missing:** Cross-surface context propagation mechanism; Shared identity and session tokens for the user across surfaces; Event synchronization and conflicts resolution protocol

### "Provide a real-time, clear, and secure status dashboard for the owner showing current Mac UI state, task execution progress, errors, and next suggested actions."
- **useful because:** The owner currently lacks clear visibility into what the Mac control agent is doing or blocked on. A status dashboard would build trust and enable manual intervention if needed.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** real-time or near real-time
- **cost:** Low to moderate depending on UI complexity; mostly front-end and data aggregation
- **security:** Dashboard must run locally or securely on owner's Mac with no sensitive data leaving without consent; access controlled.
- **missing:** Real-time data aggregation from mac_run_actions, mac_delegate, relay_job_status; Local rendering UI component with authentication protocols

### "A unified interface for the owner to define, prioritize, and manage complex multi-step workflows and single Mac tasks, interoperable across Mac UI control, voice, and browser sessions."
- **useful because:** Currently the owner cannot express detailed, priority-based instructions or adjust them dynamically for the Mac-vision agent or the system as a whole. This would give them direct control over what gets done, when, and how.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** interactive latency, seconds per update
- **cost:** Moderate to high, requiring UI/UX development, natural language processing, and integration layers
- **security:** Must securely manage owner input and task data with fine-grained access controls and confirmation for destructive commands
- **missing:** A dedicated task/workflow authoring UI; Backend support for dynamic task priority and deadline management; Cross-surface synchronization of active workflows and owner modifications

### "Dynamic, verified Mac UI interaction replay and rollback system that records accessibility events and UI state changes for any multi-step delegated workflow, enabling error recovery and undo."
- **useful because:** Currently, once a multi-step delegated workflow executes, there is no guaranteed way to verify actual UI state changes or roll back partial work on failure. This capability would increase reliability and owner trust by enabling safe retries and undo.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes after each workflow execution
- **cost:** Moderate; storage and compute for event capture and UI snapshots, plus UI to control replay/undo
- **security:** Requires strict access control to accessibility APIs and captured UI data, no data leaving device without consent, auditing of replay actions
- **missing:** Event capture and replay tooling for macOS accessibility events; Persistent storage for UI state snapshots and event logs; Undo/rollback UI and interaction logic

### "Context-aware, in-the-moment agent memory injection that highlights only the most relevant Mac UI state and owner preferences before each task execution, minimizing token usage and maximizing accuracy."
- **useful because:** Allows the Mac-vision agent to focus on what matters now without flooding the model with irrelevant history, improving task success and responsiveness.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds per task start
- **cost:** Low to moderate, mostly model runtime for context selection algorithms
- **security:** Memory snippets must be encrypted and tightly access-controlled, with owner control over what is saved and exposed.
- **missing:** Selective memory retrieval and injection algorithms; Context relevance ranking models or heuristics; Integration with existing memory stores for Mac-focused facts and preferences

### "A high-fidelity simulation and test environment for mac-vision UI automation to preview and verify task plans before executing them on the actual Mac."
- **useful because:** Allows safe testing of complex multi-step workflows to prevent errors or disruptions on the real system, increasing owner trust and usability.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** interactive minutes for large workflows
- **cost:** Moderate to high depending on simulation fidelity; mostly development time and compute resources for simulation engine.
- **security:** Simulation data stays local; no UI events reach the real system during simulation; care to avoid leaks of personal UI data in logs or remote storage.
- **missing:** Virtual UI environment with accessibility tree emulation; Task plan playback engine connected to virtual UI; Simulation result verification and reporting UI


## Changes it proposed to its own stack

### `model-routing` — Introduce dynamic routing of task and workflow requests to specialized models based on task complexity and modality (e.g., simple Mac action vs. complex multi-modal workflow with voice, UI and browser).
- **owner gets:** This would optimize resource use and latency, giving the owner fast responses for simple requests while enabling deep context understanding and coordination for complex ones.
- effort: Medium, requiring model selection logic integrated across involved surfaces and orchestrator.  ·  risk: Incorrect routing may cause inappropriate responses; mitigation through fallback logic and continuous model performance evaluation.
- cost: Cost-efficient by reducing unnecessary high-tier model invocations on simple tasks.  ·  latency: Decreased latency for simple tasks, with slight added routing overhead.
- security: No new risks beyond existing model use; routing decisions do not inspect private data beyond task metadata.

### `hardware` — Add a dedicated, low-latency hardware button on the pendant for 'Confirm next Mac action', reducing accidental triggers and improving owner control over destructive or high-risk tasks.
- **owner gets:** The owner can easily approve or reject actions with a tactile, physical control, improving safety and interaction speed for Mac vision agent operations.
- effort: Small hardware revision and FPGA or firmware update on pendant to add and emit button events.  ·  risk: Minimal hardware risk; potential for accidental presses reduced by button placement and debounce logic.
- cost: Low, incremental hardware cost for an additional button and minor firmware complexity.  ·  latency: Near-zero; hardware button is immediate on press.
- security: Improves security by forcing explicit owner approval for sensitive actions.


## What it asked for

_Nothing._
