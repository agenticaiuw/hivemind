# Harness derivation — mac-vision — round 158

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent's full computer use loop to safely and reliably interact with all Mac UI elements via accessibility controls without stealing focus or falling back to mouse clicks."
- **useful because:** This is the single most useful thing the owner can have on the Mac. It allows true AI-driven interaction with any app or window, not just APIs, and without disturbing user focus or relying on fragile pixel methods.
- **path:** mac-vision
- **model tier:** gpt-4.1-mini
- **latency:** Real-time low-latency interaction under 1 second per step.
- **cost:** Low API cost per step but requires robust local permissions.
- **security:** Requires macOS Accessibility granted explicitly to the pendant binary; has full potential to drive UI and fabricate user input, so owner control is essential.
- **missing:** macOS Accessibility permission granted to the AI Pendant Agent binary; Device-side firmware that tracks and confirms UI mutating actions as safe

### "A unified, ranked goal store that aggregates owner-stated tasks, daily routines, and inferred priorities to tell all agents what the owner currently wants done."
- **useful because:** No agent currently has a reliable, prioritized list of what the owner wants done now. A unified ranked goal store enables all agents, especially mac-vision, to plan and act meaningfully based on actual owner intent rather than guesswork.
- **path:** mac-planner → mac-vision → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** Background synthesis within a few seconds.
- **cost:** Moderate API cost for ranking and synchronizing tasks; mostly offline computation.
- **security:** Requires explicit owner input or trusted agent inference to populate; must be encrypted and access-controlled to protect private goals.
- **missing:** A persistent, writable goal or intent store with priority and deadline metadata; Agent logic to infer goals from memory facts and routine commands

### "Context-aware contextual marker system using existing pendant button and firmware to bookmark meaningful moments during Mac interaction, linked to specific UI states and agent decisions, with multi-modal confirmation beyond simple button press."
- **useful because:** Goes beyond simple moment bookmarking by embedding context in the marker — helps agents resolve ambiguous goals, confirm transactions, and improve interaction safety without adding new physical buttons.
- **path:** mac-vision → pendant
- **model tier:** gpt-5.6-luna
- **latency:** Real-time interaction within 1 second.
- **cost:** Minimal device-side compute and SD card use; small API cost for coordination and log storage.
- **security:** Requires secure mapping of context to marker; avoids misuse by limiting payload size and signing markers.
- **missing:** Firmware logic on pendant to interpret contextual triggers and encode metadata; Agent-side logic to use contextual markers for decision support

### "Integrated mac-vision UI state snapshot upload and relay for external agent collaboration, with opt-in visionUploadConsented, respecting privacy but enabling remote assistance and debugging."
- **useful because:** Owner currently cannot share their live UI state externally for help or remote debugging without risking privacy. This capability enables controlled, consensual transmission of UI accessibility states to trusted agents, improving support and agent collaboration.
- **path:** mac-vision → relay-realtime → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** Background upload with near real-time availability.
- **cost:** API cost for data uploads and storage; minor processing overhead.
- **security:** Must require explicit owner consent (visionUploadConsented) and encrypt all transmission; limited data scope to accessibility tree only; no pixel capture.
- **missing:** visionUploadConsented grant with endpoint implemented; Agent logic to manage consent and data transmission


## Changes it proposed to its own stack

### `hardware` — Add a second, dedicated hardware button on the pendant for context-specific interaction gestures and confirmations, distinct from the single existing microphone/push-to-talk button.
- **owner gets:** This solves the current gesture budget problem—where the pendant's single button must cover all triggers and confirmations—greatly improving usability and safety without requiring complex press timing logic.
- effort: Moderate hardware redesign and firmware update effort.  ·  risk: Physical redesign delay, slightly increased device size and cost, but low risk if carefully implemented.
- cost: Moderate BOM increase, negligible power increase.  ·  latency: None.
- security: None.

### `firmware` — Develop a fine-grained confirmation and transaction approval latch on the pendant firmware that ties specific UI mutating requests from mac-vision to physical user approval via a dedicated button, with a small secure storage buffer and timeout.
- **owner gets:** This ensures that high-risk or mutating actions on the Mac cannot be taken silently by the AI agent; the owner explicitly confirms sensitive operations with a deliberate physical gesture.
- effort: Medium, requires firmware change and mac-vision integration.  ·  risk: Delayed actions if user unavailable; complexity in syncing state between Mac and pendant; failure fallback needed.
- cost: Minimal in device resources and API cost.  ·  latency: Small delay for action confirmation.
- security: Strongly improves security and control for the owner.
- depends on: physical button on pendant


## What it asked for

_Nothing._
