# Harness derivation — mac-vision — round 255

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I want to start the mac-vision accessibility loop to read and control the Mac UI based on the granted Accessibility permissions and loop enabled flag. Provide capability to read accessibility tree snapshots and run controlled UI interactions on the Mac."
- **useful because:** This allows mac-vision to perform the essential function of interpreting and interacting with the Mac UI components to automate tasks, which cannot be done otherwise. It leverages permissions already granted by the owner.
- **path:** mac
- **model tier:** realtime
- **latency:** sub-second interaction latency
- **cost:** mostly model inference cost, very low API calls
- **security:** Requires trust as it acts on the UI, but user consent is demonstrated by Accessibility grant. No screen recording is used.
- **missing:** An API route or tool that exposes accessibility tree snapshots for mac-vision and a safe, reversible method to run UI control actions asynchronously.

### "I want to read the live open work contexts assigned to mac-vision to track partial or interrupted work, using the /workbench/contexts route or any equivalent."
- **useful because:** Knowing exactly what open work the owner wants mac-vision to focus on ensures no duplication or wasted effort. It provides continuity across interrupted sessions and makes sure mac-vision's actions align with owner's stated priorities.
- **path:** mac
- **model tier:** realtime
- **latency:** under a second
- **cost:** negligible API call costs
- **security:** No sensitive data beyond work context is exposed. Owner grants read access to the workbench contexts by running the mac-vision agent.
- **missing:** The route /workbench/contexts or equivalent needs clear documentation for use by mac-vision, reliable update of contexts on work handoff, and authorization for mac-vision to read them.

### "Enable mac-vision to perform continuous UI monitoring and interaction with visual state confirmation using the macOS Accessibility API combined with occasional screen pixel verification to ensure state correctness."
- **useful because:** This would allow mac-vision to verify that UI actions it performs actually change the visible state as intended, reducing the risk of silent failure or unexpected UI changes that Accessibility events alone may miss.
- **path:** mac
- **model tier:** realtime
- **latency:** sub-second for verification after actions
- **cost:** moderate due to occasional pixel capture and intensive comparison logic
- **security:** Requires permission for screen recording or pixel access; must be clearly disclosed to owner and opt-in only.
- **missing:** A hybrid UI state verfication mechanism combining Accessibility tree data with pixel-based screenshot confirmation; a secure and explicit owner's opt-in for screen pixel capture separate from Accessibility grant.

### "Provide a real-time prioritization and open task queue for mac-vision derived from owner-stated task facts and multi-surface input, integrated with the workbench context system for tracking."
- **useful because:** Currently mac-vision lacks a live ranked task list of owner goals to prioritize its actions, causing potential inefficiency and lost focus on the owner's true priorities. A live prioritized task list would enable intelligent, context-aware action sequencing and owner alignment.
- **path:** mac
- **model tier:** realtime
- **latency:** under a second for updates
- **cost:** low for metadata and task ranking computations
- **security:** Requires access to owner's task data, must respect privacy and task sensitivity settings; owner control and transparency is essential.
- **missing:** A multi-surface, durable task priority queue integrated into the memory projection accessible to mac-vision with pull and push capabilities.; A task ranker and filter subsystem that respects owner-set priorities and urgency.

### "Create an integrated safety validation layer for Mac control automation that uses multi-modal confirmation: accessibility tree state, on-screen visual pixel checks, and owner safety policies before any destructive or irreversible action."
- **useful because:** This would maximize the owner's safety and confidence in mac-vision automations by requiring multiple layers of confirmation and policy compliance before high-impact changes, preventing accidental data loss or system disruption.
- **path:** mac
- **model tier:** realtime
- **latency:** sub-second to a few seconds depending on action complexity
- **cost:** moderate due to multi-modal data processing and policy evaluation
- **security:** Requires secure policy storage and audit trails of decisions; owner control over policy strictness is mandatory.
- **missing:** A unified multimodal verification layer combining accessibility tree readings, pixel state checks, and owner-configurable safety policies.; Interface for owner to define and update safety policies and override conditions.

### "Create a surface-agnostic open work and task state sync system that can unify owner priorities, facts, and live workflow context across all devices: Mac, iPhone, browser, pendant, and relay, allowing mac-vision and others to coordinate and delegate naturally."
- **useful because:** Owner often uses multiple devices and the current system silo task or context data. A unified cross-surface task state management would enable seamless continuation, delegation, and load balancing of owner-directed work, improving efficiency and user experience.
- **path:** mac → ios → browser → pendant → relay
- **model tier:** realtime
- **latency:** sub-second to sync updates
- **cost:** moderate depending on sync frequency and data volumes
- **security:** Needs strong encryption and access controls to protect sensitive work and data across devices.
- **missing:** Cross-device task state sync protocol and storage backend.; Unified API for work/context read/write accessible by all surfaces and agents.; Conflict resolution and task assignment management in multi-device context.


## Changes it proposed to its own stack

### `interaction` — Integrate mac-vision's accessibility loop with an explicit undo and error recovery mechanism based on UI snapshots and workbench's claimed-versus-actual job states to avoid destructive or irreversible actions without owner control.
- **owner gets:** Prevents unintended destructive actions by mac-vision through clear rollback paths and error detection in the UI, increasing user trust and safety in automated Mac control.
- effort: High, requiring substantial coordination between UI state monitoring, job ledger integration, and owner feedback channels.  ·  risk: Implementation complexity could cause new failure modes; extensive testing and fallback mechanisms needed to avoid deadlocks or stuck states.
- cost: Moderate, due to additional processing and state storage.  ·  latency: Slight increase in response latency due to verification and rollback logic.
- security: Requires secure storage and access handling for UI snapshots and job state data.
- depends on: mac-vision accessibility loop capability; workbench context and job ledger APIs

### `firmware` — Enhance pendant firmware to perform local pre-validation of Mac UI control intents before sending them to the Mac, using limited local state and user physical confirmations to avoid unintentional destructive commands.
- **owner gets:** Adding local validation on the pendant reduces risk of unsafe or unintended Mac UI automations by including a hardware/firmware safety filter that can catch risky commands and require explicit user confirmation before sending.
- effort: Moderate firmware engineering and testing compatible with existing pendant-Mac communication protocols.  ·  risk: Adds latency and complexity to command transmission which could cause delays or missed inputs if not optimized.
- cost: Minimal, mostly development and testing cost.  ·  latency: Small increase in command latency from pre-validation steps.
- security: Improves security by filtering commands before the Mac accepts them.
- depends on: Current pendant-Mac communication protocol; Existing physical button input and event signaling


## What it asked for

_Nothing._
