# Harness derivation — mac-vision — round 196

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a ranked, durable task and goal list specifically for the Mac vision agent combining owner priorities from memory projected 'task' facts and day plan reminders."
- **useful because:** The vision loop currently has no native prioritized task queue, forcing manual or unreliable execution. A dedicated ranked task list keyed to owner priorities enables seamless autonomous task selection and execution on the Mac, increasing usefulness and autonomy.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** minutes
- **cost:** low per invocation, dominated by memory and reminder reads
- **security:** Stores task intents and audience scope correctly; tasks are owner sensitive but on-device.
- **missing:** A unified priority scoring and task queue store for Mac-agent tasks.

### "Provide a capture and reconciliation tool for multi-step Mac UI workflows that compares planned workflow states vs observed accessibility tree states during execution."
- **useful because:** Delegated workflows on Mac often diverge from expectations. A reconciliation tool that validates UI state continuity and flags discrepancies improves trust, enables recovery from partial failures, and helps debugging.
- **path:** mac-vision → mac-planner
- **model tier:** background
- **latency:** seconds to minutes depending on workflow length
- **cost:** medium, due to UI snapshot processing and diffing
- **security:** Sensitive UI state is processed securely without leaking owner private data.
- **missing:** Standardized UI state snapshot representation, reconciliation algorithms.; Workflow state model and change observation APIs.

### "Provide a detailed Mac vision loop telemetry API to log every UI action taken, accessibility tree snapshot, fallback events, and errors for post-mortem analysis and debugging."
- **useful because:** The vision loop can silently degrade or fail without clear signals. Telemetry enables owners and developers to audit interaction quality, diagnose failures, and improve automation reliability.
- **path:** mac-vision → dashboard
- **model tier:** background
- **latency:** seconds per batch upload
- **cost:** medium, dominated by log storage and indexing
- **security:** Telemetry data contains detailed UI and state info; must be appropriately confined and encrypted.
- **missing:** A dedicated telemetry logging and retrieval backend.; Standardized event schema for UI interactions.

### "Create a comprehensive, adaptive Mac task orchestration capability that combines all known priority signals, integrates with live Mac UI accessibility state, and autonomously schedules and executes both short and longer workflows with full state tracking and recovery."
- **useful because:** This would unlock truly autonomous Mac UI interaction driven by the owner's evolving priorities, improving productivity and trust through resilience and situational awareness.
- **path:** mac-vision → mac-planner → unified → dashboard
- **model tier:** realtime
- **latency:** seconds to minutes
- **cost:** moderate, due to state tracking and planning computations
- **security:** Sensitive owner data involved; must maintain privacy and control on-device; fail-safe for unintended UI control.
- **missing:** Unified priority and scheduling framework for Mac tasks.; Full integration of accessibility UI state and workflow control APIs.; Robust error detection, recovery, and audit logging for UI operations.

### "Provide a secure capability that allows the Mac vision agent to verify and confirm destructive actions (file deletion, mail sending, purchases) with the owner using a physical pendant confirmation gesture before proceeding."
- **useful because:** Prevents unintended destructive operations from automated UI actions, increasing owner safety and trust while allowing maximal autonomy otherwise.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** seconds
- **cost:** low
- **security:** Requires secure input channel from pendant to Mac agent, confirmation recorded but minimal data leakage risk.
- **missing:** Physical gesture confirmation infrastructure on the pendant and relay; Secure real-time channel from pendant to Mac vision agent


## Changes it proposed to its own stack

### `model-routing` — Implement dynamic, context-aware routing that allows low-latency model tiers to coordinate with background planners and specialized Mac UI automation models, balancing interaction speed and planning depth.
- **owner gets:** Keeps Mac UI automation responsive and robust by using the best model for the moment and task complexity, enhancing interaction quality and reducing wait times.
- effort: medium engineering, requires coordination between live planners and model selection APIs.  ·  risk: Misrouting could cause delays or model mismatches; fallback and monitoring needed.
- cost: Increased API usage costs, optimized by routing rules.  ·  latency: Potential latency improvements when routing to faster models.
- security: Model routing based on task context does not impact data security beyond current norms.
- depends on: Unified task orchestration framework; Access to workload metrics

### `integration` — Build a telemetry and audit logging pipeline integrated across the Mac vision loop, background planners, and dashboard surfaces, enabling the owner to review automation actions, errors, and recovery status transparently.
- **owner gets:** Gives the owner insight into what the automation is doing, builds trust, supports debugging and improved system safety.
- effort: medium to high, needs cohesive logging formats, storage, and UI dashboards.  ·  risk: Telemetry data leakage if not secured properly; needs strict encryption and access controls.
- cost: Moderate storage and indexing costs.  ·  latency: Low impact on runtime latency, mostly background processing.
- security: Requires strong access restrictions and encryption for telemetry data.
- depends on: Unified task orchestration framework; Telemetry backend infrastructure


## What it asked for

_Nothing._
