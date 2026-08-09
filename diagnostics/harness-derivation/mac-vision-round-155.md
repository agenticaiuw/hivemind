# Harness derivation — mac-vision — round 155

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable the mac-vision computerUse accessibility-driven loop with multi-step reversible UI actions controlled by owner-stated goals and integrated with Mac task state."
- **useful because:** Allows the system to act fully on the Mac UI in a safe, reversible way without stealing focus or using pixel capture, unlocking complex workflows and task completion across apps based on owner priorities.
- **path:** mac-vision → mac-planner → unified → relay-realtime
- **model tier:** gpt-5.6-luna for deep planning and orchestration; gpt-4.1-mini for real-time loop decisions
- **latency:** Realtime UI interactions within 1-3 seconds per step, orchestration planning within 5-10 seconds for multi-step tasks
- **cost:** Moderate cost due to complex planning and state tracking; amortized by improved automation success and safety
- **security:** System requires macOS Accessibility permission for the running binary; all UI actions are reversible and observed with receipts; no pixel capture or screen recording.
- **missing:** Owner manual grant of macOS Accessibility to AI Pendant Agent binary; Owner manual enabling of computerUse.loopEnabled and optionally visionUploadConsented

### "Invent and implement an owner goal prioritization and inter-agent task distribution system based on existing and newly derived tasks, calendar events, and reminders, with support for priority scoring and deadlines to drive agent action coordination."
- **useful because:** Currently, the system has only hand-typed or clock-scheduled tasks with no coherent prioritization or inter-agent goal consensus. A unified goal priority system will let agents work on the most important goals efficiently and avoid duplicated or deprecated tasks.
- **path:** mac-planner → mac-vision → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** 5-15 seconds per new task assessment and routine periodic re-ranking
- **cost:** Low to moderate depending on complexity of agenda and number of active tasks
- **security:** Tasks and priorities contain sensitive owner data; all storage and interchange require secure, private storage and strict access control.
- **missing:** An API to insert new ranked tasks and update priorities across agents; A shared task graph or agenda store with scoring and ordering

### "Add undo and receipt tracking infrastructure for all mac-run-actions and delegated UI actions to ensure safe, reversible computer control with logging and visual feedback on success or failure."
- **useful because:** Users can trust the system to try actions knowing they can be reverted cleanly if needed, and the system can confirm what happened accurately, increasing confidence especially in complex Mac workflows.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** Undo/receipt queries should respond within 1-2 seconds, actions within 1-3 seconds.
- **cost:** Low overhead on existing job status framework and action receipts.
- **security:** Execution logs and undo information are sensitive and must be securely stored and access-controlled.
- **missing:** A durable job receipt and undo tracking store with rich metadata; Integration in UI actions to log and validate each step; User confirmation or notification feedback channel

### "Create an adaptive action broker for computerUse loop: for each requested UI task, decide to use mac_run_actions if simple, or fallback to mac-vision accessibility tree UI steps for complex/ambiguous tasks, with undo support and contextual recommendations."
- **useful because:** Maximizes success and efficiency of automated Mac UI interactions by combining high-level API actions with fine-grained UI control. Enables robust fallbacks and dynamic response to UI changes and task ambiguity.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna for planning, gpt-4.1-mini for loop decisions
- **latency:** Fallback or complex task decisions within 3-5 seconds, real-time loop responsiveness under 1 second for clicks and reads.
- **cost:** Moderate due to AI planning overhead and multi-tool coordination.
- **security:** All actions reversible and logged. Complex UI actions mean careful risk management and owner permission.
- **missing:** A decision engine to classify and route tasks between mac_run_actions and mac-vision UI actions; Integration with undo/receipt system and task priority system for context; Per-action risk scoring and fallback triggers

### "Provide a multi-modal, context-aware Mac assistant that uses voice commands through the pendant mic, visual accessibility automation, and typed Mac app controls cooperatively for seamless context switching and error recovery."
- **useful because:** The owner can switch effortlessly between talking to the pendant to command Mac apps, seeing UI feedback, and typed control, all integrated contextually to recover from failures and maintain fluent multi-step workflows.
- **path:** mac-vision → relay-realtime → mac-planner → unified
- **model tier:** gpt-5.6-luna and gpt-4.1-mini in tandem
- **latency:** Sub-second responsiveness to spoken commands and under 5 seconds for multi-step visual recovery actions
- **cost:** Moderate due to multi-modal integration and fallback orchestration
- **security:** Sensitive voice and UI data; requires strict permissions and encrypted communication channels
- **missing:** Fine-grained permission model to allow voice and UI control; Synchronization protocols for voice, UI, and typed command states; Error recovery and fallback planning across modalities

### "Empower the AI Pendant Agent with event-driven UI snapshotting on the Mac that records accessibility tree deltas and integrates with the owner's working memory for instant context-aware action recommendations."
- **useful because:** The system gains real-time context-driven insights from UI state changes without intrusive or resource-heavy full screen capture, enabling precise, situation-aware assistance and automation.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna for memory and context reasoning
- **latency:** Under 2 seconds for snapshot delta capture, under 5 seconds for integrated memory update
- **cost:** Low to moderate, mostly memory and context graph updates
- **security:** Sensitive information about UI state requires strong access control and encryption
- **missing:** Event-driven accessibility tree delta capture mechanism; Context graph schema to store UI state deltas and integrate with memory

### "Develop an integrated goal and task lifecycle manager with deadlines, dependencies, and progress monitoring across all agents and surfaces, accessible and modifiable by voice, text, and UI automation."
- **useful because:** Ensures the owner always knows what is being worked on, can modify priorities dynamically, and sees real progress feedback from multiple agents working cooperatively, improving coordination and productivity.
- **path:** mac-planner → mac-vision → relay-realtime → unified
- **model tier:** gpt-5.6-luna
- **latency:** 10 seconds for updates, near real-time progress feedback
- **cost:** Moderate, layered storage and API complexity
- **security:** Sensitive task and goal data needs secure storage and controlled modification privileges
- **missing:** A shared task lifecycle API with support for dependencies and progress; Cross-agent synchronization mechanisms; UI and voice interfaces for lifecycle handling


## Changes it proposed to its own stack

### `hardware` — Design and build a next-generation pendant device with multiple physical buttons and a gesture recognizer, more RAM and flash, enhanced I2S audio peripherals, a dedicated GPU for vision tasks, and a second CPU core for local AI inference.
- **owner gets:** Gives the owner more expressive and reliable physical controls, higher quality and lower latency audio, local processing power to support offline AI, and the ability to handle more complex vision and sensor inputs without relying on the Mac or relay.
- effort: High: requires hardware design, firmware overhaul, supply chain, and integration testing.  ·  risk: Hardware defects or delays could stall system progress; firmware bugs could degrade user experience; mitigated by rigorous testing and phased rollout.
- cost: Significant additional BOM cost (>$100) and power increase; offset by better user experience and device longevity.  ·  latency: Lower latency for on-device AI and audio processing; more responsive physical controls.
- security: More on-device processing reduces data exposure; more complex hardware requires careful security design.


## What it asked for

_Nothing._
