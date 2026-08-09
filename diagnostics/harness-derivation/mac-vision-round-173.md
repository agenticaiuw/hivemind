# Harness derivation — mac-vision — round 173

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "The owner can ask the Mac-vision agent to safely operate any Mac graphical application or UI entirely by accessibility API reads and commands, without stealing focus or relying on pixel scraping."
- **useful because:** This would enable robust, focus-respecting, reversible control of any app the owner runs, vastly expanding the owner's ability to delegate computer tasks while preserving privacy and multitasking integrity.
- **path:** mac-vision → mac-planner → relay-realtime → pendant → browser-extension
- **model tier:** gpt-4.1-mini
- **latency:** real-time interactive (sub-second latency)
- **cost:** Moderate API cost from local planning and accessibility queries, minimal cloud cost; no pixel capture or image models.
- **security:** Requires strict macOS Accessibility permission for the running binary; no pixel capture means UI content never leaves device without explicit consent; focus not stolen or changed arbitrarily; reversible and safe commands only.
- **missing:** macOS Accessibility permission grant for the running binary; local interrupt-aware incremental macOS accessibility tree UI interaction APIs; Owner UI to review and confirm planned multi-step UI interactions before execution; Real-time context projection combining task list, UI state, and owner intent

### "The owner can ask to see a continuously updated task list merged from their reminders, calendar, and any expressed natural language goals or tasks, directly integrated into the Mac-vision agent's context for prioritization and clear computer action planning."
- **useful because:** This enables the Mac-vision agent to prioritize what actually matters to the owner, improving decision-making for computer actions and reducing wasted focus on irrelevant tasks or stale information.
- **path:** mac-vision → mac-planner → relay-realtime → pendant → browser-extension
- **model tier:** gpt-5.6-luna
- **latency:** seconds (background refresh)
- **cost:** Low API cost mostly reading Apple Reminders/Calendar via EventKit plus natural language parsed tasks
- **security:** Needs read permission to Reminders and Calendar; natural language tasks are stored securely on-device only; owner controls scope.
- **missing:** Consolidated owner task context store that merges EventKit data with typed task facts; Owner UI or voice commands to add, update, or prioritize tasks and goals; Authorization for Apple EventKit reads from the running binary

### "The owner can ask the Mac-vision agent to carry out complex, multi-step workflows by natural language goal specification, with real-time progress reporting and the ability to confirm or abort partial steps."
- **useful because:** This allows owners to delegate truly complex computing tasks, such as editing documents, configuring settings, or running chained commands, which single short commands can't express. It increases trust and user control through confirmations.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** multi-minute (long-running background execution)
- **cost:** Moderate to high API cost for planning, execution monitoring, and step confirmation dialogue
- **security:** Requires careful design to avoid destructive unapproved actions; explicit user confirmation for high-impact steps essential; access control enforced.
- **missing:** A multi-step executable planner integrated with accessibility API actions; User interface for review, confirmation, and control of ongoing workflows; Persistent state storage for partial workflow progress and rollback

### "The owner can ask the Mac-vision agent to provide always-on, context-aware assistance by monitoring the Mac's UI for key state changes and suggesting shortcuts or automations proactively based on recurring patterns or recognized workflows."
- **useful because:** This empowers the owner to save time and reduce repetitive work without constantly instructing the agent, making the AI more helpful and anticipatory in daily use.
- **path:** mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** gpt-5.6-luna
- **latency:** seconds (background monitoring)
- **cost:** Moderate API usage due to ongoing context analysis; mostly local compute; low network bandwidth.
- **security:** Host privacy-sensitive data on-device; no proactive actions execute without explicit owner confirmation; logs are encrypted.
- **missing:** Continuous UI event subscription layer for mac-vision accessibility tree changes; Pattern recognition models trained on owner workflows; Owner UI for reviewing and enabling suggested shortcuts


## Changes it proposed to its own stack

### `hardware` — Add a second physical button to the pendant device with distinct GPIO input, interrupt-driven and debounce-filtered, mapped to an easily programmable interrupt handler in firmware.
- **owner gets:** This would enable a wider range of user gestures and interactions, making the device more versatile for things like multi-step control sequences, explicit confirmations, or mode switching without overloading the single existing button.
- effort: Moderate hardware and firmware changes; redesign of the pendant enclosure and PCB necessary; updates to firmware button handling code.  ·  risk: Physical redesign could introduce manufacturing delays; new button may confuse owners initially until trained; firmware bugs may cause unintended button behavior.
- cost: Small increase in bill of materials cost and assembly complexity; negligible power impact.  ·  latency: No impact on latency.
- security: None specifically; physical security unchanged.

### `firmware` — Implement a comprehensive physical button gesture recognizer on the pendant firmware to distinguish single press, double press, long press, and press-and-hold gestures on the existing single button.
- **owner gets:** This increases the input vocabulary of the pendant without needing extra hardware, allowing more commands or modes accessible from a single button, improving user control and flexibility with minimum cost.
- effort: Moderate firmware development and testing; update button event handling and debounce logic; add state machine for timing gestures.  ·  risk: Incorrect gesture recognition could cause user frustration; possible battery life impact due to more complex firmware logic.
- cost: No hardware cost increase; negligible power draw increase.  ·  latency: No impact on interaction latency.
- security: None specifically; input recognition changes only.

### `integration` — Integrate the owner's natural language task list (typed facts, hand-entered tasks) with the Mac reminders and calendar event readout into a unified context projection for all Mac-vision agent planning and prioritization.
- **owner gets:** This centralizes and updates all actionable information the Mac-vision agent needs to prioritize and decide what to automate or suggest next, reducing friction and discarded context.
- effort: Moderate software integration effort to merge multiple data sources and keep them in sync; update context projection and prompt state.  ·  risk: Potential syncing bugs causing stale or inconsistent context; user confusion if task sources conflict.
- cost: Low; mostly internal server and agent CPU usage.  ·  latency: No direct impact; context updates occur asynchronously.
- security: Needs careful handling of private reminders and calendar data; encryption and local storage recommended.
- depends on: Authorization for Apple EventKit reads from the running binary; Owner permission to unify and read tasks

### `interaction` — Build an owner-facing user interface integrated in the pendant's companion Mac app, to review, approve, and control multi-step computer automation workflows planned and executed by mac-vision.
- **owner gets:** This provides the owner transparency, safety, and real-time control over actions the AI takes on their Mac, building trust and preventing unintended changes or errors.
- effort: Moderate UI development on the Mac app; message passing implementation; integration with mac-vision workflow management.  ·  risk: UI complexity may overwhelm owner if not well designed; delays in approval could slow automation.
- cost: Minimal; mostly development effort.  ·  latency: Potentially increases time before automation executes due to review step.
- security: Critical for safety to prevent unauthorized or runaway automation; UI access must be securely gated.
- depends on: Computer use loop enabled with accessibility permission; Multi-step Mac delegate capabilities


## What it asked for

_Nothing._
