# Harness derivation — mac-vision — round 210

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Correlate and validate UI state on the Mac with workbench context claimed progress"
- **useful because:** Workbench contexts track claimed workflow progress but do not observe real UI state on the Mac. This capability would detect UI drift, errors, or interrupted workflows by comparing vision loop UI snapshots to expected states, enabling better recovery and accurate status reporting for the owner.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds
- **cost:** medium, due to continuous accessibility tree processing and diffs
- **security:** Must securely handle UI data, prevent leakage. Validation can avoid false positives to prevent disruption.
- **missing:** UI state snapshot diff engine integrated with workbench context tracking; Methods to specify expected UI states per workflow step

### "Enable choreographed multi-app and multi-surface Mac workflows coordinated by mac_delegate"
- **useful because:** Many owner tasks involve multiple apps and surfaces (browser, pendant, Mac apps). Coordinating these with synchronized state, progression signals, undo support, and combined audit trails would enable sophisticated, reliable automation of complex workflows beyond simple single-app actions.
- **path:** mac-vision → browser-extension → unified → mac-planner
- **model tier:** realtime
- **latency:** under a second to few seconds per step
- **cost:** medium to high, depending on workflow complexity and integration
- **security:** Requires careful management of credentials, permissions, and undo boundaries for safe operation.
- **missing:** Protocols for state sync and signal passing between surfaces; Rich multi-step plan executor with rollback and error recovery; Audit trail integration across surfaces

### "A Mac vision loop real-time UI reconciliation service that detects and corrects UI state divergence from complex multitask workflows"
- **useful because:** Owners working with multitasking or apps requiring multi-step UI sequences often experience frustration when workflows get out of sync. This capability lets the vision loop track and fix UI divergence, enhancing reliability and trust.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** sub-second updates
- **cost:** moderate, requiring frequent accessibility tree snapshots and AI reconciliation
- **security:** High confidentiality on UI state data, with strict access control and encryption.
- **missing:** full accessibility-tree snapshot route with delta capabilities; integration hooks into mac_delegate and undo system

### "An owner-driven prioritization and dynamic task insertion interface for Mac vision agent"
- **useful because:** Currently no direct way for the owner to input or rearrange tasks specifically for mac-vision to execute reliably. This interface would make mac-vision's work genuinely responsive and aligned with owner intent.
- **path:** mac-planner → mac-vision
- **model tier:** background
- **latency:** seconds
- **cost:** low to moderate, primarily UI and storage integration
- **security:** Authentication required to prevent unauthorized task injections or prioritization changes.
- **missing:** a dedicated task priority UI or command interface; backing store and API linking to memory/facts task facts


## Changes it proposed to its own stack

### `model-routing` — Add orchestration and synchronization protocols between mac-vision, browser-extension, mac-planner, and the pendant to enable complex choreographed multi-application workflows with shared state and undo
- **owner gets:** Complex tasks that span multiple apps and devices become seamless and reliable, reducing manual coordination effort and errors.
- effort: Large; requires protocol design, model and agent coordination, and robust failure handling  ·  risk: Potential cross-surface state sync bugs that could cause inconsistent task progress; requires careful testing and rollback capabilities
- cost: Moderate to high compute cost due to synchronization and planning models  ·  latency: Increases latency for multi-step workflows but allows parallelism within steps
- security: Cross-surface credential and data sharing risk; strong access controls and data isolation needed
- depends on: Existing mac_delegate and multi-surface communication channels


## What it asked for

_Nothing._
