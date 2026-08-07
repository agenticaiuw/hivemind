# Harness derivation — mac-vision — round 124

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a fully autonomous vision-powered computer-use loop on the Mac: take screenshots, interpret UI visually with the vision model, and make intelligent UI interactions without stealing focus or interrupting the owner."
- **useful because:** This enables seamless, context-aware computer control through vision combined with voice and browser extension interaction, making complex workflows fully natural and reliable for the owner.
- **path:** mac-vision → relay-realtime → browser-extension → mac-planner
- **model tier:** gpt-4.1-mini for vision + gpt-5.6-luna for orchestration
- **latency:** Sub-second to 2 seconds for key UI decisions
- **cost:** Moderate API calls for vision; low for orchestration and relay routing
- **security:** Screenshots and UI content are sensitive; requires strong local encryption and owner explicit consent with revocation ability
- **missing:** Full accessibility trust and screen recording permission; Vision upload consent from owner; Robust fallback when vision loop disabled

### "Implement a multi-surface intelligent workflow coordinator that seamlessly orchestrates tasks across Mac local apps, browser automation, and wearable voice commands."
- **useful because:** This unifies control and task execution across disparate surfaces, making daily computing and information retrieval fluid and hands-free when desired.
- **path:** mac-planner → browser-extension → relay-realtime
- **model tier:** gpt-5.6-luna composed with gpt-4.1-mini for feedback loops
- **latency:** Few seconds, suitable for multi-step tasks
- **cost:** Moderate; mainly orchestration and cross-surface integration
- **security:** Needs careful session and credential management across surfaces
- **missing:** Inter-surface communication protocols; Consistent session state sharing

### "Enable proactive Mac status monitoring that provides user real-time updates via their pendant voice and Mac UI dashboard on battery, network, and app state, reducing user need to check manually."
- **useful because:** Owner gains timely awareness without manual checks, improving device use efficiency and reducing anxiety over device state.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** gpt-4.1-mini for low-latency event detection and gpt-5.6-luna for contextualizing updates
- **latency:** Sub-second updates for critical events
- **cost:** Low due to lightweight monitoring
- **security:** Requires access to system state, but no sensitive personal data leaves device
- **missing:** Reliable event hooks for status changes; Pendant voice integration

### "Create a truly continuous, autonomous AI vision loop on the Mac that interprets screen content with a vision model and makes real-time intelligent UI decisions and interactions without interrupting the owner or stealing keyboard/mouse focus."
- **useful because:** It would enable hands-free, highly context-aware computer control beyond existing API or script limitations, integrating deeply with other surfaces for a unified AI experience.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** gpt-4.1-mini for vision inference, gpt-5.6-luna for orchestration and decision-making
- **latency:** Under 1 second for critical UI events; up to 2 seconds for complex decisions
- **cost:** Moderate—vision processing is costly but powerful; orchestration lightweight
- **security:** Screen content is highly sensitive; requires owner explicit consent and strict local encryption with no data sent externally unless permitted
- **missing:** Permissions: computerUse.loopEnabled, visionUploadConsented, Accessibility trust, Screen Recording permission on Mac; Reliable, low-latency UI snapshotting APIs or a pixel-based capture system that does not disrupt owner; Fallback mechanisms when vision loop is disabled or consent is withdrawn

### "Add a continuous, privacy-preserving vision co-processor subsystem integrated into the pendant and Mac that locally processes screen content to deliver semantic UI understanding for AI control without sending raw images externally."
- **useful because:** This would allow the owner to have always-on AI vision capabilities without privacy concerns tied to cloud processing or full screen recording permissions.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** Lightweight specialized vision model on co-processor, gpt-5.6-luna for coordination
- **latency:** Real-time or near-real-time UI semantic insight delivery
- **cost:** High hardware plus moderate inference cost; amortized by local processing gains
- **security:** Strong on-device encryption and no raw image export; owner control over consent and data flow
- **missing:** Specialized hardware vision co-processor; Firmware and software integration for privacy-focused local vision; APIs for semantic UI data exchange between co-processor and main AI stack


## Changes it proposed to its own stack

### `hardware` — Upgrade the Mac pendant and bridge firmware to support secure, low-latency screen capture and UI context feeds to the local AI vision model without interrupting the owner or compromising privacy.
- **owner gets:** This hardware-level improvement would enable richer UI understanding and faster interactions, making the AI vision loop more effective and less intrusive.
- effort: Significant firmware and hardware design and testing effort required, plus OS integration.  ·  risk: Potential device instability or security risks mitigated by strict access controls and rollback mechanisms.
- cost: Moderate increased hardware cost and power draw balanced by significant usability benefits.  ·  latency: Reduces latency for the vision loop by enabling local, real-time context feeds.
- security: Stronger security protocols needed at hardware and firmware level to protect screen data.
- depends on: Permissions for vision upload and computer use loop; Host Mac OS support for new capture APIs


## What it asked for

_Nothing._
