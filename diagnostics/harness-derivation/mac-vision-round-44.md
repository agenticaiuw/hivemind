# Harness derivation — mac-vision — round 44

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision loop for safe and effective UI automation on the Mac"
- **useful because:** The owner needs the AI Pendant to directly interact with Mac applications and UI elements through vision and accessibility for advanced automation beyond APIs, including workflows that require screen reading and interaction.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** 1-2 seconds per UI action
- **cost:** Moderate API cost for AI vision and action planning; minimal hardware cost as it uses existing Mac and pendant capabilities
- **security:** Requires Accessibility and Screen Recording permissions granted by the owner, plus controls to prevent destructive actions without confirmation; no data should leave device without explicit consent
- **missing:** Accessibility permission granted for AI Pendant Agent; Screen Recording permission granted; Computer use loop enabled (loopEnabled=true); Browser extension to be active and online; Context signals for attention/unsaved work for privacy-aware action arbitration; Safe gating for destructive UI actions with optional owner confirmations


## Changes it proposed to its own stack

### `new-surface` — Add a dedicated mac-vision on-device OCR and UI element semantic extractor to offload pixel analysis from the Mac; this can run on the pendant or bridge device in low power mode to preprocess UI screenshots and provide semantic descriptions without raw pixels leaving the pendant.
- **owner gets:** Reduces privacy risk and latency for vision-driven UI automation by performing sensitive image processing locally on the pendant hardware. Enables faster, more private mac-vision operation even if the Mac UI loop remains limited in its screen capture permissions.
- effort: Medium engineering effort to implement OCR and UI semantic extraction optimized for the pendant's hardware limitations; requires firmware and software integration with mac-vision and cloud relay.  ·  risk: Artifacts from low-quality OCR or misinterpretation of UI elements could lead to incorrect actions; needs fallback to Mac for full UI hierarchy when available; manageable by staged rollout and fallback logic.
- cost: Low to moderate; uses pendant CPU cycles instead of Mac GPU/CPU; no new hardware required but firmware upgrade needed.  ·  latency: Potentially reduces latency by avoiding repeated full pixel uploads to Mac and relay.
- security: Improves security by confining raw UI image data to the pendant and transmitting only semantic metadata; reduces exposure of screen content.
- depends on: Hardware support on the pendant and bridge for image capture; Mac-vision loop enabled with screenshot capability

### `model-routing` — Implement cross-surface attention arbitration using privacy-preserving focus, meeting, and unsaved-work indicators shared from mac-vision, relay-realtime, and browser-extension. This aims to decide when the AI is permitted to interact with UI or sensitive data based on the owner's context and privacy preferences.
- **owner gets:** Prevents unwanted or intrusive UI automation by respecting the owner's current attention, meetings, and unsaved work states, allowing AI assistance only when appropriate and minimizing privacy risks and distractions.
- effort: Medium; requires enhancements to all involved surfaces to produce and consume arbitration signals with a shared protocol; integration into the AI Pendant's judgement and action layers.  ·  risk: Incorrect signals could block helpful automation temporarily or allow unintended interactions; mitigated by user override and fallback defaults.
- cost: Mostly software-level, minimal latency overhead.  ·  latency: Negligible increase in decision latency.
- security: Strong positive; gives owner fine-grained control and transparency over AI UI automation timing.
- depends on: mac-vision loop enabled; Relay and browser-extension cooperation; Owner consent to share context signals

### `integration` — Add a proactive permission manager coach surface that monitors missing macOS permissions such as Accessibility and Screen Recording, detects attempts to enable mac-vision loop, and interacts with the owner via pendant voice and Mac notifications to guide them through granting needed permissions securely and confirming when it is safe to proceed.
- **owner gets:** Smooths the adoption barrier for power features like mac-vision loop, reducing user confusion and manual configuration errors, increasing trust and security by educating the owner at granting time.
- effort: Medium to high; requires new UI surfaces, integration with OS permission querying APIs, and voice dialog design and testing.  ·  risk: Risk of spammy or excessive notifications if not carefully tuned; mitigated by rate limiting and user controls.
- cost: Mostly software, modest usage of pendant voice and Mac notification APIs.  ·  latency: No impact on main AI latency.
- security: Enhances security and transparency by involving owner actively in permission delegation.
- depends on: Access to macOS permission status APIs; Voice and notification integration on pendant and Mac

