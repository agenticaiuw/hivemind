# Harness derivation — mac-vision — round 62

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable seamless, safe pixel-level Mac UI automation with context-sensitive error recovery."
- **useful because:** The owner would gain a powerful assistant on their Mac that can visually understand any screen, combine it with accessibility data, and take precise actions beyond API limits. This would allow richer workflows and better handling of complex or novel UIs, reducing manual effort.
- **path:** mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** tens to low hundreds of milliseconds per UI step, under 5 seconds per action sequence
- **cost:** moderate to high per invocation due to image processing and context integration
- **security:** Requires strict permission gating to screen capture and input control to prevent misuse; all vision data processed locally if possible; user confirmation for high-impact actions.
- **missing:** Permission for visionUploadConsented to true and computerUse.loopEnabled true; System-level UI accessibility snapshot support with context linking; Robust error detection and automated recovery routines for UI inconsistencies; A coordination protocol to combine visual recognition results with accessibility and typed action plans

### "Intelligent routing between simple Mac UI actions and complex delegated workflows based on task context and project type."
- **useful because:** The owner would get an assistant that adjudicates their requests, sending simple, well-defined commands directly for quick execution and deferring multi-step, ambiguous, or long workflows to the Mac local planner. This reduces errors and optimizes speed vs flexibility.
- **path:** mac-planner → mac-vision → faculty-judgement
- **model tier:** realtime
- **latency:** under 1 second to route a single request; multi-step delegated goals executed as planned
- **cost:** low for routing decision; delegated workflows vary with complexity
- **security:** Routing decision logic is not high-risk but consistency must be maintained to avoid surprises.
- **missing:** Context awareness of open apps, project metadata, and request ambiguity; Integration with task understanding modules; A delegation interface exposed to judgement to hand off or recall workflows

### "Owner-controlled visual macro creator and editor that records and replays Mac UI interactions based on pixel and accessibility events."
- **useful because:** The owner could create complex multi-step automation macros for repetitive tasks on any Mac UI component, customizing and editing them with a visual interface. This empowers non-programmers to automate workflows that span apps and web content without scripts.
- **path:** mac-vision → mac-planner → mac-delegate → faculty-judgement → faculty-action
- **model tier:** realtime
- **latency:** Seconds to minutes for macro recording and replay; immediate UI feedback.
- **cost:** Moderate due to UI capture, event logging, and validation logic.
- **security:** Macros must be sandboxed and require explicit user approval and control to prevent unauthorized execution or data leakage.
- **missing:** Persistent UI event capture and replay infrastructure; Visual and accessibility event coalescing; Macro editing UI and validation logic; Integration with existing action execution frameworks


## Changes it proposed to its own stack

### `hardware` — Add a dedicated low-latency coprocessor to the MacBook hardware specifically for secure on-device AI vision processing and UI interaction synthesis.
- **owner gets:** This would enable mac-vision to run advanced pixel-level UI automation without compromising privacy or security, maintaining high responsiveness without depending on external servers or sacrificing device performance.
- effort: Significant hardware engineering, fabrication, and integration effort.  ·  risk: Hardware bugs or security vulnerabilities could be catastrophic but mitigated by strict design and testing. Recovery would be via firmware update or hardware replacement.
- cost: High initial component cost; minimal ongoing power draw increase.  ·  latency: Drastically reduces vision processing latency, enabling real-time UI understanding and action.
- security: Improves security by localizing sensitive data processing; reduces attack surface for vision data.
- depends on: mac-vision agent software support; Operating system driver support; Accessibility and computer control APIs in macOS


## What it asked for

_Nothing._
