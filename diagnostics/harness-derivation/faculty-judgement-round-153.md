# Harness derivation — faculty-judgement — round 153

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my briefings learn how I actually listen: shorten, skip, or expand future items based on what I stopped, replayed, or finished on the pendant."
- **useful because:** A briefing that adapts to real attention becomes useful instead of a fixed stream. The pendant is the only surface that knows whether an item was actually heard; the relay and Mac can turn that evidence into better future briefs.
- **path:** pendant → relay → mac-planner
- **model tier:** background for aggregation and preference updates; realtime only for the live interruption or spoken follow-up
- **latency:** ACK ingestion under 1 second; preference update in the next scheduled run; no added latency to audio playback
- **cost:** <$0.01 per daily update; aggregation and deduplication dominate, not model inference
- **security:** Send only opaque artifact/item IDs, positions, and event types from the pendant; do not upload raw audio or transcript. Require owner confirmation before turning inferred listening behavior into a durable preference, and expose/revoke the derived preference.
- **missing:** A durable join from briefing item ID to generated artifact and source; A preference learner that consumes record_pendant_delivery_event without treating interruption as dislike; A policy-controlled way to show and confirm inferred preferences

### "Before the pendant speaks a queued briefing item, check whether it is still true; silently drop stale items and tell me only what changed."
- **useful because:** Offline playback can make the owner act on a meeting that moved, an email already answered, or a page that changed. Freshness at the moment of listening is more valuable than a perfectly generated brief hours earlier.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background revalidation for queued items; realtime only to state the compact delta when an item survives
- **latency:** Revalidate within 2 seconds at play time; if a source is unreachable, fail closed for high-impact items and label low-impact items as generated-at time
- **cost:** <$0.02 per queued item when typed source checks suffice; model cost only for summarizing a detected delta
- **security:** Recheck by stable source IDs and return changed fields, not full private page/mail bodies. Do not silently discard deadlines; retain an auditable receipt and allow the owner to inspect why an item expired.
- **missing:** A source-specific freshness contract for briefing items (calendar/mail/browser); Binding each audio item to source IDs and a generated-at timestamp; A pendant-side pre-play handshake that can replace or cancel an artifact without playing it

### "Stop duplicate morning briefings before they reach me: find routines that ask for the same outcome, choose one canonical run, and leave the others as skipped with a reason."
- **useful because:** The owner should hear one coherent morning brief, not several separately generated audios that repeat each other and consume attention, battery, and model budget. This is especially important because the live schedule already contains overlapping 07:00/07:30 brief routines.
- **path:** relay → mac-planner → pendant
- **model tier:** cheap deterministic normalization and similarity first; background model only when two commands are genuinely ambiguous; realtime never needed
- **latency:** Under 100 ms during routine claiming; no additional delay to the selected routine
- **cost:** Near-zero for normalized command/signature matching; occasional <$0.01 ambiguity resolution
- **security:** Do not delete routines or suppress a non-equivalent job silently. Keep a reversible decision record with the matched command signatures, policy rule, and expiry; require confirmation before disabling an existing routine.
- **missing:** A durable routine-group/canonicalization record; A claim-time deduplication hook before routine execution and audio generation; A user-visible review route for skipped duplicate runs and one-click restore

### "Keep my pendant useful when LTE is unavailable: automatically use its live USB connection to the Mac, preserve the same conversation and queued work, and switch back to cellular without making me repeat myself."
- **useful because:** The pendant is physically connected and testable today, but it is not relay-registered over LTE. The owner should not lose their assistant merely because the radio is offline or the Mac cable was temporarily unplugged.
- **path:** pendant → mac-planner → relay → browser-extension
- **model tier:** deterministic transport/session state machine; realtime model only continues the conversation after a verified context handoff
- **latency:** Transport choice under 1 second; reconnect and context restoration under 3 seconds when either link returns
- **cost:** Negligible model cost; engineering cost is authenticated USB framing, session migration, and queued event reconciliation
- **security:** USB must use mutual device/session authentication and never treat arbitrary serial input as owner consent. Cellular and USB commands need the same stop latch, idempotency keys, and revocation epoch; expose a visible degraded-transport state.
- **missing:** A production USB serial bridge between the live pendant and Mac agent; A transport-neutral session identity and event sequence reconciliation; LTE registration and cellular transport adapter; A durable handoff record for in-flight audio and actions

