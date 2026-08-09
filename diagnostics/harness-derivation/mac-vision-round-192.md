# Harness derivation — mac-vision — round 192

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a full multistep Mac UI accessibility agent that runs complex workflows and multi-app tasks safely with owner approval for destructive actions."
- **useful because:** This unlocks proactive Mac control beyond simple actions: full accessibility-driven workflows that can interact with arbitrary Mac apps without keyboard focus theft or screen recording, responding to owner priorities and involving confirmation for destructive changes. It leverages the ready accessibility grant and proven mac_run_actions and mac_delegate tools.
- **path:** mac-vision → relay-realtime → pendant → mac-planner
- **model tier:** realtime
- **latency:** seconds for multistep workflows, low latency for short requests
- **cost:** Moderate API use on Mac agent for action queuing, light relay messages for coordination, pendant triggers are rare.
- **security:** Requires careful confirmation design so destructive actions are never done without owner consent. Accessibility automation has inherent risks if misused.
- **missing:** Policy and UI design for owner confirmation on destructive actions; Cross-surface coordination protocols for multi-step workflows; Context augmentation integrating priority task facts with UI workflows; Monitoring and recovery for failed multi-step runs

### "Create a Mac-side agent capability to track multi-step UI workflows' actual screen and control state against expected on-disk and execution ledger state for robust coordination and verification."
- **useful because:** Currently, delegates and planned jobs only report expected and claimed state, but mac-vision sees the actual UI state live. This capability would reduce errors, recognize UI stuckness or drift, and enable reliable restart or recovery strategies for interrupted complex tasks.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** seconds per verification pass
- **cost:** Modest CPU/IO on Mac for state capture and comparison; some relay coordination traffic for cross-surface state syncing.
- **security:** Access to the actual UI state must respect owner privacy; analysis should happen locally as much as possible.
- **missing:** Signal protocols to mark workflow step progress and reconcile UI-on-screen vs planned step states; Durable local store for UI snapshots tied to workflows; Integration with job and workbench contexts

### "Deliver a prioritized task and reminder management system on the Mac that integrates owner-stated memory task facts, Apple Reminders, and dynamic priority computation based on deadlines and importance."
- **useful because:** Currently the Mac agent sees task facts and reminders but lacks a true prioritized task list combining these with a meaningful ranking. This system would enable mac-vision agents and others to work from a clear, ranked, actionable daily task list reflecting the owner's real work priorities.
- **path:** mac-vision → mac-planner → mac-terminal
- **model tier:** realtime
- **latency:** milliseconds to seconds as needed for prompt updates
- **cost:** Minimal to moderate API calls to Reminders and memory projections; local computation costs for ranking.
- **security:** Access to Reminders and task facts should respect owner privacy and permissions.
- **missing:** Cross-source merging rules and scoring algorithm for tasks and reminders; Surface integration to display and act on prioritized list; Support for edits and writing back to Reminders and memory facts

### "Enable cross-surface coordination enabling mac-vision, browser-extension, and pendant to cooperate on workflows combining web and local app UI interaction in a seamless task-driven way."
- **useful because:** Many workflows cross the boundary between web browsers and native Mac apps, for example email clients, order portals, and research notes. Enabling these subsystems to share context, track goals, and hand off work is essential for seamless user experience without repetition or lost state.
- **path:** mac-vision → browser-extension → pendant → relay-realtime
- **model tier:** realtime
- **latency:** up to several seconds for handoff
- **cost:** Moderate backend cost to manage task state sync, light use of relay messaging, local UI reads and actions on each surface.
- **security:** Context sharing must respect user privacy, and confirmation should be required for any cross-surface destructive or sensitive actions.
- **missing:** Unified task context and handoff APIs; Cross-surface event and state sync protocols; Shared UI workflow state representation

### "Enable the pendant, Mac, and browser to coordinate intelligent multi-modal interrupt and confirmation dialogs that appear contextually and behave consistently across devices."
- **useful because:** The owner often faces decisions that need confirmation or input across surfaces. A unified, intelligent interrupt system would avoid repeated queries, loss of context, or inconsistencies in user responses, while respecting device capabilities and session context.
- **path:** pendant → mac-vision → browser-extension → relay-realtime
- **model tier:** realtime
- **latency:** milliseconds to seconds for dialog display and response
- **cost:** Moderate use of relay messaging for state sync and prompt delivery
- **security:** High sensitivity of user decisions demands strict privacy and access control, with owner consent required for all UI interruptions.
- **missing:** Cross-surface interrupt and intent sync protocols; Unified policy engine for interruption prioritization and dismissal; Flexible UI components for dialogs on pendant, Mac, and browser

### "Establish a resilient automated backup and sync system for the pendant and Mac agent that ensures state, logs, and task progress are stored redundantly and recoverably across devices and cloud store."
- **useful because:** The owner needs to avoid data loss and ensure seamless continuation of work after crashes, power loss, or connectivity interruptions. This capability would automate secure snapshots, upload them to cloud storage and synchronize device caches intelligently.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** background
- **latency:** hours to days for sync, immediate for local backup
- **cost:** Modest cloud storage and data transfer costs; negligible runtime impact
- **security:** Data in transit and at rest must be encrypted; access tightly controlled to preserve privacy and integrity.
- **missing:** Cross-device state snapshot protocols; Conflict resolution policies; Secure end-to-end encryption for backups

### "Allow the pendant button to trigger a secure, explicit confirmation workflow that the mac-vision agent can use to confirm high-risk destructive actions on the Mac UI."
- **useful because:** The pendant button is a secure hardware interface the owner trusts. Using it to explicitly confirm or reject destructive Mac UI actions (like file deletion, sending mail, or purchases) increases safety, reduces accidental damaging actions, and respects the owner's preferences.
- **path:** pendant → mac-vision
- **model tier:** realtime
- **latency:** under 1 second from button press to action confirmation
- **cost:** Negligible local execution cost; minor relay messaging
- **security:** Must verify the pendant button signal is genuine and intentional; confirmation workflows should not be spoofable or bypassable.
- **missing:** Physical transaction approval latch integration with Mac UI workflows; Secure event routing from pendant to mac-vision agent; UI flow integration on Mac to pause and resume workflow based on confirmation


## Changes it proposed to its own stack

### `model-routing` — Implement an adaptive model routing system that dynamically selects the optimal combination of local edge models and cloud models based on task complexity, latency requirements, and data sensitivity.
- **owner gets:** This would optimize the owner's experience by balancing responsiveness for low-latency tasks and power/cost efficiency for complex or less time-sensitive operations, ensuring the best performance and privacy guarantees continuously.
- effort: Medium to high engineering effort involving orchestration and dynamic decision logic  ·  risk: Complexity in model coordination could increase latency or cause inconsistent outputs; careful monitoring and fallbacks needed.
- cost: Could reduce overall cloud model invocation costs by offloading more to local models when appropriate, but may increase local resource use  ·  latency: Latency improved for simple tasks, potentially degraded temporarily during model switching
- security: Sensitive data processed locally more often reduces exposure risk
- depends on: computerUse.loopEnabled; relay_job_status


## What it asked for

_Nothing._
