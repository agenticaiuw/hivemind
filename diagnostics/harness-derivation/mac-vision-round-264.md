# Harness derivation — mac-vision — round 264

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable mac-vision to read, rank, and act on the owner's live prioritized Mac UI task list"
- **useful because:** Currently, mac-vision lacks an actionable prioritized task list to automate. This will enable the system to dynamically schedule and execute user priorities via UI automation on the Mac, bridging intent to action seamlessly.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** under 1 second per prioritization update
- **cost:** minimal, uses existing state reads and light processing
- **security:** Needs user permission to read task and reminder data; must respect privacy and only act on authorized tasks.
- **missing:** durable list or priority API for owned tasks and goals for UI automation, task reconciliation with workbench state

### "Add a UI state reconciliation capability to mac-vision to verify on-screen UI matches intended workbench context"
- **useful because:** Currently, the system has workbench contexts representing claimed progress on tasks, but no way to confirm if the UI actually reflects that progress. This will allow mac-vision to verify the screen and report mismatches or failures.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** under 1 second per reconciliation
- **cost:** moderate, involves UI accessibility reads and comparison logic
- **security:** Needs permission to read UI accessibility tree; must avoid exposing sensitive UI content externally
- **missing:** Mechanism to capture and diff UI state snapshots against claimed workbench contexts

### "Create an intelligent UI action planner for mac-vision that designs detailed step-by-step UI interactions for complex Mac tasks"
- **useful because:** Mac-vision currently can only run short 1-3 step action lists or delegate entire complex goals without intermediate planning. This makes it difficult to handle longer, complex workflows requiring detailed UI navigation or conditional steps.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** seconds to minutes for complex plans
- **cost:** moderate, involves design/planning language model use
- **security:** Must run fully locally on owner's Mac to protect privacy; action confirmation needed for destructive operations
- **missing:** A UI action planner capable of composing and validating multi-step Mac UI automation plans from goals before execution

### "Provide a system-wide UI state monitoring and validation framework for the mac-vision agent"
- **useful because:** No current system verifies that UI changes claimed by workflows or workbench contexts actually appear on screen. A validation framework monitoring UI state would enhance reliability, detect errors, and enable self-healing workflows.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** few seconds for validation checks
- **cost:** moderate, requires continuous accessibility tree reads and diffing logic
- **security:** Needs privacy and data protection for UI state data; must avoid exposing sensitive info outside the Mac.
- **missing:** Mechanism to capture UI state snapshots and compare them to expected states per workflow context.; Integration with workbench and mac_delegate to react to validation results.

### "Create an AI-driven multi-step UI interaction planner that designs stepwise Mac UI control sequences from owner goals"
- **useful because:** Currently mac-vision can only handle short 1–3 step actions or full delegation of goals, lacking the ability to plan detailed, conditional, multi-step UI workflows autonomously. This would greatly enhance flexibility and autonomy.
- **path:** mac-local-agent
- **model tier:** realtime
- **latency:** seconds to minutes depending on complexity
- **cost:** moderate, with natural language planning and validation models
- **security:** Must operate fully on device for privacy; destructive steps need confirmation safeguards.
- **missing:** Planner component for conditional, multi-step UI flows.; Action sequence validation methods.; Integration to run planned sequences via mac_run_actions.


## Changes it proposed to its own stack

### `interaction` — Implement a resilient permission and sandboxing framework for mac-vision UI automation to enable safe expansion of its capabilities to read, act, and verify state autonomously on the Mac.
- **owner gets:** Allows mac-vision to gain richer, safer control and observation across Mac apps with user trust, letting automation reach a new level of reliability and complexity while protecting user data and preventing unintended actions.
- effort: high, involving macOS security model expertise, UI automation frameworks, and user UX flows for consent and fallback.  ·  risk: Potential risk of excessive permissions or user confusion mitigated by clear UI, limited scope, and audit logs.
- cost: Low API cost, but requires developer effort and possible macOS-specific components or entitlements.  ·  latency: No impact on runtime latency beyond initial setup.
- security: Increases security surface; must be carefully designed and tested.

### `model-routing` — Develop a specialized, mac-vision-aware LLM routing framework that routes UI automation and reasoning requests to dedicated models optimized for UI planning, verification, and small-step execution.
- **owner gets:** Improves responsiveness and accuracy in multi-step UI tasks by running them through mission-specific models rather than generic ones, enabling smoother and more reliable computer control workflows.
- effort: medium, requires LLM orchestration layer enhancement and model training or fine-tuning.  ·  risk: Misrouting could lead to degraded performance temporarily; fallback to general model required.
- cost: Moderate due to specialized model hosting costs.  ·  latency: Potentially faster per-step interaction times due to optimized models.
- security: Model specialization has low security risk but requires data isolation in training.
- depends on: interaction

### `hardware` — Integrate tactile and haptic feedback hardware into the pendant to signal mac-vision UI automation status, task progress, and requests for owner attention or confirmation.
- **owner gets:** Provides non-visual ambient feedback to the owner about the state of Mac automation activities, enabling awareness and timely intervention without interrupting workflow.
- effort: medium, hardware integration and embedded firmware updates required.  ·  risk: Additional power consumption and hardware complexity; mitigated by efficient design.
- cost: Moderate hardware cost increase for the pendant.  ·  latency: No impact on automation latency.
- security: No direct security impact, feedback device only.


## What it asked for

_Nothing._
