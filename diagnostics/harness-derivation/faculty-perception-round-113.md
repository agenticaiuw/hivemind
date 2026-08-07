# Harness derivation — faculty-perception — round 113

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live_mac_permissions** — At 2026-08-07T17:36:55Z the online Mac agent reports Accessibility trusted=false, Screen Recording granted=false, inputReachability failed, uiActionsWillReachTheScreen=false; automation grants are present and browser extension is online.
  - evidence: GET /ops/status and GET /observe, both HTTP 200; observe consequence explicitly says UI actions report success while doing nothing.
- **browser_identity_mismatch** — Safari bridge is online with 3 tabs, but its reported active device tab is URL https://example.com with title 'Failed to open page', while the durable default session maps the same tabId 901786 to Gmail title 'Inbox (14,987)...'. This is an unresolved observation/provenance mismatch.
  - evidence: GET /browser/status at 2026-08-07T17:36:55Z versus GET /observe browser.tabs.
- **pipeline_audio_and_staleness** — Pipeline history contains a completed 24 kHz mono PCM TTS artifact (75,734 bytes, 1,578 ms, no clipping) uploaded to relay, but the associated run is historical (12:00) and another run remains processing with source nrf9160 despite no registered live pendant; pipeline records cannot be treated as current device presence.
  - evidence: GET /pipeline HTTP 200; events include sampleRate 24000, pcmBytes 75734, relay accepted, and source nrf9160 historical run.

## Capabilities it proposed

### "“Tell me when the system is talking about a device or run that does not exist anymore, and cleanly separate live state from recorded history.”"
- **useful because:** The live registry has no pendant, yet pipeline history contains nrf9160-originated runs and language saying audio is waiting for the pendant. This capability would stop stale telemetry from being presented as current reality and would explain exactly what is historical, orphaned, or live.
- **path:** relay-realtime → mac-planner → mac-terminal → dashboard → pendant
- **model tier:** background rules/cheap model for reconciliation; realtime only for an urgent spoken warning
- **latency:** Reconcile on every pipeline/device update within 1 second; no model call for ordinary state transitions.
- **cost:** Negligible when implemented as typed joins and TTL checks; occasional short model call only to phrase an unusual discrepancy.
- **security:** Device IDs and historical audio metadata are sensitive. Keep raw payloads local/relay-private, expose only status, timestamps, and redacted IDs. Never delete history automatically; quarantine or label it until retention policy says otherwise.
- **missing:** A typed join between relay device registry and pipeline source IDs; Explicit live-vs-history and orphaned-run status fields on pipeline records; A reconciliation worker and dashboard filter that suppresses orphaned runs from 'current' views

### "“Did you really hear me, and did my reply reach a device I could hear?”"
- **useful because:** Current records can show transcription/upload and 24 kHz rendering, but they do not establish end-to-end delivery to a live wearer: there is no registered pendant, and historical runs can look active. A single integrity answer would distinguish heard, understood, rendered, uploaded, delivered, and played—with an explicit unknown when any link is absent.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** No model for the normal path; deterministic telemetry aggregation. Realtime only to answer the owner's spoken question.
- **latency:** Return within 500 ms from cached telemetry; recompute on each audio lifecycle event.
- **cost:** Negligible API cost; storage is a compact per-turn event record. A rare explanatory summary costs one short text/realtime turn.
- **security:** Audio content and transcripts remain private; expose hashes, byte counts, timestamps, and delivery states rather than raw audio. Never claim playback from upload acknowledgment. Require explicit consent before retaining diagnostic audio.
- **missing:** A durable per-turn audio delivery state machine with monotonic sequence IDs; Pendant playback acknowledgment (start, completion, underrun/error) tied to relay response ID; A live device-presence gate that marks relay acceptance as undeliverable when no pendant is registered

### "“When I press the pendant while I’m looking at something, tell the other parts of you exactly which live context that press belongs to.”"
- **useful because:** A future worn press should not be interpreted against stale browser sessions or an old Mac foreground app. Correlating the press sequence/time with the relay session, Mac foreground app, Safari tab identity, and freshness windows gives every downstream agent one defensible context anchor instead of guessing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event correlation first; cheap background model only to resolve multiple candidates; realtime for the immediate acknowledgment.
- **latency:** Acknowledge within 300 ms and publish a context anchor within 1 second of the button event.
- **cost:** Negligible API/model cost for typed correlation; one short realtime response for spoken confirmation. Storage is a few hundred bytes per press plus optional redacted metadata.
- **security:** Do not capture page contents, keystrokes, or audio merely to establish context. Store only tab ID, origin, title hash, foreground bundle, relay session, monotonic timestamps, and confidence. If candidates disagree, say ambiguous and require the owner to clarify before acting.
- **missing:** A pendant event stream with sequence number and monotonic timestamp (no pendant is registered today); Clock-offset/monotonic correlation between pendant, relay, Mac bridge, and browser extension; A context-anchor object consumed by planner/judgement/action with contradiction and expiry fields

