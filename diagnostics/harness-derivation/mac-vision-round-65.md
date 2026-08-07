# Harness derivation — mac-vision — round 65

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to request a real-time natural language explanation of each UI automation step mac-vision plans to take before it executes the step, with option to approve, modify, or reject."
- **useful because:** Gives the owner transparent insight and control over potentially impactful GUI automation steps, increasing trust and reducing error risk.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to a few seconds per explanation and decision
- **cost:** low per action, mainly conversational modeling compute
- **security:** Explanations must not leak sensitive data; user controls must prevent unauthorized automation.
- **missing:** natural language explanation generation integrated with typed action plans; interface for owner confirmation and modification


## Changes it proposed to its own stack

### `integration` — Integrate typed accessibility UI actions with the memory and context projection system to enable reliable, context-aware GUI automation on the Mac, coordinated with browser-extension and pendant voice control.
- **owner gets:** Provides seamless cross-surface automation that can dynamically choose the best surface to act through based on context, maximizing success and minimizing friction.
- effort: medium to high, involves cross-layer coordination and robust testing.  ·  risk: Potential for undesired automation if context or state is misinterpreted; mitigated by multi-agent verification and undo capabilities.
- cost: moderate, primarily in realtime coordination and context management overhead.  ·  latency: small delay in decision but keeps UI interaction smooth.
- security: Requires secure context sharing and clear policy boundaries.
- depends on: cap-a4c0ec8d; chg-a82e0b13; chg-498a3489

### `hardware` — Upgrade the pendant and MacBook integration hardware and firmware to enable secure, low-latency sharing of mac-vision's accessibility UI context snapshots and partial screenshots for richer assistance and failure recovery.
- **owner gets:** Enhances the owner's ability to get accurate and timely assistance from the AI hive mind when mac-vision automations encounter ambiguous UI states or errors, combining visual/audio context from multiple devices.
- effort: medium to high due to hardware firmware updates, security validation, and application programming.  ·  risk: Data leakage risk mitigated by encryption and strict access controls; increased power draw and latency mitigated by careful optimization.
- cost: moderate cost for hardware enhancement and maintenance.  ·  latency: Improved latency in cross-device context sharing, enabling faster recovery.
- security: Requires rigorous encryption and access policy enforcement.
- depends on: cap-a4c0ec8d; chg-a82e0b13

### `memory` — Build a fine-grained, typed context and event log specifically for mac-vision's UI interaction loop, storing each discrete UI action, result, and user override for full audit and undo capabilities.
- **owner gets:** Enables the owner to review, understand, and undo any mac-vision automated changes easily, enhancing trust and recoverability.
- effort: medium, involves memory schema design, storage, and UI surface for review and undo.  ·  risk: Data volume growth and complexity; mitigated by TTL and compression policies.
- cost: moderate due to storage and retrieval costs.  ·  latency: Minimal impact on realtime actions, mainly background processing.
- security: Sensitive UI data must be protected.
- depends on: chg-a82e0b13; cap-a1aa3bf5

### `interaction` — Create an interaction model for mac-vision where the owner can seamlessly switch between autonomous automation, guided step-by-step control, and manual intervention on the Mac GUI control loop.
- **owner gets:** Provides flexible control flow for the owner; they can let automation handle routine tasks, guide uncertain ones, or take manual over control anytime, preserving trust and efficiency.
- effort: medium, needs UI design, interaction scripting, and integration with state monitoring.  ·  risk: Complexity in UI and state sync causing confusion; mitigated by clear UI feedback and logging.
- cost: Low to moderate, mostly integration and UI updates.  ·  latency: Minimal except for interaction state sync.
- security: Must ensure transitions and control cannot be hijacked.
- depends on: cap-a4c0ec8d; cap-a1aa3bf5

### `routines` — Implement scheduled health checks and self-tests for mac-vision accessibility automation loop to detect UI changes, accessibility API breakages, or risky states and alert the owner.
- **owner gets:** Maintains reliability and safety of the mac-vision automation loop by proactively finding issues before they affect the owner's work, minimizing disruption.
- effort: low to medium, mostly scripting and notifications.  ·  risk: False positives or excessive alerts; mitigated by tuning and owner preferences.
- cost: Low, periodic automated checks.  ·  latency: None on realtime actions, background only.
- security: Safe as checks do not expose sensitive data.
- depends on: mac_run_actions; mac_vision


## What it asked for

_Nothing._
