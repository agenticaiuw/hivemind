# Harness derivation — mac-vision — round 205

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable autonomous Mac UI task execution coordinated with owner-prioritized live tasks and verified by accessibility state observation."
- **useful because:** Allows the Mac-vision agent to read the owner's current prioritized task facts, plan and execute Mac UI actions reliably, verify task completion by cross-checking the claimed workbench contexts against real-time accessibility tree snapshots, and resume interrupted workflows securely.
- **path:** mac-vision → faculty-judgement → faculty-perception → faculty-action
- **model tier:** realtime
- **latency:** seconds to a few minutes per multi-step task
- **cost:** Moderate API and compute cost for live context reads, planning and observation; low incremental cost for coordinated action execution.
- **security:** Requires full accessibility trust, handling of sensitive data about user tasks and UI state, on-device verification to avoid exposure of UI details.
- **missing:** a durable local store for Mac UI action state snapshots matching workbench claim contexts; a resume-capable execution engine that can restart multi-step UI workflows from known state; a ranking model to prioritize owner tasks dynamically from fact projections

### "Verify actual UI state on the Mac matches the claimed workbench context state after multi-step actions, and flag any unexpected discrepancies for review or retry."
- **useful because:** Currently, the system can claim workbench context states and plans multi-step Mac UI actions, but has no direct way to verify the actual UI has reached the expected state after each step or at task completion. This capability ensures reliability and correctness of the Mac-vision agent's UI-driven automation.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** realtime
- **latency:** seconds per verification step
- **cost:** Moderate due to accessibility tree snapshots and model comparison
- **security:** Sensitive UI state must be processed locally or anonymized; no UI content should be leaked externally; requires trusted accessibility permission.
- **missing:** A local state snapshot and diff store for accessibility UI trees linked to workbench context state; A reconciliation engine to compare UI snapshot vs expected workbench state and identify drift; UI anomaly detection model to flag unexpected UI changes or failures

### "Implement a multi-surface, persistent UI workflow engine that resumes interrupted multi-step Mac UI workflows based on saved workbench contexts and observed UI state."
- **useful because:** Mac workflows can be complex and interruptions are frequent. Having a persistent engine that can resume workflows by reconciling saved workbench contexts with live accessibility UI state observations would significantly increase robustness, reduce repeated interactions, and improve owner experience.
- **path:** mac-vision → faculty-action → faculty-perception → mac-planner
- **model tier:** realtime
- **latency:** minutes for complex workflows
- **cost:** High for tracking state persistently and for reconciliation checks, moderate for user notification and workflow planning
- **security:** Requires secure handling of sensitive user workflow data, trusted local state stores, avoidance of leaking details externally; needs strong permissions for accessibility and data stores.
- **missing:** A robust persisted context store for multi-step UI workflow state; A reliable UI state reconciliation mechanism to identify resume points; User interface or voice protocols to confirm workflow resumption and interruption handling

### "Automatically extract and maintain a highly detailed map of the Mac's GUI elements, including contextual state and dynamic content, to enable precision targeting and error recovery for UI automation."
- **useful because:** Although accessibility APIs provide a tree, they lack rich semantic understanding and run-time contextual awareness. This capability would build a deep model of app UI states, allowing the Mac-vision agent to interact reliably, adapt to UI changes, and recover from unexpected UI states.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** realtime
- **latency:** seconds between UI observations
- **cost:** Moderate to high due to continuous semantic analysis and UI state modeling
- **security:** Requires detailed accessibility data exposure within the trusted environment; must avoid leakage of UI content externally.
- **missing:** Advanced semantic UI interpretation models; Persistent, indexed UI state database linked to dynamic app states; Error recovery frameworks that leverage UI state models

### "Allow the owner to define and update dynamic, multi-dimensional task priorities and dependencies across their Mac workflows, going beyond simple structural indicators."
- **useful because:** Current task handling uses only broad structural priority cues. Enabling the owner to explicitly rank, tag, and define dependencies among tasks and workflows would allow the system to optimize agent scheduling, focus on critical work, and handle complex dependencies automatically.
- **path:** mac-vision → faculty-judgement
- **model tier:** realtime
- **latency:** under 5 seconds
- **cost:** Low to moderate, mostly storage and indexing
- **security:** Handling user-defined priority metadata securely; problem if mishandled data causes incorrect agent behavior.
- **missing:** UI and voice interfaces for the owner to specify task priorities and dependencies; Extended task schema to support tagging and dependency specs; Priority resolution and conflict detection engine

### "Integrate a trustworthy, on-device execution audit log that records every UI action attempted or completed by the Mac-vision agent with state before and after each action."
- **useful because:** This would allow both the owner and agents to review, debug, and verify Mac UI automation efforts, providing accountability and enabling failure recovery and replays. It addresses a significant gap in observability and control over autonomous UI actions.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** realtime
- **latency:** milliseconds per UI action logged
- **cost:** Low to moderate storage and processing cost, proportional to UI action frequency
- **security:** Secure state handling to avoid leakage; ensure audit logs cannot be tampered with or deleted without trace.
- **missing:** Signed immutable logs or cryptographic proof chains on-device; Per-action state snapshot hook into UI automation loop; Log querying and visualization toolchain


## What it asked for

_Nothing._
