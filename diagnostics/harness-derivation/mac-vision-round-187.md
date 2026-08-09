# Harness derivation — mac-vision — round 187

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision computer-use loop by granting macOS Accessibility permission to the AI Pendant Agent binary and turning on loopEnabled and visionUploadConsented flags."
- **useful because:** This unlocks safe, reliable, fine-grained UI control on the Mac via accessibility APIs, which is essential for full autonomous computer use by the agent on behalf of the owner.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds
- **cost:** negligible API cost; user time to grant permission
- **security:** Requires user's trust to allow UI interaction without focus stealing or unintended clicks; permission limited to the specific agent binary.
- **missing:** User manual step granting macOS Accessibility permission to AI Pendant Agent binary, safe UI control policy to prevent disruption.

### "An advanced delegated workflow manager on the Mac (mac_delegate extension) that handles complex multi-step commands beyond single action sets, including app switching and UI navigation, while guaranteeing undo capability and non-destructive behavior unless confirmed."
- **useful because:** Many useful computer tasks cannot fit within 1-3 actions. A robust delegated workflow manager enables seamless complex automation while maintaining owner control and safety.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds to minutes depending on task length
- **cost:** moderate to high depending on workflow complexity; potential for longer compute times and state management.
- **security:** Workflow execution must be tightly controlled to avoid unintended destructive actions; owner confirmation required for sensitive steps.
- **missing:** Robust local state and history tracking; improved error recovery and user notifications; integration with reversible actions and user confirmations.

### "Real-time detected UI element engagement and feedback loop from the mac-vision computer-use loop to the pendant LED and audio signals, giving the owner tactile and audio cues about what UI element is active or being controlled."
- **useful because:** This would close the sensory loop for the owner wearing the pendant, making interactions transparent and safe, especially when the loop is active and could otherwise steal focus or perform unwanted UI actions.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** milliseconds to seconds for feedback
- **cost:** low compute cost, minor radio cost for feedback signals
- **security:** Must not leak private UI details externally; processing remains local and encrypted relay only relays abstract signals.
- **missing:** Data push from mac-vision loop state to pendant bridge; LED/audio pattern definitions; owner customization UI.

### "Dynamic Mac voice command aliasing and confirmation system extendable via the pendant button, enabling the owner to define or rename voice commands that map to mac_run_actions or mac_delegate workflows, with safety confirmations."
- **useful because:** This empowers the owner to customize their voice interaction dynamically and safely, enabling smoother workflows and fewer accidental commands, especially when used with the pendant physical button.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** under a second for alias resolution and confirmation
- **cost:** moderate compute; scale depends on number of aliases and workflows
- **security:** Alias database must be protected; confirmation required for critical commands.
- **missing:** Alias manager UI and voice interface; pendant button-context integration; confirmation UX design.; Built from existing mac_run_actions, mac_delegate, relay-realtime

### "Agent-controlled multi-modal urgent interruption system that can alert the owner via pendant LED flashes, audio cues, vibration, and Mac notifications, prioritized by real-time task urgency and owner context."
- **useful because:** The owner currently lacks an integrated, multi-sensory, context-aware alert system that can interrupt or notify them appropriately according to task priority and current activity, improving timely awareness and reducing missed critical events.
- **path:** pendant → mac-vision → relay-realtime → mac-planner
- **model tier:** realtime
- **latency:** milliseconds to seconds
- **cost:** moderate compute and network cost, minor power use for haptics/LED
- **security:** Must respect owner's privacy and interruption preferences; alerts must be controllable and revocable.
- **missing:** Tight integration between mac-vision loop and pendant feedback channels, context-aware prioritization algorithm, owner-configurable interruption policy.

### "Predictive resource and focus management system that automatically schedules breaks, adjusts system volume/brightness, pauses notifications, and suggests the optimal workflows to maintain owner's productivity and well-being throughout the day."
- **useful because:** The owner currently lacks a proactive system that simultaneously manages system resource states, focus breaks, and task ordering based on their context and load, improving mental and physical health and sustained productivity.
- **path:** mac-planner → mac-vision → pendant
- **model tier:** background
- **latency:** minutes
- **cost:** moderate compute cost
- **security:** Data privacy must be ensured; adaptive controls should be reversible and owner-overridable.
- **missing:** Integration with health and system metrics APIs, machine learning models for stress/load prediction, and smooth cross-surface communication.

### "Cross-device secure ephemeral data sharing and clipboard synchronization between the pendant, Mac, and mobile devices with automatic encryption and ephemeral retention policies."
- **useful because:** Owner currently cannot seamlessly and securely share clipboard or ephemeral data between devices without manual transfer steps, limiting fluid interaction and context continuity.
- **path:** pendant → mac-planner → relay-realtime → mobile
- **model tier:** background
- **latency:** seconds
- **cost:** low to moderate compute and network cost
- **security:** End-to-end encryption essential; ephemeral data deletion must be guaranteed and auditable.
- **missing:** Secure cross-device communication protocols, ephemeral storage management, and user control interfaces.

### "A smart persistent multimodal context memory that records and recalls complex user context and cross-surface interaction history, enabling agents like mac-vision to resume interrupted workflows and adjust actions based on full context history."
- **useful because:** The owner currently lacks integrated context memory that spans devices and sessions, limiting the agent's ability to act with historical awareness and continuity, reducing efficiency and user satisfaction.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** seconds
- **cost:** moderate compute and storage cost
- **security:** Memory must respect privacy, allow selective forgetting, and prevent data leakage between surfaces.
- **missing:** Cross-surface context APIs, memory synchronization, data governance policies, and UI for memory management.


## Changes it proposed to its own stack

### `hardware` — Add a second user-configurable button to the pendant dedicated to urgent context-aware signaling and multi-function control gestures, increasing physical interaction bandwidth without complicating the existing single-button economy.
- **owner gets:** This would allow the owner to safely express multiple commands or confirmations from the pendant with simple physical gestures, improving control and feedback without increasing latency or risk on the critical microphone-activation button.
- effort: Moderate firmware and hardware redesign, plus updated driver and gesture recognition software.  ·  risk: Physical redesign may delay development; firmware complexity increases risk of bugs which can be mitigated by thorough testing and staged rollout.
- cost: Incremental hardware cost increase modest; firmware development moderate; impact on power draw minimal.  ·  latency: No negative impact; potentially reduces command latency.
- security: No direct impact, but new button mappings must be securely and carefully managed to avoid spoofing or accidental command triggers.


## What it asked for

_Nothing._
## Its own summary

Discovered key tools and environment: mac_run_actions for Mac control, mac-vision loop disabled pending macOS Accessibility permission, hardware specs of pendant and IO elements, and owner's preferences. Proposed enabling mac-vision loop via macOS Accessibility permission grant, a prioritized Mac task queue, complex delegated workflow manager, real-time UI feedback from mac-vision to pendant LEDs/audio, and dynamic voice command aliasing with pendant button integration. These proposals address core blockers and expand owner-agent interaction safely and meaningfully.

**Biggest unknown:** Whether the owner will grant macOS Accessibility permission to the AI Pendant Agent binary, enabling the mac-vision loop to operate and unlock fine-grained UI control on the Mac.

