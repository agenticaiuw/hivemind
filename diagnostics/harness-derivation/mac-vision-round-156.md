# Harness derivation — mac-vision — round 156

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Create a dynamic active task and goal prioritization service on the Mac that merges reminders, calendar events, hand-typed tasks, and routine schedules into a unified, ranked list for agents like mac-vision to consume and act on."
- **useful because:** This would allow the owner to have a central, live view of their highest priority work and goals, enabling more purposeful and context-aware automation and assistance across devices and agents.
- **path:** mac-planner → mac-vision → unified → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** background refresh every few seconds
- **cost:** Moderate due to data integration and ranking computations
- **security:** Needs access to personal reminders, calendar, and memory stores; must respect private data boundaries and user consent.
- **missing:** Aggregated data integration layer combining Reminders, Calendar, Memory facts, and Routines; Priority ranking algorithm that includes deadlines, importance, and owner input; API access for agents to read and signal completion

### "Allow the AI Pendant to serve as a context-aware physical input device triggering contextual Mac workflows, with gesture-sensitive payloads beyond the basic button press, interpreted by mac-vision and unified for seamless multi-agent collaboration."
- **useful because:** This enhances the owner's hands-on control over complex, personalized Mac workflows through a physical interface, making automation approachable and reactive to physical presence and intent.
- **path:** pendant → mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** under 100 ms for response to physical input
- **cost:** Low CPU cost, minor firmware update, moderate integration effort
- **security:** Needs secure handling of gesture input, user confirmation for high-impact workflows, and privacy safeguards for contextual triggers.
- **missing:** Gesture payload parsing firmware update on pendant; Interpretation and routing by mac-vision and unified layers; API extension for multi-agent context signals


## Changes it proposed to its own stack

### `interaction` — Implement multi-tiered activation states in mac-vision for computer-use loop: starting with a read-only mode reading accessibility tree without UI mutation; followed by a dry-run simulation mode that silently verifies intended steps and potential focus theft; finally a live mode with full UI control and undo support.
- **owner gets:** This incremental trust model lets the owner verify and control the AI's computer actions safely, building confidence and minimizing mistakes while enabling progressive automation capability.
- effort: Moderate engineering time to build stateful activation layers and monitor fallback behaviors.  ·  risk: If misconfigured, partial activation might produce confusing or failed interactions; requires careful fallback and recovery support.
- cost: Minimal additional compute cost; mostly engineering complexity.  ·  latency: Low latency impact since actions are sequenced carefully.
- security: Enhances security by preventing unplanned destructive UI actions.
- depends on: macOS Accessibility permission granted; computerUse.loopEnabled flag enabled; mac-vision capability to queue and track UI actions

### `integration` — Build an integrated context communication bus between the AI Pendant, mac-vision, mac-planner, and unified agent layers to pass physical gesture triggers, task priorities, and UI action confirmations in real-time.
- **owner gets:** This real-time context bus would enable seamless collaboration and fallback between hardware-triggered physical inputs and software agent decision making, improving responsiveness and reliability of complex automated workflows.
- effort: Significant work to define protocols, implement reliable low-latency messaging, and ensure fault tolerance.  ·  risk: Potential for message loss or delay causing delayed or untriggered workflows; mitigated by retries and state synchronization.
- cost: Low to moderate network and CPU cost.  ·  latency: Critical to be low latency to maintain fluid interaction.
- security: Needs strong encryption and authentication to prevent injection or interception of control messages.
- depends on: Basic pendant button press event telemetry; mac-vision and unified agent process IPC; Reliable network link or USB connection


## What it asked for

_Nothing._
