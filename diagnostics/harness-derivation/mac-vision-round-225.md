# Harness derivation — mac-vision — round 225

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a durable and prioritized Mac Work Intent Store for incoming Mac tasks and goals that the Mac-vision agent can read and act on."
- **useful because:** Currently there is no central place storing what the owner wants done on the Mac, only scattered facts or reminders. A proper queue with priority, metadata, and persistent state lets the Mac-vision agent autonomously pick up and act on high priority tasks.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** under 1 second
- **cost:** low API cost mainly for read/write ops
- **security:** Stores owner intentions explicitly; must be secured to prevent spoofing or data loss.
- **missing:** Implementation of a persistent queue or store of Mac task intents; Metadata like priority and deadline in task facts; API routes to manage and query this queue

### "Add a verification and audit layer comparing Mac UI workflow claims (workbench contexts) with actual UI state read by mac-vision, triggering retries or safe fallback on inconsistency."
- **useful because:** Because UI automation can fail silently or diverge from claimed state, having a trustable consistency check ensures reliability and user trust. This layer reduces silent UI automation failures and improves recovery.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** under 2 seconds
- **cost:** moderate due to UI state reads and comparisons
- **security:** Must validate UI state data integrity; avoid false positives that disrupt user work.
- **missing:** Systematic comparison logic between workbench claimed state and UI accessibility tree; Recovery or retry protocols implemented in the Mac agent

### "Establish coordination signals and context interfaces for multi-agent, multi-step Mac workflow resumption, handoff, and fail-safe continuation, integrating UI state awareness from mac-vision."
- **useful because:** Workflows started on one agent or interrupted must resume smoothly on another. Coordination signals allow for robust, seamless multi-agent collaboration, ensuring the user experience is cohesive and uninterrupted.
- **path:** mac-vision → mac-planner → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** under 2 seconds
- **cost:** moderate API cost for state sync; design complexity
- **security:** Must protect user data privacy in multi-agent state sharing.
- **missing:** Signal protocols for workflow handoff; Shared or federated context graph for workflow state; Event hooks for interruption and resume

### "Enable the mac-vision agent to autonomously and safely resume interrupted Mac UI workflows exactly where they left off by capturing, storing, and verifying detailed UI accessibility tree snapshots as checkpoints."
- **useful because:** Current Mac UI workflows can be interrupted by crashes, reboots, or permission changes, causing lost progress and inconsistent states. Checkpointing UI state enables precise resumption, increasing reliability and trust in automation.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** 1-3 seconds
- **cost:** moderate, due to accessibility tree storage and comparison
- **security:** Stored UI state contains personal app and possibly sensitive info; must be secured locally and encrypted.
- **missing:** API and storage for snapshotting UI state checkpoints; Verification logic comparing checkpoint to live UI before resuming; Recovery protocols for mismatches and retry logic

### "Provide a fast, context-aware multi-tier Mac automation planner that dynamically chooses between mac_run_actions, browser_run_actions, and mac_delegate workflows, optimizing for speed, reliability, and user preference."
- **useful because:** Currently, selecting which tool or approach to use for a given Mac automation task is manual or ad hoc. A smart planner reduces redundant attempts and latency by picking the best tool tier dynamically, improving user experience and system efficiency.
- **path:** mac-vision → mac-planner → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** sub-second to 1 second for decision making
- **cost:** low to moderate compute cost per decision
- **security:** Planner must respect user preferences for destructive actions and privacy and be transparent on choice criteria.
- **missing:** Dynamic capability to introspect current UI state and user context; Decision-making model for tier selection; Integration hooks for automatic fallback between tiers

### "Develop an intent-aware Mac UI mutation confirmation and policy system that classifies Mac UI actions into safe, destructive, or irreversible categories and enforces user consent or auto-approval based on preferences."
- **useful because:** Many Mac automation actions risk unwanted data loss or irreversible changes, undermining trust. A classification and confirmation system ensures only acceptable actions run, while respecting user autonomy and minimizing prompts.
- **path:** mac-vision → unified → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** under 1 second
- **cost:** low compute cost for classification and policy enforcement
- **security:** Classification relies on accurate action intent detection; must guarantee no unauthorized destructive actions are executed.
- **missing:** Accurate classification models for Mac UI actions; User-configurable consent policy interface; Integration with mac_run_actions and mac_delegate for gating

### "Enable mac-vision to collaborate with the pendant and relay agents to perform contextually aware Mac actions triggered by physical hardware events (e.g., button presses), integrating low-latency on-device triggers with high-level Mac UI workflows."
- **useful because:** Physical hardware triggers on the pendant provide a tangible, immediate input that can initiate complex Mac UI workflows safely and responsively. This integration combines the strengths of wearable hardware and deep Mac control for seamless user experience.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** under 1 second for trigger propagation and Mac action start
- **cost:** moderate for event handling and queued execution
- **security:** Must securely authenticate hardware events and enforce user intent; avoid false positives triggering destructive actions.
- **missing:** Event API or protocol for hardware-triggered Mac agent calls; Contextual mapping of button presses to meaningful Mac workflows; Failure and fallback handling for lost or duplicate triggers


## Changes it proposed to its own stack

### `interaction` — Implement a context-sensitive permission and confirmation UI overlay on the Mac activated by mac-vision before performing sensitive or destructive UI actions, with short spoken confirmation and undo options.
- **owner gets:** This allows the owner to retain control and confidence by visually and audibly confirming sensitive Mac UI automation actions before they occur, preventing unwanted changes and enabling quick reversals.
- effort: Medium development effort integrating accessibility automation with on-screen UI and speech output.  ·  risk: Potential to interrupt workflow or annoy if overused; mitigated by context sensitivity and user preferences.
- cost: Moderate due to additional UI rendering and speech synthesis calls.  ·  latency: Low to moderate, as confirmation occurs before action execution.
- security: Improves security by preventing unauthorized or mistaken destructive actions.
- depends on: mac_run_actions; computerUse.loopEnabled; speech synthesis capability

### `model-routing` — Integrate a dynamic routing mechanism in the AI orchestration system to evaluate task complexity in real-time and assign either mac_run_actions, browser_run_actions, or mac_delegate accordingly, with fallback and retry logic based on success/failure signals.
- **owner gets:** Improves automation responsiveness and success by using the best-suited tool for each task dynamically, reducing latency and errors in Mac UI control and browsing workflows.
- effort: Medium, requires real-time task complexity assessment and routing logic design.  ·  risk: Incorrect routing might cause suboptimal UX but can be corrected with fallback mechanisms.
- cost: Low to moderate, mainly compute resource for routing decisions.  ·  latency: Improves overall latency by reducing wasted attempts.
- security: Minimal security impact, but must respect user preferences and policy.
- depends on: mac_run_actions; browser_run_actions; mac_delegate; mac-planner; mac-vision


## What it asked for

_Nothing._
