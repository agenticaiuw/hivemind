# Harness derivation — mac-vision — round 104

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a privacy-first system capability for the owner to grant and revoke accessibility and screen recording permissions dynamically, guided by transparent explanations and minimal interruption"
- **useful because:** Currently, key permissions required for advanced AI-assisted computer control on the Mac (accessibility and screen recording) are missing or not trusted. The owner has no easy or trusted mechanism to manage these in a way that supports seamless AI assistance but protects privacy and control. This would unlock advanced Mac vision loop features while respecting user agency and trust.
- **path:** mac-planner → relay-realtime → mac-vision → unified
- **model tier:** gpt-4o-vision-preview
- **latency:** Interaction to grant or revoke permission within seconds, with minimal interruption to user workflow
- **cost:** Low API cost; most cost in UX and system integration work rather than modeling costs
- **security:** Sensitive system permission changes require strong confirmation and audit trail; must prevent unauthorized escalation; no data leaves device during permission grant except metadata for record-keeping as per user settings
- **missing:** Standardized, user-friendly OS flows to enable/disable accessibility and screen recording with AI assistance; Audit and prompt system integrated with AI to explain and request permissions contextually; Clear user control dashboard for permission management

### "Grant the AI Pendant agent trusted status in macOS Accessibility settings with transparent user prompts and fallback instructions"
- **useful because:** The AI Pendant agent cannot interact fully with Mac UI because macOS Accessibility permissions are not trusted. Providing a smooth, clear pathway for the owner to grant and revoke this trust status empowers safe and effective AI assistance on the Mac GUI level.
- **path:** mac-planner → relay-realtime → mac-vision
- **model tier:** gpt-4o-vision-preview
- **latency:** Permission enablement flow completes within minutes during idle time
- **cost:** Low cost mostly in UX design and static prompts; minimal API/model cost
- **security:** Strong user confirmation needed; permission grant logs must be kept secure and auditable; no elevation beyond system dialogs
- **missing:** macOS-trusted accessibility enablement workflow guidance; Fallback and recovery instructions for permission grant failures


## Changes it proposed to its own stack

### `model-routing` — Add capability routing to enable real-time vision model calls with local fallback option on Mac hardware, integrated with the AI Pendant mac-vision agent to provide seamless, low-latency vision capabilities without cloud upload requirement for privacy-sensitive tasks.
- **owner gets:** Today, the mac-vision loop is off because vision upload consent is missing. Local vision model routing with fallback reduces dependence on cloud and privacy exposure, enabling mac-vision to run effectively and safely.
- effort: Medium to high, requires integration with local Mac hardware acceleration, model deployment, and routing logic across model tiers.  ·  risk: Possible increased complexity in agent coordination; fallback failures must be handled gracefully.
- cost: Higher local resource usage on the Mac, reduced cloud model usage and cost.  ·  latency: Improved latency with local processing, preserving user experience.
- security: Enhances privacy by limiting screen data leaving device.
- depends on: Enable accessibility and screen recording permissions; Enable computerUse.loopEnabled and visionUploadConsented flags


## What it asked for

_Nothing._
