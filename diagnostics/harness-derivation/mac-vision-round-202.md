# Harness derivation — mac-vision — round 202

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to read and act on the owner's live priority task list on the Mac, combining memory facts of kind 'task' and the dayPlan reminders to provide a ranked, current backlog of what the owner wants done on the Mac."
- **useful because:** The current mac-vision agent has no stored queue of owner work, only fragmented priorities in memory and reminders. A live, ranked priority list allows mac-vision to autonomously pick meaningful next tasks to act on, improving usefulness significantly.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** 1 second to read and rank tasks
- **cost:** Low API usage; mostly local model cost
- **security:** Privacy of owner priority tasks and reminders; read-only for the agent
- **missing:** A joined API or view for kind:'task' facts with dayPlan reminders as a single ranked list

### "Enable mac-vision and other Mac surfaces to verify actual on-screen UI state against claimed UI state during multi-step workflows, by reading UI accessibility trees and matching them to the workbench context claim to detect divergence or failure in real time."
- **useful because:** This would improve workflow reliability, trust, and recoverability by detecting when something the system thinks happened on the Mac UI did not actually complete or changed unexpectedly, enabling live intervention or restart.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** <1 second per UI read
- **cost:** Low API and model cost, mostly local UI tree processing
- **security:** Detailed UI state read; sensitive content in UI may be seen; requires careful handling and owner consent
- **missing:** No existing API to compare claimed UI state from workbench contexts to real accessibility tree state on the Mac

### "Implement an improved undo and recovery capability for mac-vision by integrating mac_run_actions and mac_delegate with the Mac jobs and receipts system, allowing undo of UI actions and recovery after failures."
- **useful because:** This capability would allow the mac-vision agent to revert UI changes it made during workflows, increasing trust and preventing mistakes from requiring manual intervention or restart.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** <2 seconds for undo operation
- **cost:** Moderate CPU and API usage for calculating undo and applying it
- **security:** Undo operations can potentially reveal or affect user data; should always require owner confirmation before irreversible steps.
- **missing:** Better linking between mac_run_actions/mac_delegate steps and Mac jobs receipts with status, exit codes, and environment context.; Operations to automate undo based on receipts

### "Provide mac-vision with direct typed semantic access to selected text and document identity under the macOS Accessibility model for better contextual understanding and interaction within applications."
- **useful because:** Currently mac-vision can only read UI accessibility trees without typed semantic info about selections or document IDs, limiting its ability to precisely interact or automate complex text/document workflows.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** <1 second per read
- **cost:** Low API cost
- **security:** Accessing document identity and selected text may reveal private or sensitive contents; requires careful permission handling and owner consent.
- **missing:** Typed semantic selected-text and document identity read capability from macOS Accessibility APIs or equivalent.

### "Allow mac-vision to build and maintain an autonomous dynamic prioritized task and goal backlog by synthesizing and inferring from all memory kinds (task, entity, preference) plus scheduled routines and live system signals, rather than relying only on user-typed 'task' facts or read-through reminders. This backlog would evolve with owner interaction and autonomous discovery of intent."
- **useful because:** The current state has no comprehensive or dynamic backlog representing what the owner wants done. Enabling autonomous synthesis would make mac-vision proactive and more contextually aware of owner priorities without manual backlog feeding.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** 1-2 seconds to synthesize and update backlog
- **cost:** Moderate model cost to synthesize and infer across memory kinds and routines
- **security:** Deep inference across private owner data with privacy and trust implications.
- **missing:** A comprehensive memory synthesis engine that fuses multiple memory kinds and routines into a dynamic, actionable backlog.


## Changes it proposed to its own stack

### `integration` — Implement a new integration layer that automatically cross-checks multi-step mac_delegate workflow plans against live accessibility UI snapshots read by mac-vision to verify actual UI state vs claimed workflow state, enabling real-time failure detection, retries, and recovery.
- **owner gets:** This would dramatically improve reliability, trust, and seamlessness of complex automated UI workflows on the Mac by ensuring what the agent expects on screen matches reality.
- effort: High, involves coordination between mac_delegate, mac-vision, and workbench contexts, plus building accessibility UI snapshot diffing and alerting.  ·  risk: Incorrect state detection may cause unnecessary retries or confusion; must have safe fallback and manual override.
- cost: Moderate CPU and API cost from accessibility snapshot comparisons and checks each workflow step.  ·  latency: Adds minimal latency if done asynchronously or in parallel with step execution.
- security: Requires continued careful access to sensitive UI state under strong owner consent controls.
- depends on: vision-loop accessibility APIs; GET /workbench/contexts/:contextId


## What it asked for

_Nothing._
