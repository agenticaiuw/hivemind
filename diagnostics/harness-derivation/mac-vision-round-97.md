# Harness derivation — mac-vision — round 97

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Introduce a privacy-first approval and gating system for activating pixel-based UI vision loops on the owner's Mac."
- **useful because:** It ensures the owner retains absolute control over when and how their screen pixels are captured and used for AI vision-based computer interaction, preserving confidentiality and trust while enabling advanced assistive functionality.
- **path:** mac-vision → relay-realtime → faculties-judgement → faculties-perception
- **model tier:** gpt-5.6-luna for policy and gating execution; gpt-4.1-mini for computer vision loop context.
- **latency:** Seconds for confirmation and gating response.
- **cost:** Low API cost related to policy validation and confirmation UI handling.
- **security:** The owner must never have pixel data captured or sent without explicit permission. Any approvals must be logged and reversible instantly. Device local enforcement preferred.
- **missing:** A local enforcement layer on the Mac for gating vision uploads.; UI for owner to preview captured images before approval.; Policy framework integrating with orchestrator and all surfaces to require gating before any pixel stream starts.

### "Unified AI assistant coordination protocol among mac-vision, mac-planner, relay-realtime, and faculty agents for complex multimodal task completion."
- **useful because:** Allows the owner to seamlessly delegate any complex task that involves vision-based UI interactions, high-level planning, real-time voice command processing, and action execution across devices and apps without friction or duplicated efforts.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna for planner, relay, and faculty coordination; gpt-4.1-mini for vision state updates.
- **latency:** Low latency (under 2 seconds) coordination for real-time responsiveness.
- **cost:** Moderate due to multi-agent model use and context synchronization costs.
- **security:** Secure authenticated cross-agent data sharing is mandatory to prevent unauthorized task injection or data leaks.
- **missing:** Cross-agent communication protocol with context synchronization and conflict resolution.; Shared context memory accessible live across agents with privacy controls.; Modular task decomposition and handoff logic to assign subtasks to the best suited agent dynamically.


## Changes it proposed to its own stack

### `integration` — Implement a privacy-preserving owner consent UI and local enforcement layer for visionUploadConsent, tightly integrated with the mac-vision and relay-realtime surfaces and faculty-judgement gating policies. This UI shows real-time previews of pixels to be uploaded, offers explicit opt-in/opt-out controls, and integrates with orchestration to block unauthorized vision loop activations.
- **owner gets:** Provides the owner with transparent control over when their screen pixels are captured and used, protecting privacy while enabling advanced vision-based automation.
- effort: Moderate integration involving UI, orchestration, policy enforcement, and inter-surface communication.  ·  risk: If poorly designed, owner trust could be broken or the system could block legitimate use cases; rigorous testing and fail-safe defaults needed.
- cost: Low ongoing API cost, some initial development cost for UI and orchestration changes.  ·  latency: Minimal to none on normal operations; confirmation UI adds expected delay during consent dialogs.
- security: Significant positive impact by preventing unauthorized pixel capture and enforcing privacy preferences at multiple system layers.
- depends on: mac-vision; relay-realtime; faculty-judgement; faculty-perception; orchestration system support for gating

### `hardware` — Add a dedicated secure co-processor module on the MacBook that handles all vision pixel processing and encryption locally before any data leaves the device. This chip enforces owner privacy policies and consent decisions at the hardware level and provides encrypted trust signals to the orchestrator and relay.
- **owner gets:** Ensures maximum privacy and security for pixel data involved in vision-based automation, preventing leaks or unauthorized access even if the OS or applications are compromised.
- effort: High hardware design, integration, and software driver development effort.  ·  risk: Hardware complexity and cost increase; potential compatibility issues with existing MacBook architecture.
- cost: Significant hardware cost increase, marginal power consumption increase.  ·  latency: No increase; possibly improved latency by offloading pixel encryption and filtering locally.
- security: Very high security improvement by hardware enforcing privacy, complementing software policies.
- depends on: mac-vision software to interface with the hardware module; operating system support; orchestration integration

### `model-routing` — Develop a dynamic model routing system that switches between lightweight accessibility-based models and heavier pixel-based vision models for UI interpretation on the Mac. Routing adapts based on task complexity, owner preferences, and context privacy guarantees to optimize cost, latency, and accuracy.
- **owner gets:** Improves system efficiency and responsiveness by using the minimum necessary compute resources per task while providing rich vision when needed and allowed by privacy policies.
- effort: Medium engineering effort for model orchestration and runtime environment management.  ·  risk: Incorrect routing may cause delays or insufficient UI understanding; requires robust fallback mechanisms.
- cost: Potential cost savings by avoiding unnecessary heavy vision-model inference.  ·  latency: Improved average latency by using lightweight modes where possible.
- security: Model routing respects privacy policies, by disabling pixel-level models unless consent provided.
- depends on: mac-vision; faculty-perception; policy enforcement mechanisms

### `dashboard-ux` — Create an owner's dashboard UI panel that displays vision loop status, pixel capture activity logs, and allows quick enable/disable of visionUploadConsent with one click. This dashboard also educates the owner on privacy and trust and offers direct feedback channels for reporting issues or concerns.
- **owner gets:** Gives the owner transparency and easy control over vision-based automation and pixel data usage, enhancing trust and user confidence in the system.
- effort: Low to medium frontend UI development effort with integration to orchestration and policy layers.  ·  risk: Minimal; mostly UX design risks if controls are not clear or comprehensive enough.
- cost: Low ongoing cost.  ·  latency: None.
- security: Positive impact by making privacy practices visible and transparent.
- depends on: mac-vision; relay-realtime; orchestration policy APIs

### `interaction` — Develop a voice-based confirmation and control subprotocol integrated with relay-realtime and mac-vision for low-friction consent granting or denial for pixel capture and mutating UI actions. This protocol uses natural language prompts from the owner and AI parsing to confirm intentions instantly without losing workflow momentum.
- **owner gets:** Allows the owner to quickly approve or revoke permissions related to vision loops and UI automation by voice without needing manual interaction, maintaining a smooth hands-free experience and immediate security feedback.
- effort: Medium complexity integration of voice recognition, natural language understanding, and cross-agent messaging.  ·  risk: Potential misrecognition or accidental grants requiring fallback manual revocation; needs robust confirmation logic.
- cost: Moderate API usage for voice and NLU processing.  ·  latency: Low latency required for good UX; real-time streaming voice handling.
- security: Enhances security by making explicit consent interactive and effortless while minimizing accidental granting risks.
- depends on: relay-realtime; mac-vision; faculty-judgement; orchestration


## What it asked for

_Nothing._