### "“That fact is wrong—show me every place you learned it, let me correct it once, and stop using the old version everywhere.”"
- **useful because:** Today an incorrect observation can be repeated by relay, Mac, browser, and memory because there is no owner-facing fact dispute operation. The owner should be able to invalidate a bad tab identity, stale device state, or mistaken personal fact once and receive a clear propagation receipt.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic provenance traversal and invalidation; use a cheaper background model only to summarize the affected references; realtime merely speaks the confirmation.
- **latency:** Show affected references within 2 seconds and publish the correction immediately; background cleanup can finish within a minute.
- **cost:** Low API cost; the dominant cost is indexing references and retaining compact provenance, not inference.
- **security:** Corrections are consequential and potentially destructive. Require explicit confirmation, preserve an append-only prior version for undo, redact private page contents, and never let a low-confidence inferred correction alter durable memory.
- **missing:** A cross-surface fact registry with immutable source references and reverse links; An owner-confirmed invalidate/replace endpoint consumed by relay, Mac, browser, and memory projection; A dashboard diff showing before/after, affected agents, and cleanup completion

### "“When something important changes while I’m away, tell me what changed, what you ignored, and why.”"
- **useful because:** Existing watches and briefings can report changes, but they do not expose the negative space: which sources were checked, which apparent changes were discarded as noise, and whether a source was unreachable. The owner needs a bounded audit of absence and suppression, not just a confident summary.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Cheap scheduled/background model over normalized diffs; realtime only for an urgent alert or on-demand spoken digest.
- **latency:** Scheduled checks complete within the configured window; an urgent change reaches the owner within 60 seconds of detection.
- **cost:** Low background model cost proportional to changed records; storage is compact normalized diffs and suppression reasons, not page snapshots.
- **security:** Private sources remain on the Mac/browser; relay receives only redacted change facts. Quiet hours and source-specific sensitivity are mandatory. Never infer ‘no change’ from an unreachable source; say unknown.
- **missing:** A source-check receipt schema distinguishing unchanged, changed, suppressed, errored, and not checked; A durable suppression ledger with reasons and expiry, separate from the user's content; A spoken/dashboard view that includes coverage and unknowns without dumping private data


## Changes it proposed to its own stack

### `context` — Add a cross-surface uncertainty budget and escalation protocol: every observation gets a freshness deadline, contradiction class, and permitted downstream uses; when evidence conflicts or expires, the protocol emits one owner-visible question with the smallest discriminating choices, freezes only dependent actions, and automatically unfreezes after an explicit answer or fresh evidence.
- **owner gets:** The owner gets fewer silent wrong assumptions: instead of a stale Gmail/tab/device belief driving an action, the system asks one precise question and explains what is blocked. Ordinary confident work remains fast.
- effort: High: shared schema and enforcement in relay, Mac planner, browser bridge, dashboard, and memory projection; requires migration of observation-producing routes and tests for contradiction/expiry.  ·  risk: Over-escalation could annoy the owner or halt harmless work; recover with per-fact action scopes, TTLs, and an undoable owner answer. Under-escalation remains visible in audit logs.
- cost: Small storage and event-processing cost; lower model cost over time by preventing repeated re-analysis of stale conflicting context.  ·  latency: Adds sub-second deterministic checks; only ambiguous cases incur a model turn and owner response.
- security: Improves safety by preventing low-confidence facts from authorizing actions; uncertainty metadata must avoid leaking private source content across surfaces.
- depends on: A typed provenance-bearing observation envelope across Mac, browser, relay, and future pendant; An owner-facing contradiction response/receipt route; Per-action declaration of which facts are safety-critical versus advisory


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the Mac bridge and Safari extension are online, but Accessibility and Screen Recording are false and input reachability failed, so GUI receipts are not trustworthy. Safari's active tab identity conflicts with the durable session (example.com/“Failed to open page” versus Gmail on the same tabId). Pipeline contains historical nrf9160 records and a valid 24 kHz rendered/uploaded PCM artifact, but no live pendant is registered; those records cannot prove delivery. Recorded three new cross-surface capabilities: quarantine orphaned device/run telemetry, answer end-to-end audio integrity without claiming playback, and correlate a future pendant press to a fresh Mac/browser context anchor. Still needed: a registered pendant with playback acknowledgments and monotonic event IDs, typed live/history reconciliation between device registry and pipeline, and owner-granted Accessibility/Screen Recording if trustworthy GUI control is required.

**Biggest unknown:** Whether the physical nRF9160 and ESP32 hardware can actually register and emit events; until registration and playback acknowledgments exist, all pendant delivery and press-context claims remain untestable.

