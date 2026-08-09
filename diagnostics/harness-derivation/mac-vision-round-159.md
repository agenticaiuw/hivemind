# Harness derivation — mac-vision — round 159

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision loop on the owner's Mac with accessibility permissions granted to drive the Mac's UI through the accessibility tree without stealing focus or requiring screen recording."
- **useful because:** This allows safe and efficient computer interactions by reading and acting on UI controls without pixel capture, preserving owner privacy and multi-task workflow without disruption.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** real-time, under 5 seconds per interaction
- **cost:** Low per interaction, mainly CPU usage on Mac and server APIs called
- **security:** Requires owner consent for Accessibility permissions to prevent unauthorized control. No screen pixels captured. Actions are only executed as planned with UI component access agreed by the OS environment.
- **missing:** Owner grant for Accessibility permission to AI Pendant Agent binary; ComputerUse.loopEnabled true; VisionUploadConsented true for off-machine UI state upload if needed

### "Provide a system-wide Mac task and goal manager integrated with the AI Pendant to record, prioritize, and track owner-stated tasks beyond simple reminders and calendar events."
- **useful because:** Currently, the system lacks a durable, prioritized, and accessible task list reflecting the owner's actual intent and goals across surfaces, limiting utility and coherence of agent actions on the Mac.
- **path:** mac-planner → mac-vision → relay-realtime → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** background or scheduled sync; real-time UI query under 2 seconds
- **cost:** Moderate API costs for syncing and querying; low local UI management overhead
- **security:** Requires secure storage and owner control of task privacy; syncing strictly by owner consent.
- **missing:** API and UI for owner-friendly task input and edits; Integration with macOS Reminders, Calendar, and memory stores; Surfaces permissions for persistent task management

### "Implement cross-surface context and UI state synchronization between mac-vision, mac-planner, browser-extension, and relay-realtime to create a unified owner experience across all devices and apps."
- **useful because:** Currently, each surface operates mostly in isolation. Synchronizing state and UI context improves coherence, preventing repeated work, unnecessary queries, and enables faster context recovery after switching devices or apps.
- **path:** mac-vision → mac-planner → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** real-time or near-real-time state sync under 1 second
- **cost:** Moderate to high cost for frequent syncing of UI and context snapshots across surfaces
- **security:** Careful privacy controls needed to avoid leaking UI or sensitive info across device surfaces.
- **missing:** Cross-surface event bus or shared context mapping; APIs to push and pull UI/accessibility state and context; Unified memory graph update APIs

### "Create a secure, explicit owner consent and audit framework for mac-vision accessibility and UI control actions that logs each UI interaction, what was clicked or typed, and allows the owner to review and revoke permissions or undo actions."
- **useful because:** This would build owner trust and safety by making every mac-vision UI action visible, reversible, and under their explicit control, overcoming current privacy and safety concerns that block the loop from being enabled.
- **path:** mac-vision → mac-planner → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** interactive, under 5 seconds per audit query
- **cost:** Low cost: mostly local logs and reporting
- **security:** The audit logs could reveal sensitive UI interactions, so they must be stored securely and access controlled by the owner only.
- **missing:** Logging framework integrated with mac-vision actions; Audit UI for owner to review, approve or undo actions; Permission and revocation APIs

### "Develop a rich natural language Mac file manager accessible via mac-vision that can browse, search, open, move, rename, and delete files and folders using voice or typed instructions, integrated with context-aware suggestions from memory."
- **useful because:** No current mac-vision capability enables complex file management tasks through natural language and UI control, limiting the owner's ability to manage local files hands-free.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** real-time, under 3 seconds for UI action planning
- **cost:** Moderate per-use cost due to parsing, UI interaction, and context retrieval.
- **security:** File operations can be destructive; requires strong confirmation and undo capabilities.
- **missing:** mac-vision UI action expansion for file explorer apps; Context-aware file indexing and search integration; Undo and confirmation UI flows

### "Integrate the pendant's UART diagnostic log bug reports automatically into the Mac's issue tracking and development workflow, allowing the owner and agents to triage hardware and firmware issues seamlessly."
- **useful because:** Currently, bug reports from the pendant's UART log are manually handled or disconnected from the owner's development workflow, reducing efficiency and visibility into hardware issues.
- **path:** mac-planner → relay-realtime → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** background sync within minutes
- **cost:** Low cost, mainly local log parsing and upload with metadata tagging.
- **security:** Sensitive log data must be secured and only shared with trusted owner tools; owner control of report generation is essential.
- **missing:** Log parsing and report synthesis tools; Integration points with issue tracking systems; Owner-configurable filters and triggers


## Changes it proposed to its own stack

### `hardware` — Add a second, low-latency, multi-function physical button or touch sensor to the pendant, dedicated to mac-vision and other agent gesture inputs.
- **owner gets:** Allows the owner to invoke and confirm complex multi-step gesture commands safely and deliberately on the pendant without slowing down the main talk button or relying on ambiguous gestures.
- effort: Medium hardware design and firmware update work.  ·  risk: Minimal risk if tested; potential for accidental triggers if poorly designed.
- cost: Low additional component cost and negligible power increase.  ·  latency: Improves latency and reliability of multi-step commands on the pendant.
- security: Enables stronger explicit physical user consent gestures for high-risk actions.


## What it asked for

### `c16-622d` (context) — mac-vision agent current task list
- why: To understand what the owner currently wants done on the Mac for focused computer use via mac-vision
- would change: With a current prioritized task list, I can plan and propose actionable next steps that align with the owner's current goals, avoiding guesswork and wasted effort.

