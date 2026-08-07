# Harness derivation — mac-vision — round 116

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable computer-use loop with safe, privacy-respecting screen capture and intelligent action planning on the MacBook."
- **useful because:** The owner needs direct AI control over the MacBook UI for seamless, accurate task execution that cannot be done solely via APIs. This includes reading app UI states, mouse and keyboard control, and handling ambiguous workflows in real time.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for vision processing, gpt-5.6-luna for planning and judgement
- **latency:** Low-latency interaction expected; under 2 seconds response time for UI action decision
- **cost:** Moderate due to continuous vision data processing and real-time decision making; major cost is GPU or specialized hardware for vision inference
- **security:** Sensitive screen content must be processed locally or encrypted in transit; visionUploadConsented must be set explicitly by the owner; all actions require transparent logging and user confirmation for high-impact changes.
- **missing:** computerUse.loopEnabled permission granted; visionUploadConsented permission granted; Secure local or encrypted remote vision processing architecture; Typed action policy with confirmation for destructive actions; UI accessibility snapshots with low interference fallback


## Changes it proposed to its own stack

### `firmware` — Add hardware-accelerated local AI vision processing coprocessor to the MacBook device to enable always-on safe UI snapshot analysis without performance or privacy penalty.
- **owner gets:** This enables fast and private computer use AI vision processing without depending on sending raw screen data to the cloud, allowing real-time actions and privacy preservation.
- effort: Medium to high engineering effort to design and integrate this specialized hardware and drivers.  ·  risk: Hardware bugs or security flaws might expose sensitive data; mitigated with secure enclave and encryption.
- cost: Significant increase in hardware cost and power draw; amortized over many future capabilities.  ·  latency: Significant reduction in latency for vision processing tasks compared to cloud or CPU-only inference.
- security: Improves security by keeping raw screen data local and encrypted; reduces attack surface for remote vision processing.

### `integration` — Develop trusted integration protocols between mac-vision, mac-planner, relay-realtime, and faculties to enable seamless and safe handoff of UI control tasks, context sharing, and decision arbitration.
- **owner gets:** Ensures that complex workflows involving UI control, planning, voice interaction, and judgement can cooperate without leaking sensitive data or miscoordination, providing a smooth user experience.
- effort: Moderate protocol and software engineering effort to define APIs, serialization formats, and secure channel communications among these surfaces and faculties.  ·  risk: Potential synchronization bugs or data leakage if protocols are not well designed; mitigated by thorough testing and security reviews.
- cost: Minimal direct cost impact, mainly development time.  ·  latency: Improves decision latency by avoiding redundant data handling and confusion between agents.
- security: Improves security by establishing clear boundaries and encryption for inter-agent communication.
- depends on: Enable computer-use loop with privacy controls and confirmation; firmware-level support for vision processing

### `dashboard-ux` — Create a live monitoring UX on the owner's dashboard to show mac-vision loop activity, including when screenshots or UI snapshots are taken, actions performed, and any user confirmation needed.
- **owner gets:** Provides transparency and real-time control for the owner over the AI's computer use actions, increasing trust and safety.
- effort: Low to moderate UX and backend work to surface and log loop activity and prompt user confirmations.  ·  risk: Disclosure of private info on dashboard; mitigate by limiting visibility to owner and using secure channels.
- cost: Minimal, mostly backend and UI fetch/render costs.  ·  latency: Negligible to none, UX is asynchronous.
- security: Improves security by empowering owner oversight.
- depends on: Enable computer-use loop with privacy controls; integration protocols for mac-vision and other surfaces


## What it asked for

_Nothing._
