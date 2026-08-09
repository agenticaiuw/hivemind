# Harness derivation — faculty-perception — round 260

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser readiness** — At 2026-08-09T04:13Z the Mac local agent reports Accessibility and Screen Recording granted, all required automation permissions granted, requiredMissing=[], ready=true; Safari extension is online with one YouTube tab (tab 85), extension v1.2.0, pendingCommands=0. Relay is reachable and Mac bridge online. Device discovery lists nrf9160-pendant offline with lastSeenAt 2026-08-09T02:56:31.366Z; this does not establish current pendant connectivity.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) invoked GET /ops/snapshot, HTTP 200; response body contains permissions.ready=true, browser.online=true, tab metadata, relay.reachable=true. discover(devices) returned nrf9160-pendant offline.

## Capabilities it proposed

### "Before you do anything consequential, tell me whether the command survived capture, transcription, planning, and the final Mac/browser handoff; if any link is uncertain, stop instead of guessing."
- **useful because:** This would be the system's most valuable trust boundary: today a relay result or Mac completion can look successful even when the owner's speech was degraded or the final UI state is unknown. It combines the pendant's local capture verdict, relay trace, Mac receipt, and browser evidence into one causal answer rather than presenting a confident fiction.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime for the short spoken gate; background/cheap model for normalizing receipts and evidence after the turn.
- **latency:** Under 700 ms added before an irreversible action; post-action evidence can arrive within 3 s.
- **cost:** About $0.01–$0.04 per consequential turn depending on whether a vision/browser evidence pass is needed; most turns use structured events, not another model call.
- **security:** Do not transmit raw microphone audio or page secrets into the evidence ledger. Store bounded quality metrics, hashes, action IDs, and redacted before/after claims. Require explicit confirmation for destructive actions even when all links are healthy.
- **missing:** A shared turn ID propagated from pendant capture through relay STT/planning to Mac and browser receipts; A relay reader that joins the existing pipeline events, Mac action ledger, and browser provenance into one causal verdict; A defined policy for which uncertainty levels block execution

### "If my earbuds, audio bridge, or Mac output stops being usable, switch to the safest available path and tell me in one sentence—never keep speaking into a silent or wrong device."
- **useful because:** The owner experiences this as a system that suddenly goes deaf or talks nowhere. The ESP32 bridge, Mac audio route, relay, and pendant can each be healthy independently; only a cross-surface observer can detect the broken hop and choose pause, Mac speaker, or a queued replay without pretending delivery succeeded.
- **path:** pendant → relay → mac
- **model tier:** No model for detection or routing; use device telemetry and deterministic policy. Realtime only for the short spoken status when an alternate path is confirmed.
- **latency:** Detect within 1 s of a failed route and switch or pause within 2 s.
- **cost:** Near-zero API cost; bounded telemetry and one optional TTS sentence per failure.
- **security:** Never silently route private speech to an unexpected speaker or nearby Mac. Treat a changed output device as a confirmation boundary; default to pause and visual/log notification when the target is ambiguous.
- **missing:** ESP32 bridge telemetry for physical output presence, underruns, and selected endpoint; A Mac audio-route observer joined to relay delivery state and pendant offline-reality-beacon frames; A deterministic fallback policy with an owner-selected privacy mode

### "Give me a single physical panic action that freezes every pending action, browser command, relay job, and queued announcement, then tells me exactly what was stopped and what could not be stopped."
- **useful because:** A wearable is the one surface available when the Mac screen is inaccessible or an action is going wrong. Today cancellation is fragmented across jobs, browser spool, relay announcements, and Mac execution; a pendant button or spoken stop must be able to halt the whole causal chain, not just the current voice turn.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic cancellation fan-out; realtime model is not needed. Use a cheap summarizer only to speak the bounded stop report.
- **latency:** Local pendant stop immediately; relay/Mac/browser cancellation fan-out acknowledged within 2 s, with unresolved items explicitly listed.
- **cost:** Negligible API cost; one short status synthesis at most.
- **security:** The stop action itself must not require cloud connectivity. Persist a monotonic emergency epoch locally and reject stale queued work after reconnect. Never claim cancellation where a non-interruptible OS operation may already have committed; destructive actions still report their commit state.
- **missing:** A pendant-local emergency-stop epoch and button gesture in firmware; One authenticated cancel-all protocol spanning relay jobs, Mac jobs/actions, browser commands/spool, and announcements; Idempotent cancellation receipts that distinguish prevented, interrupted, and already-committed work

### "Show me the exact world you believed at any moment—what the pendant, relay, Mac, and browser each reported, which evidence you trusted, and why your next action followed from it."
- **useful because:** Today the system can retain separate traces, receipts, browser records, and device observations, but it cannot reconstruct a synchronized belief state. When an action surprises the owner, there is no way to distinguish stale browser state, delayed relay data, a bad transcription, or an incorrect judgment. A time-indexed belief replay would make every consequential decision inspectable without pretending that a later snapshot was true earlier.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic event and clock alignment first; use a cheaper background model to summarize a selected interval. Realtime is only needed if the owner asks during a live turn.
- **latency:** Record events asynchronously with no perceptible turn delay; return a 10-second replay in under 2 seconds and a model summary in under 5 seconds.
- **cost:** Low structured-storage cost and negligible API cost for raw replay; roughly $0.002–$0.02 for an optional interval summary.
- **security:** The replay may expose private page titles, messages, or action arguments. Encrypt at rest, redact secrets before persistence, enforce per-owner access, and let the owner delete an interval. Never infer missing events as negative evidence; mark clock skew and gaps explicitly.
- **missing:** A monotonic correlation clock and turn/causal ID shared by firmware, relay, Mac agent, and Safari extension; Append-only, bounded belief snapshots that record observations, freshness, confidence, policy inputs, and the decision actually emitted; A dashboard/query endpoint that reconstructs an interval while labeling unknown, delayed, and superseded evidence


## What it asked for

_Nothing._
## Its own summary

Three new owner-facing capabilities were recorded: (1) a cross-surface pre-action trust gate that refuses to act when capture/transcription/handoff evidence is incomplete; (2) automatic audio-route failure recovery across pendant, ESP32 bridge, Mac, and relay; and (3) a physical pendant emergency stop that freezes pending work across relay, Mac, browser, and announcements with honest cancellation receipts. I also recorded that Accessibility, Screen Recording, and required Mac automation permissions are now granted; Safari is online on one YouTube tab; the relay and Mac bridge are reachable. The local agent's /v1/devices/status probe is not the relay route and returned 404, while device discovery now lists nrf9160-pendant offline with a recent lastSeenAt.

**Biggest unknown:** Whether nrf9160-pendant is physically connected and what its current firmware health frame says. I still need an authenticated relay-side device-status/health read (or a route proxy to it), plus the actual pendant/ESP32 telemetry, before asserting live wearable connectivity. I do not need another TCC grant request; that blocker is resolved.

