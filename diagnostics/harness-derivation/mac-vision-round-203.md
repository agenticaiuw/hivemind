# Harness derivation — mac-vision — round 203

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a prioritized, actionable task list specifically for mac-vision to execute on the Mac, drawing dynamically from owner's current priorities and ongoing work."
- **useful because:** Currently no centralized task list exists for mac-vision; the system has scattered task facts and contextual clues but no direct queue to act on. A dedicated task prioritization feature will enable efficient, relevant, and timely actions targeting the owner's real goals on the Mac.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** seconds
- **cost:** low, mostly CPU and storage
- **security:** Only owner intent used; tasks are actions on their own Mac, minimal external data.
- **missing:** aggregation of current tasks from memory/facts, ranking logic for mac-vision relevance, integration with workbench contexts for ongoing jobs

### "Enable mac-vision to autonomously recover from failed UI actions by retrying steps, selecting alternatives, or escalating when UI state deviates from expectations during task execution."
- **useful because:** Current automation lacks resilience to UI changes or interruptions resulting in failed steps. Adding autonomous recovery strategies would enhance robustness, reduce human intervention, and improve fluency in task execution on the Mac.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds
- **cost:** medium CPU, some memory for state
- **security:** Recovery actions confined to the owner's Mac; requires careful step validation to prevent undesired operations.
- **missing:** UI error detection state machine; Alternative step selector; Escalation protocols; Persistent step execution logs

### "Leverage the connectivity between pendant and Mac to enable seamless voice command escalation to mac-vision for UI interaction when APIs or direct commands are insufficient."
- **useful because:** Owners can initiate voice commands on the pendant that escalate to mac-vision for parts of the workflow that need direct UI control, combining natural voice interaction with precise Mac control without needing to switch devices or contexts, improving fluidity and task completion.
- **path:** relay-realtime → mac-vision
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate CPU and network usage
- **security:** Voice inputs and potential UI commands remain under owner's control; escalations require authentication and confirmation.
- **missing:** voice command relay infrastructure; voice-to-UI interaction bridge; natural language understanding integrated with mac-vision capabilities

### "Provide a real-time, continuous, delegated Mac UI control loop that can understand complex multi-step workflows and recover automatically from UI failures or interruptions without human intervention."
- **useful because:** Today, mac-vision can execute isolated UI steps with accessibility permission but lacks a persistent, autonomous loop capable of running full workflows with error recovery. Enabling this would transform it into a true worker that can deal with real-world interruptions and UI changes, making the owner's Mac use more fluid and reliable.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** realtime
- **latency:** seconds
- **cost:** medium CPU and memory
- **security:** Full control over UI requires strict owner consent and careful safeguards. Input events and workflow data never leave the device unencrypted.
- **missing:** a persistent work execution state machine on mac-vision; advanced UI error detection and recovery algorithms; deeper workflow integration between workbench, vision-loop, and relay; robust delegation and handoff protocols for partial workflow interruption

### "Create an augmented Mac accessibility permission model that allows dynamic per-task consent and fine-grained control instead of all-or-nothing grant, improving privacy and trust for automated Mac control."
- **useful because:** Currently, mac-vision requires full accessibility permission, which may be too broad and risky for some owners. A more granular permission system allowing dynamic consent for specific tasks or actions would foster greater trust, security, and willingness to delegate control to automation.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** low
- **security:** Requires secure user interface for consent and robust enforcement; avoids leakage of control to unauthorized actions.
- **missing:** macOS-level extension or middleware to support dynamic accessibility grants; UI for requesting and managing per-task permissions; Integration with the agent control loop to enforce consent

### "Integrate pendant physical button input seamlessly with mac-vision task management and workflow control to enable quick manual confirmation, task switching, or escalation without voice commands or screen interaction."
- **useful because:** The pendant currently has a single button with limited gesture vocabulary. Using it meaningfully to interact with mac-vision's task and workflow system would provide a tactile, immediate way for the owner to control urgent or interactive tasks, confirm critical actions, and switch what mac-vision is focused on without interrupting other workflows or requiring verbal commands.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** sub-second
- **cost:** low
- **security:** Must avoid accidental activation or misuse; button presses should be firmly tied to explicit workflows or states; minimal data leaves the device.
- **missing:** firmware support for expanded button event encoding; Mac-side integration to interpret pendant inputs in context; UI feedback loop to owner on status and action taken


## What it asked for

_Nothing._
