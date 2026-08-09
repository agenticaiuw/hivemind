# Harness derivation — mac-vision — round 179

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Implement a persistent, ranked, and context-aware task and goals manager bridging owner-stated tasks, daily routine schedules, and reminders, to drive agent prioritization and action planning across Mac apps and browser."
- **useful because:** The owner and system currently lack a single source of truth for what the owner truly wants done next, limiting proactive agent assistance. A ranked task manager would unlock coordinated prioritization across all surfaces and agents.
- **path:** mac-planner → mac-vision → browser-extension → unified
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** Storage cost for task metadata and rankings, modest computation for ranking logic.
- **security:** Stores owner task data with access controls; owner controls visibility and edit rights.
- **missing:** Integrated goal/task store with ranking algorithm

### "Build a reliable and privacy-respecting Safari browser control and inspection framework including authenticated page-watch service, command queue with idempotency, semantic extraction, privacy redaction, and session recovery, tightly integrated with the Mac local agent and the pendant system."
- **useful because:** This allows automated, robust interaction with the owner’s web sessions, supports private and authenticated pages safely, and enables continuous update watching and extraction without losing state or leaking sensitive data.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** realtime and background
- **latency:** sub-second for UI commands, minutes for watches
- **cost:** Moderate due to network involvement and page processing.
- **security:** Strong privacy boundaries and redactions to protect credentials, PII, and private content; encrypted and signed communications; strict permissions.
- **missing:** Safari extension enhancements, bridge protocols, lease and supervisor subsystems

### "Integrate the pendant's single user button with the Mac and agents as a moment marker trigger that records context snapshots across all surfaces for later review and actuation, without adding new gestures or button types."
- **useful because:** This provides a reliable physical interaction channel to bookmark important moments or contexts securely and without confusion from gesture conflicts, enabling contextual recall or action initiation from the pendant.
- **path:** pendant → mac-vision → unified
- **model tier:** realtime
- **latency:** 100 ms per button press
- **cost:** Minimal; uses existing button and recording infrastructure on the pendant and Mac
- **security:** Ensures user control of when moments are recorded; data stored securely and private to owner.
- **missing:** Software integration for button event capture, context snapshot collection, and recall APIs on Mac and relay

### "Develop an offline-capable local reasoner for mac-vision to pre-validate multi-step UI automation plans and simulate their effects before actual execution, increasing reliability and safety of computer control without network dependence."
- **useful because:** This allows the AI to plan complex multi-app workflows on the Mac with confidence, detecting possible failures or side effects without immediately acting on the real UI and without needing the cloud.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** sub-second for plan validation
- **cost:** CPU and RAM on the Mac, requires low-latency execution environment
- **security:** Operates only on local Mac UI state, no network required or used, protects user privacy and system security.
- **missing:** A local UI state model, simulator engine, and deterministic plan validator integrated with mac-vision's computer use loop

### "Enable the mac-vision agent on the MacBook to observe real-time changes in frontmost app UI at accessibility level and publish minimal event streams summarizing meaningful UI changes for use by other agents and the owner to enable event-driven reactive workflows across surfaces."
- **useful because:** By pushing meaningful UI change events rather than polling or doing full snapshots, this reduces computational overhead and latency, and enables more responsive and efficient multi-surface AI workflows that can react to MAC UI state.
- **path:** mac-vision → unified
- **model tier:** realtime
- **latency:** milliseconds to seconds for event generation and delivery
- **cost:** Low CPU and memory impact compared to full tree snapshots
- **security:** Only accessibility-level data is published, no pixel or sensitive content without owner consent; strict access control on event stream consumption.
- **missing:** Event-driven hooks on mac-vision's accessibility tree observer, event normalization and filtering subsystem, event stream API for relay and other agents

### "An intelligent Mac UI assistant that can run complex, multi-step workflows autonomously, adapting in real time to UI changes and errors, without stealing focus or pixel capturing, and explaining its reasoning to the owner."
- **useful because:** Empowers the owner with seamless Mac automation that is understandable, trustworthy, and non-disruptive, greatly improving productivity and reducing cognitive load.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** 100 ms per step
- **cost:** Moderate CPU usage on Mac, minimal network cost
- **security:** Requires macOS Accessibility permission, full transparency and revertibility of actions, local execution of UI control logic.
- **missing:** Advanced AI-driven adaptive workflow engine, real-time UI state monitoring, transparent reasoning and explanation module

### "A unified cross-surface context memory and reasoning system that correlates events and states from Mac UI, browser sessions, and pendant sensor data to create a coherent model of owner activity and intent, enabling proactive and anticipatory agent behaviour."
- **useful because:** This would allow the system to make smarter decisions by understanding the owner's context holistically, improving the relevance and timing of interventions and reducing redundant or conflicting actions.
- **path:** mac-vision → browser-extension → pendant → unified
- **model tier:** background and realtime
- **latency:** seconds
- **cost:** Moderate CPU and network usage due to data correlation and inference
- **security:** Strict privacy controls, data silos unless owner explicitly consents to correlation, encrypted transmission and storage.
- **missing:** Cross-surface event collection and correlation framework, multi-modal context integration algorithms

### "A deep UX integration that enables the owner to give real-time verbal or typed feedback to the mac-vision agent during complex UI task execution, allowing dynamic correction, clarification, or pause/resume control of AI actions."
- **useful because:** This interaction model increases trust and usability by allowing the owner to remain in control and guide AI actions without breaking flow or switching context.
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** Low to moderate depending on conversation model usage
- **security:** Requires secure voice/text channels; privacy of conversations; user-initiated control only.
- **missing:** Integrated voice/text feedback channel, conversational context handling in mac-vision loop


## Changes it proposed to its own stack

### `hardware` — Add a second programmable user button to the pendant to enable richer physical interaction vocabulary, including distinct triggers for moment marking, mode switching, and quick context-sensitive commands, without overloading the single existing button.
- **owner gets:** The single button on the pendant limits interaction possibilities; a second button expands the range of intuitive physical commands and improves usability without ambiguous gestures.
- effort: Medium engineering effort to modify firmware and hardware layout, update driver and agent code, and test new button functionality.  ·  risk: Low risk of hardware faults; risk of confusing the owner mitigated by clear documentation and optional training.
- cost: Increased BOM cost by a few dollars; negligible power impact.  ·  latency: No significant latency change.
- security: No direct impact.


## What it asked for

_Nothing._
## Its own summary

Discovered complete hardware and software context; owner goals and tasks stores; current browser and Mac UI automation tooling states. Identified key missing grants (macOS Accessibility permission) blocking mac-vision UI automation loop. Proposed three core novel capabilities: robust mac UI accessibility loop enabling reversible control; integrated prioritized task/goal manager bridging owner tasks and routines across surfaces; and a comprehensive Safari browser control and page-watch framework integrated with Mac and pendant. Also proposed local offline plan validation and event-driven UI event streaming on Mac to improve safety and efficiency. Next steps depend critically on macOS Accessibility grant and clarifications on browser harness and task system integration.

**Biggest unknown:** Whether the macOS Accessibility permission for AI Pendant Agent binary will be granted and how soon to enable the accessibility-driven computer use loop for Mac automation.

