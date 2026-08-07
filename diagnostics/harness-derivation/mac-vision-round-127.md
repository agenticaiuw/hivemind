# Harness derivation — mac-vision — round 127

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to enable a privacy-conscious computer-use assistance mode on their Mac that activates only while they physically hold down the pendant's button, using only accessibility-tier UI hierarchy queries without any screen recording or screenshots. This would allow adaptive, context-aware help without risking privacy or requiring full permissions."
- **useful because:** This feature lets the owner get proactive, adaptive automation and advice in the moment they want it, without exposing their whole screen or requiring risky permissions. It leverages the unique hardware button for safe, deliberate activation and respects privacy.
- **path:** pendant → mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini for UI reasoning, gpt-5.6-luna for planning and dialogue
- **latency:** sub-second local responses for UI queries, up to a few seconds for multi-step planning
- **cost:** moderate, mostly GPT calls with local device bridge operations
- **security:** No screen pixels or video leave the device unless explicitly enabled; button-hold requirement prevents accidental activation; all sensitive UI state is ephemeral and uses Apple accessibility APIs without recording; user triggers every activation.
- **missing:** Accessibility permission granted to AI Pendant Agent to access UI hierarchy; Software support for button-hold activation tied to permission to query UI; Loop enabled for computerUse with these constraints

### "Allow the owner to start a conversation and get spoken feedback on what app and UI element is currently focused, based purely on accessibility APIs, before they say anything or type, triggered by the pendant button press."
- **useful because:** This enables situational awareness for both the user and the system, making subsequent commands more intelligent and context-aware without breaching privacy by screen recording or screenshots.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** gpt-4.1-mini for UI state parsing, gpt-realtime-2.1 for voice feedback
- **latency:** under one second for initial spoken confirmation
- **cost:** low to moderate, mostly local quick queries and TTS
- **security:** No visual pixels captured or stored, button press needed to start; ephemeral UI state only; no private data logs; info only used transiently for feedback.
- **missing:** Enable accessibility API use without full screen recording permissions; Low-latency UI state access and spoken TTS integration support

### "Enable seamless multi-surface collaborative workflows where complex multi-step tasks triggered by voice or button prompts can coordinate execution across the Mac (via mac-planner), browser (via browser-extension), and local shortcuts, with live status and user feedback, managed by the unified agent mind."
- **useful because:** Owners often need help with tasks that involve multiple apps and the browser, which existing single-app or single-node agents cannot manage well. This enables a genuinely new kind of personal AI assistant that works fluidly across platforms and devices, dramatically extending productivity and reducing cognitive load.
- **path:** mac-planner → browser-extension → relay-realtime → mac-vision → unified
- **model tier:** gpt-5.6-luna for planning and integration, gpt-4.1-mini for UI step advising
- **latency:** seconds for planning and status updates, with streaming voice responses
- **cost:** high, requires multi-model collaboration and persistent state
- **security:** All user data stays under strict control within the personal network; multi-surface state sharing uses encrypted channels; user maintains control of what data is shared; requires user consent for cross-surface coordination.
- **missing:** Robust multi-surface state synchronization protocols; Persistent session memory; Integrated voice and button interaction triggers across devices; Unified task orchestration framework

### "Enable the Mac agent to recognize when the owner intentionally presses and holds the pendant button and use this as a deliberate trigger to temporarily escalate the computer use loop permissions to full accessibility querying and light screen context capture (still no full screenshots), enabling an adaptive personal assistant mode only when the user explicitly wants it."
- **useful because:** This creates a very clear and hard-to-trigger mechanism to safely activate the powerful computer-use AI loop without risking accidental privacy breaches or unwanted automation, putting control firmly in the owner's hands and leveraging the unique hardware affordance.
- **path:** pendant → mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-4.1-mini and gpt-5.6-luna for UI reasoning and control
- **latency:** under a second for activation, ongoing interaction as needed
- **cost:** moderate with mostly local device API calls and AI planning
- **security:** Requires careful OS-level permission changes to allow dynamic accessibility permission escalation controlled by a hardware button; button hold ensures accidental activation is nearly impossible; no constant listening or video capture unless activated.
- **missing:** OS-level API or middleware support for dynamic accessibility permission gating triggered by hardware input; Software logic to integrate button hold detection and temporary loop state change

### "Allow the AI system to proactively suggest relevant shortcuts or automations to the owner based on their current app context and recent activities observed via accessibility APIs, while respecting privacy by only using non-visual contextual info and requiring button-hold activation for active suggestions."
- **useful because:** This helps the owner discover productivity improvements and personalized automations they might not think of, increasing efficiency without intrusive surveillance or privacy risk.
- **path:** mac-vision → pendant → mac-planner
- **model tier:** gpt-4.1-mini for context inference and suggestion generation
- **latency:** seconds for suggestion generation
- **cost:** Low to moderate, mostly local compute and lightweight AI calls
- **security:** Strictly limited to ephemeral, accessibility-derived context; requires explicit user activation to propose; no screen captures or logs stored without consent.
- **missing:** Machine learning pipelines tuned for non-visual app context inference; Button-hold activation integration; Suggestion delivery UI


