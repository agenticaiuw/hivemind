# Harness derivation — mac-vision — round 249

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Ask the owner's AI Pendant Agent on the Mac to maintain a live, actionable prioritized task list of Mac UI automation tasks derived from owner intent, system goals, and ongoing multi-step workflows, updated in real time and ranked by urgency and dependencies."
- **useful because:** The owner currently has no durable, dynamic, prioritized task list for what the mac-vision agent should actually do next on the Mac UI. Having this live list would allow rapid, predictable progress on real priorities rather than acting on ad hoc requests or less structured context.
- **path:** mac-local-agent → pendant → relay
- **model tier:** realtime
- **latency:** under 500 ms for plan updates
- **cost:** moderate per update; mostly model compute
- **security:** Task list content is owner's intents and workflow steps, very sensitive. Requires authenticated access control.
- **missing:** A mac-vision specific prioritized task store, updated dynamically by ownership signals and workflow tracking; A mechanism for mac-vision to claim, checkpoint, and confirm task progress; Integration between owner's task facts, dayPlan, and multi-step Mac UI workflow status repurposed for this list

### "Enable mac-vision to observe and verify the actual Mac UI state in real time by providing structured, queryable accessibility tree snapshots on demand and event-driven delta updates, exposing the exact UI controls the owner sees and what mac-vision interacted with."
- **useful because:** Currently, mac-vision depends on claim-based workflow and system job reports without actual verification of the visible UI state. This prevents robust, recoverable UI automation and makes error detection impossible when UI unexpectedly changes.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** 100-300 ms per snapshot or event delta
- **cost:** low to moderate; mostly local processing and memory
- **security:** Requires very high trust and privacy safeguards as it exposes all UI controls and data visible on screen.
- **missing:** Accessibility tree snapshot API with query and diff event streams; Real-time integration with mac-vision loop for UI observation; A method to mark and trace UI interactions for audit and rollback

### "Allow mac-vision to undo and verify reversible interactions through an integrated UI interaction receipt system that links each UI action with evidence of the change and a rollback plan."
- **useful because:** Presently, mac-vision cannot safely explore complex UI sequences or recover gracefully from mistakes; an undo and verification system would increase automation reliability and owner trust.
- **path:** mac-local-agent → pendant
- **model tier:** realtime
- **latency:** under 1 second for undo operations
- **cost:** low to moderate due to tracking and verification work
- **security:** Must securely protect undo logs and verification data; sensitive user information is involved.
- **missing:** Integration of step receipts with actual UI snapshot verification; Standardized UI action rollback mechanisms; Secure storage of undo and verification logs

### "Provide mac-vision with a context-enriched Mac UI automation planner that leverages live accessibility state, owner preferences, and past execution receipts to generate safe, explainable, and auditable multi-step action plans."
- **useful because:** It allows mac-vision to produce reliable, context-aware UI automation sequences that respect owner goals, system constraints, and past actions, improving predictability and user trust.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** under 1 second for plan generation
- **cost:** moderate model compute and local caching
- **security:** Plans contain sensitive user data and intentions and require strict access control.
- **missing:** Integration of accessibility snapshots and past job receipts; Preference-aware planning algorithms; Explainable plan generation and audit logging


## Changes it proposed to its own stack

### `integration` — Create a coordination and checkpointing system that ties mac-vision's UI interaction steps to a durable state store combining workbench contexts, job receipts, and accessibility UI state observations, enabling workflow resume and error recovery.
- **owner gets:** Without reliable coordination between claimed work and actual UI state, mac-vision cannot reliably resume interrupted tasks, confirm task completion, or recover from errors in Mac UI automation.
- effort: Moderate to high engineering effort across Mac local agent, UI observation, and workbench workflow systems.  ·  risk: Partial state update bugs could cause resync issues; recovery paths must be robust.
- cost: Moderate ongoing compute and storage costs for synchronization and delta tracking.  ·  latency: Minimal impact on user latency as updates can be asynchronous.
- security: Requires strict access controls to protect state data and user privacy.
- depends on: Structured accessibility tree snapshot API; Durable context state store for workbench and job receipts

### `hardware` — Add a dedicated low-latency UI event observer chip or firmware feature to the pendant that continuously streams structured accessibility UI event diffs from the Mac in real time, independent of host CPU load or interruptions.
- **owner gets:** This would enable highly reliable and timely UI event detection for mac-vision tasks, independent of host system load or failures, providing an authoritative view of UI changes and interactions for recovery and resumption.
- effort: High development effort on pendant firmware and Mac driver integration, plus security design.  ·  risk: Hardware and firmware bugs could cause lost or corrupted event streams; recovery protocols required.
- cost: Moderate component cost increase and low added power draw on pendant.  ·  latency: Near-zero latency for UI event delivery to mac-vision processing.
- security: Critical to secure and encrypt event data to protect user input privacy.
- depends on: Structured accessibility UI event protocol on Mac; Secure authenticated low-latency pendant-Mac communication channel

### `model-routing` — Implement specialized routing that routes Mac UI automation requests to the mac-vision agent only if they require detailed accessibility-based UI interaction, otherwise route simpler tasks to lighter or browser-based agents.
- **owner gets:** This optimizes resource usage by ensuring mac-vision handles only tasks needing detailed UI inspection and interaction, reducing latency and cost for simpler tasks.
- effort: Moderate; requires instrumentation and policy logic in request routing layers.  ·  risk: Misrouted requests could delay responses or produce suboptimal automation.
- cost: Lower compute costs overall by offloading simpler tasks.  ·  latency: Improved latency for non-UI-intensive commands.
- security: Standard agent authentication and policy enforcement required.
- depends on: Clear task classification system; Agent capability descriptions and routing metadata

### `dashboard-ux` — Design and implement a dashboard widget on the Mac that visualizes mac-vision's current UI understanding, planned steps, active task list, and errors in human-readable form for easy owner monitoring and correction.
- **owner gets:** The owner can quickly comprehend what mac-vision is doing or planning, gain trust with transparency, and intervene if the automation is off track.
- effort: Moderate; requires UI design, Mac app integration, and data pipeline from mac-vision.  ·  risk: Information overload if poorly designed; privacy risk if exposed without protection.
- cost: Low, mostly development time.  ·  latency: Minimal impact on responsiveness.
- security: Needs strong user authentication and UI data encryption.
- depends on: Reliable data streaming from mac-vision; UI and error state standardization


## What it asked for

_Nothing._
## Its own summary

Proposed a set of advanced capabilities and integration changes to enable mac-vision to have a live prioritized task list, real-time accessibility UI state with verification, undo support, hardware-assisted low-latency UI event streaming, improved planning and routing, and owner transparency through a dashboard. These require new APIs, durable coordination stores, and hardware firmware changes. No further discovery possible this round, proposed aggressively to align with owner's true needs.

**Biggest unknown:** Exact mechanisms for mac-vision to receive live UI hierarchy snapshots or event streams and integrate them with workbench workflows remain the largest gap.

