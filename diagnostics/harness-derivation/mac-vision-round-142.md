# Harness derivation — mac-vision — round 142

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable seamless and trustworthy Mac accessibility control loop that can autonomously browse, click, type, and manipulate user interface elements reliably without stealing focus or relying on pixel capture."
- **useful because:** This would allow the owner to delegate complex multi-step Mac workflows and UI interactions that currently require manual intervention or partial automation, significantly increasing productivity and reducing friction.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** subsecond to seconds per interaction
- **cost:** Moderate API call cost due to context reads and multi-step actions, minimal hardware cost beyond existing pendant usage.
- **security:** Full accessibility access is sensitive; must confirm safety protocols, and all destructive actions must require explicit owner consent before execution. Interactions run offline with periodic relay confirmation.
- **missing:** macOS Accessibility permission granted to the running AI pendant agent binary; A robust state and error rollback system to prevent focus steals or rogue UI interactions; Better integration of accessibility tree observations with action receipts and undo mechanisms

### "Implement a unified owner task goal manager that ingests, prioritizes, and maintains the owner's current high-priority tasks and multi-surface intentions, syncing them as actionable goals to the Mac vision and planner agents."
- **useful because:** Today the system has only hand-typed loose text tasks and scheduled routines with no true priority or state. This manager would enable proactive, context-aware, and optimized task execution aligned with what the owner truly wants done now.
- **path:** unified → mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds to minutes for planning and prioritization updates
- **cost:** Moderate API usage for synchronization and prioritization logic, no hardware cost.
- **security:** Sensitive owner data stored and prioritized; must encrypt and respect privacy, with explicit owner controls over task creation and removal.
- **missing:** A common task state schema and persistent store across surfaces; Interfaces for owner task input beyond typed facts, such as voice or quick capture; Priority algorithms that integrate calendar and reminders with ad-hoc notes and tasks

### "Create a predictive Mac interaction assistant that anticipates the owner's next likely app and UI element interaction based on usage patterns, calendar events, and ongoing tasks, and preloads or pre-navigates the UI to optimize workflow speed."
- **useful because:** This reduces friction for frequently repeated workflows and context switches on the Mac, saving the owner time and cognitive load by smartly preparing the Mac UI in advance.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** milliseconds to seconds for prediction
- **cost:** Low to moderate API usage for context reading and prediction, no extra hardware needed.
- **security:** Prediction must run locally with no data leaving the device to prevent privacy leaks. Model accuracy must be high to avoid confusion.
- **missing:** Historical UI interaction data capture and storage; Advanced prediction models trained on owner behavior; Integration with accessibility and mac_run_actions for preloading UI states

### "Provide a voice-enabled Mac interface that can take spoken commands converted to actionable steps by the mac_delegate tool, enabling hands-free control of complex multi-app workflows while driving the Mac accessibility control loop."
- **useful because:** This allows the owner to accomplish complex computer work while mobile or physically engaged elsewhere, leveraging voice recognition combined with the Mac accessibility ecosystem for robust control.
- **path:** relay-realtime → mac-vision → mac-planner → pendant
- **model tier:** realtime
- **latency:** subsecond to seconds per voice command
- **cost:** Moderate; voice processing and command interpretation are relatively expensive operations.
- **security:** Voice commands must be authenticated and confirmed for destructive or sensitive actions to protect owner privacy and security.
- **missing:** Accurate and fast voice-to-text with domain adaptation; Integration between voice engine and mac_delegate tool; Contextual awareness of UI state for command disambiguation


## Changes it proposed to its own stack

### `context` — Augment the existing context projection and memory service to automatically harvest actionable task entities from the owner's interactions, documents, emails, and voice notes, and surface these as candidate goals for Mac-vision and planner to act on.
- **owner gets:** This would reduce the manual burden of task entry, help keep the agent aligned with real owner intent dynamically, and enable proactive task suggestions and executions without relying solely on scheduled routines or hand-typed task facts.
- effort: High engineering effort to build and test natural language understanding pipelines and sync with context memory graph.  ·  risk: Misinterpretation or too aggressive task harvesting could annoy the owner; mitigated with opt-in controls and gating before execution.
- cost: Extra compute for NLP and context processing, mainly server side; negligible on pendant or Mac hardware.  ·  latency: Medium latency on task detection; realtime for execution planning.
- security: Sensitive data processing requires encryption, best done on trusted local or cloud systems.
- depends on: permission to read owner data sources such as mail, notes, files, and voice transcripts

### `integration` — Build a secure relay path so the Mac-vision agent can stream live UI accessibility tree snapshots and predicted next actions to the pendant device in real-time for confirmation, annotation, and voice query, enabling seamless mixed-device workflows.
- **owner gets:** This allows the owner to stay aware of and control complex Mac interactions from the pendant device, improving convenience, safety, and feedback while offloading heavy UI exploration to the Mac.
- effort: Medium effort to build relay protocol support and UI sync mechanisms; moderate UI work for voice and pendant feedback.  ·  risk: Potential privacy risks if data leaks; mitigate with end-to-end encryption and explicit opt-in.
- cost: Increased network usage and server relay usage; moderate API cost.  ·  latency: Low latency needed for real-time feedback; relay infrastructure must be robust.
- security: Requires end-to-end encryption and strict access control to prevent interception.
- depends on: Relay is online and has authentication with pendant and Mac agents


## What it asked for

_Nothing._
## Its own summary

Proposed seven new capabilities and changes focusing on enabling seamless Mac accessibility control, unified owner task goal management, dynamic task harvesting from owner data, predictive UI interaction assistance, secure relay path for mixed-device workflows, and voice-enabled complex Mac workflow control. These focus on bridging existing tools and layers missing for full autonomous Mac interaction and task prioritization, plus integration across devices.

**Biggest unknown:** macOS Accessibility permission granted to the running AI Pendant Agent binary and the owner's consent to enable full accessibility-based control loop remain the critical blockers. Additional missing APIs for deeper integration of task data and relay capabilities also impact progress.

