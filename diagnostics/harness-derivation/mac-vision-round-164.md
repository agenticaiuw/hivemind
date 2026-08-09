# Harness derivation — mac-vision — round 164

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable full macOS Accessibility permission grant to the AI Pendant Agent for computerUse.loopEnabled, allowing safe and robust UI automation without pixel fallback."
- **useful because:** Unlocks powerful UI automation via accessibility APIs, enabling mac-vision to plan and execute complex interactions without disturbing owner focus or relying on error-prone pixel clicks.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Realtime (under 1s) for command response
- **cost:** Low to moderate compute from Mac local agent and relay
- **security:** Requires explicit owner consent due to deep access. Must include safeguards to prohibit destructive actions without confirmation.
- **missing:** UI automation policy enforcement for destructive actions; Owner consent UI to grant Accessibility to the correct binary

### "Create and maintain a structured task store from owner-stated goals, accessible by mac-vision for prioritization and execution."
- **useful because:** Currently, the system lacks a durable, structured goal representation. A task store would let mac-vision read actionable goals, rank them, and drive UI automation meaningfully.
- **path:** mac-vision → mac-planner → unified
- **model tier:** gpt-5.6-luna
- **latency:** Background processing including daily updates
- **cost:** Moderate compute for managing structure and ranking
- **security:** Data privacy and integrity of goal store; write permissions restricted to owner or trusted agents.
- **missing:** Goal-to-task conversion pipeline; Task ranking model; API hooks to read and write tasks

### "Design a layered task prioritization and ranking system combining dayPlan reminders, memory facts, and owner-stated tasks for mac-vision to focus on what matters most in the moment."
- **useful because:** With no integrated priority system, mac-vision cannot choose the best next action reliably. Prioritization ensures efficient and owner-aligned computer use.
- **path:** mac-vision → mac-planner
- **model tier:** gpt-5.6-luna
- **latency:** Realtime but budgeted over tens of seconds for recalculation
- **cost:** Moderate compute for continuous prioritization and ranking
- **security:** Must protect owner privacy and prevent unintended action prioritization bias.
- **missing:** Unified task priority algorithm; Integration with Mac reminders and memory facts

### "A safe, real-time user approval system for all high-impact actions initiated by mac-vision on the owner's Mac, using a dedicated physical gesture on the pendant for confirmation."
- **useful because:** Ensures no destructive or irreversible computer use loop action occurs without explicit owner consent, addressing trust and safety concerns inherent in powerful automation.
- **path:** mac-vision → pendant → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Realtime (under 1s) for approval feedback
- **cost:** Minimal compute for gesture detection and relay message handling
- **security:** Requires robust cryptographic verification of gesture and secure relay channel; owner privacy ensured by local pendant confirmation.
- **missing:** Firmware support for multi-gesture recognition on pendant button; Relay protocol support for approval messages; UI for status feedback on Mac and pendant

### "A dynamic multi-surface context awareness and synchronization system that lets mac-vision know the state of browser, terminal, and other app surfaces simultaneously so it can coordinate multi-application workflows."
- **useful because:** Owners juggle complex tasks crossing multiple apps; this system enables seamless coordination by mac-vision, avoiding duplicated or conflicting UI actions and improving flow.
- **path:** mac-vision → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** gpt-5.6-luna
- **latency:** Near realtime (seconds)
- **cost:** Moderate compute and memory usage for context tracking and sync
- **security:** Context data must be scoped strictly to owner devices and apps; no external leakage allowed.
- **missing:** Inter-surface context sharing protocols; Unified memory or or shared state store accessible by all surfaces

### "A fine-grained, typed action policy enforcement layer on mac-vision's computerUse.loopEnabled to classify every intended action as read-only, reversible, or destructive, automatically gating destructive ones until owner approval."
- **useful because:** This adds a safety net to powerful UI automation by mac-vision, reducing risk of accidental data loss or unwanted changes while maintaining seamless operation for safe actions.
- **path:** mac-vision → mac-planner → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Realtime for classification and gating
- **cost:** Low to moderate compute for classification models and enforcement
- **security:** Policy must be transparent and modifiable by the owner; gating requires secure approval channel.
- **missing:** Typed classification model for UI actions; Policy enforcement primitives in mac-vision loop; User feedback and override UI

### "An integrated audio-visual timestamping and logging system where the pendant marks moments of high owner attention or interest during Mac use, correlating these moments with mac-vision's accessibility tree observations and audio capture for later review and prioritized task extraction."
- **useful because:** Enables the owner to effortlessly bookmark and later revisit moments of significance during computer sessions, improving memory, review, and workflow continuity.
- **path:** pendant → mac-vision → relay-realtime
- **model tier:** gpt-5.6-luna
- **latency:** Background with near-realtime availability
- **cost:** Low to moderate compute, mostly on relay and Mac
- **security:** Sensitive data retained locally and only uploaded with owner consent.
- **missing:** Enhanced moment mark payload capability; Synchronisation protocol for multimodal data streams


## Changes it proposed to its own stack

### `hardware` — Add a dedicated second physical button on the pendant to allow rich gesture input independent of the primary microphone button, enabling a broad variety of confirm, cancel, and mode-switch gestures for safety and control.
- **owner gets:** Provides the owner a reliable, low-latency, no-accident manual control channel for approving or rejecting high-impact commands, and for context switching without confusing the single microphone button's recording behavior.
- effort: Medium hardware redesign and firmware update effort.  ·  risk: Added hardware complexity and potential to confuse current users; mitigated by clear UI and adapter software support.
- cost: Low incremental component cost; negligible power impact.  ·  latency: No effect on computational latency; enables faster human action response.
- security: Improves security by allowing explicit manual confirmation separate from voice recording.


## What it asked for

_Nothing._
