# Harness derivation — mac-vision — round 185

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a real prioritized Mac task and goal manager that integrates with all agents to feed work to mac-vision and others."
- **useful because:** Currently there is no durable, ranked list of meaningful Mac tasks that an agent can pick from to act on. The owner often needs help managing complex task flows that span apps and sessions. Such a capability would let agents focus on what the owner actually wants next, keeping momentum and reducing cognitive load.
- **path:** mac-planner → mac-vision → mac-terminal → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low per invocation, dominated by reading/writing from local storage
- **security:** All data is private and local. Agents would coordinate work but never expose data externally without explicit request. The biggest risk is accidental data loss or corruption.
- **missing:** A unified datastore for tasks and goals with full CRUD API, priority, deadline, dependency fields; UI and voice hooks for the owner to add, update and reprioritize tasks; Inter-agent protocols for locking and work claiming

### "Have an integrated execution status and narration facility that listens to relay_job_status for Mac actions and reports clear progress and errors to the pendant speaker and UI."
- **useful because:** The owner frequently needs reassurance on the success or failure of Mac-initiated actions. Currently, there is no seamless flow of execution status from Mac agents to the owner. This facility would provide clear, user friendly verbal feedback and state in the UI, improving trust and usability.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** under a second for updates
- **cost:** very low, primarily light database polling and short synthesis
- **security:** Only status and narration data is handled; no new control surface. Recorded verbal replies could reveal task content, so data must remain local unless explicitly allowed.
- **missing:** relay job event hooks for continuous reporting; integration with pendant speaker and UI surfaces

### "Enable the mac-vision agent to safely interact with the Mac's full UI asynchronously, with undo and rollback support, for complex workflows requiring UI exploration, text entry, and control, beyond the current short action sets."
- **useful because:** The owner wants the AI to complete complex tasks currently requiring multiple clicks, window switching, and input that cannot safely be done with short mac_run_actions. This capability would allow the Mac to be controlled fully but with fail-safe undoable steps and history, increasing reliability and allowing mac-vision to handle complex, ambiguous jobs.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes, depending on task complexity
- **cost:** medium, based on extended UI observation, planning, and historical state storage
- **security:** Access to full UI control is a high risk permission; undo/rollback mitigates risk. Requires explicit owner opt-in and transparency.
- **missing:** Undoable UI state snapshot and rollback system; Extended macOS Accessibility integration for full UI traversal and action; Long term per-step history storage; Agent coordination protocols to pause/resume execution


## Changes it proposed to its own stack

### `integration` — Enable the mac-vision computerUseLoop by default when macOS Accessibility is granted to the AI Pendant Agent binary and computerUse.loopEnabled flag is set true, removing fallback to pixel-based click automation. This will let mac-vision safely automate complex UI tasks without disturbing the owner or causing focus-stealing interruptions.
- **owner gets:** This is the first step to reliable, safe, and low-impact full UI automation on the Mac by the mac-vision agent, enabling real multi-step computer workflows driven directly by AI without owner disruption.
- effort: Medium engineering effort to coordinate macOS permission prompting, feature flagging, and testing.  ·  risk: Potential interruptions if accessibility is granted but permissions are misused; mitigated by per-action step confirmation requirements and rollback.
- cost: Negligible API cost; no extra hardware cost.  ·  latency: Improves latency and reliability of UI automation by removing fallbacks.
- security: Sensitive permission required; must be opt-in by the owner explicitly.
- depends on: ownership grant of macOS Accessibility permission to AI Pendant Agent binary; computerUse.loopEnabled true grant


## What it asked for

_Nothing._
