# Harness derivation — mac-vision — round 166

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to autonomously perform 1-3 concrete UI and system control actions on the Mac, triggered by voice commands on the pendant, with safe confirmation and undo support."
- **useful because:** This would let the owner control the Mac hands-free through voice on the pendant, with the Mac agent executing actions like launching apps, typing, reminders, and shell commands. It leverages the pendant's button and voice, the Mac agent's tools, and local context for smooth interaction.
- **path:** relay-realtime → mac-vision → pendant → mac-planner
- **model tier:** realtime
- **latency:** sub-second to 2 seconds
- **cost:** mostly model inference; minimal network and Mac CPU
- **security:** Requires owner consent and macOS Accessibility permissions; confirmation before destructive actions; undo must be supported to prevent errors.
- **missing:** Clear owner policy for autonomous action execution; User interface on pendant for confirmation; Persistent tracking of action history on Mac for undo support; Full macOS Accessibility permission granted to agent binary

### "Create a shared user goal store that unifies owner-stated tasks from memory facts, calendar reminders, and active routines, accessible to all agent surfaces for prioritization and action planning."
- **useful because:** Currently, the owner has no single ranked task list or understanding of priorities across systems. A unified goal store would enable better context sharing, prioritization, and coordination among mac-vision, mac-planner, relay, and others, improving effectiveness.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** Low model cost, mostly storage and syncing
- **security:** Task content may be sensitive; must respect owner privacy and encryption in sync
- **missing:** A unified persistent store and API for task aggregation and ranking; Ranking logic for priorities beyond calendar structure; Cross-surface sync and reconciliation logic

### "Grant mac-vision the ability to read the Mac's accessibility UI hierarchy without screen recording or pixel capture, by unlocking and using the native macOS Accessibility API with the necessary permissions for the running AI Pendant Agent binary."
- **useful because:** This allows mac-vision to understand UI elements structurally, enabling precise and safe interaction with background apps without focus stealing or owner disturbance, avoiding pixel-based UI analysis which is slow and error-prone.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** sub-second
- **cost:** Minimal compute; mostly permission/configuration management
- **security:** Requires owner trust to grant Accessibility permission to the AI Pendant Agent binary; API access is powerful and can observe/alter UI globally.
- **missing:** Explicit macOS Accessibility permission grant for agent binary; User education and interface for granting and revoking this permission; Policy enforcement layer to prevent abuse or surprise actions

### "Implement a real-time voice command interpretation and confirmation system on the pendant, tightly integrated with the mac-vision agent, to trigger Mac actions safely and reliably with user-approved confirmations and an undo option."
- **useful because:** This would enable nearly hands-free, eyes-free Mac control through natural language spoken to the pendant, with confirmation gestures or voice to prevent mistakes, and with undo ensuring safety. It fully leverages the hardware and multi-agent system.
- **path:** pendant → mac-vision → relay-realtime → mac-planner
- **model tier:** realtime
- **latency:** 1-3 seconds
- **cost:** Moderate model inference; low network usage; some Mac CPU
- **security:** Needs strict owner consent flows; confirmation UI on pendant; undo tracking on Mac; protects against accidental or malicious triggers.
- **missing:** Reliable voice command interpretation model on pendant; Confirmation and gesture UI on pendant hardware; Undo stack management on Mac; Secure communication and session context sharing

### "Integrate mac-vision with the Mac's calendar and reminders APIs with appropriate permissions, to provide the owner dynamic, voice-controlled briefings of upcoming tasks and events on the pendant, with ability to ask follow-up questions and mark tasks done."
- **useful because:** Owners get real-time, personalized voice briefings and task management from any location without opening the Mac, enhancing productivity and awareness while minimizing distraction. The multi-device setup leverages Mac data and pendant voice.
- **path:** pendant → mac-vision → relay-realtime → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** Minimal model cost; mainly local API queries
- **security:** Requires calendar/reminders API permissions; sensitive personal data access; must respect privacy and data control.
- **missing:** Automation permissions granted for calendar and reminders; Voice dialogue layering over briefing content; Action commands mapped to calendar/reminder updates

### "Enable mac-vision to dynamically monitor and interact with any Mac app UI element in real time, using a high-bandwidth native accessibility stream that provides incremental updates even when the screen is locked or backgrounded."
- **useful because:** Current mac-vision cannot access detailed app UI in real time without screen recording or disruptive pixel capture. Native high-bandwidth incremental accessibility streaming would allow trustworthy, safe, low-latency interactions with all Mac apps even while hidden or locked, vastly expanding control and reliability.
- **path:** mac-vision → pendant → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** 50-100 ms
- **cost:** Minimal compute, mostly OS and permission handling
- **security:** Requires deep OS integration and strong permission containment; potential for privacy risks from unintended app UI exposure.
- **missing:** High-bandwidth incremental macOS accessibility streaming API; Persistent permission granting mechanism with fine user control; OS enforcement of access boundaries by app context

### "A unified multi-surface intention and context manager that ingests voice commands from the pendant, identifies owner intent with context table lookup and natural language processing, and routes actions to the most suitable surface or agent component, with fallback and escalation logic."
- **useful because:** Owners currently have disjointed command routing and inconsistent execution across pendant, Mac, browser, and relay. A unified intention manager would deliver seamless, reliable, multi-device agent coordination, improving usability and reducing manual routing errors.
- **path:** pendant → mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** realtime
- **latency:** 1 second
- **cost:** Moderate load on real-time models; minimal network usage
- **security:** Needs strict user intent verification and privacy safeguards to avoid misrouting or action leakage.
- **missing:** Cross-surface voice command ingestion APIs; Context syncing and conflict resolution mechanisms; Intent classification and routing engine

### "A context-sensitive safety and confirmation manager that intercepts all mac-vision initiated Mac actions, evaluates risk based on past user decisions, current app state, and action type, and requests user confirmation only when risk thresholds are exceeded, using an adaptive feedback loop."
- **useful because:** Owners need trustable safety for autonomous Mac control by mac-vision. Without nuanced confirmation they face either constant interruptions or dangerous silent errors. Adaptive safety filtering tailored per user and context enables confident hands-free control with minimal disruption.
- **path:** mac-vision → pendant → mac-planner
- **model tier:** realtime
- **latency:** sub-second
- **cost:** Low compute; mostly storage and learning model cost
- **security:** Requires secure data storage, user decision tracking, and override mechanisms to prevent misuse or denial of legitimate actions.
- **missing:** Adaptive user risk modelling and decision capture infrastructure; Real-time app state detection for risk assessment; User-facing confirmation request UI on pendant and Mac


## What it asked for

_Nothing._
