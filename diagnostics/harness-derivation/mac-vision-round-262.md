# Harness derivation — mac-vision — round 262

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "A prioritized, dynamically updated, owner-validated 'Mac Work Queue' that lists tasks the owner wants done on the Mac with metadata such as deadlines, dependencies, and progress."
- **useful because:** Currently there is no durable, structured list of what the owner expects mac-vision or other agents to act on at the OS UI level, leaving automation unguided and reactive rather than proactive.
- **path:** mac-local-agent → relay → dashboard
- **model tier:** gpt-5.6-luna
- **latency:** minutes (for re-ranking and integration)
- **cost:** medium - involves persistent storage, complex ranking, and UI coordination
- **security:** Tasks must be owner-authored or owner-approved; no agent fabrications allowed. Privacy and data protection critical for ownership of intent.
- **missing:** UI to input, manage and approve Mac tasks; Integration with reminders, calendar, and quick capture for task import; Ranking heuristics that combine owner priority, deadlines, and context; Event-based triggers to update and surface the list dynamically

### "A combined UI state and execution receipts reconciliation tool on mac-vision that can report exactly what steps in a multi-step workflow landed on the UI and which did not, to enable reliable resume, retry, or recovery."
- **useful because:** This would eliminate blind spots in complex UI workflows where the system believes it acted but the UI is out of sync due to focus loss, timing race, or unexpected modal dialogs, greatly improving reliability and owner trust.
- **path:** mac-local-agent → relay
- **model tier:** gpt-4.1-mini
- **latency:** seconds to minutes depending on recovery complexity
- **cost:** low micro-cost, dominated by local UI tree read
- **security:** Requires secure logging and restricted access to UI state and execution logs to prevent sensitive information leakage.
- **missing:** API to fetch UI snapshots aligned with execution receipts; Mechanism to diff UI state versus intended step completions; Policy for automatic retry or owner confirmation when discrepancies arise


## What it asked for

### `c28-wt89` (context) — mac-vision capabilities and best full use cases
- why: To understand how to safely and effectively turn on and use the mac-vision computer-use loop agent for UI automation on the Mac.
- would change: I could design precise computer-use loop interactions, avoid pitfalls, and propose meaningful improvements.

### `c29-4wjt` (context) — mac-vision ui snapshot and workbench contexts
- why: To see the current live accessibility tree UI snapshot and open workbench contexts on the Mac surface to know what UI elements can be controlled and what multi-step work is underway.
- would change: I can plan valid UI interactions, verify current UI context, and avoid redundant actions.

### `c30-p1zi` (context) — mac-vision agent current task list
- why: To get the owner's stated current high-priority Mac tasks and preferences to prioritize and focus Mac UI automation on what matters most to the owner right now.
- would change: This lets me prioritize work and not waste energy on irrelevant tasks.

### `c31-ab4w` (context) — workbench contexts
- why: To understand open pieces of multi-step work being tracked and their progress on the Mac--essential for handing off and resuming workflows reliably.
- would change: I can align my UI actions with current work status, reduce redundant or conflicting actions, and improve collaboration with other agents.

