# Harness derivation — faculty-perception — round 26

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-readiness** — At 2026-08-07T10:14Z Mac local agent is not ready for trustworthy UI automation: Accessibility is untrusted for the running AI Pendant Agent binary, synthesized events are rejected, and observe explicitly says ui_click/type_text/press_keys may report success while doing nothing. Screen Recording is also not granted.
  - evidence: GET /ops/status and GET /observe: permissions.ready=false; accessibility.trusted=false; eventsPost=false; uiActionsWillReachTheScreen=false; screenRecording=false.
- **browser-bridge-live-state** — At 2026-08-07T10:14Z the Chrome browser extension is offline with no attached tab and 3 pending commands; browser actions cannot currently be assumed to execute.
  - evidence: GET /browser/status and GET /ops/status: online=false, tabId=null, pendingCommands=3.
- **audio-output-observed** — A recent relay response completed end-to-end as 24,000 Hz mono s16le PCM: 164,650 bytes, 3.430 seconds, no truncation or clipping; relay accepted it for pendant download.
  - evidence: GET /pipeline run job_165a9c9a... events: TTS done sampleRate=24000, pcmBytes=164650, truncated=false, clippedSamples=0; relay_result done.

## Capabilities it proposed

### "When you tell me something was done, tell me whether it was only planned, executed on the Mac, delivered to the pendant, and actually heard or seen by me; if any stage is unknown, say exactly which one."
- **useful because:** The current system can produce misleading success: UI actions may be no-ops when Accessibility is untrusted, browser commands can remain pending while the extension is offline, and audio can be accepted by the relay without proof the pendant played it. A single owner-facing truth status prevents acting on false completion receipts.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → unified → dashboard
- **model tier:** Background model for receipt reconciliation; realtime only for the short spoken status when the owner asks. Deterministic state transitions and hashes should do most of the work without an LLM.
- **latency:** Under 1 second for a spoken status from cached receipts; asynchronous updates as each stage acknowledges. No expensive model call for ordinary acknowledgements.
- **cost:** Usually near-zero model cost; occasional receipt reconciliation under $0.01, dominated by background summarization of ambiguous failures. Small durable event records and optional audio hashes dominate storage, not API spend.
- **security:** Receipts must not include private page contents or secrets. Store operation IDs, capability/permission state, timestamps, hashes, and coarse outcomes. Browser and Mac evidence stays local unless the owner explicitly requests a remote summary. Sending, deleting, purchasing, or form submission still requires confirmation.
- **missing:** A shared append-only operation/receipt schema spanning planner, Mac action runner, browser bridge, relay delivery, and pendant playback lifecycle; A real pendant playback-start/playback-end/interrupt acknowledgement with operation ID and optional checksum; A Mac action preflight that marks UI actions impossible when Accessibility or Screen Recording is missing instead of returning success; Browser reconnect handling that either executes or expires the 3 pending commands with explicit outcomes; Dashboard and voice formatter for the four-state chain: planned, executed, delivered, experienced

### "When something I asked for silently fails or becomes ambiguous, let me press the pendant button once to capture a private recovery packet and have you prepare the exact next step—without me reconstructing what happened."
- **useful because:** Today the owner can be left with a misleading success receipt, an offline browser queue, or a Mac UI action that never reached the screen. They should be able to recover from that uncertainty with one physical gesture instead of remembering timestamps, tabs, permissions, and spoken context.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard → unified
- **model tier:** Use deterministic correlation and local redaction first; use a cheap background model to summarize the incident and propose recovery. Realtime is only needed if the owner immediately asks aloud what failed.
- **latency:** Capture must be immediate and offline-capable; packet assembly within 5 seconds after connectivity returns; spoken recovery summary under 2 seconds from cached data.
- **cost:** Usually no model call for capture. Background summarization should stay below $0.01 per incident; storage is a few KB of metadata plus bounded, redacted evidence excerpts.
- **security:** The packet may touch private browser pages, Mac logs, and audio metadata. Keep raw evidence on the Mac, encrypt the packet in transit, redact page text and secrets by default, and require explicit approval before uploading screenshots, sending reports, or retrying irreversible actions.
- **missing:** A pendant offline incident-bookmark event with operation ID, monotonic timestamp, link state, and bounded local retention; Relay correlation across recent planner, Mac, browser, delivery, and playback events with deterministic redaction; Mac/browser adapters that expose evidence references and reversible recovery candidates rather than raw private content; A background incident summarizer and dashboard review card with retry, discard, and permission-fix choices; A physical/voice acknowledgement path confirming that the recovery packet was captured


