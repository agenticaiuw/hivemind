# Harness derivation — mac-vision — round 235

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a fully autonomous Mac UI assistant that uses accessibility tree data to perform complex multi-step tasks with live verification of UI state and smart error recovery."
- **useful because:** This would allow the owner to delegate difficult or repetitive Mac workflows that currently require manual intervention or APIs that don't exist, saving time and reducing frustration. The real-time accessibility data enables safe and reliable control beyond static commands.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds for each interaction
- **cost:** moderate due to complex multi-step planning and accessibility data processing
- **security:** Requires broad accessibility permission and strict policy enforcement on destructive actions to protect privacy and prevent accidents.
- **missing:** vision-loop accessibility tree routes fully implemented and integrated; robust UI state verification and diffing features; structured multi-step plan orchestration on Mac; owner policy and preference interface for UI automation control

### "Have a prioritized, persistent task and goal management system integrated with the Mac agent that the owner can update and the Mac vision loop can act on reliably."
- **useful because:** Currently the owner has no durable prioritized task list for mac-vision or other Mac agents to use. This capability would enable the AI to focus efforts on what matters most to the owner, driving meaningful progress on their goals.
- **path:** mac-planner → mac-vision → faculty-judgement
- **model tier:** gpt-5.6-luna
- **latency:** interactive, under a second for reading and planning
- **cost:** low to moderate depending on persistence and ranking complexity
- **security:** Needs clear owner controls for adding and removing tasks, privacy controls on task content, and granular access policies.
- **missing:** durable memory store for prioritized tasks linked to owner intents; task ranking and prioritization algorithms informed by context and owner preferences; UI integration for task management in the Mac agent

### "Have a comprehensive multi-surface policy and preference system that informs AI agents including mac-vision when to act autonomously, when to ask for confirmation, and how to communicate with the owner."
- **useful because:** This would ensure consistent, safe, and user-aligned AI behavior across all devices and contexts, improving trust and usability while avoiding unwanted actions or privacy violations.
- **path:** faculty-judgement → mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** sub-second
- **cost:** low
- **security:** Must be transparent and editable by the owner, with strict auditing and rollback capabilities.
- **missing:** centralized policy store accessible by all relevant agents; real-time policy enforcement hooks in interactive and autonomous modes; user interface for owner to review and adjust policies

### "Enable live verification of UI state changes after mac-vision executes a step, to ensure that recorded workflow progress matches actual on-screen state with rollback support on failure."
- **useful because:** Currently there is no mechanism to confirm that a UI action succeeded as intended, risking silent failures and inconsistent internal state. This verification increases reliability and user trust in automated Mac control.
- **path:** mac-vision → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds for post-action checks
- **cost:** moderate due to UI diff processing and storage
- **security:** Requires access to live UI state and logs; must enforce privacy and integrity of verification results.
- **missing:** real-time UI diff and verification tools; rollback-capable UI action orchestration systems; logging and audit trails for UI changes

### "Enable the mac-vision loop to operate with dynamic UI discovery and controllable action sequencing without resorting to pixel-based screenshots, using only accessibility tree data and state diffs."
- **useful because:** This removes privacy and reliability concerns related to pixel screenshots, uses efficient accessibility data for UI control, and allows flexible, recoverable, and verifiable UI workflow automation.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to several seconds per control cycle
- **cost:** low to moderate depending on loop complexity
- **security:** Requires strict access controls to accessibility data and UI control APIs to prevent unauthorized use or leaks.
- **missing:** full accessibility tree read/write cycle implementation for mac-vision loop; reliable UI state diffing and recovery mechanisms; policy guards for loop activation and interruption


## Changes it proposed to its own stack

### `integration` — Integrate the mac-vision agent with the memory system to consume a prioritized and curated task list representing the owner's active intent, and automatically update this list based on progress feedback from UI state verification.
- **owner gets:** This creates a feedback loop where mac-vision works on meaningful owner-defined tasks and updates their status automatically, reducing owner micromanagement and increasing trust in autonomous Mac actions.
- effort: Medium engineering effort to implement integration points and adapt memory and UI feedback systems to interact.  ·  risk: Potential data mismatches or stale state leading to incorrect task progress updates; mitigatable by rollback and owner override options.
- cost: Low; mostly server-side compute and storage costs.  ·  latency: Minimal; runs asynchronously on task update.
- security: Requires secure authentication and authorization for task and UI state access to prevent leaks or misuse.
- depends on: prioritized task management capability; UI state verification and reconciliation capability

### `interaction` — Develop a natural language interface on the mac-vision agent that can summarize the current active tasks and progress from memory and UI state, and allow the owner to query, reprioritize, or defer tasks dynamically via voice commands.
- **owner gets:** This would make task management interactive and intuitive, allowing the owner to control AI-driven workflow without explicit app interfaces or menus, directly communicating with mac-vision.
- effort: Medium to high NLP integration effort coupled with UI state and memory coordination.  ·  risk: Complex natural language edge cases may cause misunderstanding; mitigable by confirmation dialog or fallback.
- cost: Moderate due to ongoing NLP processing.  ·  latency: Interactive, low-latency response expected.
- security: Requires strict safeguard to avoid unintended task changes; privacy concerns handled by local device prominence.
- depends on: prioritized task management capability; memory integration; UI state verification


## What it asked for

_Nothing._
