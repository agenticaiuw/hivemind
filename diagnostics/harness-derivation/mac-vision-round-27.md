# Harness derivation — mac-vision — round 27

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make the AI Pendant Mac Vision agent fully functional with safe, low-disruption UI control and visual context awareness"
- **useful because:** The owner wants the AI Pendant Mac Vision agent to actively assist with tasks that cannot be automated via API by interacting with the Mac UI at the accessibility level or pixel level, in a way that respects privacy and does not interrupt the owner unnecessarily. This enables hands-free, context-aware control and task automation on the owner's MacBook.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** realtime
- **latency:** under 200ms per interaction
- **cost:** moderate GPT-style API usage plus low latency compute on the Mac pendant and cloud relay
- **security:** Requires enabling accessibility permissions on the Mac and vision data consent, so the owner must trust the agent with sensitive UI data and real-time control; must have safeguards to prevent unintentional actions or privacy breaches.
- **missing:** Accessibility permission enabled for AI Pendant Agent; Vision upload consent given; computerUse.loopEnabled flag enabled for mac-vision agent; UI hierarchy snapshot context sent to mac-vision; Typed action policy for classifying and controlling UI actions to prevent risk

### "Enable a multi-modal AI assistant that coordinates the pendant, Mac vision agent, planner, and relay to provide seamless task management, voice command execution, and UI interaction with full context sharing and safety controls"
- **useful because:** This unlocks the full power of the AI Pendant system, letting the owner speak commands, have the Mac agent execute complex UI workflows safely, receive real-time voice feedback, and maintain context awareness across devices for smooth task flow and enhanced productivity.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension
- **model tier:** realtime
- **latency:** under 300ms per user interaction
- **cost:** Higher due to coordinating multiple agents and modalities, including voice and vision processing.
- **security:** Requires comprehensive permission and trust model, data encryption, local processing preference, and user confirmation steps for sensitive actions.
- **missing:** inter-device secure context synchronization protocol; multi-agent action broker with typed confirmation; integrated voice and UI interaction pipeline


## Changes it proposed to its own stack

### `integration` — Implement a secure, typed action broker middleware that intercepts all mac-vision UI control actions to classify them as read-only, reversible, or high-impact mutations. Require explicit owner confirmation on high-impact mutations before execution. This broker would mediate commands between mac-vision and the Mac OS UI to reduce risk and increase safety for enabling full computerUse.loop control.
- **owner gets:** This system enables the owner to safely allow mac-vision's powerful UI control capability while mitigating risks of unintended harmful actions. It acts as a protective layer giving the owner control and observability over mac-vision's UI actions.
- effort: Medium to high engineering effort due to deep OS integration and UI action classification design.  ·  risk: Bugs could delay or block UI actions, or leak data, but can be rolled back if designed carefully. Owner trust is key.
- cost: Moderate CPU and development cost; API cost is negligible.  ·  latency: Low added latency for action classification and confirmation steps.
- security: Significant improvement by adding a safeguard layer on top of raw UI control access.
- depends on: Accessibility permission enabled; computerUse.loopEnabled enabled; mac-vision agent running

### `context` — Establish a privacy-respecting UI and environment context stream that continuously updates the mac-vision agent about the owner's active applications, window hierarchies, and screen regions of interest without sending pixel data outside the local Mac. This context feed helps mac-vision reason about UI state and make intelligent interaction decisions without needing full screenshots.
- **owner gets:** Gives mac-vision timely, relevant, and privacy-safe awareness of the owner's current UI and workflow state to enable context-aware computer use loop actions, improving utility without compromising privacy.
- effort: Moderate, requires building a local context extractor and streaming interface, plus new APIs for subscription and updates.  ·  risk: Minimal, since no pixel data leaves the device. Potentially incomplete context if apps use custom rendering.
- cost: Low CPU and network costs; negligible API costs.  ·  latency: Minimal; near real-time updates are needed.
- security: Positive as it avoids exposing raw screen content outside the Mac.
- depends on: Accessibility permission enabled; computerUse.loopEnabled enabled

### `hardware` — Equip the pendant with enhanced local AI capabilities, including a dedicated vision processing chip and lower-latency RAM, to enable offline real-time computer vision analysis and UI interaction prediction for the mac-vision agent. This reduces dependency on cloud processing and preserves privacy.
- **owner gets:** Enables the pendant to process visual input and assist the mac-vision agent instantly even when offline or with limited network access, improving responsiveness and privacy.
- effort: High hardware development effort and integration work.  ·  risk: Hardware compatibility and power consumption issues; recovery through fallbacks to cloud processing.
- cost: High initial development and hardware cost; moderate power increase.  ·  latency: Significant latency reduction for visual processing and UI reaction.
- security: Positive by keeping sensitive vision data local.
- depends on: Vision upload consent granted or replaced with local processing


## What it asked for

_Nothing._
