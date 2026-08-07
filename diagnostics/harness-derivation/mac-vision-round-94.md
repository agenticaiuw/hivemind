# Harness derivation — mac-vision — round 94

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a fully autonomous mac-vision loop that can safely and effectively control UI elements on the Mac by visual reasoning, interacting with the screen pixels and UI elements, and deciding next concrete UI actions when APIs can't do the job, seamlessly integrated with other agents."
- **useful because:** This would allow the owner to delegate complex, UI-level control tasks on the Mac that are currently impossible or require manual intervention, thus increasing productivity and automation of workflows that involve legacy or non-scriptable UI components.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-4.1-mini
- **latency:** Real-time or near real-time interaction, ideally under a few seconds per decision cycle, to keep interaction responsive and natural.
- **cost:** Moderate API cost dominated by visual reasoning over screenshots and UI state analysis, plus maintaining context and state across many loops.
- **security:** Significant risk of undesired UI mutations or privacy violations if the loop interacts with sensitive UI elements improperly; requires strict access control, logging, user confirmation policies, and possibly offline approval gating; all image data must be handled securely and with owner consent.
- **missing:** Permission to enable computerUse.loopEnabled and visionUploadConsented; Reliable, frequent UI hierarchy snapshots and selective pixel screenshots with privacy filters; Typed action policy for mutating UI actions with confirmation gating and rollback capabilities; Robust interaction protocols among mac-vision, mac-run_actions, and mac_delegate to safely distribute workload; Context sharing mechanisms to sync visual analysis with the owner's productive tasks and intentions

### "Allow the owner to set UI mutation safety levels and action approval policies for mac-vision that balance convenience and risk, from fully autonomous to confirmation-required for destructive or sensitive UI actions."
- **useful because:** Owners can tailor the level of intervention risk they accept from the automated UI agent, increasing trust and usability while avoiding unintended consequences or privacy issues.
- **path:** mac-vision → relay-realtime
- **model tier:** gpt-4.1-mini
- **latency:** Seconds for approval interaction, instant for autonomous mode.
- **cost:** Low to moderate, mainly in managing state and policy application logic.
- **security:** Potential risk if policy bypassed or confused; needs secure storage, logging, and user override controls.
- **missing:** UI mutation policy framework; User interface for safety level configuration and real-time approval workflows


## Changes it proposed to its own stack

### `integration` — Implement a secure, privacy-preserving integration layer that manages mac-vision's access to screen pixels and UI hierarchy data under strict consent mechanisms; coordinates with mac-run_actions and mac_delegate tools to distribute tasks correctly; and provides rollback and undo capabilities for UI mutations triggered by mac-vision. This layer handles context-sharing and permission gating between devices and agents dynamically to balance autonomy with safety.
- **owner gets:** The owner gets advanced UI task automation on the Mac that is safe, private, and auditable, enabling control of legacy and complex UI tasks otherwise impossible to script or automate.
- effort: High engineering effort to design and implement robust security, privacy, and coordination protocols across multiple agents and hardware surfaces.  ·  risk: Risks include accidental or malicious UI changes, privacy leaks from screen content exposure, and increased complexity in failure states. These require strict monitoring, fallback mechanisms, and user overrides.
- cost: Moderate due to extra processing and auditing overhead, plus potential increases in data transmission and storage for context and image data.  ·  latency: Low to moderate, depending on how quickly confirmation and rollback cycles are handled.
- security: High, needs airtight permissions and consent management plus encrypted data flows and strict audit logs.
- depends on: Enable computerUse.loopEnabled and visionUploadConsented; Typed action policies for UI mutation; Availability of reliable, privacy-filtered UI snapshots and pixel data

