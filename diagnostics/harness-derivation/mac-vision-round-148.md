# Harness derivation — mac-vision — round 148

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Automate triage and prioritized action on desktop mail and webmail inboxes using the computer use loop on the Mac and browser extension."
- **useful because:** The owner manages multiple mailboxes across native Mac apps and webmail; automation can prioritize, summarize, and take routine actions faster and consistently.
- **path:** mac-vision → browser-extension → relay-realtime → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate
- **security:** Requires sensitive mailbox content access; all automation runs locally on the Mac or authenticated browser extension; user consent required.
- **missing:** integration with mail indexing APIs; trusted automation confirmation UI

### "Retrieve and launch dynamic info and tasks from visible application UIs on the Mac using the computer use loop automation."
- **useful because:** Many valuable desktop tasks stem from information visible only in app UI; automating interactions avoids manual search and saves time.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate
- **security:** Automation interacts with UI elements directly; requires macOS Accessibility permission and fail-safe undo.
- **missing:** UI context interpretation models; safe rollback mechanisms

### "Enable context-aware multi-application workflows driven by voice commands and pendant button triggers using the full Mac computer use loop and browser extension."
- **useful because:** Allows the owner to trigger complex workflows that span apps, initiated hands-free or by a quick pendant gesture, saving manual effort and switching context.
- **path:** unified → mac-vision → browser-extension → relay-realtime → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 5-10 seconds
- **cost:** higher
- **security:** Cross-application automation requires trust, fine-grained control, and error recovery. Voice commands must be authenticated and accurate.
- **missing:** robust voice command interpretation integration; multi-step task planning with undo; complex app state modeling

### "Create a smart accessibility-driven computer use loop self-test and reporting capability that confirms the loop can see and interact with UI elements before executing workflows."
- **useful because:** This capability avoids blind runs or stuck UI automation by verifying accessibility permissions, UI tree visibility, and interaction success before acting, improving reliability and safety.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** seconds
- **cost:** low
- **security:** Must not expose UI content beyond local system; must respect privacy and security constraints.
- **missing:** UI tree validation APIs; interaction feedback hooks

### "Enable the Mac vision agent to autonomously monitor and react to changes in visible app states and UI controls for real-time task assistance and suggestions."
- **useful because:** Continuous real-time UI monitoring without user intervention would enable the agent to proactively assist with tasks, detect errors, and offer context-sensitive options, improving productivity and flow.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** low-latency ongoing
- **cost:** moderate on compute
- **security:** Must operate under strict local privacy rules with no data leaks; must have user override and pause options.
- **missing:** real-time UI event hooks; event subscription infrastructure; efficient UI tree diff and change detection

### "Build an intermediary task intent ranker and prioritizer that reads across all known task stores and open reminders to produce a single dynamic ranked task list for the owner."
- **useful because:** The system currently has many task sources but no unified rank or priority logic; this would let the owner see and act on the highest priority work efficiently.
- **path:** mac-planner → unified → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** seconds to a minute
- **cost:** modest
- **security:** Requires access to all task sources; all computation done locally; strict privacy controls on aggregated data.
- **missing:** task schema harmonization; cross-source ranking models; priority tuning controls

### "Implement a gap-filling voice command interpreter that can convert ambiguous or incomplete voice inputs into specific mac_run_actions, browser_run_actions, or mac_delegate goals with fallbacks and clarifications."
- **useful because:** Voice commands are often imprecise; intelligent interpretation and fallback strategies increase success rates and reduce frustration for the owner.
- **path:** relay-realtime → mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** few seconds
- **cost:** moderate
- **security:** Voice commands are sensitive; must be authenticated and processed locally with privacy safeguards.
- **missing:** robust voice natural language understanding; contextual disambiguation; fallback dialogue flows

### "Enable fast multi-modal task creation by voice, keyboard, pen, or touch on any device, instantly shared and visible across Mac, pendant, and browser."
- **useful because:** The owner sometimes wants to capture tasks or ideas on any device in the moment, ensuring no loss and seamless cross-device visibility.
- **path:** unified → mac-vision → relay-realtime → browser-extension → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low
- **security:** Input could include sensitive data; must be encrypted and access-controlled.
- **missing:** real-time sync infrastructure; multi-input modal fusion; cross-device task store

### "Enable persistent context state sharing and synchronization between pendant, Mac, browser, and relay, including partial state loading to save memory and bandwidth."
- **useful because:** A critical gap is that context state is fragmented; sharing and syncing context across devices would create a seamless intelligent experience.
- **path:** unified → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes
- **cost:** moderate
- **security:** Context data may be sensitive; sync and storage must respect privacy and encryption.
- **missing:** context sync protocols; partial context loading and persistence models

### "Create a seamless, privacy-respecting cross-device user preferences learning and application system, where preferences learned on pendant, Mac, or browser enhance all surfaces."
- **useful because:** User experience is fragmented by device; a system that learns preferences once and applies everywhere improves owner's convenience and consistency.
- **path:** unified → mac-vision → relay-realtime → browser-extension → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes
- **cost:** low to moderate
- **security:** Preferences may reveal sensitive info; system must ensure privacy and user control.
- **missing:** secure cross-device preference syncing; personalization models


## Changes it proposed to its own stack

### `hardware` — Add a low-energy real-time event capture sensor and processor to the pendant hardware to enable ultra-low-latency gesture or environment event detection for context-aware assistant triggers.
- **owner gets:** This would enable the owner to trigger contextual assistant actions instantly without draining pendant battery, leveraging hardware acceleration and local processing.
- effort: Medium hardware design and integration effort.  ·  risk: Hardware delays or integration bugs could compromise reliability, but fallback to existing button triggers remains.
- cost: Moderate component and integration cost; low power added.  ·  latency: Significant latency reduction in gesture/environment event detection.
- security: Local processing reduces risk of data leakage; sensor data must still be protected.

### `model-routing` — Implement dynamic model routing that selects between real-time low-latency models and background high-capacity models based on query type and urgency, optimizing owner's latency and cost tradeoff.
- **owner gets:** Owner gets fast replies for conversational queries and thorough analysis for long-running tasks without delay or high cost on all queries.
- effort: Medium for infrastructure and integration.  ·  risk: Routing errors could cause degraded experience, mitigated by fallback models.
- cost: Optimizes cost by using resource-light models where possible.  ·  latency: Improves latency for real-time queries.
- security: Minimal; routing is opaque to data content.
- depends on: model availability; query classification tooling


## What it asked for

_Nothing._
