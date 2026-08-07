# Harness derivation — mac-planner — round 115

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I am in a meeting or deep work, quietly hold non-urgent notifications across my Mac and logged-in browser, interrupt me only for something genuinely urgent, and give me the held items as a short, ordered digest when I am free again."
- **useful because:** The owner currently has separate calendar, mail, browser, and pendant behaviors; none can protect attention across all of them or restore what was suppressed. This would make the pendant an attention boundary rather than another notification source, while preserving every held item and why it was classified.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic rules first (calendar event state, sender allowlists, due times, explicit keywords, browser origin); use a cheap background model only to rank ambiguous items and explain the ranking. Realtime is reserved for the one-sentence urgent interruption and the later digest.
- **latency:** Notification classification under 300 ms locally; urgent escalation under 2 s; digest generated within 30 s after the attention window ends. No network round trip for known allowlist/blocklist decisions.
- **cost:** Near-zero for deterministic events; roughly $0.001–$0.01 per digest for ambiguous-item ranking. Storage and Mac notification integration dominate engineering cost, not inference.
- **security:** Notification text may contain private mail, messages, and account data. Keep raw payloads on the Mac/browser; relay receives only urgency, category, and opaque item IDs. Require explicit owner configuration for VIP senders and emergency categories. Never auto-dismiss or delete notifications; hold, restore, and audit instead.
- **missing:** A Mac notification-center adapter that can snapshot, classify, hold, and restore notifications without losing them; A browser-extension event stream for site notifications with origin, timestamp, and opaque item ID; A shared attention-window state machine driven by Calendar plus a pendant button/voice toggle, with quiet hours and manual override; A local encrypted held-notification store and ordered digest queue; Pendant haptic/audio urgency protocol and an owner-visible audit trail showing every held/restored item


## Changes it proposed to its own stack

### `context` — Add a cross-surface causal observation ledger, distinct from ordinary memory: every Mac inspection, browser extraction, pendant event, and execution receipt gets a device clock, relay receive time, sequence/nonce, and parent observation ID. Plans carry a compact precondition vector; execution compares it against fresh observations and returns stale/conflict rather than replaying. Persist only hashes and typed facts by default, with source pointers for local evidence.
- **owner gets:** When the owner says 'do that' after switching tabs, closing a laptop, or reconnecting the pendant, the system can know whether 'that' still refers to the same thing. It prevents duplicate or stale actions while preserving a human-readable explanation of what changed.
- effort: Medium-high: shared event schema, append-only bounded ledger, adapters in relay/pipeline, Mac jobs, and browser commands; add crash/reconnect and duplicate-delivery tests.  ·  risk: Clock skew and missed heartbeats can create false conflicts; use monotonic per-device sequence numbers and treat uncertainty as review-needed, not success. Metadata itself can reveal activity, so hash sensitive payloads and enforce TTL.
- cost: Low storage and negligible model cost; deterministic comparison handles most events. Background summarization only for conflict explanations.  ·  latency: Under 100 ms for local vector comparison; reconnect reconciliation adds one inspection round trip (typically <2 s) before mutation.
- security: Improves safety without introducing approval gates. No raw audio or credentials in the ledger; retain only minimal typed metadata and encrypted local evidence references.
- depends on: Implementations of mac_readonly_inspect and mac_read_sources; Typed browser command/job receipts with request IDs; Relay delivery with idempotency and reconnect handling

### `integration` — Create a local attention broker between Mac Notification Center, browser-extension events, Calendar, and the pendant pipeline. It should maintain an encrypted, append-only held-item queue keyed by opaque IDs; apply deterministic urgency policy locally; emit only category/urgency over /pipeline/events; restore or summarize items when the attention window closes; and expose an audit record with source, reason, and disposition. This is the missing connective layer, not another briefing routine.
- **owner gets:** The owner gets uninterrupted meetings and focus time without losing notifications or having them silently discarded. When free, they receive one concise digest with the urgent items first and can see exactly why anything was held or escalated.
- effort: High: macOS notification integration, browser event adapter, queue durability/recovery, policy UI, Calendar-driven state transitions, and pendant haptic/audio states. Test crash, reboot, duplicate event, and offline cases.  ·  risk: A misclassification could delay an important alert; provide emergency allowlists, a physical pendant override, expiry-based escalation, and a visible held-count indicator. If the broker crashes, fail open for urgent/VIP sources and preserve queued metadata. Never delete source notifications.
- cost: Small local storage/process overhead; low model spend because ranking is mostly rules. Engineering cost is concentrated in private notification APIs and browser event normalization.  ·  latency: Local known-policy decisions <300 ms; ambiguous ranking can be asynchronous. Reconnection may briefly show a held-count badge before the digest is ready.
- security: Raw notification content remains on-device; relay sees opaque IDs and urgency labels. Encrypt the queue at rest, TTL old content, and require explicit opt-in for each source and browser profile.
- depends on: A supported Mac Notification Center read/hold/restore adapter; Browser-extension notification event protocol; Shared attention-window state and local policy store; Pendant urgency/override event support; Existing pipeline event and briefing consumers


## What it asked for

_Nothing._
## Its own summary

The genuinely remaining cross-surface gap is not another briefing or browser watcher: it is causal reconciliation. I proposed a cross-surface observation ledger that binds pendant events, relay delivery, browser/Mac observations, plans, and receipts with per-device monotonic sequence numbers and parent IDs. Plans carry precondition vectors; reconnect execution returns stale/conflict instead of replaying an intent twice or acting on an old tab. I also confirmed that the newly granted Mac inspection tools are still schema-only at runtime, so the immediate practical blocker is implementation of read-only inspection plus observation IDs. Accessibility/Screen Recording remain owner-controlled TCC state and must be reported honestly, not assumed.

**Biggest unknown:** Whether the relay already has durable per-device sequence/idempotency primitives hidden behind its routes; I could not inspect live Mac/browser state because mac_readonly_inspect currently returns 'schema but no implementation'.

