# Harness derivation — mac-vision — round 91

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Changes it proposed to its own stack

### `interaction` — Introduce a granular action gating and confirmation system integrated with the mac-vision loop that classifies every pixel-level interaction as read-only, reversible, or high-impact destructive. This system prompts the owner for explicit approval only for destructive or high-impact actions while allowing seamless automation and interaction for safe operations. It must log all actions for full auditability.
- **owner gets:** The owner gains transparency and control over each action the system takes on their Mac, preventing unintended destructive operations without blocking automation and intelligent assistance.
- effort: Moderate engineering to build UI for confirmations, classify actions dynamically, integrate with mac-vision loop, and implement detailed logging.  ·  risk: Improper classification could block legitimate automation or allow unsafe actions; mitigated by incremental rollout and owner override options.
- cost: Increased API calls and latency for confirmation steps; storage cost for detailed logs.  ·  latency: Confirmations add minimal delay on rare high-impact actions; general operations remain low latency.
- security: Higher security by user consent and audit trail; must ensure confirmation UIs prevent spoofing or hijacking.
- depends on: computerUse.loopEnabled; visionUploadConsented; ui_hierarchy_snapshot

### `context` — Develop a rich, continuous UI and app state context aggregation system that feeds detailed snapshots of active UI hierarchies and app states from mac-vision and mac-planner into faculty-perception. This would enable the agent to reason precisely about current screen content, app windows, menus, dialogs, and background states beyond what accessibility APIs provide.
- **owner gets:** The owner benefits from far more powerful and accurate computer automation that can visually and contextually understand the full Mac environment, enabling robust multi-step workflows and precise error recovery not possible with current partial status alone.
- effort: High engineering effort to build reliable real-time UI state capture and processing pipelines, plus integration with AI reasoning agents.  ·  risk: Potential performance impacts on Mac during snapshot capture; complexity in synchronizing UI state with real-time images; mitigated by adjustable snapshot frequency and prioritizing important windows.
- cost: Increased data storage and API invocation costs associated with frequent state captures and processing.  ·  latency: State snapshots add minimal latency but enable faster, more accurate downstream decision making.
- security: Sensitive UI data exposure requires secure handling, encryption in transit and at rest.
- depends on: computerUse.loopEnabled; visionUploadConsented

### `hardware` — Upgrade the MacBook's system to include a dedicated, isolated coprocessor for real-time visual processing and AI inference to offload pixel-level vision tasks from the main CPU, enabling continuous screen analysis without impacting the owner's workflow or privacy risks from main system interference.
- **owner gets:** This hardware enhancement allows always-on, low-latency visual understanding and control on the MacBook without draining main CPU resources or risking stability, enhancing AI automation capabilities and responsiveness while maintaining system performance.
- effort: Very high; requires hardware design, firmware development, and integration with existing OS and AI software stack.  ·  risk: Complex hardware/software integration risks, long development time, and elevated costs; mitigated by phased prototyping and careful security design.
- cost: Significant upfront hardware development and manufacturing costs, plus possible ongoing power consumption increments.  ·  latency: Reduces latency for visual processing significantly, enabling faster AI responses.
- security: Isolated coprocessor design reduces attack surface but requires secure communication channels and firmware update mechanisms.
- depends on: mac-planner; mac-vision; faculty-perception

### `model-routing` — Implement dynamic model tier routing between mac-vision (gpt-4.1-mini) and mac-planner/relay-realtime (gpt-5.6-luna) that optimizes task allocation based on complexity and latency sensitivity. Simple UI actions and screen understanding handled quickly by mac-vision, while complex reasoning, multi-step planning and coordination escalated to mac-planner/relay-realtime models.
- **owner gets:** Improves responsiveness and efficiency of the AI system by balancing load and matching tasks to best-suited models, providing the owner with fast and accurate computer control and automation.
- effort: Moderate engineering effort to build routing logic, heuristics, and adaptive task scheduling.  ·  risk: Potential task routing mistakes could delay critical actions; mitigated by fallback retries and owner override options.
- cost: Potential cost savings by limiting expensive large model usage to necessary cases.  ·  latency: Reduces average latency for common tasks by using lighter models locally.
- security: Minimal, internal model routing does not introduce new vulnerabilities.
- depends on: mac-vision; mac-planner; relay-realtime

### `memory` — Create a mechanism for mac-vision to cache visual UI element states and prior screen interactions locally to support short-term memory across UI changes and app restarts. This would allow the vision agent to maintain context without repeated visual re-acquisition, improving efficiency and reliability of multi-step workflows with complex UI.
- **owner gets:** Owner gains seamless and robust visual automation that remembers recent UI contexts and user interactions even as windows change or apps restart, allowing fluid multi-step tasks without repeating manual steps or losing track of workflow progress.
- effort: Moderate; requires local image feature caching, cross-session state sync, integration with vision and planning agents.  ·  risk: Cache staleness or corruption could cause erroneous actions; mitigated by cache validation and purging mechanisms.
- cost: Storage use for cached UI data; moderate computation overhead to manage cache.  ·  latency: Faster decisions when cached context is valid, reduced wait times for repetitive UI tasks.
- security: Sensitive UI info cached locally needs encryption and access controls.
- depends on: mac-vision; mac-planner


## What it asked for

_Nothing._
