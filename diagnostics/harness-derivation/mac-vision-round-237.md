# Harness derivation — mac-vision — round 237

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have an always-updated, owner-prioritized Mac task backlog that the mac-vision agent can access step-by-step to autonomously plan and execute UI actions."
- **useful because:** Currently there is no persistent, ranked backlog of Mac-specific work that mac-vision can work from. Such a backlog would enable clear autonomous operation, prioritization, and task management on the Mac through the AI pendant system.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate API calls for updating backlog and ranking
- **security:** stores personal task priorities and potentially confidential work details; requires secure storage and owner control.
- **missing:** An input method or integration that records or imports owner task intent into a persistent backlog format readable by mac-vision.; A ranking algorithm or policy for owner priorities and deadlines integrated with the backlog.; UI feedback to the owner about the current backlog and progress.

### "Enable a multi-tiered reactive Mac control loop combining mac_run_actions for atomic actions, mac_delegate for multi-step workflows, and mac-vision to interpret UI state and orchestrate next actions autonomously."
- **useful because:** Today mac-vision cannot decide or act beyond atomic operations; combining reactive loop tiers creates a powerful framework for autonomous Mac control tailored to task complexity and state.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds for atomic actions, minutes for multi-step plans
- **cost:** Moderate to high depending on workflow complexity and loop interactions.
- **security:** Requires robust safeguards to protect owner data and prevent unintended actions; owner policies must govern confirmations and destructive operations.
- **missing:** Precise coordination protocols between loop tiers.; Context-sharing mechanisms integrating UI state, task backlog, and progress.; Enhanced vision loop permission confidence and reliability monitoring.

### "Allow the owner to manually annotate and interleave manual intervention points within multi-step Mac workflows managed by mac_delegate, capturing UI context and letting mac-vision resume seamlessly post-intervention."
- **useful because:** Owners often need to intervene manually during complex workflows, e.g., authentication prompts or external approvals. Capturing these manual pauses and UI state/context enables safer, less error-prone resuming of tasks without starting over.
- **path:** mac-planner → mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** seconds for context capture, minutes for manual intervention
- **cost:** Low to moderate, mostly in UI state caching and workflow state updates
- **security:** Manual intervention may expose secure UI elements; annotations must be owner-controlled and possibly encrypted.
- **missing:** UI context capture and serialization triggered by manual intervention points.; User interface for marking pauses and providing context annotations.; Integration with mac_delegate workflow state and mac-vision UI observations.

### "Provide a safe, owner-controlled simulation mode for mac-vision where UI actions are planned and previewed without committing them, allowing owner review before execution."
- **useful because:** This reduces risk of undesired or incorrect UI manipulations by letting the owner preview and approve all control loop actions before they affect the Mac, boosting trust and safety.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** milliseconds to seconds per step for simulation feedback
- **cost:** Low to moderate, mainly computing planned action sequences and UI snapshots
- **security:** Simulation stores planned sensitive inputs and UI states temporarily; must be secured and ephemeral.
- **missing:** A virtual UI state model that can accept planned actions and preview outcomes.; An owner UI interface to browse, approve, or cancel planned action sequences.; Integration with mac-vision action planning loop to switch between simulation and live modes.

### "Provide a protocol and API for mac-vision to obtain and restore full macOS accessibility UI state snapshots, including focused app, open windows, and control hierarchies, for reliable workflow continuation after interruptions."
- **useful because:** Current accessibility tree snapshots alone are insufficient for precise state restoration in multi-step workflows. A richer snapshot ensures mac-vision can recover exactly where interrupted workflows left off without errors or redundant steps.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** seconds for snapshot fetch and restore
- **cost:** Moderate due to data size and processing
- **security:** Accessibility UI data may contain sensitive user data; access must be restricted and encrypted.
- **missing:** macOS APIs or extensions to capture and restore richer accessibility state beyond the current tree.; Software to serialize and deserialize accessibility state snapshots securely.; Integration with mac_delegate and workflow resumption systems.


## Changes it proposed to its own stack

