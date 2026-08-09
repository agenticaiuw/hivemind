# Harness derivation — mac-vision — round 265

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have mac-vision run a fully autonomous accessibility-driven computer-use loop on the Mac that can safely and reversibly perform complex multi-step UI interactions, adapting dynamically to UI changes and errors."
- **useful because:** The owner can delegate more complex Mac automation tasks to AI that uses the accessibility API directly, without brittle scripting or crash-prone pixel clicks. It unlocks real intelligent UI navigation for tasks APIs cannot reach.
- **path:** mac-local-agent
- **model tier:** gpt-4.1-mini
- **latency:** seconds or less for UI navigation steps
- **cost:** moderate API calls per step; cost dominated by UI state parsing and generation
- **security:** Must have fine-grained consent controls, safe defaults, and reversible step tracking. Avoid focus theft and destructive side effects without explicit confirmation.
- **missing:** Explicit user intent gating and consent UI. Full undo and step verification for complex UI sequences. Robust error handling and fallbacks for dynamic UI.; Integration with workbench contexts for ongoing multitask awareness.

### "A dynamic prioritized task list integrated into the Mac agent for mac-vision to read and act on, fed by rich contextual signals and owner inputs, with deadlines, priorities and dependencies."
- **useful because:** Currently no task list for mac-vision exists; without a granular prioritized queue the loop cannot focus on the owner's current goals effectively. A live task list allows focused, context-sensitive automation and smarter delegation across agents.
- **path:** mac-local-agent
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds for task list queries
- **cost:** Low API cost; mostly read cache and memory projection loads
- **security:** Task list ownership and modification must secure against accidental or unauthorized changes. Owner must control creation and deletion fully.
- **missing:** Task indexing, ranking, and dependency tracking logic. UI for owner to add and manage tasks with gating for agent automation trust.; Integration with existing memoryService fact and routines stores for task persistence.

### "A verified and visible UI state snapshot service that records the claimed UI state versus actual on-screen state on the Mac for multi-step workflows, enabling mac-vision and other agents to detect UI changes, failures, and intermittent glitches in automation."
- **useful because:** Automation reliability improves drastically with evidence of actual vs expected UI state to diagnose and recover from failures, restart interrupted tasks with accuracy, and provide better progress reports to the owner.
- **path:** mac-local-agent
- **model tier:** gpt-4.1-mini
- **latency:** seconds to retrieve and compare snapshots
- **cost:** Moderate; due to storage and comparison of UI accessibility trees and snapshots per workflow step.
- **security:** Snapshot data may include sensitive UI info hence must be encrypted and access controlled. Only authorized agents can query.
- **missing:** Persistent state storage for UI snapshots indexed by workflow context and step.; Verification logic comparing claimed versus actual UI component attributes.; Integration with workbench/contexts and jobs for workflow management.

### "An integrated Mac agent policy and consent management system that governs when and how mac-vision's computer-use loop is allowed to run, specifying consent levels, gating conditions, and owner-configurable guardrails for safe automation."
- **useful because:** This will protect the owner from unwanted or accidental UI automation that could interfere with ongoing work or privacy. It gives the owner clear controls and transparency over what mac-vision can do on their Mac.
- **path:** mac-local-agent → pendant
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds for policy checks
- **cost:** Low API cost; mostly config data reads and updates
- **security:** Must securely enforce policy to prevent bypass. Consent UI must be user-friendly but unspoofable.
- **missing:** Policy schema defining automation permission levels, allowed action types, and contexts.; User interfaces and workflows for owner to grant, revoke, and audit consent and automation events.; Integration with mac-vision's loop to check policy before each action or batch of actions.


## Changes it proposed to its own stack

### `hardware` — Upgrade the pendant with a second physical button distinct from the conversation-start button to enable nuanced physical interactions as discrete triggers for the mac-vision loop and other selective agent commands.
- **owner gets:** Currently there is only a single button that is heavily constrained since a gesture recognizer on it is infeasible. A dedicated second button allows reliable, non-conflicting physical input to trigger agent workflows and interactions.
- effort: Moderate hardware redesign and firmware update to support the new button.  ·  risk: Hardware design and manufacturing complexity increase slightly; firmware changes may introduce bugs but can be tested thoroughly.
- cost: Additional BOM cost for button is minor compared to the device cost. Power impact negligible due to edge-triggered input.  ·  latency: No impact on latency; physical button press detection is immediate.
- security: Additional physical security needed to prevent accidental presses; firmware must gate input sensibly.


## What it asked for

_Nothing._
## Its own summary

Recorded major proposals for mac-vision: a fully autonomous accessibility-driven UI loop, a dynamic prioritized task list, a second pendant button, verified UI state snapshot for automation robustness, and a comprehensive policy/consent management system.

**Biggest unknown:** How to design the user consent and gating model for safe, preferred mac-vision loop activation and task prioritization integration exactly, including owner trust and privacy concerns.

