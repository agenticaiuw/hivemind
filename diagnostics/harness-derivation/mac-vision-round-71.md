# Harness derivation — mac-vision — round 71

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to delegate complex UI-driven Mac tasks that require reading and manipulating the graphical interface beyond APIs, with real-time visual understanding and control."
- **useful because:** The owner often needs to automate and expedite workflows on the Mac that cannot be handled by current API-driven actions, for example, interacting with custom apps or nested UI controls. This seamlessly extends their control without manual intervention.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini on mac-vision for real-time UI understanding and control, gpt-5.6-luna on mac-planner and other surfaces for contextual planning, judgement, and action orchestration.
- **latency:** Sub-second responses on Mac vision loop for UI steps; real-time voice relay interaction; seconds for planning and sequencing on the Mac and relay.
- **cost:** Moderate cost mainly due to UI image analysis and real-time stream processing, with planned offloading to cloud relay surfaces except the must-run-on-device UI loop segments.
- **security:** Screen content and user input are sensitive; require strict user consent per session, encrypted processing, and minimal persistent storage of UI images. High assurance of user control and ability to stop UI automation at any time.
- **missing:** Activation gate and consent flow to allow UI screenshot upload and input simulation.; Typed action broker that classifies UI interactions by risk and reversibility.; Enhanced privacy mode with on-device processing options and fail-safe shutdown.

### "Provide the owner with seamless, voice-driven Mac control including natural language commands that the mac-vision loop autonomously executes with visual confirmation checkpoints and undo capability."
- **useful because:** This would allow the owner to delegate complex Mac tasks by voice alone without manual screen interaction, boosting productivity and accessibility, while giving them confidence via confirmations and easy undo.
- **path:** relay-realtime → mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini on mac-vision for UI loop execution, gpt-5.6-luna on relay and planner for voice and task orchestration.
- **latency:** Sub-second UI loop steps, real-time voice interactions faster than normal conversation speed.
- **cost:** Moderate due to real-time UI interpretation and voice processing; much work amortized on relay backend.
- **security:** Must filter dangerous commands, enforce owner identity confirmation, limit destructive actions, and provide a clear emergency stop voice phrase with immediate effect.
- **missing:** Real-time typed action broker with prompt-based risk assessment and reversible action flagging.; Secure microphone and voice recognition integration for hands-free control.

### "Allow the owner to remotely monitor and control the Mac's UI state and running applications via a secure, privacy-focused interface on the wearable pendant."
- **useful because:** The owner can get live status and send commands to the Mac when away from it, improving flexibility and utility without needing the full Mac interface or a second computer.
- **path:** pendant → relay-realtime → mac-vision → mac-planner
- **model tier:** Lightweight AI on pendant for UI status display; gpt-4.1-mini on relay and mac-vision for state interpretation and command execution.
- **latency:** Sub-second to a few seconds for command effect feedback depending on network conditions.
- **cost:** Low to moderate — primarily communication overhead and lightweight processing on pendant and relay.
- **security:** Strong encryption and user authentication required; minimal UI data cached on pendant; owner control for emergency cutoffs.
- **missing:** Secure low-bandwidth UI snapshot streaming protocol from Mac to pendant.; Lightweight UI action proxy on pendant for basic commands.


## Changes it proposed to its own stack

### `hardware` — Design and build a new wearable pendant with enhanced capabilities: a dedicated camera for visual context capture, increased RAM and flash, multiple buttons for nuanced control, and a secure biometric sensor for authorization.
- **owner gets:** A next-generation pendant can provide rich contextual information about the owner's environment, enabling more reactive and personalized assistance, as well as secure and seamless multi-factor user authentication for privacy-sensitive tasks.
- effort: High effort due to hardware design, prototyping, firmware development, and integration with the existing system.  ·  risk: Delays in hardware development or integration issues; user discomfort with new form factor or biometric data use can occur; mitigations include iterative design, user testing, and opt-in data policies.
- cost: Significant component and production cost increase over Nordic nRF9160 DK prototype; potential increase in power usage but manageable with optimized firmware.  ·  latency: Minimal effect on system latency, as enhanced pendant primarily improves sensory input quality and security.
- security: Stronger security posture due to biometric authentication; requires strict data protection policies and secure firmware updates.
- depends on: firmware capable of camera data capture and secure biometric handling; relay and Mac software updates to process enhanced pendant data streams

### `integration` — Develop a typed action broker middleware that classifies, mediates, and logs all UI and system actions from mac-vision and relay-realtime, tagging reversibility and risk level, supporting undo and safe rollback of UI control.
- **owner gets:** Ensures safety and accountability of autonomous UI actions, allowing the owner to confidently delegate complex tasks without accidental destructive changes, improving trust and utility.
- effort: Medium to high; involves designing a robust action classification model, integration with existing tools, and developing UI feedback and logging.  ·  risk: Incomplete classification may allow unsafe actions; mitigated by owner feedback and incremental rollout.
- cost: Moderate CPU and storage for logging and classification, mostly backend costs.  ·  latency: Minimal; classification runs asynchronously with UI loop execution.
- security: Enables audit trail, helps prevent malicious or unintended harmful actions, strengthens overall system security posture.
- depends on: mac-vision; relay-realtime; mac-run-actions; faculty-judgement

### `integration` — Create a secure, low-latency streaming protocol and compression format to send selective Mac UI snapshots and event diffs to the pendant device, preserving privacy and minimizing bandwidth.
- **owner gets:** Allows the wearable pendant to provide live visual feedback and remote UI control cues to the owner, bridging the gap between Mac UI state and wearable display capabilities.
- effort: Medium; requires codec and protocol design, pendant and Mac software updates, and security audits.  ·  risk: Privacy risks if improperly secured; mitigated by end-to-end encryption and strict access controls.
- cost: Modest network and CPU usage increases on Mac and pendant.  ·  latency: Designed to minimize latency impact and fit LTE-M bandwidth limits.
- security: End-to-end encryption and authentication critical to maintain trust and prevent data leaks.
- depends on: pendant hardware platform support for decoding; mac-vision software updates for UI snapshotting and encoding; relay-realtime streaming infrastructure


## What it asked for

_Nothing._
