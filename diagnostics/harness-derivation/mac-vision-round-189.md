# Harness derivation — mac-vision — round 189

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a dynamically prioritized, context-aware, and continuously updated Mac task and goal list accessible by the owner and agents, integrating tasks from memory, reminders, workflows, and day plans with deadlines, dependencies, and urgency indicators."
- **useful because:** Currently the owner and agents lack a unified, up-to-date Mac task list that reflects true priorities and dependencies, limiting intelligent assistance, planning, and execution on the Mac. Such a feature would provide greater clarity, focus, and effective automation of the owner's work on the Mac.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** seconds
- **cost:** low to moderate per update, higher for re-ranking and integration
- **security:** Tasks involve potentially sensitive personal or work data; access permissions must be carefully managed to avoid leaks or unauthorized actions.
- **missing:** Durable, cross-surface task store with update, priority, dependency, and status support; agents to write and read task facts comprehensively; integration with existing reminders, workflows, and dayPlan; UI or voice surfaces for owner interaction to manage tasks and priorities.

### "Enable the mac-vision agent to directly observe and verify the actual on-screen state of complex multi-step workflows claimed and tracked by other agents, for true end-to-end visual consistency and error detection."
- **useful because:** Currently workflows are tracked by metadata with no visual check of the real UI state; the owner risks errors or incomplete execution without real visual verification. Direct visual confirmation by mac-vision would enable robust end-to-end workflow coordination and correction.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** moderate per verification action
- **security:** Access to on-screen UI structures and workflows must be secured and consented by the owner; information leaks or unintended visual exposure must be prevented.
- **missing:** Integration of mac-vision accessibility tree reads with the workbench workflow context; mechanisms to associate visual UI states with tracked workflow steps; UI for human vetting or agent-assisted correction if mismatches occur.

### "Integrate the Mac accessibility-driven UI control observation and interaction (mac-vision) with enhanced model understanding for context-aware, adaptive help that predicts and executes next actions in complex Mac tasks with minimal owner intervention."
- **useful because:** This would leverage the full capability of the accessibility tree control and mac-vision's existing read ability to allow fluid, context-aware interaction on the Mac desktop for the owner, enabling automation of repetitive or complex UI workflows they currently do manually.
- **path:** mac-vision → unified
- **model tier:** realtime
- **latency:** sub-second
- **cost:** moderate on demand, mostly model inference costs
- **security:** Requires strict owner consent for accessibility control and input; safeguards to prevent unintended or harmful actions must be in place.
- **missing:** Advanced model integration with mac-vision for live action prediction and UI context analysis; interfaces for fallback and manual override; trust and consent management layers.

### "Allow the owner to request specific, persistent moments in their work or computer use, marked by a single button press on the pendant, which are then automatically recorded, timestamped, and indexed for later retrieval and review across all agent surfaces."
- **useful because:** The owner can capture important moments or ideas quickly without breaking their flow, with these moments becoming structured metadata usable for enhanced personal memory, planning, or automation triggers.
- **path:** pendant → mac-planner → mac-vision → unified
- **model tier:** background
- **latency:** seconds
- **cost:** minimal, mostly storage and metadata overhead
- **security:** Sensitive personal data is stored and indexed; must ensure secure storage and controlled access.
- **missing:** Integration of pendant button press events into durable moment stores; UI and voice interface for retrieval and use of moments across surfaces.

### "Real-time multimodal assistant that combines pendant button input, Mac accessibility UI state observation, and contextual knowledge from memory facts and workflows to provide instant on-screen and voice feedback and actions tailored dynamically to current user intent."
- **useful because:** This makes the AI pendant system a seamless, natural extension of the owner's capabilities by tightly coupling physical inputs, visual UI state, and AI reasoning for immediate, personalized, and context-aware assistance, far beyond static voice or screen-only systems.
- **path:** pendant → mac-vision → relay-realtime → unified
- **model tier:** realtime
- **latency:** under 500 ms
- **cost:** moderate to high depending on usage
- **security:** Must carefully manage privacy and control over sensitive UI and voice data; user control to restrict or pause any modality is essential.
- **missing:** Low-latency, multi-surface data fusion infrastructure; advanced AI models able to fuse multimodal context in real-time; enhanced pendant firmware for precise event marking and input handling.; Interfaces for seamless user consent and privacy control across surfaces.

### "Develop a dynamic, context-sensitive notification system on the Mac that filters and aggregates alerts from apps, reminders, routines, and agents, prioritizing only those requiring immediate owner attention based on current tasks and context."
- **useful because:** The owner currently risks distraction or alert fatigue; a smart notification system tailored to real-time priorities and work context would improve focus, reduce interruptions, and ensure critical signals are not missed.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** seconds
- **cost:** low-to-moderate, mainly filtering and aggregation costs
- **security:** Notifications may contain sensitive info; filtering logic must respect privacy and prevent unintentional disclosure.
- **missing:** Detailed priority models for notifications; integration with all relevant apps and agent-generated alerts; UI surfaces for aggregated notification presentation and interaction.


## Changes it proposed to its own stack

### `model-routing` — Implement a multi-tiered planning and prioritization architecture that leverages the owner's priority facts, daily schedules, and remembered context across surfaces to feed the mac-vision agent and others with the most urgent next actions optimized for real-time assistance.
- **owner gets:** This change would make the mac-vision agent and others far more effective by focusing limited real-time AI resources on what truly matters to the owner now, reducing noise and improving task completion speed and satisfaction.
- effort: Medium to high development effort across orchestration, model routing, and context syncing layers.  ·  risk: Coordination errors might cause urgent tasks to be missed or wrongly prioritized temporarily; monitoring and fallback strategies must be implemented to avoid critical failures.
- cost: Marginal increase in API costs for real-time prioritizations; computing cost can be managed by caching and incremental updates.  ·  latency: Adds slight processing time in routing phase; negligible in end-user interaction latency.
- security: Needs to carefully manage sensitive priority data across models and surfaces to respect owner privacy.
- depends on: GET /memory/facts; GET /day-plan; GET /workbench/contexts

### `firmware` — Enhance pendant firmware to support configurable multi-gesture recognition on available buttons, including differentiation of single press, double press, long press, and hold and release patterns.
- **owner gets:** This would greatly expand the owner's ability to use the pendant as a nuanced physical interface to trigger a variety of actions, moments, or modes without adding new hardware, making interaction more expressive and efficient.
- effort: Medium firmware and testing effort, low hardware risk.  ·  risk: Potential increase in debounce or latency; must ensure no impact on critical existing functions, especially microphone activation on button press.
- cost: Negligible, no hardware changes; firmware maintenance cost only.  ·  latency: Minimal increase in button processing time.
- security: None directly, but gestures must be correctly authenticated and only trusted users can configure actions.

### `dashboard-ux` — Create a unified task and notification dashboard that merges tasks from memory, routines, day plans, and notifications into one interactive UI on the Mac and possibly the pendant's companion app, showing priorities, deadlines, and relevant context.
- **owner gets:** It centralizes the owner's attention management in one place, improving situational awareness, efficiency, and the ability to rapidly adjust priorities and act on tasks and alerts without app switching or context loss.
- effort: Significant UI and backend integration work, plus UX design and iteration.  ·  risk: Initial complexity might overwhelm owner; need thoughtful design and onboarding.
- cost: Moderate development and ongoing maintenance; UI rendering costs low.  ·  latency: Negligible; mainly backend aggregation delays.
- security: Sensitive personal and work data consolidated; strong access control and encryption required.
- depends on: GET /memory/facts; GET /day-plan; GET /routines; GET /notifications


## What it asked for

_Nothing._
