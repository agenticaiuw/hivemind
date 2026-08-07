# Harness derivation — mac-vision — round 112

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe and privacy-respecting vision-based Mac control for complex UI interactions"
- **useful because:** The owner can delegate complex multi-step tasks that require visual UI analysis and precise control across multiple apps and windows when no API or direct command is available. This makes their Mac more intelligent and effective, especially for tasks involving visual context or dynamic UI elements.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** realtime, capable of low-latency visual and UI contextual interpretation
- **latency:** sub-second for basic UI reads, a few seconds for complex task orchestration
- **cost:** medium per invocation due to image processing and AI reasoning, dominated by vision interpretation
- **security:** Requires explicit user consent for screen recording, UI accessibility permissions, and robust user confirmation layers before mutating system state. Data stays local unless explicitly sent for cloud AI processing with strong encryption and owner control.
- **missing:** Ability to enable mac-vision loop with fine-grained user permission gating; A context provider for real-time, privacy-respecting UI snapshots including pixel and accessibility data; Typed action policies classifying vision-driven actions by risk and requiring confirmation for destructive actions; Integration of mac-vision with typed reversible Mac actions (mac_run_actions) and delegation (mac_delegate); An orchestrator-managed secure UI data flow pipeline with owner controls for upload and sharing permissions

### "Provide detailed, real-time visual UI context snapshots that combine accessibility tree data and pixel information under owner control"
- **useful because:** This would empower vision-based agents to decide next actions more accurately, bridging the gap between raw screen pixels and accessible interface hierarchy for more intelligent and reliable computer use automation.
- **path:** mac-vision → faculty-perception → mac-planner
- **model tier:** Requiring background and real-time cooperation between perception and vision agents
- **latency:** Sub-second for small snapshots, seconds for larger context compositions
- **cost:** Medium; requires GPU and CPU compute for image processing and context fusion
- **security:** Needs robust owner permission control and data minimization; snapshots should be encrypted and limited to minimal necessary data for each task.
- **missing:** A unified compositing layer that merges accessibility UI hierarchy with pixel screenshots efficiently; Owner-controlled gating and throttling of UI snapshot frequency and detail level; Protocols for securely sharing combined visual and semantic UI context across internal agents

### "Enable reversible keyboard and mouse action synthesis with multi-level undo for computer use loop"
- **useful because:** Allows the owner to safely rely on vision-driven UI agent clicks and keystrokes, knowing that every action can be reversed through confirmed undo steps or automatic rollback, reducing error risks and increasing trust in full computer control.
- **path:** mac-vision → mac-planner → faculty-judgement
- **model tier:** Realtime interactive with persistent state tracking
- **latency:** Sub-second to one second per action, multi-second for undo sequences
- **cost:** Medium on compute due to state tracking and reconciliation
- **security:** Actions must be audited and confirmed, with user overrides and emergency stops.
- **missing:** State tracking systems for UI interactions; Multi-level undo engine integrated with mac_run_actions and mac_delegate; Clear protocols for audit and confirmation of reversible actions


## Changes it proposed to its own stack

### `firmware` — Add a dedicated hardware control and protection module on the pendant to mediate screen recording and UI control permissions, enabling selective, owner-consented activation of the mac-vision loop without exposing broad system privileges.
- **owner gets:** This module would provide the owner with fine-grained real-time control over when and how the Mac's screen and UI can be observed and controlled by AI, dramatically improving trust and safety.
- effort: Medium, requires new firmware development on pendant hardware and integration with Mac OS permission frameworks.  ·  risk: Potential bugs could lock out access or falsely enable control; recovery would require firmware updates or local reset procedures.
- cost: Minimal hardware impact as existing pendant chips would be leveraged; firmware and software development cost.  ·  latency: Negligible latency added to permission checks.
- security: Greatly enhances security by limiting exposure and enforcing user consent hierarchically.

### `integration` — Integrate mac-vision with existing typed action tools (mac_run_actions, mac_delegate) plus layered permission and confirmation policies to provide a composite AI control system that balances autonomy with safety for the owner.
- **owner gets:** This allows the AI to handle complex computer use via vision, but always under clear permission layers and with reversible, categorizable actions that respect the owner's intent and privacy.
- effort: Medium to high; requires new orchestration code, UI for permission and confirmation dialogs, and comprehensive testing.  ·  risk: Misclassification of actions could lead to unexpected mutations; mitigated by requiring confirmations for high-risk steps.
- cost: Additional compute and development time but mostly software changes.  ·  latency: Some additional latency due to permission checks and action classification, but acceptable for interactive use.
- security: Improves security by enforcing policy and confirmation for vision-driven control.
- depends on: mac_run_actions; mac_delegate

### `browser-harness` — Develop an extension that securely coordinates real-time UI context between the Mac vision agent and the browser agent, enabling reliable browser automation even when API integration is insufficient or unavailable.
- **owner gets:** Extends vision-driven computer use into the browser environment seamlessly, allowing complex workflows that span desktop and web applications.
- effort: Medium; requires browser extension development and cross-agent communication protocols.  ·  risk: Synchronization bugs could cause inconsistent states; user controls and error recovery needed.
- cost: Moderate software development cost.  ·  latency: Low-latency cross-agent messaging is required but feasible.
- security: Extension must enforce strong sandboxing and permission models to protect user data.
- depends on: mac-vision; browser-run_actions


## What it asked for

_Nothing._
