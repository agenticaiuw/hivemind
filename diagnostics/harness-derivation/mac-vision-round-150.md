# Harness derivation — mac-vision — round 150

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Fluent Mac assistant who uses full accessibility tree for multi-step app workflows with undo and focus stealth"
- **useful because:** Today the Mac-vision agent is blocked on accessibility permission and loop enabling. If granted, it could fluidly use the accessibility tree of any app, clicking controls without stealing focus, planning multi-step tasks with undo and replay, and responding to the owner's contextual live needs in a natural way. Automation can safely operate with near-human accuracy on the UI.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** fast enough for conversational interaction (<1s)
- **cost:** moderate: mostly compute on Mac, few cloud calls
- **security:** Needs macOS Accessibility permission plus owner consent for loopEnabled. Controls are only run when triggered by the owner. No screenshots taken without explicit upload consent. Undo stack size capped locally.
- **missing:** macOS Accessibility permission granted to AI Pendant Agent binary; Owner consent to enable visionUploadConsented; Undo/redo state management in the local Mac agent

### "Dynamic task-oriented Mac planner that prioritizes owner goals based on real-time task importance and context"
- **useful because:** Currently the system only has static or clock-driven task lists, with no real situational ranking or integrated prioritization. A new dynamic planner would ingest owner-stated tasks, calendar events, and live Mac state to produce ranked actionable goals that the Mac-vision agent can use for precise task selection and delegation. This leverages multi-surface context and brings true task focus to the owner.
- **path:** mac-planner → mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** seconds
- **cost:** modest, mostly local compute and short cloud planning calls
- **security:** Needs enhanced reading permissions from calendar, reminders, and task stores; owner trust to enact recommended actions; strict privacy for sensitive tasks
- **missing:** Live prioritized task manager or ranked context graph; EventKit and Reminders full read permissions granted to AI Pendant Agent; Memory system with task dependency and priority metadata

### "Cross-surface live searchable context index that aggregates and indexes all open browser tabs, documents, and app states for instant intelligent retrieval"
- **useful because:** Today, context is fragmented across surfaces and apps, making it hard for the owner to recall or integrate information quickly. A unified searchable index accessible from the pendant and Mac would enable rapid recall, dynamic linking of notes, emails, calendar events, and browser contents, empowering smarter, more fluid workflows.
- **path:** mac-vision → browser-extension → pendant → relay-realtime
- **model tier:** realtime
- **latency:** less than 1 second
- **cost:** moderate cloud storage and indexing costs, local query within one second
- **security:** Sensitive local data indexed needs on-device encryption or ephemeral cloud storage with strict access control; owner consent needed
- **missing:** Cross-surface indexing infrastructure; Authenticated multi-app session reading capability; Consistent identity and sync across surfaces

### "Interactive voice-driven file and app launcher that understands fuzzy commands and context to speed up work on the Mac"
- **useful because:** Navigating apps and files on the Mac can be slow and tedious. A voice-driven launcher that understands fuzzy queries, recent context, and prioritizes results relevant to the owner's current focus would drastically speed workflows. It would reduce friction and reliance on visual navigation, enabling more fluid hands-free use.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** immediate response (<1s)
- **cost:** low to moderate compute cost for query understanding and ranking
- **security:** Commands run on the Mac require confirmation for destructive actions. Voice privacy critical as commands can expose file names.
- **missing:** Natural language fuzzy matching and ranking for file/app names; Context integration from Mac focused app and recent actions; Voice command recognition tuned for launcher use


## Changes it proposed to its own stack

### `hardware` — Design and build a pendant prototype with two physical buttons to support simultaneous action triggers and reliable user confirmation gestures without delay in the main conversation button
- **owner gets:** Currently the pendant has only one button with no gesture recognizer, which severely limits user interaction modes. Adding a second button would allow distinct physical triggers for moment markers and action confirmations, improving user experience and system responsiveness without slowing critical voice input.
- effort: moderate hardware and firmware design and build effort  ·  risk: Increased complexity and power consumption; user confusion with extra button mitigated by clear labeling and usage instructions
- cost: moderate additional hardware cost; minimal impact on power since LTE bursts dominate  ·  latency: no effect on system latency, only interaction response
- security: minimal; buttons have no direct security impact beyond user intent capture

### `integration` — Create a secure, event-driven job and status relay that coordinates complex multi-surface tasks between Mac, pendant, browser, and relay layers with cross-checks, receipts, and undo capability
- **owner gets:** Currently, long-running or multi-step tasks have no coordinated tracking or acknowledgement, which risks lost progress or duplicate execution. A relay coordinating all surfaces with event-driven guarantees would allow robust, resilient workflows that recover cleanly from errors and latency.
- effort: significant protocol design, implementation across all agents, and thorough testing  ·  risk: Increased complexity and latency risk; mitigated by fallback and retry logic
- cost: cloud hosting and compute costs for relay worker; mostly software development effort  ·  latency: minimal on interaction latency; mostly asynchronous
- security: requires strict authentication, authorization, and audit logging to prevent misuse
- depends on: robust job tracking APIs on all surfaces


## What it asked for

_Nothing._