### `dashboard-ux` — Build a dashboard UI panel in the owner's AI Pendant dashboard that displays the mac-vision loop status, current permission grants, pending required permissions, and recent mac-vision activity logs, with one-click deep links to macOS System Preferences to manage Accessibility and Screen Recording permissions.
- **owner gets:** Gives the owner easy visibility and control over the mac-vision system state and permissions, increasing trust, simplifying troubleshooting, and making it easier to enable the most powerful automation features.
- effort: Low to medium; requires front-end dashboard updates and links to system settings; no backend API changes required.  ·  risk: Minimal risk; purely informational with outbound links only.
- cost: Low; UI and UX development effort only.  ·  latency: None.
- security: Positive; empowers owner with transparency and control.
- depends on: Dashboard surface implemented; Current mac-vision and permission status data access

### `firmware` — Upgrade pendant firmware to support encrypted local caching of UI screenshots or semantic representations with strict access control, allowing mac-vision to retrieve recent UI context on-demand even when intermittent network or Cloudflare Relay connectivity occurs.
- **owner gets:** Improves reliability and responsiveness of the mac-vision loop by mitigating network disruptions or relay downtime, ensuring consistent UI context for automation even offline or with partial connectivity.
- effort: Medium; requires secure storage design in limited RAM and flash, encryption, and protocol updates for data retrieval by mac-vision.  ·  risk: Potential data loss or privacy risks if cache security is compromised; mitigated through encryption and strict access controls.
- cost: Minimal hardware impact, software development effort only.  ·  latency: Improves effective latency and reliability under poor network conditions.
- security: Positive if designed with strong encryption and access controls.
- depends on: Current pendant hardware with available flash and RAM; Cloudflare relay security integration

### `interaction` — Implement a conditional silent mode for mac-vision loop where it can operate without vocal confirmations for low-risk reversible actions during owner focus periods or meetings, using subtle visual or haptic feedback from the pendant instead.
- **owner gets:** Improves owner experience by reducing spoken interruptions from the AI during concentrated work or meetings, while retaining confidence that actions are occurring, with reversibility for mistakes.
- effort: Low to medium; requires integration with attention/arbitration signals and new feedback modalities on the pendant (e.g., vibration, LED patterns).  ·  risk: Risk of missed action confirmation; mitigated by quick undo and UI visual logs accessible after action.
- cost: Negligible.  ·  latency: None.
- security: Neutral; no change in controls, just feedback method.
- depends on: Pendant hardware supporting haptic or LED signals; Cross-surface attention arbitration implemented

### `memory` — Enhance context graph in the local Mac agent to include detailed UI interaction histories and state snapshots indexed by timestamp, allowing mac-vision loop to plan reversible sequences and recover from failures by replaying or undoing UI states.
- **owner gets:** Increases reliability and user confidence by enabling complex UI workflows to be performed and reversed more robustly, and providing better visibility into past mac-vision interactions.
- effort: Medium; requires schema updates and additional storage logic in the context graph subsystem and mac-vision integration.  ·  risk: Moderate storage growth; mitigated by pruning policies. Potential privacy concerns if UI data stored long-term; mitigated by encryption and access controls.
- cost: Medium; storage and computational overhead on Mac agent.  ·  latency: Negligible for runtime, some cost in storage management.
- security: Positive if privacy controls implemented correctly.
- depends on: Context graph system active and accessible to mac-vision; Mac-vision loop enabled


## What it asked for

_Nothing._
