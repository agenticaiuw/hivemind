# Harness derivation — mac-vision — round 153

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable a live prioritized owner goal store integrated across all agents that captures tasks, deadlines, dependencies, and priorities with real-time updates."
- **useful because:** Currently the system has no integrated representation of what the owner really wants done next. A live prioritized goal store allows MacVision and other agents to focus their actions on high-value work and to collaborate effectively.
- **path:** mac-planner → mac-vision → relay-realtime → pendant
- **model tier:** background
- **latency:** seconds
- **cost:** low, mostly storage and infrequent model updates
- **security:** Contains owner work and priorities, must be protected and encrypted
- **missing:** write access for agents to memory facts with kind:'task'; priority and dependency metadata schema; goal update and subscription protocols

### "Allow MacVision to share a minimal accessibility tree snapshot and UI interaction context off-device with relay-realtime after explicit owner consent to enable multi-device coordinated assistance and session continuity."
- **useful because:** Sharing UI state with relay-realtime and other surfaces allows richer multi-modal collaboration and allows remote or multi-node agents to assist the owner better, while respecting privacy and consent.
- **path:** mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** milliseconds to seconds
- **cost:** moderate (network transfer and processing)
- **security:** Owner privacy is paramount; sharing is limited to minimal accessibility tree subset and only on explicit ongoing consent.
- **missing:** consent UI and policy; relay endpoint for upload; privacy-preserving payload design

### "Build a cross-agent undo and action confirmation framework that works with mac_run_actions and mac_delegate, giving the owner the confidence to enable full MacVision control with reversible steps and explicit confirmations for destructive actions."
- **useful because:** This is the single most useful capability to enable the owner's trust and safety. It allows the owner to delegate complex Mac tasks to MacVision with confidence that mistakes can be undone or stopped before damage occurs.
- **path:** mac-vision → mac-planner → pendant → relay-realtime
- **model tier:** realtime
- **latency:** seconds
- **cost:** medium, due to tracking and validation
- **security:** Must securely track action intents and results to avoid unauthorized or mistaken reversions.
- **missing:** cross-surface action receipts; undo stack management; confirmation UI on pendant and Mac

### "Enable fully autonomous Mac task execution by MacVision with dynamic context-based UI navigation and decision-making, even on unstructured or rapidly changing interfaces."
- **useful because:** Today automation is brittle and limited to predefined steps or indirect commands. To truly empower the owner, MacVision must handle complex UI workflows where UI elements may not be fixed or predictable, adapting dynamically.
- **path:** mac-vision → mac-planner → pendant
- **model tier:** realtime
- **latency:** seconds
- **cost:** high, due to constant analysis and interaction
- **security:** Needs strict sandboxing and action review to prevent unauthorized destructive behavior.
- **missing:** advanced real-time UI interpretation models; dynamic UI element mapping and recovery; adaptive step generation

### "Integrate voice-command-driven Mac workflow scripting with visual UI feedback and undo, implemented across pendant, Mac, and relay surfaces."
- **useful because:** Voice control with visible feedback and undo capability offers a hands-free but transparent way for the owner to manage complex Mac workflows interactively and safely.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** realtime
- **latency:** seconds
- **cost:** medium
- **security:** Requires robust voice recognition authorization and undo safeguards.
- **missing:** real-time voice-to-action pipeline; UI state feedback channel; voice undo stack


## Changes it proposed to its own stack

### `interaction` — Add a macOS Accessibility permission request and grant workflow specifically for the 'AI Pendant Agent' binary, to enable computerUseLoop to control and query UI elements proactively without fallback to pixel or focus-stealing methods.
- **owner gets:** This unlocks the safe and effective operation of MacVision's computer use loop for automating complex multi-step UI interactions on the Mac, improving productivity and reliability without annoying the user.
- effort: medium (UI permissions dialogs, testing, user education)  ·  risk: If misconfigured, may cause denial of service or force fallback to pixel input which steals focus; recovery is to revoke and re-grant permissions.
- cost: minimal  ·  latency: none
- security: requires trust but is limited to a local binary, no external data exposure
- depends on: ownership consent

### `hardware` — Add a second physical button to the AI Pendant to support separate dedicated control interactions: one for voice, one for manual confirmation and mode switching.
- **owner gets:** Currently, the pendant has only one button which limits interaction design and increases complexity in gesture recognition. A dedicated confirmation button removes ambiguity in safety-critical operations and expands interface possibilities.
- effort: medium hardware redesign and firmware update  ·  risk: Physical redesign risks and additional power draw; mitigated by careful design and testing.
- cost: moderate hardware cost increase  ·  latency: none
- security: Minimal, purely physical change.


## What it asked for

_Nothing._
