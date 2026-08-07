# Harness derivation — mac-vision — round 64

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full computer use loop with pixel-based screen capture and direct GUI control on the MacBook for complex multi-step computer workflows and ambiguous tasks."
- **useful because:** Today the owner cannot have proactive, precise control on their MacBook GUI because the computer use loop is off and vision upload consent is missing. Enabling this would allow the system to see the Mac screen visually and interact with the UI for tasks that cannot be done by API or accessibility actions alone. This opens up nearly all manual computer operational scenarios to AI assistance, making the owner vastly more productive.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for immediate vision loop, gpt-5.6-luna for planning and higher judgment
- **latency:** Real-time visual processing on the Mac-vision agent, planning and decision making concurrent but slightly slower on the Mac-planner and faculty tiers.
- **cost:** Moderate per use due to continuous screen capture and pixel-level analysis, plus expanded use of the high-tier models for planning and action.
- **security:** Screen content is privacy sensitive; vision upload must be opt-in with explicit transparent consent. Action confirmation gating may be needed for certain high-impact actions to avoid accidental destructive changes.
- **missing:** computerUse.loopEnabled true; visionUploadConsented true; full pixel-based screenshot accessibility with input control integrated into mac-vision

### "Provide an advanced typed action broker on the Mac that can interpret natural language goals into the exact sequence of atomic reversible actions or multi-step plans combining Mac and browser tasks."
- **useful because:** The owner currently cannot leverage a precise typed action broker that produces auditable, reversible sequences with typed parameters for every step. This would make multi-step workflows safer, more transparent, and fully under owner's control without guessing or risking mistakes.
- **path:** mac-planner → mac-vision → browser-extension → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for broad planning and typing, gpt-4.1-mini for low-latency loop steps
- **latency:** Mix of quick typed action generation with longer multi-step planning phases. Real-time for simple commands, up to a few seconds for complex workflows.
- **cost:** Moderate due to multi-step planning and typed validation steps. Cheaper than pixel-level vision loop for routine tasks.
- **security:** Ensures actions are typed and reversible, minimizing destructive risks. Owner retains audit logs to verify execution steps.
- **missing:** A typed action broker middleware integrating typed mac_run_actions, browser_run_actions, and mac_delegate with step-level typing and confirmation.

### "Integrate live voice-controlled UI navigation on the Mac via the wearable pendant, allowing voice commands to trigger precise GUI actions through the mac-vision agent."
- **useful because:** Currently, the owner cannot directly control their Mac UI with voice commands through the pendant delivering natural language instructions. This integration would allow seamless hands-free operation, accelerating productivity and accessibility.
- **path:** relay-realtime → mac-vision → mac-planner → faculty-action
- **model tier:** gpt-realtime-2.1 for voice relay, gpt-4.1-mini for mac-vision control, gpt-5.6-luna for planning
- **latency:** Near real-time interaction with imperceptible lag for voice control and UI response.
- **cost:** Moderate due to continuous voice relay and real-time computer vision and control usage.
- **security:** Requires strict access control and privacy guarantees for voice data and screen content.
- **missing:** Voice-to-UI action mapping middleware integrated between pendant voice relay and mac-vision.; Real-time bi-directional communication channel between pendant and mac-vision

### "Enable unified multi-surface context sharing so the mac-vision agent can access browser context from browser-extension and system state from mac-planner to make more informed decisions about GUI interactions."
- **useful because:** Currently mac-vision operates with limited direct context, unable to leverage combined system, browser, and conversation state. Unified context sharing would allow cross-surface awareness, improving accuracy and relevance of Mac UI actions.
- **path:** mac-vision → mac-planner → browser-extension → unified
- **model tier:** gpt-5.6-luna for complex context integration and decision making
- **latency:** Context updates synchronized in near real-time to maintain fresh state across surfaces.
- **cost:** Low to moderate, mostly related to data synchronization and augmented prompting.
- **security:** Requires managing sensitive context data securely across surfaces to prevent leaks or misuse.
- **missing:** Unified context pooling and sharing API between mac-vision, mac-planner, and browser-extension.


## Changes it proposed to its own stack

### `hardware` — Add a local secure on-device vision processing chip and dedicated RAM in the MacBook pendant to enable fully offline and privacy-preserving pixel-based screen capture and GUI interaction with zero upload to external servers.
- **owner gets:** This would allow the owner to use advanced computer vision and UI control without any screen data leaving their immediate control, significantly improving privacy and security while enabling advanced capabilities.
- effort: High hardware development and integration effort, firmware and driver support needed, plus significant software updates.  ·  risk: Failures in hardware or firmware could disable critical features; fallback to lower-tier accessibility control needed.
- cost: Moderate to high for hardware, additional power draw estimated at 1-2W during operation.  ·  latency: Very low latency for screen capture and control actions, enabling near-instant real-time feedback.
- security: Strongly improves privacy by eliminating cloud upload of screen data; device keys and hardware root of trust needed.

### `model-routing` — Implement dynamic model routing that sends low-latency, low-complexity UI accessibility tasks to lightweight models on device or on the Mac, and routes complex pixel-based or multi-step planning tasks to larger cloud-based models.
- **owner gets:** Optimizes cost, latency, and responsiveness by applying the right tier of AI for the task. Ensures that simple tasks do not incur high cost or latency while complex tasks get the computational power needed.
- effort: Medium effort for orchestration, API, and routing logic. Requires model compatibility and integration with existing agents.  ·  risk: Routing errors or delays could impact user experience, require fallback strategies.
- cost: Reduces overall API costs by routing tasks intelligently.  ·  latency: Improves responsiveness for common actions, maintaining high quality for complex tasks.
- security: Better control of data exposure by routing sensitive tasks locally when possible.
- depends on: model-tier availability on respective machines

### `interaction` — Design a user interaction model for the AI Pendant that integrates voice, visual feedback, and haptic alerts to communicate complex computer vision tasks and requests for confirmation naturally and fluidly.
- **owner gets:** Improves transparency and trust by letting the owner understand what the AI sees and wants to do on the MacBook, and respond with natural voice or gesture commands, reducing mistakes and frustration.
- effort: High effort to design, prototype, and refine the interaction model across hardware and software layers.  ·  risk: Complexity might overwhelm or confuse the owner if not carefully tuned; requires iterative user experience testing.
- cost: Minimal direct cost, mainly development time.  ·  latency: Must operate in low-latency real time for responsiveness.
- security: Ensures no sensitive data is revealed in public or unintended contexts through controlled feedback modalities.
- depends on: voice recognition and synthesis on the pendant; real-time mac-vision action mediation


## What it asked for

_Nothing._
