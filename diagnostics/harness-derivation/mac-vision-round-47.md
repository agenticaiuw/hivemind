# Harness derivation — mac-vision — round 47

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable seamless, autonomous Mac UI navigation and control using combined accessibility and pixel vision on the AI Pendant Mac agent."
- **useful because:** The owner can have a continuous, context-aware, visually guided assistant on their Mac that can proactively manipulate app UIs, handle edge cases, and perform complex workflows without requiring API bindings or manual interactions. This would save time, reduce frustration, and unlock new automation possibilities beyond scripts or static APIs.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** sub-second to a few seconds for UI actions and replies
- **cost:** Moderate per invocation, limited by frequency and resolution of vision capture; main cost from visual model inference and UI action validation.
- **security:** Requires permanent accessibility trust and screen recording permissions on the Mac, plus strict owner control on when video data is uploaded or processed. Sensitive screen content must be protected, and mutating actions carefully rate-limited and logged to avoid misuse.
- **missing:** Accessibility trust granted persistently to the AI Pendant Agent on macOS so accessibility APIs can be used without falling back to pixel-only interaction.; Screen recording permission granted persistently to allow safe pixel vision of the Mac screen for visual UI interpretation.; Vision data upload consent given by the owner, with configurable privacy settings and on-demand toggling.; ComputerUse.loopEnabled set true by orchestrator to allow mac-vision loop continuous operation.; A layered software stack that blends accessibility tree data and pixel vision for robust UI recognition and context understanding.; Fallback mechanisms to degrade gracefully to accessibility-only or script-only actions if permissions or conditions change.; A safety framework enforcing action confirmation, undo support, and action result receipts for transparency and control.; Integration with multi-step planner and delegate to combine vision-based actions with scripted and typed actions.


## Changes it proposed to its own stack

### `hardware` — Add a dedicated, low-power image capture and preliminary vision processing unit inside the Mac pendant hardware for continuous UI screenshotting and preprocessing, minimizing latency and privacy risk by offloading vision frame selection and preliminary feature extraction from the main CPU.
- **owner gets:** This would enable near-real-time visual UI interaction without compromising Mac battery or performance, enabling the mac-vision agent to respond quickly and smoothly to UI contexts without heavy CPU load or network uploads.
- effort: Significant hardware design and firmware development, plus integration with the existing AI Pendant software stack and Mac agent.  ·  risk: Hardware bugs or design flaws could introduce battery drain or privacy leaks; careful testing and opt-in consent mechanisms needed.
- cost: Moderate increase in hardware cost and power consumption, offset by performance improvements.  ·  latency: Reduced latency for vision processing and UI update detection.
- security: Requires secure hardware design, isolated vision pipeline, and strict access control to prevent misuse or data leakage.
- depends on: Operating system and driver support for hardware-assisted screen capture and vision preprocessing.; Software stack changes to leverage and orchestrate this hardware for UI vision and interaction.

### `integration` — Develop an integrated orchestration layer in the AI Pendant system that harmonizes mac-vision's visual UI capabilities with mac-run-actions' typed command execution and mac-delegate's multi-step workflow planning, allowing dynamic switching and fallback among vision-guided pixel UI actions, accessibility tree interactions, scripting, and typed commands.
- **owner gets:** This would create a seamless and resilient system where the owner can rely on the AI to fulfill complex UI tasks regardless of platform or permission status, with fluid recovery from partial failures or limitations.
- effort: Moderate to high software engineering and testing effort to develop the orchestration logic, interface standards, error handling, and communication protocols between components.  ·  risk: Increased system complexity might cause subtle bugs or performance issues; extensive validation and monitoring needed.
- cost: Software engineering time and computational resources for coordination logic and state management.  ·  latency: Slightly increased decision-making latency due to orchestration but offset by improved overall task success and robustness.
- security: Requires secure communication and action authorization across components; proper logging and auditing are essential.
- depends on: Full capabilities of mac-vision, mac-run-actions, and mac-delegate available and stable.; Reliable communication channels and state synchronization between surfaces and agents.