## Changes it proposed to its own stack

### `relay` — Add a cross-surface freshness and contradiction ledger. Every operation receipt carries operationId, producer, observedAt, evidence class, and expiry. The relay rejects or downgrades completion claims when the latest Mac/browser/pendant evidence is older than its TTL or contradicts a newer offline/permission event; it emits a compact contradiction event for unified and dashboard rather than silently choosing success.
- **owner gets:** The owner will stop hearing 'done' when the browser was offline, a UI action could not reach the screen, or audio was merely uploaded. They get a precise 'queued', 'executed', 'delivered', or 'not verified' answer and can recover from failures without guessing.
- effort: Medium: typed event schema and D1 indexes, relay reducer, freshness policies per operation class, plus adapters in Mac and pendant firmware. Test with delayed, duplicated, and reordered events.  ·  risk: A bad TTL could label a genuinely completed long-running job stale, or an out-of-order event could create a false contradiction. Keep raw events immutable, make reducer versioned, and allow replay/reconciliation; never delete evidence when compacting.
- cost: Negligible API cost; a few hundred bytes per lifecycle event and modest D1 growth. Background reconciliation can use a cheap model only for human wording.  ·  latency: Constant-time status lookup; sub-second extra relay processing. No added voice latency unless a contradiction must be summarized.
- security: Ledger stores metadata and content hashes, not page text, email bodies, or audio. Hashes should be scoped per owner and operation to avoid cross-task correlation.
- depends on: A shared operation/receipt schema across relay, Mac, browser bridge, and pendant; Pendant playback lifecycle telemetry with operation IDs; Permission-aware Mac preflight and browser reconnect/expiry semantics

### `firmware` — Add a crash- and link-resilient causal watermark to every pendant event: a boot/session epoch, monotonic sequence number, capture uptime, link state, and operation ID are written atomically beside bookmarks, held alerts, microphone uploads, and playback acknowledgements. On reconnect, the pendant uploads missing ranges and explicitly marks gaps, duplicates, and events acknowledged by the relay.
- **owner gets:** When a request fails or arrives late, the owner can get a trustworthy reconstruction of what the pendant actually captured, held, played, or lost—even across reboot and cellular dropouts—instead of an explanation based on unreliable wall-clock timestamps.
- effort: Medium firmware/storage work plus relay ingestion and test fixtures for power loss, reboot, duplicate upload, and long offline periods. Keep the record format append-only with periodic compaction.  ·  risk: A torn write or sequence rollover could make events appear missing or duplicated. Use dual-sector commits, a boot epoch, CRC, and replay tests; never interpret a missing range as proof that nothing happened.
- cost: A small fixed metadata record per event (roughly tens of bytes) and negligible runtime power; modest flash/microSD wear. No recurring API cost.  ·  latency: Sub-millisecond event write path; reconnect reconciliation is asynchronous and should not delay interaction.
- security: Persist identifiers and timing, not raw audio or message contents. Encrypt sensitive operation references at rest and rotate the session epoch after reset if needed.
- depends on: A relay event-ingestion protocol that accepts sequence ranges and gap markers; Operation IDs shared by Mac, browser, relay, and pendant; Bounded offline retention and explicit acknowledgement semantics


## What it asked for

_Nothing._
