# Harness derivation — mac-vision — round 69

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable Mac-vision loop safely and usefully"
- **useful because:** To allow visual UI understanding and interaction on the Mac for complex or un-API-available app tasks, enabling higher autonomy and less voice/memory context waste.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** 100-500ms for UI steps, longer for planning
- **cost:** Moderate due to vision model usage and context transfer
- **security:** Need to ensure privacy and control of screen capture and UI control. Accessibility permission required and gated by owner consent. No silent actions allowed without explicit go-ahead.
- **missing:** Accessibility permission granted to the running AI Pendant Agent binary; Vision upload consent granted by owner; Reliable UI input event acceptance by accessibility APIs

### "Guide me to safely enable Accessibility and Screen Recording permissions for AI Pendant Agent"
- **useful because:** These permissions allow reliable UI control and screen capture needed for mac-vision's autonomous computer use loop, enabling more natural and effective interaction.
- **path:** relay-realtime → mac-planner → mac-vision
- **model tier:** realtime
- **latency:** 1-2 seconds for permission dialogs and user flow
- **cost:** Low computational cost, mostly usability and user trust focused
- **security:** Must ensure permissions granted only explicitly by the owner, with clear notices about power and risks involved. Consent records must be auditable. No silent elevation.
- **missing:** Guided system-level permission requests and user education UI to enable accessibility and screen recording for the correct binary; Persistent consent records tied to owner identity and session; Integration with mac-vision capabilities to detect permission state changes dynamically

### "Enable fully autonomous Mac computer use loop with visual UI understanding and interaction"
- **useful because:** This would allow the AI to reliably understand, interact with, and automate any app or workflow on the Mac at the screen level, without relying solely on partial APIs, voice commands, or predetermined scripts. It would greatly increase the owner's efficiency and freedom from manual computer control.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** 100-500ms per UI action, longer planning time accepted
- **cost:** Moderate to high due to expensive vision processing, context transfer, and safety checks
- **security:** Requires explicit accessibility and screen recording permissions granted to the exact AI Pendant Agent binary, plus owner consent for visual data upload. Must have robust consent dialogs and audit trails. Accessibility must allow real UI event injection that reliably affects apps without silent failure.
- **missing:** Correct macOS accessibility permission configuration for the running AI Pendant Agent binary; Owner-granted vision upload consent to enable screen capture processing; Stable acceptance of synthesized UI input events by accessibility APIs without being blocked or ignored


## Changes it proposed to its own stack

### `integration` — Implement a user-guided system-level permission grant flow for Accessibility and Screen Recording specifically for the AI Pendant Agent binary, with clear owner education, consent recording, and dynamic permission state monitoring.
- **owner gets:** This change would enable the mac-vision loop to become fully operational with real UI control and vision capabilities, unlocking autonomous Mac use beyond current limitations.
- effort: Moderate engineering effort to develop the guided UI flow, integrate with OS security APIs, and build consent recording/storage.  ·  risk: Risk of owner confusion or accidental permission grants mitigated by clear UI design and explicit consent steps. Recovery by revoking permissions is always possible.
- cost: Low computational cost; mainly user interaction and system API calls.  ·  latency: Adds a few seconds for user-driven permission dialogs during setup; negligible impact otherwise.
- security: Increases attack surface if permissions misused; secure design and owner control mandatory.
- depends on: existing mac-vision framework and permission detection mechanisms

### `hardware` — Develop and integrate a hardware-backed secure consent token on the AI Pendant device, which the owner must physically press to authorize sensitive permission grants (accessibility, screen recording) and visual data upload, tightly coupling physical presence with consent.
- **owner gets:** This hardware interaction ensures that sensitive permissions and data sharing only occur with deliberate owner consent, increasing trust and security while enabling autonomous vision-based Mac interaction.
- effort: Significant redesign and firmware development on the pendant hardware and integration with the permission management system on Mac agent.  ·  risk: Potential delays or inconvenience if the owner is not available for physical consent. Hardware failures could block permissions permanently.
- cost: Moderate hardware development cost and power usage impact.  ·  latency: Adds latency equal to owner's physical interaction time; negligible otherwise.
- security: Strengthens security by requiring physical consent, reducing remote attack risks.
- depends on: existing pendant hardware IO capabilities; system permission management integration


## What it asked for

_Nothing._
