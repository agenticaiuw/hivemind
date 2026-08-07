# Harness derivation — mac-vision — round 77

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the Mac-vision agent to safely and privately capture screen screenshots locally on the Mac without uploading, for enhanced UI understanding and interaction"
- **useful because:** Currently Mac-vision cannot take screenshots due to lack of visionUploadConsented, limiting its ability to interpret complex UI and plan actions precisely. Local-only screenshot capturing with no upload preserves user privacy while enabling powerful visual context for automation and assistance.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini on Mac-vision for local UI interpretation
- **latency:** Real-time low latency for interactive use
- **cost:** Minimal API usage since screen data is processed locally; mostly on-device compute cost
- **security:** No data leaves the device for privacy; user consent for local capture only; strong local sandboxing to prevent misuse
- **missing:** Local on-device screen capture and processing pipeline; UI element detection that integrates pixel info with accessibility hierarchy; Permission model to allow local capture without network upload; Integration with mac-vision action actor for better UI navigation and visible feedback

### "Enable multi-modal Mac UI interaction combining accessibility API data and pixel-based vision to maximize reliability and functionality"
- **useful because:** Pure accessibility or pure pixel-based methods alone are insufficient to handle all UI automation tasks due to app-level limitations, security settings, or complex visual elements. Combining these modes adaptively enables the owner to automate almost any UI task reliably.
- **path:** mac-vision → faculty-perception → mac-planner
- **model tier:** gpt-4.1-mini for vision tasks; gpt-5.6-luna for high-level planning and fusion
- **latency:** Realtime response (<200ms) for UI observation and combined interaction
- **cost:** Moderate, mostly from additional vision modes and fusion in planning
- **security:** Must enforce strict access control and user consent workflows; fusion layer must not expose sensitive info externally; action logging critical for accountability
- **missing:** On-device vision-enabled UI element extraction; Cross-modal data fusion system combining accessibility trees and pixel recognition; Fallback rules for degraded accessibility or visual-only UI interaction; Context-aware decision making to select the best interaction mode per UI element

### "Create a real-time collaborative feedback loop between mac-vision, faculty-perception, and faculty-judgement to share UI observations, proposed actions, and outcome verifications transparently"
- **useful because:** This enables the entire AI system to maintain a coherent shared understanding of the Mac UI state, avoid duplicated effort, and verify results promptly. It supports safety by granting multiple perspectives on proposed actions and capturing discrepancies between intended and actual effects.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** Realtime (<300ms) for UI state updates and action status feedback
- **cost:** Moderate due to constant state synchronization
- **security:** Secure messaging and state sharing to prevent injection or spoofing; access control to prevent leaks; audit trail for debugging
- **missing:** Shared state bus or message-passing protocol among these subsystems; Structured status and action reporting format with error/conflict flags; Consistent UI model updates and rollbacks based on multi-agent consensus


## Changes it proposed to its own stack

### `hardware` — Add a dedicated low-latency vision co-processor on the MacBook hardware to accelerate local UI screenshot analysis, element detection, and pixel manipulation without involving main CPU or cloud processing.
- **owner gets:** This would enable fast, privacy-preserving, continuous visual UI understanding for the Mac-vision agent, greatly improving responsiveness and capabilities while preserving battery life and data security.
- effort: High engineering effort, requires hardware redesign and driver/software stack integration.  ·  risk: Medium risk that hardware changes delay MacBook release cycles; mitigated by backward compatibility and fallback to software processing.
- cost: Significant hardware cost increase per unit; minor increase in power draw compared to software-only solutions.  ·  latency: Substantial latency reduction for vision tasks from hundreds of milliseconds to tens of milliseconds.
- security: Improved security due to local processing without cloud upload; new attack surface in hardware must be mitigated by design.

### `firmware` — Implement a secure local screenshot capture and processing firmware module that enforces user consent, manages local vision data storage, and provides a controlled API for mac-vision to access UI pixel data without exposing raw screen buffers externally.
- **owner gets:** This firmware layer adds a privacy-preserving mechanism to allow vision-based UI interaction without risking screen data leakage, enabling the Mac-vision agent to work effectively.
- effort: Moderate firmware engineering and integration with existing OS screen capture APIs and security frameworks.  ·  risk: Low to medium; firmware bugs could impair screen capture or cause denial of service, so thorough testing is essential.
- cost: Minimal, mostly development cost as this leverages existing hardware capability.  ·  latency: Low latency impact, designed for real-time operation.
- security: Improves security by sandboxing screen capture and enforcing consent policies.
- depends on: hardware vision co-processor or OS-level screen capture integration

### `model-routing` — Introduce specialized routing logic to allocate vision-heavy UI interpretation tasks to the Mac-vision agent running on the MacBook with lower-latency models; route high-level planning and judgement tasks to more powerful Mac-planner and faculty-judgement models to optimize usage and responsiveness.
- **owner gets:** Ensures the owner’s Mac-based vision tasks run efficiently with minimal delay while leveraging more powerful models off-device for complex planning, maintaining interactive speed and accuracy.
- effort: Moderate effort to implement model routing policies and integrate signals from perception and vision pipelines.  ·  risk: Low risk; potential task misrouting mitigated by fallback logic.
- cost: Potential cost saving by more efficient resource use.  ·  latency: Significant latency improvement for UI interaction tasks.
- security: No direct impact on security but maintains policy consistency.
- depends on: model catalog updates and routing infrastructure

### `integration` — Develop a unified integration layer that synchronizes across all agents (mac-vision, mac-planner, faculty-perception, faculty-judgement, faculty-action) for seamless handoff of UI context, action plans, and status results with guarantees of consistency and auditability.
- **owner gets:** This integration ensures complex workflows can flow smoothly from observing UI state to deciding actions to execution and verification, reducing failures or conflicting actions and providing clear audit trails.
- effort: High integration and coordination effort, requires cross-agent protocol design and implementation.  ·  risk: Medium complexity may introduce synchronization bugs; must provide robust recovery and logging.
- cost: Moderate, mostly in development and network messaging.  ·  latency: Low latency impact with efficient design.
- security: Essential for maintaining consistent and secure multi-agent operation.
- depends on: message passing or shared storage mechanisms


## What it asked for

_Nothing._
