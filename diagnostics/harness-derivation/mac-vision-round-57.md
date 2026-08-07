# Harness derivation — mac-vision — round 57

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a fully autonomous computer-use loop on the Mac that can safely and proactively interact with any visible application UI or system UI element using accessibility APIs whenever the owner needs it, without requiring focus theft or pixel screenshots, to perform tasks that cannot be done by APIs alone."
- **useful because:** Many Mac applications have no or incomplete APIs; the owner often needs to perform complex UI interactions like clicking buttons, typing text into forms, or navigating menus. Allowing autonomous, accessibility-tier interaction allows seamless proactive Mac task execution without interrupting the owner's workflow or exposing the screen's pixels to security risks.
- **path:** mac-vision → faculty-perception → faculty-judgement → faculty-action → mac-planner
- **model tier:** gpt-4.1-mini with gpt-5.6-luna coordination
- **latency:** under 5 seconds per action sequence
- **cost:** moderate per invocation due to reasoning complexity and UI state processing
- **security:** Requires strict owner policy for maximum access with no gates, plus observability and undo receipts for all mutations to prevent abuse or errors. Must never steal focus or interfere with active work. Accessibility data must be guarded carefully to avoid sensitive content leaks.
- **missing:** Always-on real-time detailed UI hierarchy snapshot context; Pre-authorization by owner for fully autonomous loop; UI interaction policy enforcement and prompt-less safe execution; Undo and audit trail integration for all UI interactions

### "Allow the mac-vision agent to perform multi-step, context-aware workflows that can blend API-based control and UI automation on the Mac, coordinated with browser extensions and terminal operations, to complete complex tasks end-to-end that are currently impossible due to partial system integration."
- **useful because:** Many tasks require combinations of file management, browser interactions, terminal commands, and UI clicks that no single current surface can handle alone. This integrated workflow ability would greatly increase productivity and reduce the owner's manual overhead.
- **path:** mac-vision → mac-planner → browser-extension → mac-terminal → faculty-judgement → faculty-action
- **model tier:** gpt-5.6-luna coordination with gpt-4.1-mini for vision specifics
- **latency:** Under 10 seconds for typical workflows
- **cost:** Moderate due to cross-surface coordination and plan complexity
- **security:** Must ensure safe permissions, sandboxing, and undo capabilities across all surfaces; requires clear audit and owner transparency.
- **missing:** Cross-surface orchestration protocols and state sharing; Unified action and state model for Mac and browser/terminal UI tasks; Enhanced planning models with vision and multi-surface awareness


## Changes it proposed to its own stack

### `model-routing` — Add a dynamic model routing mechanism that intelligently assigns subtasks of Mac computer-use to appropriate specialized models based on task complexity, execution context, and UI feedback. For example, delegate routine status queries to lightweight models, complex UI action planning to gpt-5.6-luna, and real-time error recovery to a focused micro-model.
- **owner gets:** This change ensures efficient use of computational and response resources, minimizing latency and cost while maximizing reliability and intelligence in Mac task automation, especially for complex tasks requiring UI understanding and action.
- effort: Moderate engineering plus new model training and integration.  ·  risk: Incorrect routing might cause delays or failures in task execution; fallback mechanisms required.
- cost: Increased infrastructure usage optimized by routing to cheaper models when possible.  ·  latency: Reduced average latency for simple tasks, slightly increased for heavy tasks due to routing overhead.
- security: Routing decisions must respect owner policies and context sensitivity.
- depends on: Fully autonomous computer-use loop enabled with UI hierarchy context and control APIs

### `mac-harness` — Develop a robust UI hierarchy and accessibility event logger integrated into the Mac harness to provide real-time streaming and snapshot views of visible UI elements, their states, and interactions. This logger should support differential updates and support both full and partial snapshots to optimize bandwidth and processing.
- **owner gets:** Provides the essential data backbone needed for any proactive or autonomous Mac UI interaction capabilities, allowing safe, rapid, and informed decisions about Mac UI automation without relying on pixel screenshots or stealing focus.
- effort: High: deep integration with Mac accessibility APIs and efficient streaming architecture.  ·  risk: Potential privacy risk if logged UI data is leaked; must include encryption and strict access controls.
- cost: Moderate: storage, CPU, and network usage.  ·  latency: Low latency updates enable real-time reactive behavior.
- security: Must be guarded to avoid sensitive information exposure.

### `interaction` — Create a reversible UI interaction framework that logs every action the Mac computer-use loop performs, with immediate undo capability and detailed receipts sent to the owner via the pendant. Include automatic detection of non-idempotent or high-risk actions and enforce read-only or low-risk mode by default unless explicitly authorized.
- **owner gets:** Protects the owner from accidental destructive actions, gives confidence in autonomous UI control, and provides transparency and control with immediate recovery options. Supports owner policy for maximum access with safety nets.
- effort: Moderate to high engineering effort, plus UI and backend integration for receipt display and undo commands.  ·  risk: Incomplete logging or undo might cause discrepancies; extensive testing and fallback required.
- cost: Low to moderate for storage and communication.  ·  latency: Minor additional delay for logging and confirmation stages.
- security: Ensures that critical actions are guarded and monitored.
- depends on: Fully autonomous computer-use loop enabled with accessibility snapshot and control APIs


## What it asked for

_Nothing._
