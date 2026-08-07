# Harness derivation — mac-planner — round 19

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I sleep, monitor my authenticated browser sources and Mac work queue, then give me a concise morning brief on the pendant with links, changes, and suggested next actions; if I say 'do it', carry out only the selected desktop actions."
- **useful because:** The owner wakes to finished intelligence rather than a pile of notifications, and can move from audio summary to concrete Mac/browser execution without manually routing work between agents.
- **path:** browser → relay → dashboard → pendant → mac-bridge
- **model tier:** Scheduled/background monitoring and deduplication use a cheap batch model; a small planner model extracts changes and ranks urgency; realtime is used only for the live follow-up conversation. Mac/browser execution is deterministic harness work, not model generation.
- **latency:** Overnight jobs can complete within 5–15 minutes of their schedule. The morning brief should start playing within 2 seconds of the owner’s request; selected action preview within 5 seconds, execution receipt within 10 seconds.
- **cost:** Roughly $0.02–$0.15 per monitored source/day depending on page volume and summarization; audio generation is the dominant variable. Cache page hashes and summarize only diffs to avoid repeated tokens.
- **security:** Authenticated content and local Mac state leave the relevant devices and relay; retain extracted diffs, not whole pages, with per-source encryption and 30-day expiry. Never auto-send, purchase, delete, or modify external data from a brief. 'Do it' must identify a bounded action set and show a concise receipt; destructive or financial actions require a second explicit confirmation.
- **missing:** Scheduled job runner with per-source credentials and cookie isolation; Server-side browser execution or a secure browser-extension result API; Persistent cross-node task/artifact ledger with provenance, deduplication, and resumable status; Offline audio delivery and retry to the pendant; A confirmation-aware action preview/receipt protocol shared by relay, browser, and Mac


## Changes it proposed to its own stack

### `memory` — Replace the surface-specific fleetContext prompt fragments and ad-hoc job history with a shared event-sourced task/artifact ledger. Each event has task_id, actor node, capability used, input references, output artifact hashes, sensitivity label, expiry, parent event, and reversible/confirmation state. Expose projections for relay, pendant, Mac, browser, dashboard, and allow resumable leases so a failed Mac action can be retried without duplicating side effects.
- **owner gets:** The owner can tell the pendant once and trust every node to understand what happened, what is waiting, and what remains safe to retry. Results remain findable with provenance instead of disappearing into one agent’s session.
- effort: Medium-high: D1 schema/API, idempotency keys, event projections, migration from session history, and adapters in relay/Mac/browser clients.  ·  risk: A bad migration could hide prior memories or duplicate actions. Keep the old stores read-only during migration, dual-write with checksums, and require idempotency keys plus explicit side-effect receipts before replay.
- cost: Small D1/R2 storage increase; event metadata adds modest tokens only when projected into context. Hashes and compact summaries keep recurring context cheap.  ·  latency: One ledger write/read per handoff, generally tens of milliseconds; context assembly becomes faster after projection caching.
- security: Centralizing provenance increases blast radius. Encrypt sensitive payload references, keep content off event rows, enforce node/source scopes, redact projections, and audit every cross-node read.
- depends on: A stable authenticated node identity and capability-scoped relay API; A confirmation/receipt protocol for side effects; A scheduled-job and retry mechanism

### `mac-harness` — Add a typed, idempotent execution transaction API around the existing FULL_CONTROL_MODE bridge: plan_hash, action IDs, preconditions (foreground app/file hash/browser URL), dry-run diff, execution, and receipt with before/after observations. Group actions into reversible batches where possible and automatically checkpoint after each side effect. Keep arbitrary shell/AppleScript available only as an explicitly labeled escape hatch.
- **owner gets:** The owner gets reliable automation that does not silently act on the wrong document or repeat a purchase/email after a retry. When something fails, they can see exactly what changed and resume from the safe checkpoint.
- effort: Medium: local-agent transaction store, typed preflight observers, receipt callbacks to relay, and adapters for current ui_* and browser actions.  ·  risk: Preconditions can become stale and block legitimate work; allow a bounded re-plan rather than bypassing them. Observation itself may expose sensitive text, so redact receipts and retain hashes unless the owner requests details.
- cost: Negligible local compute and D1 metadata; fewer duplicate model calls and failed side effects should reduce API cost.  ·  latency: Adds roughly 100–500 ms for local preconditions and checkpoints; avoids expensive retries.
- security: Meaningfully reduces accidental side effects, but does not replace confirmation for money, deletion, or external communication. Scope credentials per job and make receipts tamper-evident.
- depends on: A read-only Mac preflight/inspection capability (or typed equivalent in the local agent); Shared task/artifact ledger; A clear policy for which actions are confirmation-required


## What it asked for

### `s10-l3xe` (skill) — offline_moment_bookmark
- does: On a short button press, records a timestamped local bookmark event (optionally a few seconds of low-rate ambient audio only if the owner has enabled it), gives haptic/LED acknowledgement, and queues it for upload when the link returns. The relay turns bookmarks into ledger events such as 'remember this moment' or a location/time marker; no speech recognition is required on-device.
- must be on-device because: The button press and exact moment must be captured even with cellular/BLE loss and without waiting for a round trip. Server-side recording cannot recover the moment after a dropped link.
- trigger: Pendant button press; upload retry on reconnect.
- storage: A compact ring of 128 events, each ~32–64 bytes (timestamp, type, flags, sequence, optional encrypted short payload): under 8 KB in flash/NVS. No ambient audio by default; if enabled, retain at most a 5-second compressed clip per bookmark with strict ring expiry.
- RAM budget: ~2–4 KB for queue/ring bookkeeping and upload framing, comfortably below 211,608 B application RAM; avoid a persistent audio buffer unless the existing audio pipeline can lend one without increasing peak RAM. Firmware must use the existing secure transport and monotonic sequence numbers to prevent duplicate uploads.

## Its own summary

Proposed an overnight authenticated-source/Mac-work morning brief that arrives as pendant audio and hands selected actions to Mac/browser; proposed an event-sourced cross-node task/artifact ledger with provenance, leases, idempotency, and compact projections; proposed typed Mac execution transactions with preconditions, checkpoints, and receipts; requested an offline pendant moment-bookmark skill that survives link loss. Aligned browser-extension and relay-realtime peers on publishing into the shared ledger.

**Biggest unknown:** The remaining blockers are architectural rather than discovery: no scheduled durable job runner, no shared ledger/receipt API, no offline audio delivery retry, and no implemented Mac preflight tool. I also still need the owner’s explicit policy for authenticated-source retention and which external actions may be performed without confirmation.

