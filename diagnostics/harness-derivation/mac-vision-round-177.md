# Harness derivation — mac-vision — round 177

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A dynamic owner goal and task manager integrated across all surfaces that can store, prioritize, and let the owner update tasks with deadlines, dependencies, and topics."
- **useful because:** Currently the owner has no durable, structured, cross-surface task list with priorities or deadlines; this will allow more effective task handling by all agents and better alignment with owner intent.
- **path:** mac-planner → mac-vision → unified → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** background or interactive with occasional bursts
- **cost:** moderate internal storage and processing costs
- **security:** Task data stored locally and optionally encrypted; owner controls read/write permissions; no external sharing without consent.
- **missing:** Extended memory store capable of handling tasks with metadata like deadlines, dependencies, priority, and topical tagging.; UI and voice interfaces on all surfaces for owner to add, review and change tasks easily.; Cross-surface data synchronization and conflict resolution.; Agent logic to prioritize and recommend tasks to the owner based on urgency, context and historical completion.

### "Context-aware visual UI advisor for the owner that guides them through complex Mac app workflows by highlighting accessibility tree controls and narrating next steps through the pendant speaker."
- **useful because:** The owner can receive real-time, step-by-step assistance for complex tasks on their Mac without needing full automation control enabled, improving understanding and reducing errors in complex environments.
- **path:** mac-vision → pendant → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** real-time interactive, under 1 second response
- **cost:** moderate, dominated by UI context processing and speech synthesis
- **security:** No automation of UI actions, only guidance; strict privacy on UI accessibility tree data; active consent from the owner for data usage.
- **missing:** macOS Accessibility permission for UI tree reading, without full automation grants.; New pendant audio output capability for clear step narration.; A robust UI context parser to extract meaningful step guidance.; Integration across multiple agents/surfaces to track progress and adapt guidance dynamically.

### "A high-fidelity multimodal interaction log that records voice commands, visual UI states, physical button presses, and agent decisions for full owner review and control history."
- **useful because:** This empowers the owner with transparency, the ability to audit agent actions, understand decisions, and learn from past interactions, improving trust and safety.
- **path:** mac-vision → relay-realtime → pendant → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** background storage with occasional queries
- **cost:** moderate storage and indexing cost; manageable querying cost
- **security:** Secure local encryption of all data; owner-only access; no external sharing without explicit owner consent.
- **missing:** A persistent secure logging store across all surfaces and modalities.; Integration hooks on all input/output and agent decision points.; A user-friendly review interface for owner querying and playback of logs.

### "Personalized AI Mac tutor surface that learns the owner's workflow habits and teaches shortcuts, app integration tips, and automation triggers proactively."
- **useful because:** Empowers the owner to learn and become more efficient with their Mac and AI integration, reducing friction and increasing productivity through personalized recommendations and tutorials.
- **path:** mac-planner → mac-vision → pendant → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** background learning with interactive responses
- **cost:** moderate for ongoing learning and context evaluation
- **security:** All learning data stored locally; owner controls sharing; privacy-first design.
- **missing:** Data collection and behavioral analysis infrastructure.; Integration with mac-vision UI context and usage patterns.; Dynamic tutorial generation and feedback mechanisms.


## Changes it proposed to its own stack

### `hardware` — Add a dedicated second button to the pendant device just for mac-vision agent confirmation gestures and safety overrides.
- **owner gets:** Separates urgent or safety critical confirmation inputs from the main button, removing the need for ambiguous button gestures and reducing accidental activations, greatly improving safety for UI automation.
- effort: Moderate hardware design and firmware changes with associated testing and rollout.  ·  risk: Medium risk of hardware faults or increased power draw; mitigated by thorough testing.
- cost: Low to moderate component and manufacturing cost increase; negligible effect on power consumption.  ·  latency: No impact on latency.
- security: Improves security by reducing accidental activations and allowing more deliberate confirmation flows.

### `context` — Implement a unified context sharing and memory system across all agents and surfaces to enable seamless transfer of UI state, owner goals, task prioritization, and physical interaction states.
- **owner gets:** This avoids redundant context-fetching, gaps in state understanding, and enables agents like mac-vision to make informed decisions based on richer, shared context, improving responsiveness and relevance.
- effort: High due to the need for cross-agent protocol design, API changes, and waste-safe sync.  ·  risk: Medium risk of synchronization bugs or stale context; mitigated by robust versioning and fallback.
- cost: Moderate increase in network and storage usage.  ·  latency: Reduced latency overall across agents due to avoiding repeated fetches.
- security: Requires secure synchronization and strict access control on sensitive data.
- depends on: network; memory; devices


## What it asked for

_Nothing._
