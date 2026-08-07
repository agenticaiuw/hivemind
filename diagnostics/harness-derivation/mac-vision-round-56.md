# Harness derivation — mac-vision — round 56

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable fully autonomous Mac vision loop control with safety and precision."
- **useful because:** The owner could have real-time, pixel-level vision guiding precise UI interactions on their Mac without focus stealing or intrusive interference, enabling more complex workflows and improving productivity in ways no other node or current API can achieve.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** under 100ms per action decision
- **cost:** medium per invocation dominated by image analysis and model inference
- **security:** Requires strong user consent and local data processing to prevent privacy leaks; requires gated activation to prevent accidental interaction; needs consistent identity and accessibility permission verification to avoid misuse.
- **missing:** Fine-grained, low-latency accessibility API that works without focus stealing or focus change; Binary and trusted screen capture permission and verification integrated with the pendant's local approval; Robust UI action simulation system that respects app boundaries without causing focus telemetry or state corruption; Dedicated UI accessibility snapshot context sharing accessible by all mesh surfaces without repeated user approval

### "Allow Mac-vision to assist multi-step ambiguous workflows by combining pixel-based UI insight with API-driven automation."
- **useful because:** Combining pixel-level UI understanding with high-level typed actions and multi-step delegation allows the owner to automate workflows that require human-level visual interpretation, such as managing apps with poor API support, complex workflows spanning multiple apps, or dynamic UI elements.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** sub-second response time for workflow steps
- **cost:** medium to high depending on workflow length and action complexity
- **security:** Requires robust audit trail, user approval options for potentially sensitive UI state, and policy controls on mutating actions.
- **missing:** Integrated vision and API-based action planner capable of sequencing mixed-mode workflows; Enhanced UI state sharing and historical context memory for step continuity; User-friendly confirmation and rollback mechanisms for visual actions

### "Provide error and fallback recovery mode for mac-vision that gracefully degrades to API-only control on the Mac when vision loop is unavailable."
- **useful because:** The owner can rely on mac-vision for UI tasks but still maintain productivity without crashes or stalls when permissions, real-time access, or screen capture is restricted or offline.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime/background
- **latency:** instant fallback with minimal delay
- **cost:** low additional cost beyond current tooling
- **security:** Fallback disables vision data, restricting capabilities; must prevent insecure fallback exploitation.
- **missing:** Mode-switching logic between vision and API-only control in mac-vision agent; Fallback UI state estimation without vision; User notification and control over fallback activation


## Changes it proposed to its own stack

### `hardware` — Add a secure, user-approved screen capture and UI accessibility sharing feature embedded in the MacBook hardware and macOS kernel, with low-latency local API access for trusted agents like mac-vision.
- **owner gets:** Provides a foundation for safe, real-time visual UI control and observation on the Mac, enabling advanced AI-driven computer use loops without intrusive permissions or focus stealing.
- effort: High; requires OS-level engineering and hardware collaboration with Apple or OEM.  ·  risk: Delays or user experience impacts if the feature is buggy; potential privacy abuses without strict enforcement; recovery by disabling until update.
- cost: Minimal hardware cost increase; moderate software engineering investment.  ·  latency: Significant reduction in capture-to-model latency enabling real-time loops.
- security: Must enforce secure entitlement and user approval flows to prevent misuse.

### `integration` — Build a seamless mesh communication protocol and shared UI context memory across all surfaces and agents, enabling mac-vision to query and update shared UI state and pass visual context to mac-planner and relay-realtime without repeated user permission prompts.
- **owner gets:** Allows mac-vision's visual context to enhance multi-device and multi-agent coordination, enabling complex workflows across the owned ecosystem without redundant permission requests and improving continuity.
- effort: Medium to high, requires protocol design, agent updates, and UI context API design.  ·  risk: Complexity could cause sync issues, fallback needed for partial availability; security risks if shared context leaks, mitigated by strict access controls.
- cost: Negligible hardware cost, moderate development cost.  ·  latency: Improves real-time interaction latency by reducing redundant data fetches.
- security: Requires fine-grained access control, encryption, and auditing.
- depends on: Secure UI accessibility sharing API; Permissioned vision loop activation


## What it asked for

_Nothing._
