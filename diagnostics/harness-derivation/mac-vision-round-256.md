# Harness derivation — mac-vision — round 256

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide persistent live synchronization of Mac agent task facts and workbench contexts with the mac-vision agent active state, enabling reliable claiming and resumption of multi-step Mac workflows."
- **useful because:** This prevents lost progress, enables retry and restart of interrupted sequences, and gives the owner coherent control over all ongoing multi-step Mac tasks, with full live tracking and verification of UI and disk states.
- **path:** mac-local-agent → pendant → relay
- **model tier:** background
- **latency:** minutes
- **cost:** Low API cost, mostly data synchronizations and state diffing
- **security:** Syncing detailed UI and workflow state may expose sensitive info; must be encrypted and permissioned properly
- **missing:** full UI snapshot integration with workbench context; resumable workflow executor

### "Automate intelligent prioritization and execution of the owner's current tasks on the Mac by reading memory facts, planning the necessary steps, executing them through mac_run_actions or mac_delegate, and reporting status live with recoveries as needed."
- **useful because:** This is the highest value feature: the owner delegates explicit current tasks and the system autonomously carries out the required Mac operations accurately, speeding work and reducing manual effort and errors.
- **path:** pendant → mac-local-agent → relay
- **model tier:** realtime
- **latency:** seconds to minutes depending on task complexity
- **cost:** Moderate to high; involves continuous planning, UI interaction, job status monitoring, and confirmations
- **security:** Must respect owner's permissions and approval especially for destructive actions; all sensitive data remains local; failures must be fully observable and recoverable
- **missing:** detailed multi-step workflow data; live accessibility snapshots; rich job receipts metadata

### "Enable the mac-vision agent to autonomously monitor and verify the actual on-screen UI state against planned multi-step Mac workflows from the workbench contexts, providing a true resume and retry capability for interrupted or incomplete workflows."
- **useful because:** Today, there is no live linkage between the mac-vision agent's perceived UI state and the planned multi-step workflows in workbench contexts. This limits reliable resumption and recovery of complex Mac tasks. Enabling this will let the owner trust interruption-free task continuity, reduce repeated manual fixing, and increase automation reliability.
- **path:** pendant → mac-local-agent → relay
- **model tier:** realtime
- **latency:** seconds for verification steps
- **cost:** Moderate; involves continuous UI state polling, comparison, and event management
- **security:** Requires ongoing accessibility permission; UI state includes sensitive information; transmissions must be secure and privacy-protecting
- **missing:** Low-latency, structured, live UI snapshot integration with workbench context API; Enhanced job receipt metadata from UI actions to confirm success/failure; Protocol for graceful fallback when UI or disk states diverge

### "Build a Mac task discovery and prioritization system integrated directly with the owner's live memory facts, which produces a persistent, ranked task list the mac-vision agent can use to plan and execute actions without human intervention or separate queues."
- **useful because:** Currently the owner only has human-entered task facts and no integrated, machine-readable prioritized to-do list that the mac-vision agent can consume to schedule and perform work autonomously. Creating this capability enables ongoing AI-driven Mac task management that responds dynamically to new or changing owner priorities without manual restatement.
- **path:** mac-local-agent → pendant
- **model tier:** realtime
- **latency:** sub-second to seconds for task updates and planning
- **cost:** Low to moderate; reading memory facts and ranking is lightweight, plus API calls for planning
- **security:** Task content may include sensitive info; ensure access control and opt-ins; no automatic destructive actions without confirmation
- **missing:** Standardized, structured machine-readable task list production from memory facts; Planning integration from task list to mac_run_actions and mac_delegate invocation

### "Add a global owner setting and policy that automatically manages the mac-vision agent's interaction frequency and confirmation depth based on task criticality and owner presence, reducing unnecessary interruptions while retaining safety for destructive actions."
- **useful because:** Currently, every mac-vision interaction requires explicit permission or confirmation, which can be disruptive and limit seamless automation. An adaptive policy would make the AI assistant more user-friendly and tailored to the owner's context and preferences, balancing autonomy and control.
- **path:** pendant → mac-local-agent
- **model tier:** realtime
- **latency:** Real-time or near real-time evaluation with task execution
- **cost:** Low; policy evaluation is computationally inexpensive
- **security:** Policy must never override owner safety preferences; destructive actions always require explicit confirmation
- **missing:** Global user preference store; Dynamic context-aware policy interpreter integrated with mac-vision action loop


## What it asked for

_Nothing._
