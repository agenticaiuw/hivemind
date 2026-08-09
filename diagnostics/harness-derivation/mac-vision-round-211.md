# Harness derivation — mac-vision — round 211

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a prioritized and actionable Mac task list for the owner based on their current memory facts and daily routines."
- **useful because:** The owner currently has tasks as text facts but no actionable prioritized task list on the Mac. Providing this helps the Mac-side agent focus on what the owner really wants done next, enabling proactive automation.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** background
- **latency:** seconds
- **cost:** low per invocation for context read and model inference
- **security:** Only surface-scoped memory facts and routines are read; no private data is exposed externally.
- **missing:** A ranking and prioritization model for owner tasks integrated with live routine schedule and reminders.

### "Report claimed versus actual Mac UI state for each ongoing delegated workflow context."
- **useful because:** Allows reconciliation between what delegated workflows believe is done and what is actually visible on the Mac UI, reducing errors and duplication. Only the mac-vision agent can provide the actual UI state needed.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** background
- **latency:** seconds
- **cost:** low
- **security:** Access to current UI accessibility tree and workflow context state, no private data leaves without owner consent.
- **missing:** Integration of accessibility tree snapshot and state differencing with workbench context API.

### "Activate and extend the mac-vision agent loop with policy and safeguards for safe Mac UI automation."
- **useful because:** Permissions and readiness for full mac-vision automation now exist. Enabling this loop with safety policies unlocks unique capabilities to automate UI interactions and advance owner goals on the Mac.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** hundreds of ms
- **cost:** medium per invocation dominated by live context and interaction inference
- **security:** Requires careful containment of UI interaction scope and owner confirmation flows for destructive actions.
- **missing:** Full interaction policy and fallback handling for failed UI actions.

### "Enable the mac-vision agent to autonomously resume and continue multi-step Mac workflows after interruption by visually confirming UI state and undoing or advancing as needed."
- **useful because:** Mac workflows can be interrupted or fail mid-progress without automatic recovery. The mac-vision agent uniquely sees the visual UI state and can verify if steps completed, undo if needed, and resume. This enables reliable, autonomous Mac work continuation.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** hundreds of ms to seconds
- **cost:** medium per invocation for UI state analysis and planning
- **security:** Requires the highest level of Mac UI accessibility permissions and safeguards against unintended UI mutations.
- **missing:** A mechanism to compare visible UI state with workflow expectations and an undo stack to reverse partial executions.

### "Create an adaptive UI interaction policy engine for mac-vision allowing dynamic response to UI changes, input focus issues, and failure modes during automation."
- **useful because:** Mac UI automation frequently fails due to UI changes, focus loss, or unexpected states. An adaptive policy engine allows retry strategies, fallback actions, and context-aware choices, greatly improving reliability and reducing user friction.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** hundreds of ms
- **cost:** medium
- **security:** Policy decisions must strictly limit destructive actions without owner consent and log actions transparently.
- **missing:** Fallback strategies, retry rules, and a policy language for Mac UI automation interactions.

### "Provide a unified view combining the owner's prioritized task list, open delegated workflows, and live Mac UI state to present a comprehensive current work context."
- **useful because:** The owner and agents cannot currently see a single, coherent view of what tasks are prioritized, what workflows are in progress, and what the Mac UI reflects visually. A unified view enhances situational awareness and smarter agent collaboration.
- **path:** mac-planner → mac-vision → relay-realtime
- **model tier:** background
- **latency:** seconds
- **cost:** low to medium
- **security:** Integration of sensitive task and workflow state, UI state only viewed locally unless authorized.
- **missing:** Cross-surface integration and real-time sync of task priorities, workflows, and Mac UI accessibility snapshots.

### "Automatically detect and classify Mac UI states captured by the mac-vision agent into semantic workflow stages to assist in progress tracking and decision-making for delegated workflows."
- **useful because:** Knowing the semantic stage of the Mac UI from screenshots and accessibility trees helps agents decide next steps, detect completion or failure, and reduces reliance on opaque delegated workflow states.
- **path:** mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** medium
- **security:** Requires local analysis of UI accessibility trees and images; data should not leave device without permission.
- **missing:** Robust ML models trained on Mac UI states and associated semantic workflow labels.

### "Provide a user-configurable safety and trust dashboard for Mac UI automation by mac-vision that transparently reports recent automation actions, permissions held, and allows fine-grained enable/disable controls."
- **useful because:** Owners need visibility and control over sensitive UI automation, especially with deep system access. A transparent dashboard builds trust and lets the owner manage mac-vision's capabilities comfortably.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** low
- **security:** Reports sensitive info only accessible to the owner; must be protected.
- **missing:** UI to display logs, permission states, and controls; integration with mac-vision's action execution subsystems.


## Changes it proposed to its own stack

### `integration` — Implement cross-surface synchronization and integration for task priorities, open workflows, and live Mac UI accessibility snapshots into one unified work context view accessible by all agents.
- **owner gets:** This integration would provide the owner with a comprehensive, real-time view of their active work, improving clarity and enabling more intelligent agent collaboration across surfaces.
- effort: Medium to high, requiring work on syncing different data sources and building a coherent data model and UI presentation.  ·  risk: Complexity in syncing could introduce data inconsistencies or delays; requires careful design to ensure data privacy and security policies are enforced consistently.
- cost: Medium, due to continuous background sync and context model inference.  ·  latency: Moderate, as the sync needs to be timely but can be done asynchronously.
- security: Requires robust access control and encryption to protect sensitive task and UI state data.
- depends on: GET /memory/facts; GET /workbench/contexts; GET /vision-loop/preflight

### `hardware` — Add a dedicated secure input/output co-processor on the Mac peripheral hardware to capture user approvals and biometric confirmations for sensitive UI automation actions.
- **owner gets:** This hardware co-processor would enable the mac-vision agent to perform sensitive or destructive UI actions only after secure user approval, enhancing security and user trust.
- effort: High, as it involves hardware design, integration with existing firmware and system software.  ·  risk: Hardware integration risks, potential delays in user interaction flow if not designed carefully.
- cost: Moderate, additional hardware cost and power consumption.  ·  latency: Minimal, user input gating is asynchronous anyway.
- security: Positive, increases security by leveraging hardware-backed trust.


## What it asked for

_Nothing._
