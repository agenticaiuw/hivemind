# Harness derivation — mac-vision — round 167

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to state and prioritize current tasks/goals in a structured way the Mac vision loop can read and act on."
- **useful because:** Without a live prioritized list of open tasks and goals, the Mac vision loop cannot know what to do next or prioritize computer actions. A structured, durable task/goal store that is integrated with Mac reminders and input from the owner would enable more useful autonomous Mac assistance.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** Seconds to minutes for updates
- **cost:** Low cost; mostly API and UI integration
- **security:** Task data is private but stored locally; access controlled by normal system permissions.
- **missing:** Structured task/goal store integrated with Reminders and manual input; APIs to read and update tasks/goals from Mac vision loop

### "Provide a local, taggable, and searchable knowledge graph for the owner's Mac tasks, reminders, notes, and goals that all agents can access and update contextually."
- **useful because:** This would create a unified workspace memory that spans tasks, reminders, and goals with flexible connections and queries, allowing better awareness and coordination across Mac vision, planner, and pendant agents. It enables smart linking of work items, context-driven action suggestions, and holistic understanding of owner's projects that current isolated stores lack.
- **path:** mac-vision → mac-planner → unified → pendant
- **model tier:** background
- **latency:** seconds to minutes for updates and queries
- **cost:** Moderate due to storage and indexing overheads
- **security:** Private knowledge graph stored locally; encryption and access controls essential.
- **missing:** Unified graph store and APIs for tasks, reminders, notes, goals; Agent integration for contextual updates and queries

### "Give the Mac vision loop the ability to learn and adapt its UI interaction strategies over time based on owner feedback and success/failure outcomes."
- **useful because:** This would improve the reliability and helpfulness of automated Mac UI control by adapting to personalized usage patterns, applications, and workflows. It reduces repeated errors and unwanted interruptions by learning what works or does not with the owner's preferred apps and UI states.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** minutes to hours to integrate feedback and update strategies
- **cost:** Moderate, involving feedback capture, storage, and model tuning.
- **security:** Feedback and usage data stored locally with strong privacy guarantees.
- **missing:** Adaptive learning module focused on UI interaction outcomes; Feedback capture and evaluation framework in Mac vision loop

### "Enable mac-vision to coordinate with the pendant and relay agents for real-time spoken status and confirmation of ongoing Mac UI interactions requiring owner attention or approval."
- **useful because:** This would close the communication loop between the Mac vision loop, the wearable pendant, and the relay service to provide the owner verbal awareness and prompt for intervention or approval as needed, greatly improving transparency and trust in autonomous Mac control.
- **path:** mac-vision → relay-realtime → pendant
- **model tier:** realtime
- **latency:** milliseconds to seconds for spoken prompts and responses
- **cost:** Low to moderate, mostly messaging and TTS API cost.
- **security:** Spoken content is private and ephemeral, secured by system access controls and encrypted communications.
- **missing:** Seamless voice relay and integration capability among mac-vision, pendant, and relay agents; Real-time spoken status and prompt message formats and routing


## Changes it proposed to its own stack

### `interaction` — Implement a typed UI interaction policy for the Mac vision loop that prevents fallback to naked mouse clicks which steal focus or cause unwanted UI changes silently.
- **owner gets:** This makes the vision loop safer and less intrusive, preventing accidental focus changes and UI disruptions when accessibility actions fail, improving trust and reliability.
- effort: Medium engineering effort; working closely with macOS accessibility APIs and event handling.  ·  risk: Potential temporary regressions in UI control fidelity if fallback is disabled, mitigated by clear user communications and undo capabilities.
- cost: Low  ·  latency: None
- security: Improves security by eliminating silent mouse click fallback.
- depends on: macOS Accessibility permission granted to AI Pendant Agent


## What it asked for

_Nothing._
## Its own summary

Proposed enabling the Mac vision loop for pixel-free accessibility-driven Mac control, structured task and goal management, typed UI interaction policies, a unified local knowledge graph, adaptive UI action learning, and real-time spoken status coordination. Identified key missing elements: macOS Accessibility permission for AI Pendant Agent binary, task prioritization context, and integration for safe, effective automation. Awaiting these foundational steps before further operationalization.

**Biggest unknown:** Whether the owner will grant macOS Accessibility permission to the AI Pendant Agent binary to unlock the vision loop's accessibility control capabilities.

