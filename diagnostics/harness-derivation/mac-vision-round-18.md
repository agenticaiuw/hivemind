# Harness derivation — mac-vision — round 18

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a safe, user-consent-driven mode for mac-vision to fully control my Mac screen interactions without disrupting my work"
- **useful because:** The owner could delegate complex visual and UI interaction tasks to mac-vision, including keyboard and mouse actions, by leveraging screenshots and UI insights, while limiting interruptions and ensuring safe consent and permission handling.
- **path:** mac-vision (Mac Local Agent) → relay-realtime (Cloud Relay) → AI Pendant (Wearable Device)
- **model tier:** realtime
- **latency:** within 1-2 seconds for interactive tasks
- **cost:** moderate API cost dominated by vision and input action execution
- **security:** Requires explicit owner consent and permissions for screen recording and accessibility. Needs safeguards to avoid accidental destructive actions and preserve privacy.
- **missing:** granular user consent UI to enable vision upload and loop activation; automatic detection or guiding steps for enabling accessibility and screen recording permissions; typed action policy with reversible action support and user confirmation for high-impact operations

### "Ask mac-vision for detailed local UI snapshots on demand without enabling full vision loop, to get safe, accessibility-based UI hierarchy and element data without pixel screenshots."
- **useful because:** Provides the owner selective, privacy-preserving access to UI structure and element data for detailed agent reasoning and action planning without the risks or permissions required by full pixel vision.
- **path:** mac-vision (Mac Local Agent)
- **model tier:** background
- **latency:** seconds, non-interactive
- **cost:** low, mostly CPU for accessibility read
- **security:** No screen recording or pixel data required, but must ensure no sensitive private data leak in UI text elements
- **missing:** UI accessibility data extraction APIs and integration with mac-vision; owner control over what UI app contexts are included in snapshots


## Changes it proposed to its own stack

### `integration` — Implement a system-wide, cross-layer consent and permission manager specifically for AI Pendant agents on Mac that manages accessibility, screen recording permissions, and user consent for vision model uploads.
- **owner gets:** This manager would streamline the process for the owner to grant, repeal, or audit permissions needed by mac-vision and other agents, ensuring the owner understands and controls what capabilities the AI has, enabling safe activation of powerful UI automation features.
- effort: medium engineering effort across macOS agent, pendant UI, and backend systems.  ·  risk: Risk of confusing the owner or misrepresenting permissions, mitigated by clear UI and audit logs.
- cost: Small increase in API and UI complexity cost.  ·  latency: Negligible.
- security: Positive by centralizing and clarifying permission handling.

### `firmware` — Add a hardware button sequence on the AI Pendant device to enable emergency manual override that disables mac-vision loop's screen interactions immediately if it behaves unexpectedly.
- **owner gets:** Provides a physical, low-latency fail-safe for the owner to instantly stop any unintended or harmful AI-driven screen interactions, enhancing safety and trust in using mac-vision's powerful loop feature.
- effort: low-medium hardware and firmware development effort, plus pendant firmware update.  ·  risk: Could be accidentally triggered causing temporary disruption, mitigated by requiring a unique button combo.
- cost: Minimal hardware cost, minor firmware development cost.  ·  latency: Instant reaction required, no latency impact.
- security: Improves security by allowing immediate manual control over automation.

### `model-routing` — Develop a specialized model-routing policy that dynamically routes UI interaction commands requiring visual understanding and pixel input through mac-vision only when loop permissions and consents are active, otherwise falling back to safer, less disruptive accessibility tier with restricted actions.
- **owner gets:** Ensures mac-vision only takes full control when explicitly allowed, protecting the owner from unintended disruptions and respecting privacy and device policy constraints dynamically without losing functionality entirely.
- effort: medium effort in model orchestration and policy implementation.  ·  risk: Incorrect routing could cause degraded performance or denied actions, mitigated via robust testing and fail-safe defaults.
- cost: Moderate, depending on frequency of vision vs accessibility tier usage.  ·  latency: Minimal for allowed commands, smooth fallback latency when denied.
- security: Positive by enforcing permission-aware execution policies.
- depends on: permission and consent management integration


## What it asked for

_Nothing._
