# Harness derivation — mac-vision — round 270

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to delegate complex multi-step tasks on their Mac to the mac-vision agent with robust UI state verification and failure recovery."
- **useful because:** Currently, the mac-vision agent can plan and execute simple UI actions but lacks full integration with workbench contexts to reliably track, verify, and recover from multi-step workflows. This capability would empower the owner to offload complex tasks to the system with confidence in completion and correctness.
- **path:** mac-local-agent → relay → pendant
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate API cost dominated by real-time context processing
- **security:** Requires fine-grained access control and secure handling of sensitive UI and file system data; recovery actions must not cause unwanted side effects.
- **missing:** full integration of mac-vision with workbench context tracking; reliable UI state snapshot and verification beyond just disk state; robust failure detection and retry mechanisms

### "A priority-aware intelligent task list on Mac that integrates owner-stated task facts, live Apple Reminders and calendar tasks, and ongoing workbench contexts, with dynamic ranking and actionable suggestions."
- **useful because:** Currently there is no comprehensive, ranked task list that mac-vision can rely on for prioritizing and planning its actions. Such a combined view would make mac automation truly responsive to the owner's current work and priorities.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** under one second
- **cost:** low API cost
- **security:** Requires read access to Reminders and Calendar data, and secure handling of owner preferences and tasks.
- **missing:** integration of memory facts, dayPlan read-through, and workbench contexts into a unified task prioritization service

### "Enable confident and private macOS file management automation, driven by AI understanding the user's intent, with undo capabilities and secure handling of sensitive files."
- **useful because:** The owner often needs complex file operations on their Mac that involve multiple steps and decisions. Current automation lacks trust and recoverability, limiting how much the owner can safely delegate. A trusted file management system would save time and reduce errors.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** a few seconds
- **cost:** moderate cost dominated by secure context validation and action logging
- **security:** High sensitivity due to file system access, requires strict access controls and encrypted logs for undo support.
- **missing:** fine-grained file system action logging and undo integration; owner intent inference for file operations; tight integration with mac-vision UI actions

### "A secure and seamless voice-driven command interface on the Mac that leverages mac-vision for UI manipulation, combined with the pendant wearable for quick confirmations and input, enabling hands-free complex actions."
- **useful because:** This would allow the owner to operate and automate their Mac more efficiently without interrupting their physical workflow, with the pendant providing a low-latency, reliable interface for error correction and approvals.
- **path:** mac-local-agent → pendant → relay
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate due to multi-surface coordination and audio processing
- **security:** Must securely handle voice data, access control for UI actions, and pendant-device communication encryption.
- **missing:** full voice-driven UI command support for Mac; pendant integration for confirmations and input; multi-surface command coordination


## Changes it proposed to its own stack

### `integration` — Integrate mac-vision accessibility automation loop with workbench context management to report UI state alignment with claimed job progress and enhance failure detection and recovery.
- **owner gets:** The owner would get reliable, verified UI automation that knows exactly what part of a multi-step workflow has been completed or needs retry, reducing frustration and failed runs.
- effort: medium development effort across multiple components  ·  risk: Complexity in state synchronization may cause temporary discrepancies; careful testing needed
- cost: moderate API overhead in tracking UI states  ·  latency: minimal, mostly background monitoring
- security: Requires secure management of UI accessibility data and user workflows
- depends on: workbench context tracking robust APIs; mac-vision loop accessibility permissions granted

### `interaction` — Implement a low-latency feedback loop in mac-vision to detect and report UI failures or unexpected states during multi-step task execution, allowing prompt user or system intervention.
- **owner gets:** The owner gains transparency and control, preventing silent failures and wasted time during complex automated Mac workflows.
- effort: small to medium development effort  ·  risk: Potential user interruption annoyance if too sensitive, mitigated by adaptive thresholds
- cost: low  ·  latency: minimal
- security: minimal
- depends on: mac-vision accessibility automation loop

### `interaction` — Develop a context-aware suggestion system in mac-vision that offers proactive UI action prompts based on the owner's task priorities, behavioral patterns, and current application state.
- **owner gets:** Proactively reducing manual work by suggesting relevant actions helps the owner focus on higher-level thinking and decision-making, improving productivity and workflow fluidity.
- effort: medium development effort  ·  risk: Risk of irrelevant or noisy suggestions mitigated by user tuning and learning algorithms.
- cost: moderate due to context analysis and machine learning components.  ·  latency: low latency for prompt delivery.
- security: Requires secure handling of user interaction data and preferences.
- depends on: mac-vision loop enabled; access to owner preferences and task priorities; application state monitoring


## What it asked for

_Nothing._