### `integration` — Add a UI state reconciliation feature to the mac_delegate workbench contexts by capturing and comparing real-time accessibility tree snapshots and screenshots with planned workflow states, enabling robust resume and error detection in multi-step workflows.
- **owner gets:** This provides the only way to detect divergence between planned and actual UI states on the Mac during complex workflows, allowing resumed workflows to not restart blindly but continue precisely where they left off for reliability and safety.
- effort: High; requires careful integration of accessibility tree capture, screenshot capture, and workflow state management.  ·  risk: Potential for mismatch or false positives that could interrupt workflows; must be designed to fail gracefully and to not lose track of work.
- cost: Moderate; additional data storage and processing for UI snapshots and reconciliation.  ·  latency: Minimal to moderate depending on frequency of UI state capture.
- security: Captures sensitive UI state; access must be tightly controlled and encrypted.
- depends on: Enabling computerUse.loopEnabled; mac-vision accessibility permissions

### `firmware` — Enhance the pendant firmware to send explicit 'pause workflow' and 'resume workflow' signals triggered by physical buttons to the mac-vision and mac_delegate agents, to support owner-guaranteed manual intervention and confirmation workflows.
- **owner gets:** Owners can manually interject and approve multi-step Mac workflows at any point, using the pendant hardware they wear rather than relying only on software UI, increasing safety and control.
- effort: Moderate: firmware updates plus app and agent handler integration for these new signals  ·  risk: Low to moderate; physical signal reliability is high, but handlers must contend with timely workflow state capture and resume.
- cost: Very low on device; minor increase in data processing and workflow state complexity software-side.  ·  latency: Negligible on firmware; minimal in software processing.
- security: Physical button presses are deliberate and owner-controlled, reducing accidental triggers; integration must secure signal authenticity.
- depends on: Existing pendant firmware communication framework; mac-vision and mac_delegate agents handling signals

### `dashboard-ux` — Create a mac-vision integrated dashboard panel that visualizes the current accessibility UI tree, pending Mac workflow backlog, and ongoing multi-step workflow progress with controls for manual overrides and confirmations.
- **owner gets:** Gives the owner transparency and control over what mac-vision sees and does in real time, enabling informed manual intervention, debugging, and confidence in AI-driven Mac control.
- effort: Moderate to high for UI design, integration, and real-time data streaming.  ·  risk: Low if properly sandboxed; risk is mainly owner confusion without good UX design.
- cost: Moderate; real-time UI trees and states streamed continuously.  ·  latency: Moderate; latency depends on data volume and UI responsiveness.
- security: Dashboard accesses sensitive UI and task data; must be securely authenticated and encrypted.
- depends on: Accessibility UI state capture; Mac workflow backlog; mac_delegate workflow integration

### `model-routing` — Route specialized mac-vision tasks such as UI state interpretation, task prioritization, and action planning to dedicated smaller models that operate in parallel to the main planner to improve latency and precision.
- **owner gets:** Decreases latency for UI responsiveness and improves the accuracy of mac-vision interactions by leveraging models specialized in distinct subtasks within Mac control workflows.
- effort: Moderate to high: model training, deployment, routing logic.  ·  risk: Moderate; model output inconsistency or routing errors could degrade performance, but can be mitigated by fallback and monitoring.
- cost: Increased API/model usage costs due to multiple parallel queries.  ·  latency: Reduced latency per task, overall completion may vary depending on orchestration.
- security: Model data segregation required to avoid cross-data contamination.
- depends on: Existing multi-model infrastructure; Reliable task classification and routing

### `memory` — Build a long-term persistent context memory for mac-vision that stores UI state snapshots, action history, and task progress over weeks to improve resilience and personalization in Mac control workflows.
- **owner gets:** Owner's workflows can be resumed smoothly after interruptions even days later, with personalized improvements and learned preferences, making AI Mac control more reliable and satisfying.
- effort: High; requires storage, indexation, retrieval, and versioning of UI and action histories.  ·  risk: Medium; privacy risks if memory leaks sensitive data, requires encryption and strict access policies.
- cost: High; storage and retrieval cost, especially if large UI snapshots are stored.  ·  latency: Minimal to moderate depending on indexing and access speed.
- security: Highly sensitive data storage requires encryption, authentication, and audit controls.
- depends on: mac-vision UI state capture; memory infrastructure


## What it asked for

_Nothing._
