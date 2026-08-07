# Harness derivation — mac-vision — round 29

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe and privacy-preserving visual UI interaction and automation on the Mac with full consent controls"
- **useful because:** The owner currently cannot have pixel-level visual UI interaction by the mac-vision agent because the loop is disabled and vision upload consent is false. This limits the ability to perform fine-grained interface tasks, troubleshoot UI layout issues, or automate interactions in apps without APIs. Enabling this with strong privacy-first controls would vastly expand useful Mac automation while respecting user trust.
- **path:** mac-vision (wearer MacBook agent) for UI perception and action → relay-realtime (cloud service for speech and prompt coordination) → mac-planner (local Mac agent for plan synthesis and context) → browser-extension (for in-browser automation integration) → dashboard (for user visibility and consent management UI)
- **model tier:** realtime
- **latency:** sub-second to few seconds interaction latency
- **cost:** Medium per-interaction due to image processing, privacy checks, and prompt synthesis
- **security:** Strict controls to ensure visual data capture only with explicit user consent; all processing minimized on-device or on trusted backend with encrypted transport; logs or recordings scrubbed of sensitive data; easy revoke and audit of consent history required.
- **missing:** A formal user consent and permission gating UX flow for visionUploadConsented; On-device or backend privacy-preserving image processing hardware/software; Expanded mac-vision agent capabilities with pixel UI interaction actions; Protocols for secure image upload and temporary ephemeral storage; Cross-agent integration for UI state sharing and coordinated plan execution

### "Allow mac-vision agent to perform complex multi-step UI workflows autonomously with dynamic adaption"
- **useful because:** Currently, mac-vision is limited because the computer use loop is off and it cannot perform or adapt long, multi-step UI tasks on the Mac autonomously based on visual feedback or context. Enabling autonomous, adaptable multi-step UI workflows would let the owner delegate complicated sequences of tasks they normally do manually, improving productivity while minimizing errors or interruptions.
- **path:** mac-vision (local Mac visual perception and action) → mac-planner (local plan synthesis and monitoring) → relay-realtime (speech and command coordination) → dashboard (to visualize and debug running workflows)
- **model tier:** realtime
- **latency:** seconds to tens of seconds per step
- **cost:** Moderate due to continuous visual perception and decision making
- **security:** Requires strong owner control over what tasks can be automated and clear user-visible status of progress; robust fail-safe to stop on unexpected errors; no secret actions permitted; data processed with highest privacy standards
- **missing:** A local dynamic task planner that can interpret visual UI state changes and adjust plans; A reliable mechanism to track UI progress and handle errors based on screen or accessibility feedback; Secure channels for status and error reporting to other agents and user; A confirmation and interruption model suitable for long-running UI workflows

### "Enable owner-visible, voice-controlled undo and confirmation prompts for all mac-vision automated UI actions"
- **useful because:** With mac-vision enabled for UI automation, accidental or undesired actions can cause disruption. Having an easy voice interface for confirming or undoing UI actions improves safety and owner trust, allowing fluid use of visual UI automation with immediate recovery from errors.
- **path:** mac-vision (for action detection and status) → relay-realtime (for voice I/O interaction) → dashboard (for visualizing recent actions and confirming)
- **model tier:** realtime
- **latency:** sub-second to one second interaction latency
- **cost:** Low to moderate per interaction for quick confirmation vocal processing
- **security:** Ensures no destructive or unsafe UI actions are taken without owner confirmation; voice system must accurately identify owner commands and avoid spoofing
- **missing:** Voice interaction protocols linked to mac-vision action queue; Undo action capability in mac-run-actions and mac-delegate tools; Visual and voice UI integration for confirmation prompts


## Changes it proposed to its own stack

### `firmware` — Upgrade MacBook agent firmware and OS integration to expose a secure, high-fidelity accessibility layer API that supports advanced UI element introspection, granular action invocation, and on-demand screen content capture with user permission feedback loop.
- **owner gets:** This would provide mac-vision and allied agents with a reliable, privacy-respecting foundation for UI automation and screen understanding beyond current capabilities, enabling consistent, secure, and extensible visual automation that the owner can trust.
- effort: Major OS component and agent update requiring collaboration with OS vendors and security audits.  ·  risk: Potential security risks if not carefully sandboxed; could lead to unwanted access if permissions mismanaged; needs rollback and monitoring; mitigated by strict user prompts and logging.
- cost: Higher development and testing cost; negligible runtime cost.  ·  latency: Minimal latency added due to native integration.
- security: High impact but manageable with strict security design and user consent.
- depends on: mac-vision enhanced capabilities; secure remote coordination protocols; user consent management systems

### `integration` — Develop a unified agent orchestration protocol that tightly integrates mac-vision, mac-planner, relay-realtime, and the browser-extension agents to share UI context, ongoing plans, and adaptive responses dynamically across surfaces.
- **owner gets:** This would allow the owner to delegate complex tasks that span UI actions, browser interactions, spoken commands, and local file or app control seamlessly, leveraging strengths of each agent surface without leaks or redundant work.
- effort: Moderate integration effort building cross-agent communication and state synchronization frameworks.  ·  risk: Coordination complexity may cause sync errors or delays; fallback and error detection must be robust.
- cost: Moderate cloud and local CPU cost for state syncing and plan coordination.  ·  latency: Minimal added latency if well engineered.
- security: High due to wider data sharing; requires encrypted channels and strict data governance.
- depends on: enhanced mac-vision capabilities; expanded mac-planner services; real-time relay communication with contextual data sharing

### `memory` — Implement episodic memory of recent UI states, actions taken, and their results for mac-vision and mac-planner to consult when planning next steps or recovering from errors in UI workflows.
- **owner gets:** Having a short-term memory of UI interactions would enable more reliable multi-step workflows, rollback support, and better user assistance by understanding recent context and avoiding repeated mistakes.
- effort: Moderate engineering effort to design efficient memory structures and expose them to all relevant agents.  ·  risk: Memory corruption or memory privacy leaks; robust data handling and encryption required.
- cost: Modest additional storage and CPU costs.  ·  latency: Negligible impact on interaction latency.
- security: Memory data must be encrypted and access strictly controlled.
- depends on: ui_hierarchy_snapshot context availability; multi-agent integration


## What it asked for

_Nothing._
