# Harness derivation — mac-vision — round 180

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Allow the owner to use the pendant button as a secure physical control to approve or cancel complex Mac multi-step workflows triggered by AI agents, with feedback on success or failure"
- **useful because:** Currently, there is no seamless physical control method to confirm or abort AI-driven Mac automation steps without disrupting user interaction or requiring complex gestures. This would leverage the pendant's dedicated button for explicit user approval, improving security and trust while enabling richer automation.
- **path:** pendant → mac-vision → mac-planner
- **model tier:** gpt-5.6-luna for understanding physical signals and integrating state
- **latency:** Realtime, below 2 seconds for confirmation
- **cost:** Low, mostly local event processing costs
- **security:** Requires secure binding of pendant button events to running Mac automation context to prevent spoofing or accidental approvals. All approval events audited and logged.
- **missing:** Firmware support on pendant for multi-state button press recognition feeding to mac-vision; Secure communication channel from pendant to Mac agents; Integration in mac-vision/mac-planner to map button events to running workflows and prompt user as needed

### "Provide an API and system capability to read, interpret, and summarize the Mac's accessibility UI tree live and continuously without pixel capture, enabling real-time semantic understanding of app states and controls for decision-making"
- **useful because:** Currently, despite granted accessibility permissions, the system cannot continuously and semantically read the Mac UI to support autonomous decision-making or safe UI actions without pixel-based screenshots. A structured semantic UI tree feed would enable real-time situational awareness and precision targeting of automation.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna for semantic interpretation and context processing
- **latency:** Stream processing with subsecond refresh
- **cost:** Moderate cost for continuous data flow and interpretation
- **security:** Requires strict permission management, data is local and no screen pixels are captured or sent externally
- **missing:** Efficient accessibility tree streaming infrastructure; Semantic labeling and normalization of UI elements beyond raw accessibility values; Integration with decision-making agents

### "Enable seamless multi-agent coordination and context sharing between mac-vision, mac-planner, browser-extension, and relay-realtime so tasks and UI actions are split to the most capable surface dynamically"
- **useful because:** The owner currently cannot benefit from the collective power of different agent surfaces coordinating in real-time and sharing task context and UI state to maximize efficiency, such as offloading browser work to browser-extension or heavy planning to mac-planner while mac-vision handles direct UI work.
- **path:** mac-vision → mac-planner → relay-realtime → browser-extension
- **model tier:** gpt-5.6-luna for orchestration and context reasoning
- **latency:** Under 500ms for state sync and coordination cycles
- **cost:** Moderate, mostly messaging and context handling costs
- **security:** Requires secure messaging channels and fine-grained permission scoping to avoid cross-surface leaks or unauthorized actions
- **missing:** Real-time surface capability discovery and context sync APIs; Coherent task and action delegation protocols; Dynamic load balancing and state reconciliation algorithms


## Changes it proposed to its own stack

### `interaction` — Add a multi-layer task prioritization and goal management framework across all agent surfaces, enabling dynamic re-prioritization, contextual task merging, and deadline-aware execution scheduling. This would enable mac-vision and other agents to work from a unified, multi-source prioritized task queue rather than ad hoc or clock-bound routines, allowing for meaningful autonomous task planning and execution on the owner's Mac.
- **owner gets:** The owner currently lacks a centralized dynamic priority-based task list that the system can act on autonomously. This framework would let agents understand not just what tasks exist, but their relative importance and urgency, enabling focused action and real results rather than blind schedule triggers.
- effort: Large, requiring new memory service designs, cross-surface coordination, UI for task ranking and override, and interfaces for agent negotiation.  ·  risk: Complexity in synchronization and priority conflicts; risk of disagreement between user intent and agent prioritization. Recovery involves user override and audit logs.
- cost: Moderate increase in context propagation and compute costs for maintaining and querying the dynamic priority queue.  ·  latency: Slight additional latency to refresh and re-rank tasks but fast enough under 1s for decision-making.
- security: Requires careful permissions for agents to write and update tasks; data remains local and encrypted.

### `hardware` — Create a second dedicated physical button or multi-functional, multi-gesture button on the pendant for fine-grained physical input control, separate from microphone activation, to expand physical interaction vocabulary for the owner without mis-trigger risk.
- **owner gets:** The current single-button pendant design limits physical input options severely and restricts event vocabulary for complex context-dependent gestures, leading to latent ambiguity and user frustration. A dedicated second button or advanced multi-gesture would enhance physical interaction richness and reliability.
- effort: Requires redesign and new firmware integration on the pendant hardware and low-level software.  ·  risk: Hardware development risk, user's adaptation to new input methods.
- cost: Significant hardware cost increase, moderate firmware development cost.  ·  latency: Minimal impact, hardware event processing is fast.
- security: Low risk, physical button controlled directly by user.

### `context` — Develop a unified, shared memory projection accessible across all agent surfaces that supports mutable high-confidence task, goal, and context facts with automatic ranking and aging, enabling consistent, lived-in context for goal-driven agent action.
- **owner gets:** Currently, disconnected context and lack of authoritative mutable facts prevent coherent multi-agent collaboration and goal-driven autonomy. A unified memory projection would let the owner experience consistent and contextually aware assistance from any surface or agent, improving task completion and reducing fragmented interactions.
- effort: Large system design and implementation involving synchronization, conflict resolution, secure access, and efficient local caching.  ·  risk: Complex synchronization bugs and potential data leakage if access controls are mishandled. Moderated by rigorous testing and audit trails.
- cost: Noticeable increase in resource and bandwidth usage for context sync and updates but essential for scale.  ·  latency: Possible increased latency on context refresh but tolerable with delta updates and caching.
- security: Requires strong encryption and access management to protect ownership privacy.


## What it asked for

_Nothing._
