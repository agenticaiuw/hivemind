# Harness derivation — mac-vision — round 244

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable direct verification and recovery of mac-vision's actual UI actions on Mac by adding an accessibility-driven state snapshot-and-diff tool that compares claimed UI changes to observed changes on screen, enabling fault detection and graceful retry in multi-step UI workflows."
- **useful because:** Today, no agent can confirm that what mac-vision thought it clicked or changed is actually reflected on screen. This leads to potential drift, errors, and silent failures in complex Mac automation workflows. A real snapshot-and-compare would provide robustness, improve trust, and enable resume or recovery logic for multi-step computer use automation.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** seconds
- **cost:** low, dominated by accessibility tree snapshot processing
- **security:** Requires access to detailed accessibility tree snapshots and logs; must prevent info leakage and ensure no silent automation failures without owner awareness.
- **missing:** accessibility tree snapshot route that captures full desktop UI state pre- and post-action; diff and reconcile tool on Mac agent to report mismatch and recovery suggestions; integration with mac-vision loop to leverage actual UI state vs claimed action

### "Implement selective privacy mode for mac-vision's accessibility observations, allowing the owner to specify which applications or UI elements can be observed and automated by the agent, balancing privacy and automation power."
- **useful because:** This would give the owner greater control and trust by restricting mac-vision's automation and observation to non-sensitive apps or contexts, making the system more acceptable for everyday use, including handling sensitive or private work or communications securely.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** sub-second to seconds
- **cost:** low computational and storage cost for policy enforcement and filtering
- **security:** Requires robust app- and UI-element-level policy enforcement, and secure user interface for configuration to prevent accidental or malicious overrides.
- **missing:** policy framework for per-app and per-UI-element observation and automation permissions; UI for owner to set and modify selective privacy controls; mac-vision loop changes to respect and enforce policy


## Changes it proposed to its own stack

### `hardware` — Add a dedicated second physical button or capacitive touch zone on the pendant to act as a confident multi-purpose action trigger separate from the main mic hot-button, enabling reliable gesture triggers without latency or finger lingering interference.
- **owner gets:** This would allow multiple different action triggers with zero mistaking or latency, freeing the limited first button for mic hot-edge activation only, and supporting new interaction patterns like quick approval, bookmarking, or task toggles.
- effort: Moderate hardware redesign and firmware update; leveraging existing secure latch and marker infrastructure.  ·  risk: Possible increased power draw, minor increase in pendant size or cost; requires firmware and agent software updates to use the new input reliably.
- cost: Low to moderate hardware cost increase; power impact minimal when idle.  ·  latency: Negligible latency impact; improves interaction speed by eliminating gesture delay on first button.
- security: Neutral; new button signal handled securely by existing pendant endpoints.


## What it asked for

_Nothing._
