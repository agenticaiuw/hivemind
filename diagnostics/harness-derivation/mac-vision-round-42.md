# Harness derivation — mac-vision — round 42

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent loop safely to automate complex Mac tasks using UI accessibility and pixel-based controls with intelligent decision-making."
- **useful because:** The owner can delegate recurring or complex Mac operations that cannot be done through APIs alone. This saves time and reduces cognitive load by having the AI agent act interactively through the Mac UI, including apps that do not offer APIs.
- **path:** mac-vision → mac-planner → relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** low latency real-time on mac-vision for UI interaction; background context processing and planning on mac-planner and relay-realtime
- **latency:** A few seconds max to respond to UI changes and take actions
- **cost:** Moderate due to frequent small UI snapshots and decision cycles; heavy processing distributed across mac-planner and relay-realtime
- **security:** High risk since the loop can perform arbitrary UI interactions and mutating actions; requires explicit owner control, immutable logging of all actions, and fail-safe aborts if unexpected states occur
- **missing:** UI hierarchy snapshot context passed automatically to mac-vision; Fine-grained permissions to distinguish safe from high-risk actions; Ability to query partial or full screenshots without disturbing owner workflow; Local safety heuristics to avoid destructive or disruptive UI mutations; Context-driven gating rules managed by faculty-judgement to enable/disable loop in safe contexts

### "Provide a user-friendly interface on the Mac and pendant to review, approve, undo, or customize mac-vision's past and planned UI actions with clear explanations and screenshots."
- **useful because:** Gives the owner transparency and control over the AI-driven UI automation, building trust and enabling correction or tailoring of behavior to fit personal preferences.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** Mac and relay agents for interface and explanation generation, mac-vision for data capture
- **latency:** Seconds for interface responsiveness
- **cost:** Moderate due to UI rendering and natural language explanations
- **security:** Sensitive data handling requires careful design of data exposure, logging, and consent mechanisms
- **missing:** UI for history and control; Integration with mac-vision memory and action system; Secure, seamless multi-surface session synchronization

### "Allow mac-vision to initiate and control multi-step Mac UI workflows autonomously based on intent understanding and UI changes, with real-time monitoring and undo capability."
- **useful because:** Automates complex sequences involving multiple applications and dialogs without manual intervention, increasing owner productivity and enabling sophisticated task completion not possible through single API calls.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-judgement → faculty-action → unified
- **model tier:** mac-vision for real-time action and sensing; mac-planner and relay for high-level planning and intent modeling
- **latency:** Seconds to a minute depending on workflow length
- **cost:** Moderate to high due to complex planning, action execution, and rollback monitoring
- **security:** High risk of unintended consequences; requires strong oversight, transparent logs, and owner control mechanisms
- **missing:** Advanced intent recognition and workflow synthesis models; Rollback and error recovery frameworks; Continuous monitoring and alerting infrastructure


## Changes it proposed to its own stack

### `hardware` — Add a lightweight local camera on the Mac device focused on the screen to capture fullscreen video or images at adjustable frequencies, combined with a dedicated secure processing enclave for AI vision tasks locally without sending images externally.
- **owner gets:** Allows mac-vision to have real pixel-level understanding of Mac UI state without interrupting owner or app focus and enables responsive UI automation for apps with no API.
- effort: Medium to high, requires hardware integration and firmware updates on the Mac platform.  ·  risk: Hardware failure or security breach could expose visual data; mitigated by secure enclave and local-only processing.
- cost: Potential increase in device cost and power usage; still manageable within MacBook capabilities.  ·  latency: Improves latency by providing direct local screen capture for fast AI decision making.
- security: Must ensure strict user control and data isolation; images never leave device without user consent.
- depends on: Software integration for capturing and processing images tied to computerUse loop; Permissions system allowing controlled image capture and loop activation

### `model-routing` — Establish a dynamic multi-tier model routing system where real-time low-latency UI action decisions are done by mac-vision on device, while complex planning, multi-session memory synthesis, and long-term task coordination are offloaded to relay-realtime and mac-planner AI agents.
- **owner gets:** Maximizes responsiveness and power efficiency by allocating work to the best-suited AI agent and hardware surface, giving the owner seamless and intelligent Mac task automation without lag.
- effort: Moderate software engineering to define prompts, routing protocols, and task handoff logistics.  ·  risk: Potential complexity in debugging and coordinating AI subsystems; fallback mechanisms needed for errors or downtime of some agents.
- cost: Moderate cloud compute and network costs for coordination; on-device costs limited by task segmentation.  ·  latency: Reduced perceived latency for the owner due to specialized local agent handling UI interaction.
- security: Need robust authentication and data flow controls to prevent misuse or data leakage.
- depends on: Inter-surface communication protocols; Shared context graphs and memory systems

### `interaction` — Develop a multi-modal interaction framework combining voice commands via pendant, visual gaze or gesture detection if hardware permits, and on-screen UI feedback from mac-vision to collaboratively guide complex Mac interactions.
- **owner gets:** Allows natural, low-friction communication and approval for automation steps, fallback queries, and error recovery during Mac task automation, enhancing safety and user satisfaction.
- effort: High, requires integration of several input/output modalities and real-time feedback systems.  ·  risk: Complex UI/UX design challenges and potential privacy concerns with gaze/gesture capture.
- cost: Increased computational load, possibly requiring more powerful hardware or cloud support.  ·  latency: Potentially small increase due to multi-modal data fusion and processing.
- security: High, due to new sensor data streams and user privacy considerations.
- depends on: Hardware support for gestures/gaze or equivalent input; Reliable low-latency voice recognition and synthesis; Integration with mac-vision action loop

### `memory` — Implement a secure and efficient episodic memory system for mac-vision that logs UI states, action intents, decisions, and outcomes with time stamps and contextual metadata, accessible across all AI surfaces for continuous learning and error correction.
- **owner gets:** Enables the system to learn from past successes and mistakes in Mac UI automation, improving accuracy, reducing redundant queries, and providing audit trails for owner review.
- effort: Medium to high, involves designing data structures, synchronization protocols, and privacy controls.  ·  risk: Risk of storing sensitive UI information; must ensure encryption, access control, and data minimization.
- cost: Storage and compute costs for maintaining and querying memory data.  ·  latency: Minimal impact on real-time action loop due to asynchronous processing.
- security: High, requires strong encryption and access policies to protect sensitive data.
- depends on: Cross-surface data sharing protocols; User privacy and permission framework

### `new-surface` — Introduce a dedicated mac-vision assistant module on the Mac hardware platform with enhanced access to camera, GPU, and secure local storage for rapid UI processing and model inference.
- **owner gets:** Provides the necessary hardware/software combination to run low-latency, safe, and powerful UI interaction models that cannot run efficiently on the pendant or cloud alone.
- effort: High, involves hardware module integration and driver/firmware support.  ·  risk: Hardware integration risks and maintenance burden; potential increased attack surface if not properly secured.
- cost: Significant due to new hardware and software development.  ·  latency: Improves local processing and decision times substantially.
- security: Must be designed with user security and privacy as paramount.
- depends on: Hardware platform updates; OS-level integration for access controls and data flow


## What it asked for

_Nothing._
