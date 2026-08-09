# Harness derivation — mac-vision — round 186

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Provide the owner with a unified, AI-prioritized actionable work queue that aggregates owner-stated tasks, scheduled routines, and system-discovered actions on the Mac."
- **useful because:** Currently, there is no integrated prioritized task list that the owner or any agent can act on. This would enable the mac-vision agent to know what to do next, improving usefulness and aligning actions with owner intent.
- **path:** mac-vision → mac-planner → unified
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** low to moderate, dominated by aggregation and ranking logic
- **security:** tasks data remains on local machine or trusted relay; no sensitive data exposed without consent
- **missing:** persistent task storage; task ranking algorithm; task extraction from diverse inputs

### "Enable a secure mac_vision_loop accessibility-driven UI interaction loop that can run with granted macOS Accessibility permissions, issuing safe background UI control actions without stealing focus or needing screen recording."
- **useful because:** This would be the single most useful feature enabling robust, precise automation and UI interaction on the Mac, surpassing crude pixel-based control and unsafe cursor steals.
- **path:** mac-vision
- **model tier:** realtime
- **latency:** milliseconds to seconds
- **cost:** moderate compute for planning, minimal for execution
- **security:** Requires explicit owner permission for accessibility; strict limits to prevent accidental destructive actions; local execution is critical
- **missing:** owner permission grant UX; safe UI action policy; accessibility tree watcher integration

### "Create a shared multi-agent workflow context and coordination mechanism between mac_delegate and mac_vision_loop for handling complex multi-step workflows involving UI interactions that cannot be resolved by short action lists."
- **useful because:** Complex Mac tasks often span multiple steps, apps, or ambiguous goals. Coordinated shared context would allow distributed agents to collaborate seamlessly and reliably.
- **path:** mac-vision → mac-planner → mac-delegate
- **model tier:** background
- **latency:** seconds to minutes
- **cost:** low to moderate
- **security:** Workflow state stored locally with owner control; clear expiration and cleanup policies
- **missing:** workflow state persistence; inter-agent communication protocols; API extensions for shared context

### "Let the owner create and manage a prioritized task list directly using natural language commands via voice or text, which integrates into the unified Mac work queue and can be accessed by the mac-vision agent as immediate context for UI actions."
- **useful because:** Currently the owner cannot dynamically and naturally express tasks to do on the Mac in a way that agents can act on immediately. This greatly enhances owner-agent collaboration and task management.
- **path:** mac-vision → mac-planner → unified
- **model tier:** realtime
- **latency:** seconds
- **cost:** low, typical for voice/text NLP task parsing
- **security:** Commands processed locally or with consent; no exposure without confirmation
- **missing:** natural language task parsing; real-time task injection into task queue

### "Enable the mac-vision agent to securely stream and process live microphone audio from the pendant with high fidelity for voice command recognition and live feedback, preserving 24 kHz superwideband audio quality."
- **useful because:** The owner specifically wants high-fidelity audio path end-to-end on the pendant to enable superior voice interaction quality compared to typical lower bandwidth paths.
- **path:** mac-vision → pendant
- **model tier:** realtime
- **latency:** milliseconds to seconds
- **cost:** moderate, dominated by real-time audio processing and streaming costs
- **security:** Audio data must be strictly controlled and encrypted to respect owner privacy, with user control over when streaming is enabled.
- **missing:** high-fidelity audio driver; streaming infrastructure; real-time processing on pendant and mac-vision

### "Provide a visual multi-step task debugger and interaction recorder for mac-vision loops, capturing accessibility events, UI state changes, and owner approvals for transparent auditing and troubleshooting of automation workflows."
- **useful because:** Owners and developers need a clear way to see how the AI interacts with the Mac UI, diagnose issues, and confidently trust automation behaviors, especially for complex or critical tasks.
- **path:** mac-vision → dashboard
- **model tier:** background
- **latency:** seconds
- **cost:** moderate, requires event logging and UI state snapshot infrastructure
- **security:** All recorded data must be stored securely and with owner consent, with options to limit retention and sharing.
- **missing:** event capture hooks; UI state snapshot capabilities; visual dashboard UI for inspection; consent and privacy controls

### "Create a real-time visual context mirroring feature to broadcast the mac-vision's accessibility UI tree view and live visual state securely to the owner's trusted dashboard or companion devices for remote monitoring and manual override."
- **useful because:** Provides the owner transparency and control over AI-driven UI actions on the Mac, enabling remote support, manual intervention, and trust-building in automation.
- **path:** mac-vision → dashboard → relay
- **model tier:** background
- **latency:** seconds
- **cost:** moderate due to streaming bandwidth and secure transport
- **security:** Data must be encrypted, access-controlled, and only shared with trusted devices; sensitive info filtered or masked.
- **missing:** accessibility tree streaming infrastructure; secure relay channel; dashboard UI support for visual state


## Changes it proposed to its own stack

### `interaction` — Implement a smart priority ranking and filtering system for owner tasks and routines that includes urgency, context-awareness, deadlines, and interdependencies beyond structural rules.
- **owner gets:** The owner currently has no way to see or act on a truly prioritized, contextually ranked list of tasks, causing missed or delayed critical items and inefficiency.
- effort: moderate, requires design of ranking heuristics and integration into task aggregation  ·  risk: incorrect rankings might confuse or mislead owner temporarily; can revert to simple lists
- cost: low  ·  latency: minimal
- security: none
- depends on: unified prioritized Mac work queue capability


## What it asked for

### `c19-i451` (context) — computerUse.loopEnabled
- why: To confirm if the mac_vision computer use loop can be safely enabled with current permissions and conditions.
- would change: If enabled, I can start planning and running Mac UI interactions via accessibility for real tasks.

### `c20-z5jv` (context) — owner.task.priorityList
- why: No current prioritized task list for Mac-vision agent exists; need to build or read one to plan computer use actions effectively.
- would change: I will use the priority list to select next actions and better align with owner goals and urgencies.

### `c21-qluh` (context) — mac-delegate.workflowContext
- why: To access signals or state about ongoing multi-step workflows delegated to the Mac agent.
- would change: It allows mac-vision to participate or plan in coordination with longer workflows that need UI interaction or complex sequences.

