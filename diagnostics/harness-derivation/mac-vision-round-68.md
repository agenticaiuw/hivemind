# Harness derivation — mac-vision — round 68

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable safe, owner-consented Mac vision loop for UI interaction and control"
- **useful because:** The owner would gain powerful hands-free and context-aware control of their Mac through vision-based UI interaction, greatly extending the AI capabilities beyond scripted or API-bound tasks. It would automate complex, multi-app workflows with real-time visual understanding and feedback.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini
- **latency:** low latency for real-time UI feedback and interaction
- **cost:** moderate API cost dominated by real-time vision model inference and verification steps
- **security:** Requires explicit owner consent for screen recording and accessibility permissions, including unsafe mutating action gating and logging to prevent unwanted or risky automation. Vision data should be processed locally or encrypted in transit.
- **missing:** Owner-consent workflow for screen recording and accessibility permissions; Vision loop gating for mutating actions (approval UI or voice confirmation); Integration of accessibility snapshots with vision model to minimize raw pixel use; Error recovery and undo mechanisms for vision-driven automation; Legal and privacy safeguards for screen vision data


## Changes it proposed to its own stack

### `integration` — Build a comprehensive owner-consent and action gating framework for the Mac vision loop that interposes on mac_run_actions and mac_delegate. This framework must require explicit owner approval for any mutating action proposed by the vision loop, provide an undo stack, and log all actions with detailed context from vision analysis. It must integrate tightly with the pendant relay to surface confirmations and summary feedback to the owner. This is essential for safety and trust before vision loop activation is enabled.
- **owner gets:** The owner gains safe, auditable, and controllable visual UI interaction on the Mac without accidental or unsafe automation. Intent is confirmed before state changes, minimizing risk.
- effort: Medium to large engineering effort including UI, backend coordination, and policy design.  ·  risk: If malformed, owners might be exposed to unsafe automation or get spurious confirmation prompts. Needs thorough testing and rollback.
- cost: Moderate API interaction overhead due to confirmation flow and tracking.  ·  latency: Slight delay introduced by confirmation flow but acceptable for safety.
- security: Improves security by preventing unauthorized or mistaken mutating vision actions.
- depends on: vision upload consent; accessibility permissions enabled; fullControlMode on computerUse

### `context` — Create a specialized UI semantic context extractor that translates raw accessibility API trees and vision model outputs into a unified, structured description of visible UI elements and their properties, states, and relationships in real time. This context feeds into all vision and action layers, improving decision-making precision and reducing the need for pixel data.
- **owner gets:** Provides the AI with a rich, interactive UI model that can drive vision-guided and accessibility-driven Mac control more reliably and with less data overhead, leading to better automation, fewer errors, and improved trustworthiness.
- effort: Medium engineering effort integrating accessibility APIs, vision models, and context graph components.  ·  risk: Extraction errors could lead to incorrect automation steps. Requires ongoing refinement and validation.
- cost: Moderate computational resources needed for real-time semantic extraction and data fusion.  ·  latency: Small acceptable latency tradeoff for richer context.
- security: No sensitive data exposure beyond existing accessibility and vision permissions.
- depends on: accessibility permissions enabled; vision model availability

### `interaction` — Implement a multi-modal interaction gateway on the pendant that combines voice, tactile buttons, and visual feedback to the owner for real-time control, confirmation, and cancellation of Mac vision loop actions. This gateway must seamlessly coordinate with the Mac planner and faculty-action for smooth operation.
- **owner gets:** The owner gains an intuitive and flexible control interface to oversee and interact with the Mac vision loop in real time, increasing usability, reducing accidental actions, and enabling quick interruption or modification of AI-driven UI tasks.
- effort: Medium engineering effort spanning pendant firmware, relay coordination, and Mac AI agent integration.  ·  risk: Complexity in multi-modal syncing and timing might lead to confusing states if not carefully designed.
- cost: Minimal increase in runtime resource usage on pendant and relay.  ·  latency: Negligible added delay; designed for responsiveness.
- security: Improves operational security by requiring explicit owner interaction for critical actions.
- depends on: pendant hardware control buttons; relay infrastructure


## What it asked for

_Nothing._
