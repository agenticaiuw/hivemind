# Harness derivation — mac-vision — round 226

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `integration` — Add a mac UI state validator and reconciler component that runs alongside mac-vision to detect and repair discrepancies between claimed workflow progress and actual Mac UI state using accessibility tree captures.
- **owner gets:** Ensures that UI automation driven by mac-vision is robust to errors, interruptions, and UI changes, reducing failed tasks and improving reliability.
- effort: High: requires coupling UI state knowledge, accessibility snapshots, job/workbench context introspection, and error recovery design.  ·  risk: Automation might misinterpret UI leading to unexpected clicks; must have safe fallback and undo; requires thorough testing.
- cost: Moderate API cost due to frequent UI state validation calls and reconciliation logic.  ·  latency: Increases latency per task step slightly due to verification overhead.
- security: Needs secure access to UI state and user consent for deep accessibility usage.
- depends on: computerUse.loopEnabled; mac-vision capability enabled; GET /vision-loop/preflight; GET /workbench/contexts

### `firmware` — Extend the pendant firmware to send a lightweight, reliable physical gesture signal (such as a distinct short press pattern) to the Mac as explicit user approval or cancellation for mac-vision autonomous actions requiring confirmation.
- **owner gets:** This hardware-level approval channel allows the owner to quickly confirm or cancel potentially risky or irreversible Mac UI actions without interrupting workflow or using the Mac directly, enhancing both security and convenience.
- effort: Moderate firmware and Mac-side event handling work to define, detect, and act on the signal.  ·  risk: False positives or missed signals could disrupt automation; must have fallback timeouts and explicit failure modes.
- cost: Very low power and data cost; minor firmware code size increase.  ·  latency: Minimal latency added to user approval process.
- security: Strong security benefit by giving the owner direct physical control over automation approvals.
- depends on: pendant device available; Mac-side event listener integration; mac-vision autonomous control enabled

### `model-routing` — Introduce a dedicated AI model routing and arbitration layer that coordinates between mac-vision, mac-planner, browser-extension, and relay-realtime to optimize workload distribution, latency, and result coherence for Mac UI automation and multi-surface workflows.
- **owner gets:** The owner benefits from faster, more reliable responses and coherent action sequencing across devices and interaction surfaces, enabling complex workflows that span local UI, browser, voice, and cloud.
- effort: High complexity in the architecture and interface design, model selection and routing logic, and testing.  ·  risk: Potential routing inefficiencies or errors could delay or confuse workflow execution; requires robust monitoring and fallback.
- cost: Increased usage of realtime and background AI model compute resources.  ·  latency: Reduced end-to-end latency through optimized routing if successful; initial increase during integration.
- security: Must ensure data isolation and policy compliance across routing boundaries.
- depends on: All interacting surfaces and their models; APIs for inter-agent communication and state sharing

### `dashboard-ux` — Build a real-time dashboard on the Mac that visualizes mac-vision's UI interactions, pending and completed tasks, detected errors, and user interaction history, allowing the owner to supervise, intervene, or adjust automation behavior interactively.
- **owner gets:** Provides the owner with transparency and control over autonomous Mac actions, improves trust and error recovery, and enables feedback that can refine automation policies and priorities.
- effort: Moderate UI and backend work to expose data from mac-vision and integrate with existing stores.  ·  risk: Dashboard overload could overwhelm the owner; must focus on clarity and actionable summaries.
- cost: Low for display logic; some backend cost for real-time monitoring and state aggregation.  ·  latency: Minimal additional latency.
- security: Data must be secured and access controlled to protect privacy.
- depends on: mac-vision capability enabled; mac-vision action logs; memory projection; GET /workbench/contexts

### `memory` — Design an enhanced dynamic memory projection service that explicitly links task facts, UI state snapshots, and workflow contexts into a unified representation to inform mac-vision and other agents about current actionable priorities and execution states.
- **owner gets:** Gives agents a clear, integrated view of what the owner wants and what the machine interface state is, enabling better prioritization and reliable action sequences.
- effort: Medium complexity to redesign memory projection and context linking logic.  ·  risk: Complexity might cause slowdown or inconsistencies if not carefully implemented.
- cost: Moderate computational cost for richer context synthesis.  ·  latency: Some latency added to context retrieval operations.
- security: Sensitive task data must be secured properly and respect owner privacy preferences.
- depends on: GET /memory/projection; GET /workbench/contexts; mac-vision capability enabled


## What it asked for

_Nothing._