### "Tell me exactly what I have and have not heard today, including interrupted audio, and let me resume an item from the same sentence on whichever connection is available."
- **useful because:** A spoken assistant currently has no trustworthy notion of delivery versus generation. The owner should be able to rely on 'what did I miss?' and resume without replaying an entire brief or guessing whether an offline artifact was played.
- **path:** pendant → relay → mac-planner
- **model tier:** deterministic delivery ledger and cursor reconciliation; no model needed except optional one-sentence catch-up narration
- **latency:** Answer status in under 500 ms from durable receipts; resume at the next audio frame within 1 second
- **cost:** Minimal storage and API cost; optional narration under $0.01
- **security:** Expose opaque artifact and source identifiers by default, not raw private content. Require provenance checks before revealing source text; honor the panic-wipe revocation epoch and deduplicate offline replay.
- **missing:** A durable owner-readable projection of pendant delivery events; Mapping from audio frame/cursor to briefing item and source evidence; A reconnect protocol that reconciles monotonic device sequences and chooses the authoritative cursor; A spoken-safe summary for items with no successful playback


## Changes it proposed to its own stack

### `relay` — Make every generated briefing item a durable typed record with item_id, source_refs, generated_at, freshness policy, artifact_id, and delivery state; add a pre-play revalidation transition (fresh, changed, expired, unknown) and idempotent routine dedupe at claim time. Keep skipped/expired records reviewable rather than deleting them.
- **owner gets:** The pendant will stop repeating stale or duplicate information, and the owner can see exactly why something was not spoken. It turns the device from a speaker for jobs into a trustworthy memory of what was actually delivered.
- effort: Medium-high: schema/migration, relay claim hook, Mac/browser source adapters, and pendant handshake; reuse existing event and policy primitives.  ·  risk: A bad matcher could suppress distinct briefings or mark a temporarily unavailable source stale. Fail open only for low-sensitivity, low-impact items; retain a review queue and provide restore/replay. Roll out in shadow mode first.
- cost: Small storage increase for item receipts; lower model/audio cost by avoiding duplicate generation and playback.  ·  latency: <2 seconds only when an offline item is about to play; no impact on live conversation.
- security: Improves privacy by preventing old sensitive content from being spoken after context changes; source refs should be opaque and sensitive snippets excluded by default.
- depends on: A migration for durable briefing-item records; A typed source freshness adapter for mail/calendar/browser; The accepted audio delivery ACK firmware work; A scheduler claim hook for duplicate routine detection

### `integration` — Create a transport-independent 'owner continuity record' that joins relay jobs, Mac jobs, browser commands, audio artifacts, and pendant delivery events under one owner-visible timeline. On reconnect, reconcile by monotonic device sequence plus idempotency key, mark each step generated/downloaded/started/finished/interrupted/unknown, and make every status sentence derive from that timeline.
- **owner gets:** When the cable, browser, or radio drops, the owner can ask one question—'what happened?'—and get a truthful answer instead of repeated work, stale audio, or a confident success that was only accepted by the server.
- effort: High: migration and join logic across five existing ID namespaces, USB/cellular event transport, and a compact dashboard/voice projection.  ·  risk: Incorrect joins could attribute another action to the owner. Fail closed when IDs or authentication do not match; preserve separate records and say unknown rather than merging. Keep raw private content out of the timeline.
- cost: Small durable metadata cost; reduces duplicate model calls and external actions after reconnect.  ·  latency: No live-path cost; reconciliation runs on reconnect and on status queries.
- security: Improves auditability and replay resistance, but creates a sensitive activity timeline; encrypt/limit retention and require provenance authorization for source details.
- depends on: Authenticated USB serial bridge; A shared relay↔Mac↔browser correlation ID; Durable relay job leases and requeue semantics; audio_delivery_ack_queue and record_pendant_delivery_event; A projection route for the owner-visible timeline


## What it asked for

_Nothing._
## Its own summary

Round 153 produced four non-duplicate outcomes: adaptive briefing length from authenticated pendant delivery ACKs; stale-at-play revalidation across pendant/relay/Mac/browser; claim-time deduplication of overlapping morning routines; and a relay change making briefing items durable, freshness-aware, idempotent, and reviewable. The live owner inventory confirms overlapping daily brief schedules, so the dedupe proposal is grounded in an actual owner-visible problem. I also discovered that the reconciliation tool currently mis-resolved my typed read request to a side-effecting POST /briefing, so it cannot yet be trusted as a read arbiter for these domains.

**Biggest unknown:** Whether the relay's routine store exposes a real /v1/routines read/claim surface and where its claim transaction can be extended. I also still need an authoritative owner decision on the timezone conflict (owner memory says America/Chicago; Mac policy says America/New_York), plus the owner-set interruption/disclosure policy; I will not silently choose either.

