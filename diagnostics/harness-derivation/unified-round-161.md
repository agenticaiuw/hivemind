# Harness derivation — unified — round 161

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you answer, prove the pendant audio path is healthy: run a 24 kHz duplex test, inject realistic loss, validate the artifacts, and tell me whether to ship or fall back."
- **useful because:** The owner gets a single trustworthy go/no-go instead of interpreting codec counters. It exercises the actual pendant, bridge, relay, and Mac path and catches regressions before they become an audible failure.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** background for scheduled/regression runs; realtime only to explain the result conversationally
- **latency:** 30-90 seconds for the test and validation; spoken verdict under 2 seconds after results arrive
- **cost:** Roughly $0.01-$0.05 per run; dominated by background model narration, not the read-only diagnostics
- **security:** Synthetic audio and counters leave the device; never include microphone content. Require explicit confirmation before changing the live profile. A failed test must recommend fallback, not silently switch it.
- **missing:** A coordinator that sequences audio_link_fault_inject, audio_pipeline_validate, and the existing fixture; persistent release verdict/history; a safe profile-switch action with confirmation

### "When a routine says 'morning' or 'evening', check which clock you are using and warn me before it fires if the Mac timezone and my personal timezone disagree."
- **useful because:** The owner currently has an authoritative Mac zone and a separately remembered personal zone with no resolved policy. This prevents a daily brief or evening wrap-up from silently arriving at the wrong local time, while still allowing Mac-local routines to run normally.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** deterministic rules for zone comparison and scheduling; background model only for a concise explanation
- **latency:** Under 100 ms at schedule evaluation; warning delivered at the next natural interaction, never an unsolicited interruption
- **cost:** Near-zero model cost for normal evaluations; under $0.001 when a warning needs phrasing
- **security:** Timezone is sensitive location context. Store only the chosen IANA zone and source/provenance, not GPS. Do not infer the owner's zone from device location. Require confirmation before changing existing routine times.
- **missing:** An explicit owner timezone setting/provenance record distinct from Mac timezone; routine preflight hook; pending-warning delivery through the existing inbox/next-conversation path

### "Prepare this browser task for me, show exactly what will happen, and only carry it out after I approve the transaction on the pendant."
- **useful because:** This makes the worn device a real physical consent boundary for authenticated browser sessions: the Mac can inspect and stage, the browser can reach the private account, and the relay can preserve the nonce across a dropped link. It prevents a spoken misunderstanding from sending mail, buying, or submitting a form.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** realtime for clarifying the owner's intent; deterministic planner and executor for the staged transaction
- **latency:** Preview in 2-5 seconds; execution within 1 second after the pendant approval event reaches the bridge
- **cost:** About $0.01-$0.08 per invocation, dominated by intent clarification; browser inspection and receipts are otherwise local
- **security:** Never put page secrets or form values on the pendant. Bind approval to plan digest, world fingerprint, nonce, expiry, and replay counter. Destructive sends/purchases still need the existing confirmation policy, and cancellation must be possible offline.
- **missing:** Implement the relay side of APPROVAL_STORE_CONTRACT; connect prepare/approve to the live bridge; consume physical_transaction_approval_latch events; give approval and execution separate credentials; add browser-world revalidation immediately before submit

### "Forget everything about this topic everywhere: remove the audio, transcript, relay record, Mac artifacts, browser traces, and cached summaries, then give me a receipt listing what was deleted and what could not be reached."
- **useful because:** The owner cannot currently obtain a single, honest deletion result across the surfaces that jointly handle a conversation. This turns privacy from a local mute into an auditable lifecycle operation.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic deletion planner and receipt generator; background model only to identify artifacts and explain exceptions
- **latency:** Preview in under 3 seconds; deletion receipt within 30 seconds, with unreachable surfaces remaining explicitly pending
- **cost:** Usually under $0.02; dominated by artifact indexing, not model inference
- **security:** Deletion must be scoped by an owner-confirmed topic/turn identifier, never a vague keyword that could erase unrelated work. Preserve only a minimal tombstone and audit hash. Browser deletion must use bound tabs/apps and never expose page contents to the relay.
- **missing:** Cross-surface artifact index linking turn IDs to pendant, relay, Mac, and browser outputs; Idempotent deletion endpoints with durable tombstones and retry state; A cryptographic deletion receipt that distinguishes deleted, unverifiable, and retained-by-policy records; Owner retention/deletion policy

