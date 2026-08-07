# Harness derivation — mac-vision — round 22

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "I want my Mac vision agent to operate safely and productively to assist with complex UI tasks on my Mac."
- **useful because:** The owner cannot currently have real-time, vision-assisted Mac UI control that combines pixel understanding and accessibility insights to execute precise UI interactions or escalate complex workflows. This limits usefulness to status reads or very simple actions only.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** sub-second response to allow fluid interactive user experience
- **cost:** moderate API usage for vision and action routing, moderate compute on Mac for UI snapshot and action planning
- **security:** requires explicit owner consent for pixel and UI data capture, sandboxed local processing to prevent data leakage, strict confirmation for destructive or high-impact actions
- **missing:** continuous or on-demand UI hierarchy snapshot from Mac accessibility API without disrupting user; policy and UI for owner consent and gating; safe pixel screenshot capture on Mac with consent and privacy safeguards; integration between vision pixels and accessibility info for precise interaction; low-latency action loop with fail-safes and undo

### "I want the Mac vision agent to autonomously detect and highlight UI elements with errors or that require user intervention during workflows, then notify me via the pendant."
- **useful because:** Currently, the owner has no way to be alerted proactively about UI-level problems that the Mac vision agent sees, which can interrupt or block task progress. This capability would improve error recovery and reduce owner burden.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** seconds to alert while task is ongoing
- **cost:** Moderate usage for UI analysis and notification
- **security:** Requires UI analysis data sharing with relay and pendant, protected by encryption and consent.
- **missing:** UI error detection and classification models integrated with mac-vision; notification channel integration with pendant and relay; user notification and acknowledgement interaction design


## Changes it proposed to its own stack

### `hardware` — Add a dedicated high-efficiency camera sensor integrated with the Mac, optimized for capturing screen pixel data and ambient context without interfering with user activity or privacy, paired with a hardware-accelerated vision module for fast preprocessing.
- **owner gets:** Allows persistent real-time vision of the Mac screen environment without impacting user experience or performance, enabling better UI analysis and interaction.
- effort: Significant hardware design and firmware integration.  ·  risk: Hardware cost increase, potential privacy concerns needing clear user control and transparency.
- cost: Hardware component cost moderate, low power draw due to dedicated sensor.  ·  latency: Low latency vision data stream enabling real-time AI processing.
- security: Requires strict privacy design, local processing only, no external transmission without explicit consent.
- depends on: firmware changes for data capture; mac-vision software to consume and process vision data

### `firmware` — Implement on-device real-time accessibility UI hierarchy extraction and continuous snapshot capabilities on Mac system firmware or accessibility services, exposing these to authorized AI agents via a secure, low-latency API.
- **owner gets:** Enables AI agents like mac-vision to obtain up-to-date UI structure and element metadata without disrupting user workflows, improving decision accuracy and automated computer control.
- effort: Moderate firmware and accessibility service development, strong security design.  ·  risk: Potential risk of unauthorized UI data exposure, mitigated by strict authorization, auditing, and sandboxing.
- cost: Moderate compute and memory usage on device.  ·  latency: Low latency UI data availability for real-time AI decisions.
- security: Critical to have robust security gating and audit trails.
- depends on: mac-vision and mac-planner software updates to consume API

### `mac-harness` — Create a typed action broker for the Mac agent that intermediates all computer control actions. This broker should classify actions by safety and impact, coordinate user confirmation for high-impact or destructive commands, and provide a unified interface for mac_run_actions and mac_delegate.
- **owner gets:** Improves safety, transparency, and recoverability of computer control actions initiated by mac-vision and other agents, preventing accidental destructive commands and enabling granular user control.
- effort: Moderate software development for the broker layer and integration with existing action providers.  ·  risk: Increased latency if not optimized; risk of denial of critical actions if confirmations are mishandled.
- cost: Minimal additional compute cost, mostly development effort.  ·  latency: Very low if optimized properly.
- security: Improves security and owner control over automated computer actions.
- depends on: mac-vision, mac-planner integration to use typed actions; pendant UI for confirmations

### `interaction` — Develop a multi-modal interaction method combining pendant voice commands with visual context from mac-vision to allow the owner to give nuanced, natural-language instructions that leverage current UI state and accessible elements for more efficient task delegation.
- **owner gets:** Allows the owner to communicate complex goals and corrections naturally and efficiently, improving the practicality of AI-assisted Mac use and reducing misunderstandings or errors.
- effort: Moderate software development on interaction design, natural language understanding, and UI context integration.  ·  risk: Potential user frustration if misinterpretations occur; mitigated by fallback and confirmation strategies.
- cost: Moderate compute and engineering cost.  ·  latency: Sub-second to a few seconds response time acceptable.
- security: Maintains privacy as commands are via local voice processing and AI context is contained in the system.
- depends on: mac-vision active with UI context; pendant voice interface; mac-planner for task interpretation

### `context` — Construct a shared, persistent context graph that integrates UI state, recent actions, user goals, and multi-agent intents across mac-vision, mac-planner, relay-realtime, and the pendant, accessible by all nodes for synchronized decision making.
- **owner gets:** Ensures all parts of the AI hive mind maintain a coherent understanding of the current state, pending goals, and history to coordinate actions smoothly and prevent conflicting or redundant work.
- effort: High software engineering effort to design, implement and synchronize context graph across heterogeneous agents.  ·  risk: Complexity risks introducing bugs or state inconsistencies; must have robust conflict resolution and recovery.
- cost: Moderate to high backend and client-side compute and storage overhead.  ·  latency: Low latency updates needed to keep realtime workflows smooth.
- security: Sensitive data requires strong access controls and audit mechanisms.
- depends on: network link reliability; all agents updated to use context graph

### `memory` — Enable a short-term visual memory buffer on the pendant or relay that stores recent Mac screen snapshots and UI state for rapid review and rollback by the AI hive mind, allowing quicker recovery from errors or misunderstandings.
- **owner gets:** Provides fail-safe rollback and context refinement capabilities, allowing the AI to correct mistakes or rethink action plans based on recent visual history without re-querying the Mac directly.
- effort: Moderate development effort for memory buffer management and synchronization.  ·  risk: Storage and privacy management required to avoid data leaks and ensure controlled access.
- cost: Modest storage and compute cost, mostly on pendant or relay hardware.  ·  latency: Improves apparent AI responsiveness by avoiding repeated context captures.
- security: Requires encryption and access control for stored visual data.
- depends on: pendant or relay hardware with sufficient storage; mac-vision and relay integration to store and use memory


## What it asked for

_Nothing._
