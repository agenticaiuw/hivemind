# Harness derivation — mac-vision — round 209

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision agent to convert the owner's priority tasks and daily routines into active workflows on the Mac using proactive UI actions and scripting."
- **useful because:** This capability will let the agent proactively start meaningful computer work for the owner based on what they currently want done and their scheduled routines, improving productivity and automation.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** moderate, mostly model usage for reasoning and plan synthesis
- **security:** works within granted permissions but could affect state; destructive actions require confirmation
- **missing:** better integration of UI state tracking and feedback from mac-vision to orchestration layers

### "Provide short spoken updates from mac-vision workflow progress and confirm transitions or completions with a single short sentence by default, respecting owner preferences."
- **useful because:** Owners prefer concise spoken replies; this capability ensures clear, timely voice feedback about what the agent is doing on the Mac with minimal distraction.
- **path:** mac-vision → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** seconds
- **cost:** low to moderate, mostly model inference
- **security:** voice output is low risk, content generated locally
- **missing:** 

### "A continuous, real-time Mac UI change detector that can capture, diff, and report accessibility tree differences step-by-step for mac-vision workflows, enabling precise verification of any UI interaction or workflow step execution."
- **useful because:** Currently, mac-vision cannot reliably verify if UI actions have genuinely succeeded or if UI state changes as expected. A real-time UI diffing capability would allow exact confirmation or error detection, improving reliability and trust in automation.
- **path:** mac-vision
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to seconds
- **cost:** moderate CPU and memory for storing/accessing UI states and calculating diffs
- **security:** Only accessibility tree data, no pixel or personal content beyond UI hierarchy is captured. Access is local only for privacy and security.
- **missing:** A dedicated service or native agent module to listen continuously to macOS accessibility notifications and produce incremental UI tree snapshots and diffs.

### "A proactive Mac-vision error recovery mechanism that uses heuristics from continuous UI state monitoring to auto-correct or retry failed steps in workflows without forcing owner intervention."
- **useful because:** Workflows can silently fail due to transient UI state changes or focus issues. Automated detection and recovery would reduce friction, maintain progress automatically, and improve trust and usability of the Mac automation system.
- **path:** mac-vision → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds to minutes
- **cost:** moderate, involves complex state analysis and action retries
- **security:** Requires deep understanding of UI state and action history but remains local and limited to accessibility info.
- **missing:** Reliable UI state diffing and history keeps needed to detect deviations and recovery opportunities.


## Changes it proposed to its own stack

### `integration` — Add an integrated Mac task and routine coordinator that aggregates owner priority facts, schedules, and system utilities into a real-time actionable work queue for mac-vision to execute with failover to multi-step delegation.
- **owner gets:** This would unblock the agent from acting autonomously on owner intent and schedules, providing a single source of truth for tasks ready to be worked on at any moment, significantly improving productivity and automation.
- effort: medium to high, requires coding new coordination layers, adapters for existing stores, and decision logic for task activation and failover.  ·  risk: medium risk of task conflicts or poor prioritization initially; recoverable by manual overrides and tuning.
- cost: low to moderate, mostly compute and storage overhead for maintaining queues and decision logic.  ·  latency: low, real-time or near-real-time response expected.
- security: low, runs within existing permission boundaries.
- depends on: memory/facts; routines; day-plan; mac_run_actions; mac_delegate

### `hardware` — Add a low-latency dedicated hardware interrupt line or subsystem to the pendant that can trigger passive UI state captures or bookmark moments instantly on the Mac side without requiring active polling or audible user input.
- **owner gets:** This would enable more timely, precise moment captures and context bookmarks for workflows and error states on the Mac, driven by the owner's gesture or system events, improving responsiveness and interaction fidelity without draining power or adding latency in voice paths.
- effort: high - requires hardware design, firmware, and Mac-side integration.  ·  risk: medium - new hardware/firmware bugs and integration complexity.
- cost: moderate component and development cost, marginal power increase.  ·  latency: very low latency
- security: low as it remains local and controlled.


## What it asked for

_Nothing._