### "I think my pendant or Mac may be compromised. Freeze every remote action now, revoke browser and relay sessions, show me what was stopped, and let me restore access only after a physical pendant confirmation."
- **useful because:** Today there is no owner-facing cross-surface containment action. A lost pendant, stolen Mac session, or suspicious browser command could remain usable while the owner tries to diagnose it.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic containment and session revocation; realtime model only for concise status narration
- **latency:** Local pendant and relay freeze under 1 second; browser/Mac revocation receipt within 10 seconds
- **cost:** Negligible API cost; mostly authenticated state changes and receipt storage
- **security:** The freeze path must not depend on the potentially compromised Mac or browser. Pendant-local state and relay-side deny-listing must work independently. Recovery requires the physical approval latch plus a fresh device attestation; do not send secrets to the pendant.
- **missing:** Relay-wide emergency deny switch keyed to device/session identity; Browser and Mac session revocation adapters; A signed device-attestation and recovery protocol; A durable containment receipt and expiry policy

### "For this task, keep all page contents and audio on my Mac; use the relay only for a redacted intent, and refuse if any step would export sensitive data."
- **useful because:** The owner can use authenticated browser sessions without making the relay a silent copy of private pages or conversations. Today privacy is an all-or-nothing latch, not a per-task data-residency guarantee.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** deterministic policy enforcement and redaction; realtime model only for intent clarification and a short refusal
- **latency:** Policy decision before any browser command, under 200 ms; refusal immediate and never deferred until after export
- **cost:** Under $0.01 per task; local inspection dominates, with optional small-model redaction
- **security:** Redaction must happen before relay persistence and before model upload, not merely in the dashboard. Maintain an allowlist of domains/apps and fail closed on unknown content. The owner must explicitly choose whether transcript text is local-only.
- **missing:** A preflight data-flow policy engine spanning browser, Mac, and relay; Structured redaction before relay/job persistence; Per-task policy selection and a tamper-evident refusal receipt; Owner decision on which domains and content classes are local-only


## Changes it proposed to its own stack

### `integration` — Add a USB-session supervisor that discovers /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, authenticates the pendant/bridge pair, claims the local transport, pauses LTE retry churn, and exposes a turn-boundary handoff receipt when USB disappears or returns.
- **owner gets:** The owner can wear and test the real pendant today without pretending it is LTE-registered, and an unplug or reconnect will not duplicate audio or strand a conversation.
- effort: Medium: serial framing, session lease, reconnect state machine, and integration tests across both chips.  ·  risk: A stale claim could suppress LTE or split a turn. Use an expiring lease, monotonic turn IDs, and fail closed to silence rather than duplicate playback; recover by re-admitting at the next turn boundary.
- cost: No meaningful API cost; a small Mac background process and a few KB of state.  ·  latency: USB admission under 500 ms; handoff waits for a turn boundary rather than cutting speech.
- security: Pair by device serial plus challenge/response; never treat any arbitrary USB serial device as the pendant. Keep raw audio local unless the active session is explicitly linked.
- depends on: usb_fallback_audio_session firmware skill; mac bridge serial transport implementation; audio_delivery_ack_queue

### `relay` — Implement the approvalHandoff relay store and delivery loop as a real durable record: persist the staged transaction, select it for the next conversation, mark the spoken readback delivered, accept the pendant nonce, and revalidate plan/world fingerprints before execution.
- **owner gets:** The pendant's physical approval becomes an actual safety boundary instead of a UI promise that currently expires without ever being deliverable or executable.
- effort: Medium-high: D1 schema/index, next-conversation delivery, bridge event ingestion, and privilege-separated approve versus execute paths.  ·  risk: A replay or stale browser page could cause a duplicate action. Enforce nonce monotonicity, TTL, one-shot state transitions, and browser reinspection immediately before submit; keep denied/expired records auditable.
- cost: Low storage and request cost; roughly cents only when a model must clarify intent.  ·  latency: Adds one preview/readback round trip; execution after approval should be sub-second.
- security: Approval credential must not equal execution credential. No page secrets, form contents, or account tokens go to the pendant; only a transaction summary and opaque nonce.
- depends on: physical_transaction_approval_latch firmware skill; shared/approvalHandoff.js contract; relay job lease/requeue; browser-world revalidation

### `context` — Create an explicit time-provenance record with separate mac_local_zone and owner_personal_zone fields, and require every routine compiler/evaluator to label which one it uses; on conflict, create a held warning instead of silently converting zones.
- **owner gets:** Daily briefs and evening actions happen at the intended local time, while Mac file/calendar operations remain correctly anchored to the computer that resolves them.
- effort: Medium: schema, routine preflight, migration of existing schedules, and a next-conversation warning renderer.  ·  risk: Existing routines could shift if migrated carelessly. Preserve current schedules as Mac-local, show a dry-run conversion, and require explicit confirmation before changing times.
- cost: Negligible storage/model cost.  ·  latency: No runtime impact beyond a deterministic zone check.
- security: Treat personal timezone as sensitive location metadata; store the IANA zone and provenance, not inferred coordinates or device GPS.
- depends on: owner decision about personal timezone; routine scheduler hook; held-alert/inbox delivery


## What it asked for

_Nothing._
