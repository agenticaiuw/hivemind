# Harness derivation — mac-vision — round 220

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable robust Mac UI automation using the accessibility tree, with real-time UI state verification, adaptive multi-step workflows, and prioritized task execution."
- **useful because:** This capability lets the system reliably automate complex macOS interactions by reading the real UI tree, verifying steps, recovering from mismatches, and handling multiple applications over long-running workflows. It enables mac-vision to deliver hands-free, goal-driven Mac control aligned to the owner's real current priorities.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** Under 2 seconds for interaction confirmation, longer for background planning.
- **cost:** Medium API cost, dominated by accessibility tree parsing and multi-step planning.
- **security:** Requires macOS Accessibility granted per binary to control UI; UI snapshots remain local; task priorities respect owner preferences; high-impact commands confirmed by owner where required.
- **missing:** Accessibility UI tree snapshot API route on the Mac agent; Full integration between mac_delegate and accessibility UI state; Discrepancy detection and reporting module for UI vs planned state; Prioritized live task queue for the mac-vision agent

### "Provide a real-time UI state verification tool for all mac_delegate tasks that compares the planned UI state from receipts against the actual accessibility tree to detect and report discrepancies early."
- **useful because:** Discrepancies between the system's planned interaction state and actual mac UI can cause task failures or user confusion. Detecting these mismatches early lets the system recover, re-plan or alert the owner.
- **path:** mac-planner → mac-vision
- **model tier:** realtime
- **latency:** 1-2 seconds for detection
- **cost:** Low to medium, mainly LLM and comparison compute for small data sets
- **security:** Only compares UI state already accessible through macOS Accessibility APIs; no new sensitive data exposed; owner confirmation before recovery actions.
- **missing:** API to read accessibility UI tree snapshots; Integration into mac_delegate task receipt system for UI state verification

### "Enable a fluent multi-surface task execution system where the mac-vision agent coordinates with the relay-realtime, pendant, and browser-extension agents to share UI state, task progress, and relevant context for seamless handoff and collaboration on complex multi-step jobs."
- **useful because:** Some tasks span multiple environments (Mac UI, wearable pendant, browser) and require smooth coordination. This capability lets these agents communicate state changes, partial results, and task handoffs in real-time, improving continuity and reducing redundant work or user interruptions.
- **path:** mac-vision → relay-realtime → pendant → browser-extension
- **model tier:** realtime
- **latency:** under 1 second interaction sync
- **cost:** Medium to high, depending on communication requirements
- **security:** Sensitive task and UI state is shared among trusted surfaces only; requires authentication and encryption; honors owner privacy and data control settings.
- **missing:** Real-time cross-surface state sync APIs and event message bus; Standardized task progress and context schemas

### "Add a UI state diff and recovery assistant that monitors the accessibility tree on the Mac in real time, detects user interface changes or regressions that break workflows, and automatically proposes recovery or rollback steps to the owner via the pendant or Mac interface."
- **useful because:** UI elements on the Mac can change unexpectedly (app updates, crashes, dynamic content), breaking automation workflows. Automatic detection and recovery proposals reduce user frustration and manual intervention, improving overall reliability and trust in the automation.
- **path:** mac-vision → pendant
- **model tier:** realtime
- **latency:** seconds to detect and propose
- **cost:** Low to medium, mostly logic on diffs and recovery scripts
- **security:** All UI state is local; recovery proposals require owner confirmation; no sensitive new data collected.
- **missing:** API to monitor accessibility tree changes in real time; Integration with automation workflow engine for rollback and recovery actions

### "Enable true real-time accessibility tree snapshots and continuous monitoring on the Mac to fully inspect UI structure and state without relying on incomplete or fallback signals."
- **useful because:** Currently no direct accessible route to get full, real-time accessibility UI tree snapshots. This is fundamental for reliable planning, verification, and error recovery of any mac-vision driven automation.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** sub-second snapshot latency
- **cost:** Medium: mainly CPU for serializing/parsing accessibility trees.
- **security:** Accessibility APIs are powerful and grant full reading/control of Mac UI; snapshots stay local and are not sent off. Requires robust permission controls and owner awareness.
- **missing:** A dedicated accessible API endpoint on the Mac agent to query full accessibility tree snapshots continuously or on-demand.

### "Implement seamless multi-agent mac automation resume and recovery to pick up interrupted UI workflows exactly where they left off, using persistent UI state snapshots and context reconciliation."
- **useful because:** Multi-step UI workflows often fail or get interrupted, causing loss of progress and requiring owner intervention. Automated resume and recovery increases reliability and trust in mac-vision as a personal assistant capable of deep, multi-application work.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** seconds to detect and resume
- **cost:** Medium to high, depending on complexity of UI state diffing and heuristic recovery logic.
- **security:** Requires stable, persistent storage of UI state snapshots which may contain UI data. Owner data privacy must be respected and snapshots encrypted at rest and in transit.
- **missing:** Persistent UI snapshot storage backend integrated with mac_delegate workflows; Heuristic or AI-based reconciliation of UI state vs planned progress for recovery actions.

### "Create an autonomous UI anomaly detection and intelligent recovery advisor that observes mac-vision UI workflows, detects breakdowns automatically from live accessibility data, and proposes step-by-step recovery or alternative plans to the owner."
- **useful because:** Automation on dynamic UIs often breaks due to changes or unexpected states. Autonomous anomaly detection and recovery advice reduce frustration, improve success rates, and minimize owner involvement.
- **path:** mac-vision → pendant → mac-planner
- **model tier:** realtime
- **latency:** a few seconds for detection and recommendation
- **cost:** Medium, mostly LLM and event-stream processing compute.
- **security:** Only uses local accessibility data already accessible; all suggestions require owner confirmation; no new sensitive data collected or sent.
- **missing:** Continuous live accessibility tree monitoring integration; Anomaly detection models tuned to UI changes and automation failure modes


## What it asked for

_Nothing._
