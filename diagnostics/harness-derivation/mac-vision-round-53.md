# Harness derivation — mac-vision — round 53

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, fully autonomous computer use loop on the Mac with real-time UI accessibility and pixel control"
- **useful because:** The owner could delegate complex Mac tasks that cannot be done through API alone, including GUI navigation, app control, and error recovery, all while preserving privacy and safety.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** low latency under 100ms per UI decision/action
- **cost:** moderate compute and context transfer mainly for high-frequency loop; most cost in cloud for complex inference and undo logging
- **security:** Requires strict permissions management, data encryption in transit, explicit owner consents, transparent undo logs for all actions, and minimal pixel data upload only with strict opt-in
- **missing:** Accurate, stable permissions for Accessibility and Screen Recording scoped to exact binary instance; Consent and controls for Vision upload from Mac screen; UI hierarchy snapshot context streaming with fine-grained access control; A layered action confirmation UI and undo system integrating multiple surfaces; A typed, observable action broker separating read-only, reversible, and high impact commands with user prompts; Integration between active agents for real-time feedback and intervention


## Changes it proposed to its own stack

### `hardware` — Add a dedicated hardware security module in the MacBook dedicated to managing Accessibility and Screen Recording permissions granularly and securely for AI agents, enabling per-binary permission granting and revocation without system restart.
- **owner gets:** This would make enabling AI control loops safe and instantaneous without reboots or broad permission grants, improving usability and security for the owner.
- effort: High engineering on macOS hardware and OS security layers.  ·  risk: Complex integration risks and potential for permission mismanagement, mitigated by strict cryptographic design and logging.
- cost: Moderate hardware cost increase, minimal power draw increase.  ·  latency: None on user experience, lower latency for permission change propagation.
- security: High-security improvement by minimizing attack surface of overly broad permissions.

### `model-routing` — Introduce a model routing layer that dynamically assigns real-time UI understanding and control tasks to the mac-vision agent while offloading heavier long-term planning and multi-step ambiguity resolution to mac-planner and mac-delegate agents.
- **owner gets:** This optimizes responsiveness and efficiency of Mac control, making immediate UI decisions low-latency and more reliable, while complex workflows get robust planning and error recovery.
- effort: Medium effort integration between agents and model orchestration backend.  ·  risk: Routing errors could cause delayed or incorrect behavior, mitigated by fallback and diagnostics.
- cost: Slight increase in cloud compute for routing logic.  ·  latency: Reduces latency on real-time UI actions, improving owner experience.
- security: Requires secure communication and identity verification between agents.
- depends on: computerUse loop permissions

### `integration` — Integrate mac-vision, mac-planner, browser-extension, and relay-realtime with a shared ephemeral memory and action log that records all UI and system actions with undo capability and transparency for the owner.
- **owner gets:** Owner gains confidence, control and audit trail over all autonomous Mac and browser actions, enabling recovery from mistakes and trust for autonomous operation.
- effort: Medium, requiring sync protocol and UI development across all surfaces.  ·  risk: Data integrity risks mitigated by cryptographic logs; complexity in syncing state across devices.
- cost: Increased storage and bandwidth usage for logs.  ·  latency: Minimal, mostly background syncing.
- security: Sensitive logs, must encrypt and limit access.
- depends on: mac-vision real-time loop functionality; permissions

### `interaction` — Develop an owner-facing interaction dashboard on the pendant that shows current Mac automation state, pending actions, recent activity with undo options, and manual override controls for computerUse loop.
- **owner gets:** Gives the owner strict real-time visibility and partial control over what mac-vision is doing, increasing trust and allowing immediate halting or correction of undesired actions.
- effort: Medium UI/UX development effort on the pendant and integration with mac-vision agent.  ·  risk: Potential complexity for owner; must be designed for ease of use and non-disruptive interaction.
- cost: Minimal, mostly software.  ·  latency: Minimal impact.
- security: Needs secure authentication for owner interaction.
- depends on: mac-vision real-time loop functionality; integration of action log

### `memory` — Implement context-aware UI state memory for mac-vision to remember user preferences, app states, and recent commands across sessions securely and contextually.
- **owner gets:** Enables smoother continuous interactions without repeated instructions, improving fluency and reducing errors in UI navigation and control.
- effort: Medium engineering with secure storage and context management subsystem.  ·  risk: Privacy risks if memory leaks; mitigated by encryption and strict access control.
- cost: Increased local storage and some cloud sync required.  ·  latency: Minor increase in cycle time.
- security: Sensitive data storage demands high security discipline.
- depends on: mac-vision real-time loop functionality

### `routines` — Create scheduled health checks and maintenance routines for mac-vision’s computerUse loop including permission sanity checks, log pruning, and performance optimizations.
- **owner gets:** Ensures continuous reliability, optimal performance, and security of the AI control loop on the Mac, reducing risk of failure or degraded experience over time.
- effort: Low to medium, mostly engineering scripts and monitoring tools.  ·  risk: Very low, mostly operational.
- cost: Minimal.  ·  latency: None for user experience.
- security: Improves system stability and security posture.
- depends on: mac-vision real-time loop functionality

### `dashboard-ux` — Design a visual workflow editor on the Mac dashboard that allows the owner to visually compose, test, and debug mac-vision's UI automation scripts with drag-and-drop and branching logic.
- **owner gets:** Gives the owner direct empowerment to customize and control their Mac automation without writing code, making powerful automation accessible and transparent.
- effort: High UI/UX and backend engineering combining live UI observation, scripting, and simulation.  ·  risk: Complexity risk mitigated by iterative design and user testing.
- cost: Moderate cloud and local compute for simulation and script runtime.  ·  latency: No impact on runtime latency, mostly authoring tool latency.
- security: Needs secure sandboxing of scripts and controlled execution.
- depends on: mac-vision real-time loop functionality; integration with mac-vision memory and action logs


## What it asked for

_Nothing._
