# Harness derivation — mac-vision — round 154

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Have a fully safe and reversible mac-vision computer-use loop that can operate without stealing mouse focus or using screen pixels, to automate complex Mac workflows through UI controls."
- **useful because:** This would let the owner delegate multi-step Mac workflows to the AI safely, with guaranteed non-destructive automation and no disruptive focus theft, improving productivity dramatically.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-4.1-mini
- **latency:** low-latency interactive feedback expected (seconds)
- **cost:** Primarily API calls for UI tree extraction and action dispatch, minimal extra cost beyond current run.
- **security:** Must have a macOS Accessibility permission securely granted only to a signed binary, clear action classifications, and explicit confirmations for destructive or irreversible operations.
- **missing:** macOS Accessibility permission for the agent binary; Expanded mac-run-actions toolset to include soft confirmation and reversibility; A robust UI control discovery and action planning engine beyond shallow action lists

### "Have durable, prioritized, and context-aware goal/task memory integrated with day planning and voice commands, to manage what the owner really wants done in a dynamically updated way."
- **useful because:** Without a durable and ranked task memory store, the owner sees disjointed task reminders only based on calendar/deadline and manually entered tasks, limiting usefulness of AI planning and automation.
- **path:** mac-planner → unified → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** background or low-latency depending on user interaction needs
- **cost:** Storage reads/writes for task data, priority ranking, and context integration lightly dominate costs.
- **security:** Tasks may include sensitive user data, so encryption and user control of memory access is critical.
- **missing:** Durable task goal persistence with dependency and priority metadata; Context graph integration for richer task understanding; Voice input integration with task memory

### "Enable a seamless multimodal workflow where the owner can issue voice commands to start complex Mac tasks, have mac-vision plan and preview UI actions for approval via spoken summaries, and execute them safely with undo support, integrating voice, UI, and memory layers."
- **useful because:** This would give the owner a natural conversational way to automate and control Mac workflows that span multiple applications and UI elements, with explicit preview and undo steps for safety and confidence.
- **path:** relay-realtime → mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** Interactive real-time with some background planning (seconds to a minute).
- **cost:** Costs dominated by AI inference for natural language understanding, UI planning, and state management.
- **security:** Requires strict access control to prevent malicious or unintended automations; confirmation steps reduce risk.
- **missing:** Inter-layer integration workflows between voice command capture, Mac UI planning, and stateful task memory; Undo/redo logic embedded in mac_run_actions or mac_delegate; Natural language summarization for spoken previews of UI plans

### "Enable the mac-vision loop to detect and alert for dangerous UI state changes or irrecoverable errors during long-running Mac automation, pausing execution and asking for owner confirmation before proceeding."
- **useful because:** Safe automation requires preventing unexpected destructive states or stuck conditions that the owner cannot recover from without intervention.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** Real-time or near real-time detection and alert (under a second).
- **cost:** AI checks on UI state changes and error logs; minimal external cost.
- **security:** Automation must limit false positives while protecting against unwanted system changes; owner intervention guards against misuse.
- **missing:** UI state anomaly detection algorithms integrated with accessibility tree input; Alerting and pausing mechanisms within mac-vision loop; Owner confirmation handlers

### "Implement a context-aware, incremental UI automation planner that uses partial accessibility tree reads and inferred goal state to reduce latency and increase reliability of long multi-step Mac workflows."
- **useful because:** Current automation with full UI tree snapshots is latency-heavy and may miss dynamic UI changes; incremental context tracking improves responsiveness and success.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-4.1-mini
- **latency:** Milliseconds to a second per incremental update.
- **cost:** Compute cost for partial tree analysis and AI inference, replacing full snapshot reliance.
- **security:** Must not leak sensitive UI states outside local processing; incremental updates reduce exposure window.
- **missing:** Incremental accessibility tree diffing APIs; Goal state inference algorithms linked to partial UI context

### "Allow the owner to create custom multi-step UI automation scripts using natural language input, which are then compiled by an AI planner into mac_run_actions for execution on the Mac, with real-time feedback and error handling."
- **useful because:** Gives the owner the ability to automate repetitive or complex tasks without programming knowledge, enhancing productivity.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Interactive, seconds-level feedback expected.
- **cost:** AI model inference for natural language understanding and plan compilation dominate.
- **security:** Must validate generated scripts to prevent harmful commands; confirmation steps mitigate risk.
- **missing:** Natural language to multi-step action plan compiler; Execution monitoring and error reporting integration


## What it asked for

_Nothing._
## Its own summary

Proposed key capabilities around safe, reversible mac-vision UI automation with accessibility permissions, integrated goal/task memory with prioritization, multimodal voice-to-Mac workflows with preview and undo, anomaly detection in automation, incremental UI state planning, and natural language custom automation scripting. Also proposed adding a second pendant button to improve physical gesture confirmation reliability.

**Biggest unknown:** The most critical unmet need remains a securely granted macOS Accessibility permission for the running mac-vision binary, enabling safe, reliable UI interaction without focus stealing or pixel capture.

