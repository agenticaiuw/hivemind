# Harness derivation — mac-vision — round 233

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Create and maintain a prioritized Mac task list integrating owner intents and dayPlan reminders, so mac-vision can autonomously select and act on what matters most."
- **useful because:** This would finally give mac-vision a durable, prioritized work queue derived from explicit owner intents and system-sourced reminders, enabling fully autonomous, relevant Mac UI actions without confusion or guesswork.
- **path:** mac-planner → mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** low
- **security:** Must respect owner preferences and confirm destructive actions; only run on explicitly prioritized tasks.
- **missing:** Integration with memory facts and dayPlan reminder APIs to build and update the prioritized list.; UI and voice surface to report the prioritized queue and accept priority adjustments.

### "Track and report actual on-screen UI state alongside delegated workflow claimed state, to detect discrepancies and enable robust workflow recovery."
- **useful because:** Currently, the Mac workbench tracks claimed vs on-disk state but does not track real UI state visible to mac-vision. Reporting this would catch and resolve mismatches during automated UI workflows, increasing reliability and owner trust.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** medium
- **security:** Requires access to real-time UI state, which is currently gated by accessibility permissions; data stays local unless owner consents to sharing.
- **missing:** A UI state diff and verification system integrated into workbench contexts and jobs.; Enhanced loop reporting to create claimed vs actual UI snapshots.

### "Coordinate multi-surface workflow execution, managing and synchronizing tasks split between Mac UI actions, browser actions, and pendant signals."
- **useful because:** Owner workflows often span multiple devices and surfaces. A coordination capability would let mac-vision seamlessly manage complex multi-step workflows involving all components, enabling richer, faster task completion.
- **path:** mac-vision → browser-extension → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** high due to coordination complexity
- **security:** Requires maintaining cross-device state and communication securely; careful access control needed.
- **missing:** Cross-surface workflow state model and synchronization protocols.; Integration with existing multi-step delegation systems.

### "A fully integrated, autonomous Mac task manager that reads Apple Reminders and Calendar events with real read-write access, prioritizes tasks intelligently based on overdue/due/high priority, user preferences, and context, and actively chooses and executes the top-priority tasks on the Mac independently."
- **useful because:** Today the owner has no true autonomous Mac task queue or task management that reflects their actual Calendar and Reminders. This would allow mac-vision to operate with real decision-making power, reducing overload and increasing helpfulness.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** medium
- **security:** Requires owning the user's calendar and reminders access securely; must respect privacy, only act on what is prioritized by owner preferences, and confirm irreversible actions.
- **missing:** True read-write API access to Calendar and Reminders with reliable authorization.; Task prioritization models integrated with owner preferences and context.; Autonomous execution logic for task selection and action planning on the Mac.

### "A trusted, fine-grained action confirmation and auditing system integrated with mac-vision and the pendant, allowing the owner to review and approve each sensitive or destructive Mac UI action before it runs."
- **useful because:** This solves the risk and trust barrier for autonomous Mac UI actions by letting the owner validate or veto actions via a secure, audited interface on the pendant, increasing confidence and safety.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** low to medium
- **security:** Requires secure, encrypted communication between devices; careful authentication and action auditing for transparency.
- **missing:** A fine-grained action gating and prompt system in mac-vision.; A secure communication and UI interface on the pendant to display and approve actions.; Detailed audit trails for all commands issued by mac-vision.


## Changes it proposed to its own stack

### `hardware` — Add a dedicated, secure hardware interface on the pendant for mac-vision to receive tactile or context-aware confirmations and signals from the owner to approve, pause, or modify autonomous Mac actions in real time.
- **owner gets:** This bridges the gap between autonomous mac-vision execution and owner control, ensuring safety and trust with a dedicated easily reachable hardware channel, avoiding accidents and providing direct feedback.
- effort: Medium firmware and hardware engineering effort, plus Mac software to integrate the input.  ·  risk: Hardware failure or firmware bugs could cause missed or delayed confirmations; mitigated by robust fallback and manual override paths.
- cost: Low hardware cost; adds a small button or gesture interface with secure protocol.  ·  latency: Low latency; immediate tactile feedback and input.
- security: Requires hardened secure channel to prevent spoofing.
- depends on: mac-vision autonomous task manager; pendant firmware enhancements


## What it asked for

_Nothing._
