# Harness derivation — mac-vision — round 199

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable robust multi-step Mac UI workflow control with persistent progress, live state reconciliation, and safe error recovery"
- **useful because:** Multi-step workflows involving UI on the Mac can be complex and may be interrupted or fail. A system that claims work and tracks progress with live reconciliation against actual UI state is essential for reliable task execution and error handling.
- **path:** mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds-level interaction
- **cost:** moderate API usage dominated by state reads and reconciliation calls
- **security:** Must respect destructive action confirmation policies; must not execute critical destructive steps without explicit owner approval
- **missing:** Orchestration layer for mac-vision loop to claim and act on workbench contexts; UI state reconciliation tools comparing live accessibility tree with workbench job state; Error detection and rollback mechanisms for partial UI workflow failures

### "Allow mac-vision to automatically derive and execute UI interaction sequences based on the owner's 'current tasks' facts and preferences"
- **useful because:** This automates the path from high-level owner priorities into concrete UI actions on the Mac, allowing autonomous progress without manual re-interpretation each time. It leverages the exact owner priorities known today.
- **path:** mac-vision → faculty-judgement → faculty-action → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds-level
- **cost:** Moderate usage dominated by planning model calls and UI tree reads
- **security:** Must respect owner's destructive action confirmation preferences and avoid performing dangerous steps without explicit confirmation
- **missing:** A planner component that converts task facts into step-by-step UI action sequences; Integration with live accessibility tree to validate UI states before action

### "Create a confirmation and policy framework for mac-vision to manage destructive actions on Mac UI"
- **useful because:** Reliable automation requires safeguards that prevent unwanted destructive actions (like file deletions, sending mail, purchases) without explicit owner consent, aligned with their preferences. This framework enforces safe acting.
- **path:** mac-vision → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds-level
- **cost:** Low to moderate, mostly policy evaluation
- **security:** Must ensure no destructive UI actions occur without owner consent; must log decisions and actions for audit
- **missing:** A policy definition and enforcement layer for destructive UI actions in mac-vision; User interaction and confirmation dialogs or hooks for critical steps

### "Propose a capability to coordinate mac-vision actions with voice note commands and recorded owner intentions"
- **useful because:** Voice notes and recorded commands can trigger UI workflows or clarify intent in natural language, improving flexibility and fluidity. Coordination with mac-vision actions enables better task handoff and confirmation.
- **path:** mac-vision → relay-realtime → faculty-perception → faculty-action → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** seconds-level
- **cost:** Moderate usage dominated by speech recognition and intent extraction
- **security:** Require owner confirmation before acting on voice notes that trigger destructive actions or sensitive workflows
- **missing:** Integration API between voice note subsystem and mac-vision control loop; Intent extraction and mapping from voice note to UI workflows

### "Enable a real-time, live accessibility tree comparison tool that verifies current Mac UI state against expected workflow state to detect discrepancies and automate recovery strategies."
- **useful because:** No system currently checks if the on-screen UI controls match what the agent believes the Mac state to be. This tool would prevent errors from unnoticed UI changes or workflow divergence, allowing for reliable and robust automation.
- **path:** mac-vision → faculty-perception → faculty-judgement
- **model tier:** gpt-5.6-luna
- **latency:** seconds-level
- **cost:** Low to moderate, dominated by tree reads and comparison logic
- **security:** Must not disclose UI state externally; must validate intent before recovery actions.
- **missing:** Current no accessible reconciliation tool for UI state exists; Need a way to link live accessibility data with workflows and job receipts

### "Provide a capability for the pendant and mac-vision to jointly manage secure owner-confirmed destructive actions on Mac UI workflows, leveraging physical button presses for emergency abort or confirmation."
- **useful because:** Destructive actions carry high risk and should require unequivocal owner approval. Use of the secure pendant button as a hardware confirmation channel adds safety and auditability to destructive UI actions.
- **path:** mac-vision → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna
- **latency:** seconds-level
- **cost:** Low, mostly stateful event tracking and integration
- **security:** Ensures destructive actions do not execute without explicit physical owner confirmation; guards against remote or accidental triggers.
- **missing:** Integration between pendant button press events and mac-vision UI action approval flow; Policy defining what requires pendant confirmation


## Changes it proposed to its own stack

### `context` — Implement a persistent goal and task state store shared across all system agents that supports priority, deadlines, and dependencies.
- **owner gets:** Today, no shared authoritative prioritized task list exists. A persistent, comprehensive goal/task store that all agents can read and update would enable coordinated, multi-agent, long-lived work management.
- effort: High: Requires cross-agent coordination and data schema design.  ·  risk: Data synchronization conflicts; potential privacy leaks; complexity of priority management.
- cost: Moderate runtime resource and storage cost.  ·  latency: Negligible to moderate latency depending on design.
- security: Must enforce privacy and access controls on task data.

### `new-surface` — Add a Mac Accessibility UI state auditor service that monitors and reports mac-vision agent UI actions and current accessibility tree snapshots for auditing and debugging.
- **owner gets:** The owner can get insights and error reports about what the mac-vision agent is doing live on the Mac UI, including detecting mismatches between expected and actual UI states and understanding failures.
- effort: Medium; requires a new Mac-side daemon or mac-vision enhancement to maintain logs and state views.  ·  risk: Privacy concerns; secure access control needed.
- cost: Moderate storage and processing cost for logs and state.  ·  latency: Minimal impact on real-time UI action latency.
- security: Must ensure logs and reports are accessible only by authorized agents or the owner.
- depends on: mac-vision accessibility loop enabled

### `interaction` — Allow the mac-vision agent to request and synthesize native macOS UI accessibility notifications (like focus change, control state change) for intelligent event-driven UI automation.
- **owner gets:** Event-driven UI automation allows the agent to respond immediately and robustly to UI changes without polling or unsafe assumptions, enabling faster, reliable user task automation.
- effort: Medium; requires integration with macOS accessibility notification APIs and event routing to mac-vision.  ·  risk: Potential privacy exposure of screen content or user activity if misused; requires careful permission management.
- cost: Low runtime cost but requires persistent event listener.  ·  latency: Improves latency and responsiveness.
- security: Must enforce strict permissions and auditability.
- depends on: mac-vision accessibility loop enabled


## What it asked for

_Nothing._
