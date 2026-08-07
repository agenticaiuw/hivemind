# Harness derivation — mac-vision — round 73

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the mac-vision agent to safely enable and use full accessibility permissions on the Mac, including trusted accessibility and screen recording, with owner-approved privacy controls."
- **useful because:** This would unlock the full power of mac-vision to interact with apps and UI elements, see live screen content, and automate complex workflows that currently require either manual intervention or limited automation. It would enable true visual understanding combined with UI control.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime-2.1
- **latency:** sub-second response for typical UI queries and actions
- **cost:** moderate due to local vision processing and UI interaction overhead
- **security:** Requires explicit owner consent each time accessibility or screen recording permissions are used, with clear and auditable logs of all actions. Data must not leave device unless explicitly permitted.
- **missing:** owner permission flow for enabling accessibility and screen recording; privacy-preserving local vision processing; UI interaction gating and monitoring tooling

### "Enable AI pendant to coordinate multi-agent context-driven UI automation workflows that combine live UI state, user intents, and app statuses across mac-vision, relay-realtime, and mac-planner."
- **useful because:** Provides seamless and robust assistance by leveraging strengths of different agents and devices. Can predict and decide most appropriate UI actions or automation steps based on full context, reducing errors and user frustration.
- **path:** mac-vision → relay-realtime → mac-planner
- **model tier:** realtime-2.1
- **latency:** under 1 second for decisions and dispatch
- **cost:** moderate, dominated by context gathering and model reasoning
- **security:** Requires secure, private sharing of UI and app state across trusted agents. Must log all cross-agent decisions and balance privacy with utility.
- **missing:** infrastructure and protocols for cross-agent state sharing; shared memory or event streams for real-time synchronization; context-aware orchestration models


## Changes it proposed to its own stack

### `hardware` — Add a dedicated secure, privacy-preserving vision co-processor on the Mac or pendant to handle local screen capture and UI semantic analysis without needing full system screen recording permission.
- **owner gets:** Enables mac-vision agent to see screen content and UI structure for powerful UI automation and assistance while preserving privacy by keeping raw pixels and processing local and secure.
- effort: High, requires hardware design and integration with macOS security model and AI pendant firmware.  ·  risk: Hardware delays or bugs could reduce AI responsiveness or privacy guarantees; fallback to software-only methods needed.
- cost: Significant hardware and integration cost; moderate power use increase.  ·  latency: Improves latency for screen understanding compared to remote vision model calls.
- security: Enhances privacy and security by localizing sensitive data processing.
- depends on: firmware enhancements; bridge integrations; AI pendant firmware changes

### `integration` — Develop seamless integration of the mac-vision loop with mac-planner and relay-realtime to enable cooperative switching between pixel-based vision, UI-tree accessibility commands, and browser-native actions based on current permissions and context.
- **owner gets:** Maximizes automation capabilities by dynamically using the best available mode and agents for task execution, ensuring robust, reliable outcomes even with partial permissions or changing user needs.
- effort: Moderate development to design protocol, shared context structures, and switching logic.  ·  risk: Increased complexity could create coordination bugs or inconsistent states; needs strong testing and fallback strategies.
- cost: Low to moderate software engineering cost; negligible runtime cost.  ·  latency: Improves overall system responsiveness by using most efficient control method available.
- security: Requires careful access policy enforcement and monitoring to avoid privilege escalation or unintended control.
- depends on: faculties-perception; faculties-judgement; relay API improvements


## What it asked for

_Nothing._
