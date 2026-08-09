# Harness derivation — mac-vision — round 181

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable true visual accessibility-driven control of Mac apps with multi-step task execution via accessibility API, allowing deep UI automation without screen recording or pixel interference."
- **useful because:** The owner currently cannot enable the computerUseLoop due to lack of macOS Accessibility permission for the running binary, limiting the system's ability to autonomously interact with Mac apps via their UI in a low-interference manner. Enabling this would unlock seamless and safe autonomous control of complex workflows on the Mac.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-4o-mini
- **latency:** 5s
- **cost:** low to moderate per invocation, dominated by local accessibility tree reads and planning.
- **security:** Requires a macOS Accessibility permission grant to the running agent binary by the owner. The agent must report lack of permission gracefully and never fallback to pixel-based interaction without consent.
- **missing:** macOS Accessibility grant for the running binary; computerUse.loopEnabled set to true by the owner; visionUploadConsented granted by the owner

### "Integrate the physical pendant button press state with the Mac agent to trigger complex Mac workflows or data capture moments, using multi-payload records on the existing timestamp marker rather than competing for gesture budget."
- **useful because:** Currently the pendant's one button is the main physical input and cannot be further subdivided into multiple gestures without conflict. Utilizing the existing timestamp marker record to carry multiple payloads triggered by the button would let the owner initiate diverse Mac-side actions without adding hardware or gesture conflicts.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** gpt-4o-mini
- **latency:** 2s
- **cost:** very low; largely local state and single SD write to pendant memory
- **security:** No increased hardware risk; proper payload validation required to avoid unintended actions.
- **missing:** software support on the pendant to encode and store multiple payloads on the timestamp marker record; Mac-side support to interpret and act on multi-payload timestamp marker events

### "Create a ranked and contextual unified task and goal store that gathers current owner intent from Apple Reminders, Calendar, and hand-typed tasks, enriched by AI summarization, priority, and dependency analysis, which can be accessed and dynamically updated by all system agents including mac-vision."
- **useful because:** Today the owner has no single prioritized task list that the agents can rely on for clarifying current work or goals. This unified store would allow all agents to align their activities on what matters most to the owner right now and adapt plans flexibly.
- **path:** mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** gpt-4o-mini
- **latency:** 5s
- **cost:** moderate due to aggregation, analysis, and summarization work
- **security:** Needs access to Apple Reminders and Calendar data and secure storage or memory for task state; owner consent required.
- **missing:** An agent or service that aggregates and ranks tasks and reminders from multiple sources, with AI prioritization logic; Updater integration on all agents to read/write from this unified task store dynamically

### "Provide explicit risk management and user confirmation flow for high-impact or destructive Mac interface actions via the mac-vision agent, with detailed logging and undo support to increase safety of autonomous Mac UI control."
- **useful because:** Allowing mac-vision or other system agents to autonomously take impactful or destructive operations on the Mac risks mistakes with negative consequences. Explicit risk classification and a user approval flow, integrated with undo operations and action history, would make autonomous Mac control safer and acceptable to the owner.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-4o-mini
- **latency:** 5s initial, more for user approval interaction
- **cost:** low to moderate; mostly workflow and UI action overhead
- **security:** Potentially sensitive actions recorded; strong permissions and user consent needed; user must control approval.
- **missing:** action risk classifier integrated with mac_run_actions and mac_delegate; UI for user approval on pendant and Mac; full undo and logging of autonomous UI operations


## What it asked for

_Nothing._
