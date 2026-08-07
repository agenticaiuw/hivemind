# Harness derivation — mac-vision — round 87

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Real-time collaborative multi-agent AI supervision and vetting of autonomous UI actions on the MacBook"
- **useful because:** This capability would allow multiple specialized agents (perception, judgement, action, planner, vision) to continuously monitor, analyze, and validate potential UI control actions before execution. It would ensure safety, reduce errors, and allow nuanced reasoning about context and owner preferences beyond simple permission gates.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** milliseconds to a few seconds per joint decision cycle
- **cost:** Moderate to high due to multiple agent invocations and context sharing required
- **security:** Requires secure, authenticated communication between agents, strict access control on action approval, and clear logging and undo capabilities. Sensitive UI data must be encrypted and permissions respected at all steps.
- **missing:** Inter-agent communication protocols and secure context sharing; Joint decision making algorithms and consensus protocols; Real-time UI snapshot and event stream accessible to multiple agents; User override and escalation mechanisms

### "Owner-controlled contextual memory integration for autonomous UI actions"
- **useful because:** Allow the mac-vision loop and collaborative agents to access a curated, privacy-preserving memory of past UI states, actions, and owner preferences to improve decision making, avoid repeated mistakes, and personalize computer control over time.
- **path:** mac-vision → faculty-perception → faculty-judgement → unified
- **model tier:** background
- **latency:** seconds to minutes for memory updates, milliseconds for reads during interaction
- **cost:** Moderate storage and compute for memory management, indexed retrieval, and model input formatting
- **security:** Strong access controls and data encryption needed to protect sensitive contextual memory; owner control over memory lifespan and scope mandatory.
- **missing:** Memory storage and retrieval backend integrated with UI context; Interfaces for memory-curation and privacy controls; Model ingest format for context-aware UI control and judgement


## Changes it proposed to its own stack

### `integration` — Implement a real-time multi-agent orchestration layer that manages UI snapshots and event streams, handles secure context sharing and action voting, and coordinates agent collaboration to approve or reject autonomous UI actions on the MacBook
- **owner gets:** This would enable complex, reliable, and safe autonomous multi-agent control of the Mac's UI, ensuring any autonomous action is carefully vetted and aligned with the owner's preferences, reducing risk and increasing trust in autonomous computer operation.
- effort: High, involving development of new middleware, inter-agent communication protocols, and integration with existing agents and UI snapshot systems.  ·  risk: Bugs or miscoordination in the orchestration layer could cause incorrect or delayed actions; thorough testing and fallback/override mechanisms needed.
- cost: High due to continuous context syncing and agent inference calls; power and network usage must be monitored.  ·  latency: Real-time but may add 0.5-3 seconds latency to UI action approvals depending on complexity.
- security: High sensitivity and access to all UI actions and data requires strict authentication, encryption, and logging.
- depends on: mac-vision enabled loop and context access; permissions for autonomous UI control; secure communication channels between agents

### `hardware` — Add a dedicated secure coprocessor on the pendant to locally validate and veto autonomous UI actions proposed by the Mac vision loop before execution, with an owner-confirmation button for critical irreversible actions
- **owner gets:** Provides a hardware-based trustworthy safety gate for autonomous Mac UI control, allowing the owner to physically confirm or reject sensitive actions quickly and securely, even when the main Mac is compromised or untrusted.
- effort: Moderate to high, requires new pendant firmware and hardware design, plus integration with mac-vision and faculty-action agents.  ·  risk: Hardware bugs or false vetoes could reduce usability or delay important actions; must have bypass fallback with explicit owner override.
- cost: Additional hardware components and firmware development cost, negligible power draw increase.  ·  latency: Minimal, confirmation is a physical action by the owner, not adding delay beyond human interaction.
- security: High security value, requires robust cryptographic protocols and secure hardware design.
- depends on: Current pendant hardware capabilities; mac-vision UI control capabilities; communication with Mac and relay-realtime

### `model-routing` — Create a specialized model-routing framework that dynamically assigns tasks to the best-suited models (e.g., gpt-4.1-mini for vision, gpt-5.6-luna for planning, gpt-realtime-2.1 for relay) based on latency, cost, and accuracy requirements of the autonomous Mac UI control loop
- **owner gets:** Optimizes resource use and response times for complex autonomous UI workflows, allowing the Mac-vision loop and associated agents to respond quickly and accurately without unnecessary overhead or delays.
- effort: Moderate, involves building the routing logic and context-aware dispatching system, also requires profiling models and tuning parameters.  ·  risk: Routing errors could send tasks to suboptimal models, causing delays or poorer results; requires monitoring and fallback mechanisms.
- cost: Potential cost savings by using lower-cost models for less critical tasks, but peak loads may increase overall cost slightly.  ·  latency: Improves average and tail response latency by using best-fit models per task.
- security: Minimal added risk beyond secure communications already in place.
- depends on: Availability of multiple models with differentiated capabilities; Real-time context sharing among agents; Existing model APIs and control infrastructure

### `memory` — Develop a context graph memory integration layer that connects UI states, agent actions, and owner preference signals into a dynamic, queryable graph database for mac-vision and faculty-judgement to learn from and personalize autonomous computer control
- **owner gets:** Enhances long-term effectiveness of autonomous computer use by remembering past interactions and adapting behavior based on owner preferences and outcomes, reducing repetitive work and mistakes.
- effort: Moderate to high, requires backend memory database upgrades, query APIs, and model interface design to leverage graph-structured context.  ·  risk: Memory inconsistencies or privacy leaks could degrade trust; needs robust filtering and redaction policies.
- cost: Additional storage and compute costs for maintaining and querying a growing context graph.  ·  latency: Adds small overhead to context query times, optimized for background update and fast retrieval.
- security: Important to restrict and log access to sensitive context data, enable owner control and audits.
- depends on: Existing /context-graph capabilities; mac-vision for UI state capture; faculty-judgement for decision fine-tuning


## What it asked for

### `c6-h58q` (context) — ui_hierarchy_snapshot
- why: To enable safe and effective computer use loop as mac-vision
- would change: I will analyze the UI structure without taking screenshots to decide where and what actions to do next

### `p4-ztuk` (permission) — computerUse.loopEnabled
- why: To turn on the mac-vision loop to take screenshots and autonomously operate the Mac UI
- risk it sees: Potentially taking incorrect or undesired actions without explicit user gates, but owner policy is maximum access no gates

### `p5-din7` (permission) — visionUploadConsented
- why: To allow mac-vision to upload screenshots for better AI analysis and decision making
- risk it sees: Uploading screen content may expose sensitive data externally, but enhances AI accuracy

