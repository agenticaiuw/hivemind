# Harness derivation — mac-vision — round 253

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Create a transparent Mac-vision UI state verification and discrepancy reporting capability that continuously observes actual Mac UI states during task execution and alerts the owner or relevant agents if the visible state diverges from the planned workflow state or expected outcomes."
- **useful because:** This increases trust and reliability of automated Mac interactions by detecting missteps, UI changes, or unexpected dialogs early and allowing intervention before task failure becomes costly.
- **path:** mac
- **model tier:** background
- **latency:** seconds to minutes depending on verification frequency
- **cost:** Moderate CPU for polling and state comparison, low network cost for alerts
- **security:** Strict on-device analysis preferred. Alerts can be encrypted and only shared with owner or trusted agents to prevent leakage of screen content.
- **missing:** A reliable UI snapshot and state diff mechanism accessible to mac-vision in the current accessibility model.; An alerting channel to the owner, either via pendant audio or UI notifications.; Policies for acceptable UI divergence and escalation.

### "Provide a continuous Mac desktop context summarization and briefing readout capability that synthesizes calendar, reminders, ongoing tasks, and recent communications into an adaptive, spoken briefing for the owner each morning."
- **useful because:** This briefing enables the owner to start the day informed of what needs attention and recent changes without manually checking multiple apps and sources, saving time and improving focus.
- **path:** mac
- **model tier:** realtime
- **latency:** 1-2 minutes for briefing prep
- **cost:** Moderate CPU and LLM cost for summarization and adaptive briefing generation
- **security:** All briefing content handled locally or encrypted when shared; owner consent required for any cloud-based processing.
- **missing:** Unified data access API for calendar, reminders, emails, and task sources.; Adaptive briefing synthesis model tuned for the owner's preferences and priorities.; Speech generation and output on the pendant or Mac speakers.


## Changes it proposed to its own stack

### `integration` — Build a 'Mac Work Task Broker' service that consolidates all owner work intent signals for the Mac into a single prioritized, actionable task list API and UI. It exposes this list to all Mac surface agents, including mac-vision, planner, and delegate, enabling coordinated multi-agent Mac task execution.
- **owner gets:** The owner will have clear visibility of what work is outstanding on their Mac and the system can optimally delegate fragments of work to the right agent, avoiding duplicated effort or forgotten tasks.
- effort: Large engineering effort to integrate memory, day plan, workbench, and job state sources. Requires UI and API design.  ·  risk: Data consistency issues if integration is incomplete; owner confusion if task list presentation is unclear.
- cost: Moderate cloud and local compute cost. Storage needed for additional state.  ·  latency: Adds minor latency in task retrieval but speeds up agent decision making overall.
- security: Sensitive task data handled with strict access controls, local storage preferred.
- depends on: Proposed capabilities to gather and prioritize Mac work tasks; Existing routes GET /memory/facts, GET /day-plan, GET /workbench/contexts

### `hardware` — Add a physical 'task progress confirmation' button or switch on the pendant that the owner can press to directly signal task completion or step approval to the Mac-vision agent. This bypasses UI ambiguity and increases task reliability by adding a trusted physical interaction channel.
- **owner gets:** The owner gains clear, direct, low-effort confirmation of task progress without needing to manually confirm steps via voice or UI, increasing confidence and reducing frustration in multi-step tasks.
- effort: Hardware design and manufacturing update. Firmware updates to handle the new input and report it to the Mac-vision system. Integration on the Mac side to listen and act accordingly.  ·  risk: Hardware feature failure may cause missed confirmations, but the physical button is straightforward and low risk.
- cost: Small increase in hardware cost and power usage due to new input and processing.  ·  latency: Near real-time task progress feedback, reducing delays from uncertainty.
- security: Trusted direct owner input reduces risk of false positives or unintended actions.


## What it asked for

_Nothing._
