# Harness derivation — mac-vision — round 149

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac_vision accessibility tree interaction to drive Mac UI without focus stealing or screenshot fallback."
- **useful because:** Allows mac_vision to transparently and safely control Mac applications using accessibility APIs, enabling complex multi-step local workflows and undo without disruptive UI effects.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 100ms to 500ms per UI step
- **cost:** Low API cost, mostly lightweight local operations
- **security:** Requires macOS Accessibility permission for the running binary and owner enabling computerUse.loopEnabled; must prevent accidental destructive actions.
- **missing:** Owner must grant macOS Accessibility to the AI Pendant Agent binary; Owner must enable computerUse.loopEnabled flag to unlock the loop

### "Provide a consolidated and prioritized owner current goals manager."
- **useful because:** Allows all agents, including mac-vision, to know what the owner currently wants done, with priorities, deadlines, and dependencies, allowing effective task execution and decision making.
- **path:** mac-planner → unified
- **model tier:** background
- **latency:** Seconds, no hard realtime needed
- **cost:** Moderate from context processing and storage
- **security:** Must respect owner privacy and limit sharing only to explicitly authorized agents.
- **missing:** A new data store or extended memory Service handling owner goals with priority metadata; Decision logic or ML model to rank and prioritize goals effectively

### "Integrate mac_vision accessibility-driven UI control with mac_run_actions and mac_delegate for seamless, safe Mac control workflows."
- **useful because:** Combines rich UI state from accessibility tree with concrete shell or application control actions to execute workflows, verify steps, and allow undo; prevents destructive mistakes while maximizing automation.
- **path:** mac-vision → mac-planner
- **model tier:** realtime
- **latency:** 100ms to 1s per composite UI/action step
- **cost:** Low API cost, moderate compute for local UI processing
- **security:** Requires layered control approval on destructive actions; full audit trail and undo tracking mandatory.
- **missing:** A coordination layer between mac_vision UI plan and action executors; Undo and action receipt system operational end to end

### "Provide a real-time visual feedback system for the owner that shows what mac-vision intends to do in the Mac UI before it acts, with explanations of each planned step."
- **useful because:** This would allow the owner to understand and intercept or modify mac-vision's UI automation plans in real time, increasing trust and reducing accidental or undesired actions.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** realtime
- **latency:** 200ms per update
- **cost:** Moderate, requires streaming UI plan and rendering components
- **security:** Exposes intended UI actions and screen element data only to the owner locally; must ensure no external leakage.
- **missing:** UI plan serialization and visualization components on desktop and pendant

### "Create a mac-vision offline mode that allows the pendant or Mac to perform local UI automation and decision making without network connection, relying solely on locally cached models and UI snapshots."
- **useful because:** This would improve reliability and privacy, letting the owner use the AI-powered Mac control features even when offline or with poor connectivity.
- **path:** mac-vision → pendant → mac-planner
- **model tier:** background
- **latency:** Seconds, no hard realtime needed
- **cost:** Higher local compute and storage cost to maintain local models and caches
- **security:** Sensitive UI and model data remain local; operation must handle version drift gracefully.
- **missing:** Local model caching and update synchronization logic; Offline-capable UI observation and reasoning components


## Changes it proposed to its own stack

### `firmware` — Add a dedicated second hardware button on the pendant that can be assigned to confirm or cancel complex or destructive mac-vision UI automation actions, decoupling physical intent confirmation from existing single-button limitations.
- **owner gets:** Allows safe and unambiguous physical confirmation of high-impact actions, improving trust and preventing accidental destructive commands.
- effort: Medium hardware design and firmware update effort.  ·  risk: Requires hardware and firmware review to avoid accidental double assignment; can fallback to current single-button usage.
- cost: Small additional component cost and minimal power draw increase.  ·  latency: Negligible.
- security: Physical button press is inherently secure; reduces the chance of unintended permission escalation.

### `dashboard-ux` — Create a dedicated interactive dashboard on the owner's Mac that visualizes all current agent activities, mac-vision UI plans, pending tasks, and scheduled routines with real-time status and ability to override or pause actions.
- **owner gets:** Allows the owner to maintain complete situational awareness of the autonomous AI system's operations, increasing trust and control.
- effort: Moderate UI/UX development effort plus backend integration.  ·  risk: Complex UI could overwhelm the owner if not designed carefully; must guard against exposing sensitive data externally.
- cost: Moderate from frontend and backend compute for live updates.  ·  latency: Latency depends on update frequency; generally low impact.
- security: Dashboard operates locally on owner's Mac and enforces strict access control.
- depends on: mac_vision accessibility loop; routine scheduling


## What it asked for

_Nothing._
