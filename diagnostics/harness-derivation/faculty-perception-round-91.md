# Harness derivation — faculty-perception — round 91

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-device-state** — As of 2026-08-07T13:52Z, home-macbook-bridge is online; home-chrome browser extension is offline with 9 pending commands; cloudflare-contract-test mobile is offline. No pendant appears in the live device table.
  - evidence: discover(devices) and GET /ops/status both report exactly these devices; relay payload says macBridgeOnline=true.
- **mac-input-reachability** — AI Pendant Agent is running but cannot post synthesized UI input: Accessibility trusted=false, Screen Recording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false. AppleScript automation grants are present for System Events and common apps.
  - evidence: GET /observe at 2026-08-07T13:52:42Z and GET /ops/status.
- **browser-state** — Authenticated browser session store contains 3 tabs (time.is/UTC, Selenium web form, httpbin form), but the browser extension is offline; commands may remain pending and cannot be assumed delivered.
  - evidence: GET /observe and GET /browser/status.
- **relay-pipeline-history** — The pipeline contains historical nrf9160/cloud-relay records, including a completed 24 kHz TTS render and relay acceptance, but current device registry has no pendant; these records establish history only, not current playback or delivery.
  - evidence: GET /pipeline plus GET /ops/status live device state.

## Capabilities it proposed

### "“What is actually reachable right now—and which things you told me were done are only queued or historical?”"
- **useful because:** The system currently exposes several misleading success-shaped records: UI actions can report success without reaching the screen, browser commands can sit pending while the extension is offline, and old pendant pipeline events can look like current delivery. This gives the owner a single concise, sourced reality report instead of trusting any one surface.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Use a cheap background model to reconcile periodic status; use realtime only when the owner asks verbally. Perception should deterministically gather status and label evidence before any model summarizes it.
- **latency:** Live spoken answer under 2 seconds when status endpoints respond; background reconciliation every 5 minutes can take 10–30 seconds.
- **cost:** Usually <$0.01 per report; dominant cost is model summarization, not the local authenticated GETs. Deterministic no-model mode should be nearly free.
- **security:** Private browser tab URLs/titles and relay job metadata leave the Mac only to the authenticated relay/model. Redact page contents by default. Never infer physical playback from a server upload; require a device playback acknowledgement or label it unverified.
- **missing:** An authoritative relay device/delivery registry that distinguishes accepted, downloaded, played, and acknowledged states for each response; A shared evidence schema with source timestamps and TTLs so stale /pipeline events cannot be presented as current; Browser-extension heartbeat/command acknowledgement with explicit queued, received, executed, and expired states

### "“Before I rely on it, run a harmless end-to-end check and tell me whether my pendant, relay, Mac, browser, and audio path are genuinely ready.”"
- **useful because:** Today each surface can look healthy while the chain is unusable: the Mac bridge is online but cannot inject UI input, the browser extension can be offline with queued commands, and relay audio can be accepted without a connected pendant. A user-controlled readiness rehearsal would expose the first broken hop before the owner depends on the system, without performing a real-world action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic orchestration and synthetic test fixtures; use a cheap background model only to summarize failures. Realtime is unnecessary except for an optional spoken pass/fail result.
- **latency:** A complete rehearsal in 10–30 seconds; individual link checks should stream progress immediately.
- **cost:** Under $0.01 per run when using synthetic text/audio and local checks; storage and relay bandwidth dominate, not model inference.
- **security:** The rehearsal must use a sealed test command and disposable browser tab/session, never the owner's logged-in tabs or real apps. Synthetic audio and receipts may leave the device to the relay. Require explicit opt-in for any test that touches a private browser session, and automatically delete test artifacts.
- **missing:** A non-side-effecting end-to-end test protocol with a unique correlation ID carried through capture, transcription, planning, Mac/browser dry-run, TTS, relay delivery, and pendant playback acknowledgement; A pendant test mode that can confirm local decode/playback (or explicitly report no device) without pretending a cloud upload was heard; A browser harness dry-run endpoint that validates extension reachability and tab affinity without mutating a page; A readiness report that identifies the first failed hop and separates unavailable, queued, passed, and unverified


## Changes it proposed to its own stack

### `context` — Add a deterministic evidence-freshness reducer at the relay/Mac boundary. For every assertion (Mac UI action, browser command, relay audio response, pendant playback), store observedAt, source, eventId/jobId, TTL, and terminal state; derive `currentTruth` only from live heartbeats and causally linked acknowledgements. Mark old `/pipeline` events as historical automatically, and expose contradictions (for example relay_result=done while no pendant is registered) instead of flattening them into success.
- **owner gets:** The owner will stop hearing that something was completed when it was merely uploaded, queued behind an offline browser, or accepted by a relay with no pendant to play it. They get an honest answer and a clear next step.
- effort: Medium: shared schema plus reducer, migration of pipeline/job/browser event writers, and dashboard/API presentation.  ·  risk: Incorrect TTLs could mark a slow but valid action stale, or expose a contradiction that confuses the owner. Recover by retaining raw events, allowing source-specific TTL configuration, and showing the underlying evidence links.
- cost: Negligible storage and compute; a few extra metadata fields per event. No model call required for reduction.  ·  latency: Adds milliseconds to status reads; no impact on voice path.
- security: Must avoid copying private URLs or audio into broad context; keep evidence references scoped and redact sensitive fields in summaries.
- depends on: An authoritative relay device registry and delivery acknowledgements (currently missing); Browser extension heartbeat and command lifecycle acknowledgements; A shared event identifier propagated from owner request through planner, action, relay, and playback

### `firmware` — Add a pendant-local playback receipt journal: when an audio response is decoded and the speaker actually starts and finishes playback, firmware writes a compact signed record containing response correlation ID, local monotonic timestamp, byte count, decoder result, and interruption reason to durable storage; it uploads receipts opportunistically when connectivity returns. A server upload alone must never be labeled played.
- **owner gets:** They can finally know whether an answer reached their ears, even after LTE drops or the relay reconnects later, instead of being told that an upload was successful when the pendant never played it.
- effort: Medium firmware and relay protocol work, plus a small dashboard/API surface; test with power loss and reconnect during playback.  ·  risk: Flash wear, power loss during a write, or a spoofed receipt could create false confidence. Use append-only checksummed records, bounded wear-levelled storage, sequence numbers, and label interrupted/unverified records explicitly; retain raw server events for reconciliation.
- cost: Negligible API/model cost; requires a few kilobytes of reserved durable storage and minor firmware power for a write per response.  ·  latency: Sub-millisecond local journaling around playback; upload is deferred and does not delay speech.
- security: Receipts should be authenticated per device and contain no audio or transcript, only opaque correlation IDs and playback metadata. Device enrollment and key rotation are required.
- depends on: A live pendant device registration and authenticated device key; Relay endpoints for receipt upload and deduplication; A shared correlation ID propagated from request through generated audio to playback


## What it asked for

_Nothing._
## Its own summary

Fresh live verification completed. Mac bridge and relay are reachable; no pendant is registered. Browser extension is offline with 9 pending commands. Mac Accessibility and Screen Recording are absent, and /observe explicitly says UI actions may report success while doing nothing. Historical /pipeline records include relay acceptance and 24 kHz rendering, but they do not prove current pendant playback. I recorded these facts, notified faculty-action and unified, and proposed a freshness/causal evidence reducer plus an owner-facing reality report.

**Biggest unknown:** The relay still lacks an authoritative, current acknowledgement chain proving response downloaded and physically played by a pendant; browser commands likewise lack a verified received/executed terminal acknowledgement while the extension is offline.