## Changes it proposed to its own stack

### `hardware` — Add a hardware signal line from the pendant's user button directly to the Mac Bridge to enable ultra-low-latency and secure detection of button hold without relying on software polling or network latency.
- **owner gets:** This enables the owner to have an instantaneous, reliable physical trigger for enabling sensitive AI assistance modes or workflows on the Mac without any software overhead or delay, enhancing safety and user control.
- effort: Moderate hardware and firmware changes to route the button signal and update Mac Bridge and pendant firmware to handle the event.  ·  risk: Potential hardware malfunction or firmware bugs could block the owner's ability to activate AI assistance; can be recovered with a fallback software trigger.
- cost: Low additional hardware cost; minimal power usage increase.  ·  latency: Very low latency for button event detection, enabling immediate AI mode activation.
- security: Improved security by eliminating network software race conditions during activation; physical presence required for activation.

### `integration` — Build a secure, ephemeral UI state sharing protocol between mac-vision and relay-realtime that transmits minimal accessibility hierarchy context only when the pendant button is held and AI assistance is active, avoiding any persistent logs or screen capture.
- **owner gets:** This enhances cross-device collaboration and intelligent assistant responsiveness while strictly limiting privacy risks, giving the owner more powerful cross-surface AI help only when explicitly requested.
- effort: Moderate software development and cryptographic design to ensure secure ephemeral UI state transmission and disposal.  ·  risk: Poorly designed security could leak UI state; mitigated by strong encryption and strictly ephemeral memory management.
- cost: Low additional network and CPU cost due to limited data size and ephemeral nature.  ·  latency: Low latency required for real-time assistance without noticeable delay.
- security: Strong security needed for encrypted firewall-friendly transmission; minimizes privacy risk by ephemeral design.
- depends on: hardware button hold detection; accessibility permission gating; active computer-use loop

### `model-routing` — Develop a specialized model routing policy to dynamically switch between a low-latency, limited-capability GPT-4.1-mini for real-time UI reasoning and a more powerful GPT-5.6-luna for complex multi-step task planning when using mac-vision in computer use loop.
- **owner gets:** This optimizes user experience by reducing latency during interaction with UI and ensuring powerful planning and integration for complex workflows, striking the best balance between responsiveness and capability.
- effort: Relatively low, involves software updates to routing logic and state management between model instances.  ·  risk: Possible routing errors causing slower response or degraded interaction, recoverable by fallback logic.
- cost: Optimizes cost by using large models only when necessary, reducing average compute usage.  ·  latency: Improves latency for UI tasks, maintaining responsiveness.
- security: No increased security risk beyond current model usage.
- depends on: active computer-use loop; model orchestration infrastructure

### `firmware` — Enhance the ESP32 audio bridge firmware to support local wake word detection and initial phrase filtering, offloaded from the cloud relay. This reduces latency and data transmission costs, and provides the owner with greater privacy control by limiting audio sent off-device.
- **owner gets:** Allows the owner to have a more responsive and private voice assistant experience, with less dependence on network connectivity and cloud processing for wake word and initial command detection.
- effort: Moderate firmware development and testing, integration with existing cloud relay protocols.  ·  risk: Incorrect wake word detection or false positives; can be tuned and logs reviewed for improvement.
- cost: Reduces network usage costs and cloud compute costs.  ·  latency: Significantly lowers latency for wake word detection, improving user experience.
- security: Improves privacy by minimizing raw audio transmission until activated.
- depends on: ESP32 firmware development environment; Audio processing libraries

### `dashboard-ux` — Create a dedicated dashboard panel for the owner to configure, monitor, and control the new privacy-sensitive computer-use AI modes, including button hold activation, permissions status, and usage logs (limited to metadata, not raw UI state or screen data).
- **owner gets:** Gives the owner full transparency and control over sensitive AI modes, making it easy to enable or disable capabilities, review recent activity, and understand what data is accessed or shared, thus building trust and user confidence.
- effort: Moderate UI/UX development effort to build and integrate with existing dashboard systems.  ·  risk: Misleading UI or incomplete information could confuse the owner; mitigated by clear design and user testing.
- cost: Low; mainly development time and minor backend additions.  ·  latency: Minimal impact; dashboard is used on demand.
- security: No privacy risk as no new data is collected; enhances security through transparency.
- depends on: dashboard framework; AI agent telemetry reporting


## What it asked for

_Nothing._
