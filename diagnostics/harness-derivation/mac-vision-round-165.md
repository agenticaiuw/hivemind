# Harness derivation — mac-vision — round 165

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full mac-vision computer use loop with macOS Accessibility permission granted, to allow UI reading and reversible interface actions without pixel capture or focus theft."
- **useful because:** Allows proactive, context-aware automation of Mac control, unlocking powerful AI help with the owner's daily computer tasks without disruptive UI effects.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** realtime
- **latency:** sub-second to a few seconds per step
- **cost:** moderate API usage; mostly local compute and permission dependent
- **security:** Requires owner macOS Accessibility grant to trusted binary; no pixel capture; full audit and telemetry; reversible steps; opt-in only
- **missing:** UI-focused confirmation interaction design; Owner training for granting and revoking Accessibility permission

### "Enhance the pendant button moment marker system (s10-l3xe record) to encode multiple contextual moment types or confirmation signals securely, allowing the owner to mark moments or confirm agent actions beyond start/stop conversation, without requiring multiple physical button gestures."
- **useful because:** The pendant has a single physical button with limited gesture vocabulary. Extending the payload allows richer contextual inputs and confirmations without adding physical complexity or latency. It empowers the owner with more control and safety for AI-driven interactions.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** sub-second marker recognition and action
- **cost:** minimal flash writes and protocol support; negligible power
- **security:** Ensures owner physical confirmation; prevents unwanted agent actions; respects existing single-button hardware constraints
- **missing:** Protocol for encoding multiple moment types within existing marker storage; Agent handling logic for new confirmation payloads

### "Provide a secure multi-step interaction confirmation mechanism combining the pendant button's physical press with mac-vision's UI context detection, to ensure high-risk actions are confirmed visually and physically by the owner before execution."
- **useful because:** Enables safe automation of potentially destructive or impactful actions on the Mac by integrating physical owner control with AI context awareness. Minimizes accidental actions and maximizes owner confidence in automation.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** a few seconds per confirmation step
- **cost:** low; mostly local software coordination
- **security:** Prevents unauthorized actions without owner physical consent; requires reliable context detection; fallback if button press unavailable
- **missing:** Integration logic for combining pendant button input with UI context state; User interface concepts for confirming actions across surfaces

### "Develop a descriptive, segmented UI exploration and action language for mac-vision using macOS accessibility tree, allowing fine-grained, fail-safe UI element identification and interaction with fallback avoidance of focus stealing, pixel capture, or disruptive clicks."
- **useful because:** This enables mac-vision to reliably automate Mac UI tasks by understanding and navigating the accessibility tree in detail, safely interacting with UI elements in a way that respects the owner's workflow and prevents disruptive behavior.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** seconds to parse and decide steps
- **cost:** local computation, low API cost
- **security:** No pixel capture, uses accessibility only; careful interaction needed to avoid unintended clicks; owner permissions required
- **missing:** Detailed UI segment/element ontology; fallback action detection and avoidance; Extensible interaction scripting language for mac-vision

### "Allow the owner to delegate complex multi-step computer tasks that involve coordination across multiple applications with uncertain or evolving steps, with a dialogue-style planning and execution system that verifies intentions at each step and allows interruption or modification on the fly."
- **useful because:** Owners often face workflows that cannot be reduced to a small fixed list of steps and need AI assistance in planning, adapting, and executing tasks interactively to reduce cognitive load and interruptions.
- **path:** mac-vision → mac-planner → relay-realtime → dashboard
- **model tier:** realtime
- **latency:** variable, minutes for complex tasks
- **cost:** moderate API calls with local execution, incremental planning
- **security:** Requires careful intent verification to avoid errors and unwanted changes; needs UI context confirmation; owner input at each stage; falling back to safe states
- **missing:** Advanced multi-step task management and dialogue system beyond mac_delegate; Real-time UI state validation and user confirmation mechanisms

### "Create an AI-powered personalized and context-aware continuity system on the Mac and pendant that remembers owner preferences, ongoing projects, and interaction threads across sessions and surfaces, enabling seamless switching and resuming of tasks and conversations without losing context or requiring manual state saves."
- **useful because:** Owners frequently switch devices and contexts throughout the day, losing momentum and context. An AI system that preserves and recalls this context across hardware and software boundaries would improve productivity, reduce repetition, and feel truly responsive to the owner's working style.
- **path:** mac-vision → pendant → relay-realtime → mac-planner → dashboard
- **model tier:** realtime and background mix
- **latency:** quick recall for immediate context, slower updates in background
- **cost:** moderate storage and computation for context graphs and retrieval
- **security:** Requires secure storage of sensitive data (projects, preferences). Needs robust privacy controls and owner override.
- **missing:** Cross-surface context memory synchronization; Task and project state modeling beyond simple facts; Contextual session stitching logic


## Changes it proposed to its own stack

### `integration` — Integrate the pendant button input system with mac-vision's UI accessibility context awareness to enable seamless owner confirmation of high-impact or sensitive Mac actions by requiring physical confirmation gestures alongside UI context conditions, minimizing accidental or undesired actions.
- **owner gets:** This change enhances safety and control for the owner by combining physical presence confirmation with AI context awareness, avoiding destructive or unwanted automation mistakes.
- effort: Medium engineering effort to map pendant input to context UI states and handle confirmation workflows.  ·  risk: If poorly designed could cause owner frustration or blocking; recovery by fallback to explicit owner override.
- cost: Low software development cost.  ·  latency: Minimal latency, mostly local coordination.
- security: Increases security by requiring physical confirmation for risky actions.
- depends on: computerUse.loopEnabled; pendant_store_enqueue_mark


## What it asked for

_Nothing._