### `hardware` — Upgrade the pendant and Mac hardware interface to support low-latency, high-fidelity streaming of UI pixel data and accessibility events with edge-based pre-filtering and privacy masking to minimize sensitive data exposure before transmission. Add tamper-resistant hardware security modules to enforce consent and logging policies physically.
- **owner gets:** The owner benefits from fast, secure, and private device interaction data streams ensuring mac-vision can operate in real-time with confidence that privacy is preserved and the device state is reliable and tamper-evident.
- effort: Significant hardware design and firmware development involving collaboration with chip and OS makers.  ·  risk: Hardware bugs or security flaws could expose sensitive data or disable functionality; mitigation involves rigorous testing and formal verification where possible.
- cost: High initial component and development cost; low incremental operating costs once deployed.  ·  latency: Significantly reduced effective latency for UI data handling.
- security: Improved security posture by hardware-rooted protections.
- depends on: Consent frameworks and software integration layers for UI data handling

### `context` — Develop a dynamic, multi-source context management system that aggregates UI state from mac-vision, app status from get_mac_status, actionable commands from mac_run_actions, and multi-step goals from mac_delegate, synchronizing all with the owner's voice intents received via relay-realtime and the browser-experience.
- **owner gets:** The owner gains a coherent, consistent, and up-to-date situational awareness and task context model enabling seamless transitions between agent surfaces and more intelligent decision-making and action execution across devices and modalities.
- effort: Moderate to high, requiring cross-agent protocol design, shared data schemas, and robust conflict resolution mechanisms.  ·  risk: Potential for stale or inconsistent data causing confused agent behavior; requires fallback and recovery strategies.
- cost: Moderate due to continuous state monitoring and syncing overhead.  ·  latency: Minimal if well-optimized.
- security: Requires careful authorization and compartmentalization of context data to protect sensitive information.
- depends on: Baseline UI and device state feeds; Integration layer for data sharing and permissions

### `model-routing` — Establish a multi-tier model routing framework where gpt-4.1-mini on mac-vision handles real-time pixel-level UI reasoning, gpt-5.6-luna on mac-planner manages high-level task planning and coordination, and relay-realtime uses low-latency models to mediate live interaction and voice commands. This framework dynamically delegates workloads and shares results to optimize responsiveness and resource use.
- **owner gets:** Enables the owner to have AI agents specialized by capability and device constraints collaborate effectively, ensuring seamless and efficient task completion with minimal latency and maximal accuracy.
- effort: Moderate, requiring middleware for routing decisions, shared schemas, and possibly real-time telemetry.  ·  risk: Routing errors or model misalignment could cause delays or inconsistent behaviors; robust fallback and monitoring needed.
- cost: Moderate, shifting computation between cloud and device as needed.  ·  latency: Improved overall system latency by avoiding unnecessary heavyweight calls.
- security: Low to moderate; requires secure communication channels and authentication.
- depends on: Context aggregation system; Defined agent roles and capabilities

### `dashboard-ux` — Create a dedicated UI dashboard on the Mac and pendant to show pending and past mac-vision UI actions, including approval prompts, undo options, detailed logs of what was done, and real-time status, with controls to adjust action safety policies.
- **owner gets:** The owner can transparently monitor and control mac-vision's autonomous UI interventions, increasing trust, understanding, and ability to revert mistakes or adjust automation levels without complex command entry.
- effort: Medium effort for UI/UX design, development, and integration with action history and telemetry.  ·  risk: Minor risk of clutter or distraction if UI is not well designed; mitigated by good UX and user testing.
- cost: Low to moderate, mostly local resource use and occasional sync with agent status servers.  ·  latency: Minimal; UI updates can be asynchronous.
- security: Requires secure local data storage and possible authentication for control interface.
- depends on: UI mutation safety policy framework; Action execution telemetry and logging


## What it asked for

_Nothing._
## Its own summary

Proposed enabling a fully autonomous mac-vision loop integrated with safety, privacy, and coordination layers; hardware enhancements for secure, low-latency UI data streaming; context aggregation system for multi-agent synchronization; multi-tier model routing for optimized response; user-configurable UI mutation safety policies; and dashboards for transparent control and monitoring. These address owner needs for secure, real-time UI control on the Mac beyond current capabilities.

**Biggest unknown:** Exact privacy and consent mechanisms acceptable to enable screen capture and UI control on the Mac, and the owner's preferred balance of autonomy versus intervention for mac-vision.

