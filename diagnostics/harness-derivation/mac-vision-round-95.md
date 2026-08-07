# Harness derivation — mac-vision — round 95

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable vision-driven Mac control with real-time UI understanding and contextual typed actions"
- **useful because:** The owner can command their Mac using visual context from the screen and precise typed action sequences. This unlocks complex workflows involving UIs where APIs are unavailable, helping the owner get things done by sight and voice with high accuracy and safety.
- **path:** mac-vision → mac-planner → relay-realtime → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime for UI perception and decision, background for planning and delegation
- **latency:** sub-second for visual understanding, seconds for typed action sequence plan and delegation
- **cost:** medium API cost mainly from real-time vision processing and backup LLM planning; hardware usage moderate for vision
- **security:** Vision data and typed actions can expose sensitive app content. Requires strong access control and opt-in consent (visionUploadConsented) before activation. High-impact actions must be confirmed by the owner. Data stays mostly on-device or encrypted.
- **missing:** Enable computerUse.loopEnabled with visionUploadConsented for safe vision capture and processing; Typed action broker tightly integrated with visual UI understanding to suggest and execute mac_run_actions and mac_delegate calls; Real-time UI snapshot streaming from Mac accessibility for accurate visual and structural context; Seamless communication across the wearable pendant, Mac, relay service, and orchestrator to manage state, permissions, and action flow


## Changes it proposed to its own stack

### `interaction` — Implement a tightly integrated vision-to-typed-action interaction layer that combines real-time UI snapshots, visual UI element recognition, typed action proposal and execution, and owner confirmation feedback.
- **owner gets:** Allows the owner to leverage visual context for precise and safe Mac control beyond what current typed actions or APIs support; enables complex, multi-step workflows driven by sight and intent.
- effort: Medium to high engineering effort due to real-time vision processing, integration with Mac accessibility APIs, and secure interaction flow design.  ·  risk: Potential privacy exposure from screen content capture; must enforce strict opt-in and usage policies. Incorrect interpretation of UI could cause wrong actions; mitigated by owner confirmation steps.
- cost: Moderate increase in API call volume and local compute power required for vision processing. Potential hardware power impact if very frequent captures occur.  ·  latency: Designed for sub-second vision update latency, ensuring responsive interaction but requires careful balancing of compute and network resources.
- security: High; screen capture and typed action execution must be well guarded. Data encryption and minimal transmission essential.
- depends on: Enable computerUse.loopEnabled with visionUploadConsented; Expand Mac accessibility snapshot APIs for real-time UI state; Extend mac_run_actions to support typed action proposals from vision input

### `new-surface` — Create a dedicated 'vision bridge' service that acts as a real-time conduit between the Mac's accessibility/vision data, the Mac-vision agent, and relay-realtime for processing and decision-making. This bridge manages permissions, data flow, and buffering to optimize latency and privacy.
- **owner gets:** This surface decouples vision data capture from the Mac-vision's AI model, providing robust, low-latency, and secure handling of sensitive screen data and UI context. It enables scaling and future upgrades in vision processing independently.
- effort: Moderate engineering effort to build a secure, performant relay service tailored for vision data streaming and control orchestration.  ·  risk: The new surface must be tightly secured to prevent leaks of sensitive visual data. Added complexity in the data pipeline needs careful monitoring.
- cost: Some additional compute and network costs from hosting and running the bridge service, offset by optimized data flows reducing overall latency and resource usage.  ·  latency: Improved end-to-end latency by buffering and preprocessing vision data before AI interaction.
- security: Requires robust encryption and access controls for all data streams passing through the bridge.
- depends on: Basic vision data capture permissions and capability; Relay infrastructure to support low-latency streaming and orchestration

### `hardware` — Equip the pendant with a low-power vision co-processor or dedicated accelerator capable of pre-processing screen capture data, running lightweight perception models, and enabling local vision-based UI analysis.
- **owner gets:** This hardware addition allows much of the vision processing needed for UI understanding to happen locally and efficiently on the wearable, reducing latency, data transmission, and power consumption from sending raw screen captures to the Mac or cloud.
- effort: Hardware design, prototyping, firmware, and integration effort is substantial and long-term, requiring specialized chip development or integration of off-the-shelf vision AI accelerators.  ·  risk: Added hardware complexity and more points of failure. Must maintain privacy and data security on-device. Development delays or cost overruns possible.
- cost: Increased hardware cost and possibly higher power draw, though optimized for low power usage to extend pendant battery life.  ·  latency: Significantly reduced processing latency for vision tasks local to the pendant, enabling near-instant UI perception and reaction.
- security: High security on-device processing reduces transmission of sensitive screen data.
- depends on: Current pendant hardware baseline; Firmware capable of running ML models or interacting with vision co-processor


## What it asked for

_Nothing._
## Its own summary

Recorded proposals to enable vision-driven Mac control with integrated typed actions, a real-time vision-to-action interaction layer, a dedicated vision bridge service, pendant hardware upgrades for local vision processing, and model routing for task allocation across devices.

**Biggest unknown:** Enabling computerUse.loopEnabled with visionUploadConsented and expanding real-time accessibility snapshots on the Mac for rich UI state visibility remain critical and unsolved dependencies.

