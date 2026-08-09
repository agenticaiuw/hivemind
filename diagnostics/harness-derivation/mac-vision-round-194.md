# Harness derivation — mac-vision — round 194

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow me to convert owner-stated task facts into executable Mac UI workflows using the vision loop, so I can act on what the owner wants done on the Mac interface automatically."
- **useful because:** Today, owner task facts are passive and unexecuted. This capability turns stated tasks into real UI actions, making the AI effectively complete Mac tasks proactively and reliably, saving the owner time and effort.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 3s
- **cost:** medium: requires UI state reading and action validation
- **security:** Requires full accessibility control and trust, with reversible actions and confirmation steps to prevent unintended changes.
- **missing:** UI semantic interpretation module; Workflow to UI step compiler; Persistent UI workflow state store

### "Add a capability to verify and reconcile the intended state of complex Mac UI workflows claimed in workflow contexts against the actual UI as seen by the vision loop, to detect drift and ensure consistency."
- **useful because:** Currently only file system work has a claimed-vs-actual verification. Extending this to UI workflows would increase reliability of multi-step computer tasks and allow better recovery from interruptions or errors.
- **path:** mac-vision → mac-planner → faculty-perception
- **model tier:** gpt-5.6-luna
- **latency:** 4s
- **cost:** low-medium: mainly logic and UI snapshot comparison
- **security:** Requires access to live UI state and workflow tracking information, all locally controlled.
- **missing:** UI snapshot diffing and state tracking; Workflow context integration

### "Enable routines and reminders to trigger automated UI actions on the Mac through the vision loop, to complete scheduled tasks end-to-end without manual intervention."
- **useful because:** Routine commands currently produce text or reminders. Automating their completion via UI actions reduces owner workload, avoids forgotten steps, and integrates planning with execution.
- **path:** mac-planner → mac-vision → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 3s
- **cost:** medium: requires integration between scheduling and UI ability
- **security:** Requires secure automation with ability to confirm or abort destructive actions.
- **missing:** Routine-to-UI action compiler; Safe UI action execution environment

### "Develop a shared persistent store representing open, in-progress Mac UI workflows or subtasks, integrated with workbench contexts, to enable tracking, switching, and resumption of multi-step UI work."
- **useful because:** Today, multi-step computer tasks are tracked only in file state or ephemeral memory. Tracking UI workflows persistently lets the AI resume or delegate tasks sensibly, avoiding lost effort and confusion.
- **path:** mac-vision → mac-planner → faculty-judgement
- **model tier:** gpt-5.6-luna
- **latency:** 4s
- **cost:** low-medium: mostly local state management and API integration
- **security:** Local data only, requires stable API endpoints for workbench contexts.
- **missing:** Persistent UI workflow state persistence; UI-workflow and context API bindings

### "Provide a unified, AI-driven Mac vision agent that continuously monitors the owner’s active tasks and software UI state, predicts the next needed action, and executes proactive UI interactions without waiting for explicit commands to help the owner complete workflows faster and reduce cognitive load."
- **useful because:** Currently, task-driven UI actions require manual prompting or delegation and lack proactive automation. This capability would transform the Mac vision agent from a reactive executor into a proactive assistant that anticipates and accelerates task completion through seamless, intelligent UI interaction.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 2s
- **cost:** high, due to continuous UI and task monitoring and real-time plan generation.
- **security:** Requires maximum accessibility permission, strict safeguards against unintended automation, and owner override/confirmation workflows to protect from errors and unauthorized actions.
- **missing:** Real-time UI semantic extraction and prediction; Continuous task monitoring and intent prediction; Proactive action planner integrated with UI automator

### "Create a capability allowing the AI system to build an integrated mental model of the owner’s digital workspace—including all active documents, browser tabs, apps, and open UI states—and use that to enable seamless context switching and cross-application automation."
- **useful because:** Currently, context switching is limited and isolated to single apps or sessions. A workspace-wide mental model would allow the AI to understand the owner’s full digital state, anticipate needs, bridge gaps between apps, and automate multi-app workflows coherently.
- **path:** mac-planner → mac-vision → browser-extension → faculty-perception
- **model tier:** gpt-5.6-luna
- **latency:** 5s
- **cost:** high, because it requires extensive context gathering, fusion, and semantic understanding across multiple UI sources.
- **security:** Requires broader access across apps and strict privacy protections, with owner consent and transparent control over data.
- **missing:** Cross-application UI and session snapshot fusion; Semantic workspace modeling; Inter-app context sharing APIs

### "Implement a robust, multi-tiered confirmation and safety system on the Mac vision agent’s automated actions, including situational confirmations, step-by-step validation, rollback capabilities, and anomaly detection for error prevention."
- **useful because:** Automated UI interactions are risky and prone to mistakes that may disrupt the owner. This system would ensure mistakes are minimized, automations are reversible, and the owner retains ultimate control with confidence in safety and correctness.
- **path:** mac-vision → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 3s
- **cost:** medium, needing execution tracing, UI feedback, and anomaly analysis.
- **security:** Involves capturing and storing UI state and actions temporarily with strict access controls and audit trails.
- **missing:** Execution tracing on UI actions; Rollback and undo integration; Anomaly and error detection modules


## What it asked for

_Nothing._
