# Harness derivation — mac-vision — round 106

Model: `gpt-4.1-mini`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Enable low-latency, trusted typed action broker for mac-vision loop, separating read-only, reversible, and high-impact actions with observability and safe undo."
- **useful because:** This typed action broker would classify every mac-vision UI operation into clear categories, allowing the owner and other surfaces to easily audit, observe, and optionally undo changes. It segregates high-risk operations (e.g., file deletion, destructive automation) from low-risk reads or reversible UI manipulations. Such granularity enables more complex, responsive, and risk-aware automation on the Mac while respecting owner control policies and safety constraints.
- **path:** mac-vision → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini on mac-vision for immediate tagging and classification, gpt-5.6-luna for broader judgement and coordination.
- **latency:** Subsecond classification for quick response during loop operation, longer judgement cycles for policy updates and audit logs.
- **cost:** Low to moderate API cost, mostly CPU usage for tagging and maintaining audit logs.
- **security:** Incorrect classification could lead to insufficient owner confirmation or unexpected destructive effects, so the system must always err on the side of caution and require owner confirmation for high-impact actions. Detailed audit logs must protect privacy and be securely stored.
- **missing:** Typed action classification layer integrated into mac-vision loop actions.; Reversible action tracking and undo stack accessible via the Mac agent and higher surfaces.; Policy definitions for action categorization, confirmation triggers, and logging.; UI to display and manage audit trail and undo controls.

### "Provide owner with multimodal feedback and real-time confirmation interface while mac-vision executes multi-step tasks on the Mac."
- **useful because:** The owner should be able to see what mac-vision is doing in real time, including UI interactions, typed input, and app launches, via the wearable pendant relay and Mac surface UI. This keeps the owner informed and in control, allowing immediate intervention or cancellation of unexpected actions. It also enhances trust by showing transparent task progress and step-by-step confirmations for sensitive actions during automation workflows.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-judgement → faculty-action
- **model tier:** gpt-4.1-mini for low latency event-driven UI narration and feedback, gpt-5.6-luna for judgement to interpret and moderate owner commands and interruptions.
- **latency:** Real-time feedback with under 1 second latency for typical interactions; confirmations within a few seconds.
- **cost:** Moderate cost dominated by the real-time audio relay and UI state streaming, plus processing for feedback synthesis and interruption handling.
- **security:** Owner data privacy must be strictly enforced. Information streamed for feedback should be filtered to avoid sensitive data leaks. Immediate confirmation mechanisms must avoid mistakes or accidental command executions.
- **missing:** Realtime UI event/state streaming from mac-vision to relay-realtime via mac-planner.; Low-latency audio narration and owner feedback interface on the pendant.; Abort/cancel command pathways tightly integrated across surfaces during live task execution.

### "Enable cross-surface coordination for mac-vision, relay-realtime, and mac-planner to share goals, observations, and intents in real time to robustly support multi-modal user interactions."
- **useful because:** The owner benefits from a seamless integrated assistant experience that handles voice via relay, UI actions via mac-vision, planning via mac-planner, and judgement via faculty-judgement, with constant synchronization. This coordination makes complex workflows transparent, responsive, and adaptive across devices and surfaces with minimal latency.
- **path:** mac-vision → relay-realtime → mac-planner → faculty-judgement → faculty-action
- **model tier:** Distributed model use: gpt-4.1-mini for reactive control on mac-vision and relay-realtime, gpt-5.6-luna for planning, judgement, and extended memory on mac-planner and faculty layers.
- **latency:** Sub-second latency for synchronization, multi-second for complex planning and judgement cycles.
- **cost:** Moderate to high cost due to frequent state sharing, synchronization, and model calls across multiple surfaces.
- **security:** Synchronizing sensitive user intents and data must be encrypted and carefully permissioned; risk of leaks or data mismatch increases with complexity and multipoint synchronization.
- **missing:** Real-time goal and context sync infrastructure between mac-vision, relay-realtime, and mac-planner.; Conflict resolution and priority arbitration logic across surfaces.; Secure, low-latency messaging and shared context storage.; Unified user session and identity management across surfaces.


## Changes it proposed to its own stack

### `integration` — Integrate consistent and periodic UI hierarchy and state snapshot streaming from the Mac to mac-vision and faculty-perception to enable accurate awareness for UI automation and loop control.
- **owner gets:** The owner benefits from highly reliable, up-to-date awareness of the Mac UI state, enabling robust and contextually-aware automation that avoids errors and unintended actions, increasing trust and usefulness of the computer use loop.
- effort: Moderate development effort to build stable UI snapshot streaming and subscription mechanisms, with compression and privacy filters to handle sensitive data.  ·  risk: If snapshots lag or are incomplete, automation may act on stale UI state, causing errors. Must fallback gracefully and allow manual intervention. Data leakage risk mitigated by strong filtering and encryption.
- cost: Moderate additional bandwidth and storage usage on Mac and in relay layers.  ·  latency: Minimal latency added, snapshots sent on demand or periodic schedule.
- security: Sensitive UI data is handled carefully with owner consent and encryption.
- depends on: Permission for computerUse.loopEnabled; VisionUploadConsented; Accessibility API full trusted status

### `hardware` — Add a dedicated hardware button or gesture sensor on the wearable pendant to allow the owner to instantly interrupt or pause all mac-vision computer automation activities.
- **owner gets:** This gives the owner immediate, low-friction manual control to stop any unwanted or erroneous automation on their Mac, increasing safety and trust when the loop is operating.
- effort: Low to moderate hardware and firmware development effort to add the button or gesture sensor and integrate it with the real-time relay and mac-vision loop control state.  ·  risk: Hardware failure or button misfire could cause false interrupts or unavailable interrupts. Fail-safe software fallback required.
- cost: Minimal additional hardware cost and very low power usage increase.  ·  latency: Near-zero latency for interruption signal.
- security: Button press signals must be securely authenticated and protected to prevent spoofing or accidental triggers.
- depends on: wearable pendant hardware platform with extensible I/O; relay-realtime integration

### `memory` — Implement persistent per-task memory context storage within mac-vision to track multi-step automation workflows, decisions, states, and reversions for better resilience and auditing.
- **owner gets:** Enables the mac-vision loop to handle complex and long-running UI workflows on the Mac with checkpointing, rollback, and audit trails. This increases reliability and safety while also allowing resumption if interrupted or queried for history.
- effort: Moderate software development effort to build persistent context layer integrated with existing loop state and job tracking.  ·  risk: Memory corruption or loss of context would cause task failures needing manual recovery. Requires secure storage to avoid privacy leakage.
- cost: Additional persistent storage required locally on Mac and possibly cloud-synced backups for resilience.  ·  latency: Minimal runtime impact; mostly affects storage and retrieval timings.
- security: Strong encryption and access control needed to protect sensitive task data.
- depends on: Robust mac agent session and job tracking; Persistent storage on Mac or cloud; Security and privacy controls


## What it asked for

### `c10-qbk0` (context) — ui_hierarchy_snapshot
- why: Needed to understand current UI structure on Mac for safe and precise navigation by the computer use loop.
- would change: Allows mac-vision to plan next accessibility actions precisely without guesswork, reducing risk of errors or interference with the owner.