### `dashboard-ux` — Create a dedicated mac-vision dashboard panel for the owner to view, approve, or override planned UI actions, review visual context snapshots, and manage privacy settings for vision data upload consent and screen recording permissions.
- **owner gets:** This interface empowers the owner with transparent control over mac-vision's operations, enabling trust, quick intervention, and personalized privacy management, thus making autonomous UI automation safer and more acceptable.
- effort: Moderate UX/UI design and development effort on the dashboard system, integrating live agent state and permissions management.  ·  risk: If poorly designed, the dashboard might overwhelm or confuse the owner; usability testing is critical.
- cost: Moderate development and maintenance cost for a new dashboard panel.  ·  latency: Minimal impact on latency as this is a control interface, not part of the core action loop.
- security: Access control and encryption must protect the dashboard especially due to sensitive UI snapshots and permission toggles.
- depends on: mac-vision providing live state and proposed actions data.; Dashboard platform capable of rendering UI controls and history.

### `model-routing` — Introduce a specialized real-time model routing tier that dynamically selects between lightweight accessibility-only models and more powerful but resource-intensive pixel vision models based on current permissions, power state, task complexity, and user preferences.
- **owner gets:** This intelligent routing optimizes performance, cost, and privacy by deploying the best-suited model for each UI interaction or decision, enabling mac-vision to operate effectively even in constrained environments or permission-limited states.
- effort: Moderate complexity in routing logic, state monitoring, and model management across tiers.  ·  risk: Routing errors or misclassifications could degrade experience; robust testing and fallback mechanisms required.
- cost: Operational cost varies by model usage; potentially reduced average cost by using lighter models when possible.  ·  latency: Routing adds minimal overhead but can prevent costly model invocations unnecessarily.
- security: Model routing control must be secure to prevent unauthorized model switching or data exposure.
- depends on: Reliable context and permission state tracking.; Availability of diverse model tiers in the system.

### `memory` — Implement context-sensitive memory caching for mac-vision that retains recent UI state snapshots, owner preferences, interaction histories, and permission changes to accelerate decision-making and reduce redundant operations in the UI loop.
- **owner gets:** Speeds up mac-vision responsiveness and accuracy by leveraging prior knowledge and recent UI interactions, reducing lag and user interruptions, and improving overall experience.
- effort: Moderate software engineering effort to integrate memory caching frameworks and tune for UI contexts.  ·  risk: Stale or incorrect memories could cause errors; must have validation and expiration policies.
- cost: Slightly increased local storage and computational overhead.  ·  latency: Lower latency for repeat or related UI tasks due to cached context.
- security: Memory data must be securely stored and access-controlled to protect sensitive UI and owner data.
- depends on: Access to relevant state and interaction data streams.; Integration with mac-vision planning and decision subsystems.

### `routines` — Create a natural language enabled routine for the owner to request complex UI workflows on the Mac that the system breaks down into typed mac-run-actions or vision-guided UI manipulations, with fallback prompts for input when actions are ambiguous or require permission.
- **owner gets:** Simplifies ownership experience by allowing the owner to express goals naturally, which the system translates into actionable steps across different control tiers and surface capabilities, thus enabling powerful automation without manual scripting.
- effort: High complexity in natural language understanding, planning, and execution across heterogeneous capabilities.  ·  risk: Misinterpretations could trigger unwanted actions; needs robust testing, confirmations, and undo mechanisms.
- cost: Increased compute cost for natural language processing and multi-tier orchestration.  ·  latency: Potentially longer planning times offset by improved autonomy and usability.
- security: Needs strict authorization controls and audit trails for all generated actions.
- depends on: Stable mac-run-actions and mac-vision capabilities.; Strong planner and delegate coordination infrastructure.

### `firmware` — Develop firmware upgrades for the pendant device to support enhanced local caching, low-latency UI event processing, and secure encrypted communication channels for sensitive permission and lattice state signaling with the Mac agent and cloud relay.
- **owner gets:** Improves responsiveness and reliability of UI automation by distributing some workload locally on the pendant, reducing communication delays, and safeguarding permission signals and state info against tampering or leakage.
- effort: Moderate to high firmware development and testing across multiple device platforms and network conditions.  ·  risk: Firmware bugs could affect device stability or security; extensive testing and fallback recovery needed.
- cost: Development cost with minor impact on device power consumption.  ·  latency: Significant reduction in latency for UI event feedback and control signals.
- security: Strong encryption enhances overall system security and owner privacy.
- depends on: Hardware support for upgraded capabilities.; Software stack integration for new firmware features.


## What it asked for

### `c5-cvwf` (context) — ui_hierarchy_snapshot
- why: To safely and effectively interact with the Mac UI using accessibility actions without taking focus or screenshots
- would change: Allows mac-vision to explore UI elements and plan low-impact actions without visual interference

