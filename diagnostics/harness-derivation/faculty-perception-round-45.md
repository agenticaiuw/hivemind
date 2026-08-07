# Harness derivation — faculty-perception — round 45

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-perception** — At 2026-08-07T11:20Z Mac bridge is online and relay reachable, but AI Pendant Agent still lacks effective Accessibility and Screen Recording: /observe reports accessibility.trusted=false, eventsPost=false, inputReachability=failed, uiActionsWillReachTheScreen=false; /ops/status permissions.ready=false (screenRecording missing). The attempted grant did not apply to the running binary identity.
  - evidence: GET /observe and GET /ops/status returned HTTP 200 with these exact fields; running host is com.aipendant.agent at /Users/evanliu/Applications/AI Pendant Agent.app.
- **audio-perception** — The live pipeline contains a concrete format asymmetry: one cloud-relay job reports inputTelemetry sampleRate=15625 Hz, while its generated response telemetry is 24,000 Hz mono PCM and completed successfully (164,650 bytes, 3,430 ms, 0 clipped samples). Thus output 24 kHz is evidenced, but end-to-end 24 kHz capture is not established.
  - evidence: GET /pipeline at 2026-08-07T11:20Z, run job_165a9c9a-e5e3-4e29-b500-2fad63115ab9: inputTelemetry.sampleRate=15625; tts done meta.sampleRate=24000.

## Capabilities it proposed

### "“When something happened through my pendant, tell me exactly what was heard, what the system understood, what reached my Mac, and what I actually received — including anything that was lost or uncertain.”"
- **useful because:** Today the owner can receive a reply without knowing whether the microphone capture, transcription, planning, Mac handoff, TTS generation, relay delivery, or pendant playback actually succeeded. A cross-node evidence reconstruction would make failures diagnosable instead of silently turning into false confidence, especially after a dropped link or delayed offline event.
- **path:** pendant → relay → mac-planner → faculty-perception → faculty-judgement → dashboard
- **model tier:** Background model for assembling and summarizing the event ledger; realtime only for an immediate short spoken answer when the owner asks on the pendant. Deterministic correlation and integrity checks should do the core work without an LLM.
- **latency:** On-demand spoken status in 1–3 seconds when telemetry is already present; background reconciliation within a minute after connectivity returns.
- **cost:** Usually <$0.01 per reconstructed event, dominated by a small background summarization call; deterministic correlation, hashes, and status classification are effectively free. Audio payloads should not be resent to the model when existing transcripts and format metadata suffice.
- **security:** The ledger may expose private speech, browser destinations, and action results. Keep raw audio local or short-lived, encrypt relay records, use opaque event IDs with per-device authentication, redact transcript content from dashboard previews by default, and require confirmation before sharing an incident report externally.
- **missing:** A single cross-node event ID propagated from pendant capture through relay transcription, Mac planning/action, TTS upload, pendant download, and playback acknowledgement; Signed append-only stage receipts with timestamps, source, format, byte counts, and explicit unknown/failed states; Pendant playback acknowledgement and retention semantics, including a way to distinguish downloaded, started, completed, and interrupted audio; A reconciliation worker and owner-facing timeline that marks contradictions instead of selecting one unverified story; A privacy/retention control for raw audio and transcript evidence


## Changes it proposed to its own stack

### `integration` — Add a perception-backed execution contract between faculty-perception and faculty-action: before any Mac GUI or vision action, the action planner must receive a short-lived signed capability snapshot (Accessibility trust, inputReachability, Screen Recording, foreground app, browser online state) from /observe. The executor must hard-stop or reroute when the snapshot says uiActionsWillReachTheScreen=false, and receipts must include the snapshot ID and observed pre/post evidence. Refresh on expiry or foreground-app change; never infer readiness from HTTP 200 or an action's nominal success.
- **owner gets:** The pendant will stop claiming it clicked or typed when macOS silently ignored the event, and can honestly explain why it cannot act or switch to a safer browser/API route.
- effort: Medium: schema plus relay/Mac-agent verification, action-router integration, and tests for stale snapshots, permission loss, and foreground changes.  ·  risk: A false negative may pause an otherwise safe action; recover by offering a retry after reprobe or a non-GUI route. A compromised local agent could forge state unless snapshots are authenticated and bound to the running binary.
- cost: Negligible API cost; one small local status read per action batch and a few hundred bytes of metadata per receipt.  ·  latency: ~50–150 ms for a local probe; no model latency unless rerouting requires planning.
- security: Improves safety by preventing unauthenticated/ineffective UI actions; snapshot must avoid exposing window contents and must be scoped to capability state only.
- depends on: Effective Accessibility and Screen Recording grants for the exact running binary when GUI control is desired; A typed receipt schema that can carry snapshot ID and evidence; Action router support for non-GUI fallback paths

### `context` — Create a fleet-wide contradiction detector that compares independent observations from pendant, relay, Mac, browser, and playback telemetry and emits typed contradictions rather than silently choosing a winner. Initial rules should catch nominal UI success while inputReachability is false, a response marked delivered without a playback acknowledgement, mismatched audio sample rates, stale browser-online claims, and event timestamps that move backward. Each contradiction gets severity, affected request IDs, first/last observed times, and an owner-safe explanation; it must remain visible until resolved or explicitly acknowledged.
- **owner gets:** The owner gets an honest warning that the system's story is internally inconsistent before relying on a missed click, unheard answer, or stale private-page result. Today each subsystem can look healthy in isolation while the end-to-end experience is broken.
- effort: Medium-high: typed observation schema, rule engine, durable contradiction state, and a small dashboard/pendant summary surface. Start with deterministic rules; add no model dependency for detection.  ·  risk: Noisy warnings could train the owner to ignore alerts. Mitigate with severity thresholds, deduplication, expiration, and only surfacing contradictions that affect a requested outcome. Incorrect clock assumptions could create false positives; compare monotonic sequence numbers where possible.
- cost: Near-zero model/API cost; modest D1/storage growth for compact observations and contradiction records. Raw audio/content is not required.  ·  latency: Subsecond after each stage receipt; a short background reconciliation pass after delayed/offline events.
- security: Improves integrity without collecting new content, but status metadata still reveals activity patterns. Encrypt records, scope them per owner/device, and retain only unresolved contradictions plus a short history.
- depends on: A common event/request correlation ID across all nodes; Signed, timestamped stage receipts from pendant, relay, Mac, browser, and playback; A durable acknowledgement/retention policy for contradiction records; Owner-facing severity and notification policy


## What it asked for

_Nothing._
## Its own summary

Fresh probes after the orchestrator's grant action show the grant did not take effect on the actual running binary. Mac bridge and relay are online, but GUI perception/control is not trustworthy: Accessibility is false, synthesized events are rejected, inputReachability is failed, Screen Recording is false, and permissions.ready is false. Browser extension is offline with 3 pending commands. I recorded these facts and proposed a new perception-backed execution contract that cryptographically/temporally binds action receipts to a live /observe capability snapshot, preventing false claims and enabling safe rerouting. I also recorded that output TTS has a successful 24 kHz trace, while one captured input trace is 15,625 Hz, so end-to-end 24 kHz capture remains unproven.

**Biggest unknown:** Why macOS granted permissions to a different binary identity despite the requested exact identity, and whether the pendant's actual microphone capture path is intended to be 15,625 Hz or 24 kHz.

