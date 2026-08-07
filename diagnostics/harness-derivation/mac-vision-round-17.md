# Harness derivation — mac-vision — round 17

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full computer use loop with vision on MacBook for seamless task automation and live screen understanding."
- **useful because:** The owner can delegate complex desktop tasks needing visual context, improving productivity and accessibility with minimal manual input, leveraging the AI pendant ecosystem uniquely.
- **path:** mac-vision → relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** realtime
- **latency:** sub-second to one second for most interactions
- **cost:** moderate API usage due to vision processing; local compute minimal
- **security:** Requires granting Accessibility and Screen Recording permissions, plus user consent for vision upload; potential privacy risks with screen content accessible remotely; must include strong user control and transparency.
- **missing:** A secure, transparent interface for requesting and managing Accessibility and Screen Recording permissions.; Robust consent flow for vision upload with clear user education.; System to enforce limited scope and audit for computer control actions.; Tight integration across devices for seamless cross-device state and control.; Backup/rollback mechanisms for automated actions to prevent negative outcomes.


## Changes it proposed to its own stack

### `hardware` — Add a hardware privacy indicator LED on the MacBook that lights up whenever screen recording or AI vision upload is active, ensuring physical awareness of surveillance state.
- **owner gets:** Provides a trustworthy, unspoofable signal that vision or screen capture is ongoing, enhancing owner confidence and privacy while enabling AI vision features.
- effort: Medium hardware design and system integration effort.  ·  risk: Minor risk if LED malfunctions or is ignored; requires OS and driver support.
- cost: Low incremental hardware cost and power use.  ·  latency: None.
- security: Improved security by reducing covert surveillance risk.

### `interaction` — Implement a staged onboarding assistant on the pendant and Mac that educates the owner about the benefits and risks of enabling AI vision and full computer control, guiding them through each permission grant with contextual examples and reversible trials.
- **owner gets:** Increases owner trust and understanding, reducing friction and fear around granting powerful permissions, thereby unlocking advanced AI capabilities safely.
- effort: Moderate; requires UI/UX design, multi-device coordination, content creation, and backend support for reversible state trials.  ·  risk: Low risk of confusion; mitigated by user testing and feedback.
- cost: Minimal.  ·  latency: Minimal.
- security: Positive, by increasing informed consent and transparency.
- depends on: Accessibility and Screen Recording permission mechanisms; Vision upload consent flow

### `model-routing` — Enable conditional routing of vision data processing across on-device Mac, wearable pendant, and cloud relay based on privacy, latency, and task complexity preferences set by the owner.
- **owner gets:** Owner can balance privacy and performance dynamically, keeping sensitive data local when needed or leveraging cloud compute power for complex tasks.
- effort: High complexity integrating routing logic and managing state synchronization.  ·  risk: Complex system may introduce latency or inconsistency; requires robust fallback mechanisms.
- cost: Potentially higher cloud API costs if offloading is frequent.  ·  latency: Improvement or degradation depending on routing choice.
- security: Better privacy control but requires thorough vetting to prevent leaks.
- depends on: Hardware capabilities for on-device processing; Consent and privacy controls

### `integration` — Develop deep integration between Mac local agent, wearable AI pendant, and cloud relay to synchronize user state, tasks, and context for seamless multi-device AI assistance including vision, voice, and UI control.
- **owner gets:** Enables fluid interaction where vision data from Mac enhances pendant voice agent understanding and vice versa; leverages strengths of each device to deliver richer, context-aware assistance.
- effort: Significant engineering for state sync, protocol design, and error handling across devices and network.  ·  risk: Synchronization errors or data inconsistencies could degrade experience; requires robust conflict resolution.
- cost: Moderate to high due to ongoing network and compute use.  ·  latency: Improves responsiveness by leveraging local device strengths.
- security: Requires airtight data privacy controls and encrypted messaging.
- depends on: Hardware and software upgrades on all devices; Robust privacy and consent mechanisms

### `memory` — Augment memory layer with vision-derived context capture that attaches visual UI states and snapshots to ongoing interactions and task histories for improved long-term assistance and recall.
- **owner gets:** Owner gets richer contextual memory that includes visual states, improving AI's ability to help with complex or interrupted tasks over time, personalized to screen interactions and app states.
- effort: Moderate development to extend memory schema and capture mechanisms; enhanced indexing for vision data.  ·  risk: Sensitive visual data stored requires encryption and user control over retention period.
- cost: Some increase in storage and compute for vision context archives.  ·  latency: Minimal impact; mostly background processing.
- security: Increased attack surface for privacy if not well secured.
- depends on: Vision capture capability; Consent and privacy controls

### `firmware` — Add firmware support for low-latency local processing of vision events and UI interaction logging directly on the pendant to reduce reliance on cloud and Mac compute, improving responsiveness and offline function.
- **owner gets:** Enables faster voice-vision interaction cycles and partial function even without connectivity, enhancing reliability and user experience.
- effort: High; requires firmware and hardware updates for efficient local processing and interaction logging.  ·  risk: Firmware bugs or hardware limitations may affect performance and reliability.
- cost: Potential increase in hardware complexity and power consumption.  ·  latency: Improves latency for certain tasks.
- security: Needs secure sandboxing and data protection in firmware.
- depends on: Hardware upgrades; Software support on pendant

### `dashboard-ux` — Create a dedicated dashboard UX on Mac and web to monitor, control, and audit AI vision actions, permissions, and interaction history, giving the owner full transparency and control over computer vision loops and data.
- **owner gets:** Builds trust by making AI vision activities visible and manageable; allows instant revocation of permissions or stops of continuous vision capture/actions.
- effort: Moderate UI/UX design and development effort across platforms, plus backend logging and event streaming.  ·  risk: Potential complexity confusing some users; mitigated by good design and education.
- cost: Moderate due to additional UI and event processing.  ·  latency: None.
- security: Enhances security by giving the user explicit control and audit capabilities.
- depends on: Logging and telemetry event support; Vision loop permission controls


## What it asked for

_Nothing._
