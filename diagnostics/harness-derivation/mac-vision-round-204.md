# Harness derivation — mac-vision — round 204

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a transparent UI state reconciliation for Mac ongoing work: combine vision loop UI observations with workbench context claims so the owner can see precisely what is actually on screen vs. what the system believes is in progress, including interrupted tasks."
- **useful because:** This solves a current invisibility gap where workflows may be interrupted or retried but the owner does not know what the AI believes is in progress vs. what is really on screen. It improves trust and coordination between human and AI on Mac workflows.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 1-2 seconds for reconciliation and reporting, asynchronous for all but live owner queries
- **cost:** Moderate API cost for continuous UI state extraction and reconciliation; bounded by accessibility tree and workbench query size
- **security:** Requires reporting of live UI state which the owner may consider sensitive; should remain local or end-to-end encrypted with owner control
- **missing:** fine-grained UI state snapshot diffing against prior snapshots; workbench context claims that report UI leaf node matches; owner policy on visibility and privacy preferences

### "Provide a prioritized and owner-driven task queue integrated with mac-vision loop that dynamically reads owner tasks from memory projections and allows adding, prioritizing, and marking tasks done, with live synchronization to Mac reminders and backends."
- **useful because:** Currently the Mac-vision agent has no reliable prioritized work queue to act on. This capability provides a living to-do list genuinely reflecting owner intent and urgency with real-time updates, enabling proactive autonomous action and better human-AI collaboration on the Mac.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 500ms to 2s per update, batching acceptable
- **cost:** Light to moderate API cost, mainly UI state reads and synchronization with Reminders and memory projection reads
- **security:** Requires handling sensitive task data and user priorities securely with local storage and encryption
- **missing:** bidirectional live sync support for Apple Reminders; owner-driven priorities expressible with deadlines, dependencies, labels; UI components on mac-vision to display and update tasks

### "Enable a safe autonomous Mac-vision loop policy that defines when automatic UI interactions may start, stop, retry or escalate to human intervention, including confirmation gates for destructive actions and feedback loops for error detection."
- **useful because:** With the Mac-vision loop enabled and permissions granted, the next bigger problem is managing autonomy safely. The owner needs clear policies controlling AI actions to ensure trust, avoid annoyances or errors, and provide escalation paths. This capability would underpin safe autonomous Mac operation.
- **path:** mac-vision → faculty-judgement → faculty-perception → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** Fast for local decision making, minutes for complex escalation planning
- **cost:** Low API cost, mostly policy evaluation and telemetry from local AI loops
- **security:** Requires storing and enforcing owner preferences securely; must not override owner consent or sensitive actions without explicit approval
- **missing:** detailed autonomous interaction policy schema; local feedback and telemetry capture for action results; UI to present escalation and status to the owner clearly

### "Provide a UI state verification and correction system for interrupted or long-running Mac tasks that integrates vision loop screen observations with a UI-level undo history and user feedback, enabling AI to detect and fix drift between expected and actual UI states."
- **useful because:** Currently, there is no way for Mac vision to confirm if interrupted workflows or multi-step tasks remain consistent with the owner's screen. Detecting and fixing UI drift will enable more reliable autonomous Mac operation and user trust in long work sessions.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 1-3 seconds for validation, user feedback can be asynchronous
- **cost:** Moderate API cost for accessibility tree snapshots, undo history tracking, and feedback loop integration.
- **security:** Requires capturing and processing UI state possibly exposing sensitive info; must preserve user privacy and control.
- **missing:** persisted undo history of UI actions; UI snapshot diffing and state verification tools; user interface for feedback and manual correction

### "Create a multitier task urgency estimation framework that integrates owner tasks, system states, and external context (like calendar, location, time of day) to dynamically reprioritize Mac tasks for the Mac-vision agent's proactive action."
- **useful because:** The Mac-vision agent currently has only rudimentary task priorities. A dynamic, contextual urgency estimation would enable more nuanced and owner-aligned proactive behavior on the Mac, improving productivity and user satisfaction.
- **path:** mac-vision → faculty-judgement → faculty-perception
- **model tier:** gpt-5.6-luna
- **latency:** under 500ms for urgency reprioritization updates
- **cost:** Low to moderate API cost for context synthesis and ranking.
- **security:** Requires access to sensitive owner context data including calendar and location; must enforce strict privacy and security.
- **missing:** access to integrated calendar and location context prior to task ranking; context fusion model tuned for urgency estimation; privacy-aware task reprioritization policy

### "Develop a mac-vision surface UX that expresses ongoing agent state, including visibility into what the AI believes about ongoing Mac workflows, task priorities, and errors encountered during automation steps."
- **useful because:** To build owner trust and ensure smooth cooperation, the AI's current view of the Mac workflows and automation status must be accessible and understandable to the owner, including any detected errors or required interventions.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** 1-2 seconds for state polling and UI refresh
- **cost:** Low API cost mainly for UI updates and state queries.
- **security:** UI state and error reporting may reveal sensitive info; must provide owner control and data minimization.
- **missing:** UI framework for mac-vision to show agent state and feedback; bindings to internal task priority and job tracking systems; error classification and reporting mechanisms integrated into mac-vision


## What it asked for

_Nothing._
