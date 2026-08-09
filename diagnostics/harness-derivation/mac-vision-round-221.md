# Harness derivation — mac-vision — round 221

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to fully control the Mac UI via an accessibility-driven plan and execute loop with visible action receipts and undo."
- **useful because:** The owner would gain a true AI-driven UI control interface on the Mac that safely reads and operates apps via accessibility APIs without needing screen pixels or brittle shortcuts. This enables complex workflows beyond API coverage, reducing friction and increasing control.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** seconds for planning and execution steps
- **cost:** moderate API calls per UI action, dominated by accessibility reads and control signals
- **security:** Requires trusted accessibility permissions, safe undo mechanisms to prevent harmful UI actions, and visible receipts for audit. Actions must avoid focus theft and silent mouse fallbacks.
- **missing:** A dedicated mac-vision route for planning UI actions from accessibility trees that is stable and real-time.; A robust execute endpoint on the Mac agent to run planned UI commands with failure detection and undo.; Cross-agent protocols to integrate mac-planner intent with mac-vision execution and confirmation.; Fine-grained accessibility tree streaming or browsing APIs without screen recording.

### "Expose a real-time accessible UI tree browsing and non-intrusive control API for mac-vision with fallback notifications on permission changes or degraded input events."
- **useful because:** This lets the owner or higher-level agents understand and navigate the live UI state more reliably than cached or pixel-based snapshots, improving safety and reliability in UI automation.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** hundreds of milliseconds per subtree retrieval or control query
- **cost:** low to moderate, mostly local system calls and cache management
- **security:** Must respect user permission and privacy; read-only access to controls unless explicitly granted interaction rights. Permission changes must immediately notify the agent.
- **missing:** Access to incremental or on-demand accessibility UI snapshots from the running Mac agent.; Hooks for detecting accessibility permission revocation or fallback to mouse events.; Non-intrusive UI control interfaces that avoid focus steal or window raise.

### "Enable mac-vision to update or augment the owner's prioritized task facts in memory based on live UI observations and workflow progress."
- **useful because:** Allows the owner's current tasks and priorities to be continuously refined and expanded from live work patterns on the Mac, making task management more dynamic and relevant.
- **path:** mac-vision → memoryService → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** Low per update but continuous
- **security:** Must ensure no unauthorized task creation or modification without owner consent.
- **missing:** Capability for mac-vision to write kind:task facts reliably.; Better contextual linking between live UI actions and memory task facts.; Safe update protocols to avoid task drift or noise.


## Changes it proposed to its own stack

### `integration` — Create a protocol and orchestration layer bridging mac-planner UI planning outputs with mac-vision execution inputs and the workbench context system for multi-step UI workflows.
- **owner gets:** This enables seamless, recoverable, and auditable multi-step UI task execution that combines higher-level planning with low-latency precise UI control, giving the owner powerful end-to-end Mac automation.
- effort: Moderate to high engineering across Mac local agents, UI planning, workbench context, and relay coordination layers.  ·  risk: Complex synchronization and error handling risks; must handle partial failures gracefully and ensure secure command handoff.
- cost: Increased CPU and API calls during planning and execution phases; mostly software cost.  ·  latency: Small latency added in coordination steps but negligible compared to action execution.
- security: Requires strict trust boundaries and confirmation gates for executing UI actions planned by other agents.
- depends on: Dedicated mac-vision plan and execute endpoints.; Reliable accessibility permission and action receipt systems.; Workbench context and job ledger infrastructure.

### `hardware` — Add a secure hardware gate or physical control interface on the pendant to approve or veto complex UI actions initiated by mac-vision before execution on the Mac.
- **owner gets:** Provides the owner with ultimate control and safety for powerful UI automation, preventing unintended destructive actions and ensuring trust in the AI driving their Mac.
- effort: Moderate hardware and firmware development plus integration with the agent trust model.  ·  risk: Hardware-firmware compatibility issues; risk of user disabling gate and losing security benefit.
- cost: Small incremental hardware cost.  ·  latency: Low added latency for UI action approval.
- security: Significant increase in security and user trust for automation.
- depends on: mac-vision UI execute capability with undo and receipts.; Owner interface on the pendant for interaction approval.


## What it asked for

_Nothing._
