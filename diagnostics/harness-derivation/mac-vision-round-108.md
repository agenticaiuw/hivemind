# Harness derivation — mac-vision — round 108

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, permission-aware, real-time computer vision control on macOS with full accessibility and pixel-level input capabilities."
- **useful because:** The owner can get seamless, reliable Mac control for multi-step and ambiguous workflows beyond simple API calls, increasing productivity and reducing frustration with manual operations on the Mac desktop interface.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime tier for low-latency interaction and background AI models for complex planning.
- **latency:** sub-second response for routine UI queries, up to a few seconds for multi-step complex workflows.
- **cost:** Dominated by realtime vision model inference on device or companion hardware, with less for planning models.
- **security:** Local device vision data is sensitive; must have privacy-preserving on-device processing and permission gating before pixel-level operations affecting state. No unknown or unsupervised mutation allowed.
- **missing:** granular permission system for vision upload and computer control; device skill integration for safe local vision processing; ability to toggle computerUse loop with owner-confirmed safety; typed action policy layered on vision-driven UI control to classify and audit actions

### "Allow multi-modal fallback and cooperation between accessibility API controls and pixel-based input for Mac computer use workflows within the AI assistant system."
- **useful because:** Ensures robust Mac control by using accessibility APIs when possible for safe, low-impact control, falling back to pixel-based input only when necessary for complex or unsupported UI interactions, thus maximizing reliability and minimizing user disruption.
- **path:** mac-vision → mac-planner → faculty-action
- **model tier:** Mixed: realtime interaction model with fallback planning models to decide control mode.
- **latency:** Sub-second for API access; up to a second for fallback pixel operations.
- **cost:** Low to moderate, primarily software integration and some additional model inference cost.
- **security:** Careful gating of pixel-based input to prevent accidental destructive actions; audit logs required.
- **missing:** API for seamless switching and cooperation between control modes; Fallback planning and decision model to choose control method per step


## Changes it proposed to its own stack

### `hardware` — Add dedicated local neural vision acceleration hardware on the Mac device or companion accessory to enable efficient, low-latency on-device vision processing for real-time UI understanding and control.
- **owner gets:** Provides the necessary on-device processing power for privacy-preserving, fast vision-based computer control without requiring constant cloud interaction or high latency.
- effort: High, requires hardware design, manufacturing, OS-level integration, driver and API development.  ·  risk: Hardware bugs or integration failures could delay overall feature availability, but fallback to non-vision interaction remains possible.
- cost: Significant upfront cost and power draw increase, offset by user productivity gains.  ·  latency: Greatly reduces latency for vision processing compared to cloud-based or CPU-only solutions.
- security: Improves security by limiting sensitive visual data to local processing only.

### `integration` — Integrate a typed action brokering and policy enforcement layer for vision-driven computer control workflows on Mac, coordinating between accessibility APIs, pixel-based input, and multi-step automation planning across all AI surfaces.
- **owner gets:** Ensures that vision-based UI control actions are classified, auditable, and reversible where possible, preventing unauthorized or harmful mutations while enabling powerful computer use.
- effort: Moderate to high, requires coordination between Mac OS accessibility APIs, AI models, policy layers, and user permission controls.  ·  risk: Complexity could introduce bugs or delays; policy misclassification could lead to action blocks or false positives.
- cost: Mostly software development cost and some runtime overhead for action classification and auditing.  ·  latency: Small, mostly done asynchronously or in parallel to user action.
- security: Increases overall system security and owner trust by enforcing policies and logging all vision-driven UI actions.
- depends on: hardware vision acceleration

### `interaction` — Develop an owner-facing permission and consent user interface integrated into the AI Pendant and Mac surfaces that allows real-time control and fine-grained overrides for computerUseLoop vision upload and computer control toggles.
- **owner gets:** Gives the owner direct, transparent control over when vision-based computer control is active, protecting privacy and preventing accidental or unwanted automation actions.
- effort: Medium, requires UI/UX design, cross-device synchronization, and integration with existing policy enforcement layers and vision loop implementation.  ·  risk: Poorly designed UI could confuse the owner or lead to inadvertent permission grants; must be intuitive and trusted.
- cost: Primarily software development and testing cost.  ·  latency: None significant; UI is user-driven.
- security: Increases trust and control, reducing risk of unauthorized use.
- depends on: integration typed action policy; hardware vision acceleration


## What it asked for

_Nothing._
