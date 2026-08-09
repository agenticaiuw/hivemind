# Harness derivation — mac-vision — round 254

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide a comprehensive prioritized task list interface for mac-vision to read all owner-stated and system-derived tasks for the Mac surface, including deadlines, dependencies, and priorities."
- **useful because:** mac-vision currently lacks a cohesive list of tasks it should work on, which prevents effective prioritization and automation of meaningful Mac work.
- **path:** mac
- **model tier:** realtime
- **latency:** 200ms to fetch and rank tasks
- **cost:** Low API cost, mostly access to memoryService facts and dayPlan, plus ranking logic
- **security:** Tasks are owner data, privacy preserved with local access only; task data is existing owner facts and reminders.
- **missing:** Unified task aggregation; Ranking and dependency analysis; Task state synchronization

### "Implement multi-surface workflow coordination allowing mac-vision to delegate multi-step UI workflows spanning native Mac apps and browser control, maintaining persistent context and resuming after interruption."
- **useful because:** Many useful Mac workflows require both native and web UI steps, and being able to delegate and resume such workflows seamlessly across surfaces would be uniquely powerful.
- **path:** mac → browser
- **model tier:** realtime
- **latency:** Variable, typically up to 500ms per workflow step
- **cost:** Moderate API cost including mac_delegate, mac_run_actions, browser_run_actions and workbench context management
- **security:** Requires careful user consent for delegation and UI control permissions; context data handled securely and erased after use.
- **missing:** Persistent workflow context storage; Cross-surface delegation protocol; Resumption and error recovery mechanisms

### "Create a memory-enriched autonomous Mac UI assistant that proactively reads the live accessibility tree, combines it with owner task priorities and context from memoryService, and autonomously completes short UI workflows end-to-end without human instruction or scripting."
- **useful because:** The owner lacks a truly autonomous assistant for Mac UI tasks that understands both current UI state and owner intention to act fully proactively, saving significant time and frustration.
- **path:** mac
- **model tier:** realtime
- **latency:** sub-second per step
- **cost:** Moderate token consumption for memory and UI state integration, local computation focused
- **security:** Requires very careful memory management and consent for autonomous actions; all sensitive UI data stays local, autonomy features configurable and permit revocation.
- **missing:** Deep memory integration with UI state; Robust autonomous plan generation and step execution; Safety and revert mechanisms for autonomous UI actions

### "Develop seamless cross-device UI state synchronization and action delegation so mac-vision can visualize the current UI states on the Mac, iPhone, and pendant simultaneously, enabling unified multi-device workflows and seamless cross-device handoff."
- **useful because:** Owners work across multiple devices with distinct UI interfaces; seeing all UI states together and being able to delegate actions fluidly boosts productivity enormously.
- **path:** mac → ios → pendant
- **model tier:** realtime
- **latency:** 100ms UI sync, 500ms delegation
- **cost:** Higher API usage due to cross-device communication, moderate complexity
- **security:** Sensitive UI data encrypted and kept local; cross-device delegation requires explicit consent and strict boundary controls.
- **missing:** Cross-device UI state capture protocols; Unified multi-device action orchestration; Handoff and error recovery across device boundaries


## Changes it proposed to its own stack

### `model-routing` — Integrate multimodal reasoning that combines real-time UI state from mac-vision's accessibility tree, memory-based owner priorities, and multi-device state into a unified decision model that plans and delegates actions across devices seamlessly.
- **owner gets:** Currently, UI state, memory, and multi-device views are siloed. Unifying them will allow fluid cross-device workflows with context-aware reasoning, vastly improving responsiveness and task completion.
- effort: High - involves new model pipelines and data integration.  ·  risk: Misalignment in data fusion could cause incorrect or unexpected actions; needs careful fallback and human-in-the-loop override.
- cost: Increased API usage and compute time due to multimodal inference.  ·  latency: Somewhat increased per action latency due to complex fusion.
- security: Sensitive data handled in encrypted secure environments; model outputs audited and controlled.
- depends on: Cross-device UI state sync; Deep memory integration


## What it asked for

_Nothing._
