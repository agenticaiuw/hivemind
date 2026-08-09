# Harness derivation — mac-vision — round 151

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable continuous, context-aware computer control with the mac-vision agent, including safe reversible UI interactions and direct accessibility UI element manipulation."
- **useful because:** This capability would allow the owner to delegate complex computer tasks and UI interactions to the mac-vision agent without needing screen captures or full manual intervention, speeding workflow and reducing cognitive load. It would be the most sophisticated way to control the Mac via accessibility APIs for precise, safe automation, enabling workflows that combine Mac apps, scripting, and UI elements adaptively.
- **path:** mac-vision → mac-planner → relay-realtime → pendant → browser-extension
- **model tier:** realtime
- **latency:** 1–2 seconds per interaction loop
- **cost:** Low to moderate API call cost dominated by accessibility tree parsing and LLM inference
- **security:** Requires macOS Accessibility permission for full UI tree access but does not perform pixel capture; all UI inputs are reversible and logged with user confirmation; no sensitive data leaves device without explicit consent.
- **missing:** macOS Accessibility full grant to AI Pendant Agent binary; visionUploadConsented permission for UI context upload; robust computerUse.loopEnabled integration for full control loop; LLM enhancements for real-time UI understanding and action planning; Safety policy and confirmation UI for reversible actions

### "Develop a unified open goal management system that the mac-vision agent and other agents can read, write, prioritize, and act on with shared state."
- **useful because:** Currently, there is no central, ranked task store reflecting what the owner truly wants accomplished. A unified goal management system visible to mac-vision and all other agent surfaces would allow seamless task prioritization, progress tracking, and coordinated multi-agent task execution with clear owner priorities.
- **path:** mac-vision → mac-planner → relay-realtime → pendant → browser-extension
- **model tier:** background
- **latency:** seconds to minutes for synchronization and ranking
- **cost:** Moderate API cost dominated by distributed syncing and state management
- **security:** Requires user control over permissions and encryption to protect owner task data and privacy.
- **missing:** Cross-surface shared state backend with conflict resolution; Task ranking model policies; User-friendly task input and feedback interfaces

### "Enable the mac-vision agent to generate and execute complex, multi-step UI workflows on the Mac using real-time accessibility tree state and user context."
- **useful because:** Currently, the agent can only perform simple 1-3 step actions or delegate ambiguous multi-step goals without explicit control. Enabling mac-vision to reason about the detailed accessibility UI tree state and generate safe, confirmable action sequences would greatly enhance its utility in automating sophisticated computer tasks.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** realtime
- **latency:** 2-3 seconds per action sequence generation and execution
- **cost:** Moderate API usage dominated by LLM inference and UI state querying
- **security:** Requires robust fail-safe and undo mechanisms, and explicit user confirmations for changes. UI context remains local unless explicitly shared.
- **missing:** Real-time, detailed accessibility tree snapshot API with high fidelity; Integration of continuous UI state updates with LLM decision making; Undo and confirmation UI in pendant and Mac environment

### "Develop a privacy-respecting, on-device UI state compression and summarization system for mac-vision to minimize data sent off-device while maintaining actionable context."
- **useful because:** Directly exporting full accessibility trees or screen captures raises privacy and bandwidth concerns. A locally compressed and semantically summarized UI state feed would allow mac-vision to operate efficiently, with sensitive details minimized or abstracted, enhancing privacy and speed of UI-driven automation.
- **path:** mac-vision → pendant → relay-realtime → mac-planner
- **model tier:** background
- **latency:** seconds for local compression and summarization
- **cost:** Low API cost; mostly local computational cost
- **security:** Sensitive UI data stays on device; only minimal semantic summaries leave. Potential for accidental leak mitigated by strict local policies.
- **missing:** Specialized UI state compression algorithms; On-device summarization model integration; Policy controls for data sharing and user approvals


## Changes it proposed to its own stack

### `integration` — Integrate the mac-vision agent's accessibility-driven UI loop tightly with the pendant and relay realtime agents to enable voice-driven, confirmable UI manipulation and multi-modal computer control.
- **owner gets:** By combining the unique strengths of the wearable pendant (low latency voice input and feedback), the always-on relay (offline continuity), and the Mac's UI accessibility context (detailed app state), the owner gains a truly seamless, multi-modal, highly efficient way to control their computer and workflow fluidly.
- effort: Large engineering effort spanning device firmware, Mac accessibility integration, relay protocol upgrades, and voice interaction design.  ·  risk: Complex error recovery needed for misrecognized commands or lost connectivity; requires rigorous safety and user confirmation systems to avoid unintended actions.
- cost: Significant development cost in SDK and server infrastructure; moderate ongoing API cost for voice and UI action orchestration.  ·  latency: Low-latency voice and UI loop integration essential; 1-second end-to-end action response budget expected.
- security: Requires strict access controls and encryption end to end; must meet owner privacy expectations.
- depends on: computerUse.loopEnabled permission granted; macOS Accessibility full grant; visionUploadConsented permission for UI context upload

### `firmware` — Add a second hardware button or multi-gesture physical interface on the pendant to separately trigger distinct mac-vision approval or undo gestures without compromising the primary microphone button.
- **owner gets:** Currently the pendant only has one button for recording moments or approvals, which limits the complexity of physical interaction gestures. A separate button or expanded gesture recognition would allow safer, faster, and more expressive confirmation and undo actions paired with mac-vision UI control workflows.
- effort: Medium hardware and firmware design and validation effort.  ·  risk: Minimal risk; needs to maintain existing button performance and low latency microphone power-up.
- cost: Minor incremental hardware cost and power draw.  ·  latency: No impact after design completion.
- security: N/A; physical input only.


## What it asked for

_Nothing._
