# Harness derivation — faculty-perception — round 32

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-operability** — At 2026-08-07T10:36:32Z the Mac bridge is online and relay reachable, but Mac agent is not ready: Accessibility trusted=false, synthesized input rejected because permission is granted to a different binary; Screen Recording is false. Consequently ui_click/ui_menu/type_text/press_keys receipts cannot be trusted and UI actions do nothing.
  - evidence: GET /ops/status and GET /observe both report trusted:false, eventsPost:false, screenRecording:false, uiActionsWillReachTheScreen:false.
- **browser-operability** — Browser bridge home-chrome is offline as of 2026-08-07T10:36:04Z, with 3 pending commands; browser sessions/tabs exist locally but browser actions cannot execute while extension is not polling.
  - evidence: GET /ops/status and GET /browser/status report online:false, pendingCommands:3; GET /jobs shows repeated browser_navigate failures explicitly stating extension offline.
- **audio-pipeline-observation** — A recent relay response pipeline run rendered 24,000 Hz mono PCM successfully (164,650 bytes, 3.430 s, 0 clipped samples), while input telemetry for the same interaction was 15,625 Hz PCM capture (937,500 bytes, 1.441 s transcription duration). Pendant offline alert/bookmark events are being surfaced from microSD, but listed nRF9160 runs remain status=processing after delivery.
  - evidence: GET /pipeline response: job_165... tts done meta sampleRate=24000, pcmBytes=164650, clippedSamples=0; inputTelemetry sampleRate=15625; jobs job_276... and job_e8... contain alert_delivered done events with status processing.

## Capabilities it proposed

### "Before you try to do something, tell me whether you can actually reach the needed device or account; if one path is down, use a safe alternative or explain exactly what I need to fix, and never claim success from a fake receipt."
- **useful because:** Right now the Mac bridge is online but cannot inject UI events because Accessibility is granted to the wrong binary, while the browser extension is offline with queued commands. A single truthful preflight would prevent 45-second browser failures and misleading UI-action receipts, and would let the owner know whether a request can be completed from the pendant before waiting.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for readiness classification and route selection; realtime only to speak the short preflight/result over the pendant
- **latency:** Under 500 ms for cached heartbeats and permission state; up to 2 s for a fresh cross-surface probe. Never wait for a dead browser or UI action timeout.
- **cost:** Usually near-zero using cached deterministic health state; occasional background classification around 2k prompt tokens. Realtime cost only for the spoken response.
- **security:** Do not expose bearer tokens, tab URLs, or private account details in the spoken status. Browser preflight may inspect only extension heartbeat and tab/session metadata, not page contents. UI permission probes must be zero-delta and read-only. Require confirmation before any fallback that changes a different surface or sends/submits data.
- **missing:** A typed, freshness-bounded cross-surface readiness contract (pendant link, relay reachability, Mac accessibility/input reachability, screen recording, browser polling, session affinity); A planner preflight that maps requested action types to required reachability and rejects impossible routes before enqueueing; A queue policy that expires or quarantines stale browser commands instead of leaving pendingCommands=3 indefinitely; A receipt invariant: UI actions cannot be marked successful unless an independent postcondition or trusted accessibility evidence confirms the effect

### "After you do something for me, let me ask “Did it really happen?” and get one honest answer that traces the whole chain—from my button press and spoken request, through relay delivery and Mac/browser execution, to what was actually observed afterward—plus the exact point where evidence stops if it cannot be proven."
- **useful because:** Today the surfaces each report local progress, but the owner cannot distinguish a request that was spoken, queued, delivered, attempted, or genuinely changed the world. A single cross-device evidence answer would prevent false confidence, especially when a connection drops or an executor returns success without UI reachability.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic event-chain reconciliation first; use a cheap background model only to turn conflicting evidence into a concise explanation. Realtime is used only if the owner asks from the pendant.
- **latency:** Return a cached chain in under 500 ms; reconcile newly arriving receipts asynchronously and notify the pendant when the verdict changes. Never block on an unavailable surface.
- **cost:** Near-zero for hash/event reconciliation; occasional background summarization under 1k tokens. Storage is the dominant cost: compact append-only evidence records and hashes, not audio or page contents.
- **security:** Keep page contents, credentials, and raw audio out of the chain; retain only opaque identifiers, timestamps, action types, tab/session hashes, and postcondition summaries. Sign records per surface and reject forged or replayed events. Require confirmation before exposing sensitive destination names in spoken output.
- **missing:** A shared append-only evidence protocol with per-surface signatures, monotonic sequence numbers, clock uncertainty, and explicit states (heard, accepted, delivered, attempted, observed, disproven, unknown); Pendant-side acknowledgement events for request receipt and playback completion, including offline buffering and later upload; Mac/browser postcondition attestations that describe what changed without exporting private page content; A relay reconciler that handles late, duplicate, and contradictory events and exposes one verifiable chain to the dashboard and voice agent


## Changes it proposed to its own stack

### `dashboard-ux` — Add a live 'can act now' matrix and preflight timeline to the dashboard and spoken status: each surface reports heartbeat age, required permission, trusted evidence, and fallback route. Mark queued browser commands as stale after a deadline and require explicit retry after the extension returns. For every attempted UI action, display 'requested', 'observed', or 'not verified' rather than treating an executor return value as success.
- **owner gets:** The owner can immediately see why a request cannot happen and fix the right thing (grant Accessibility to the actual AI Pendant Agent binary, enable Screen Recording, or bring the browser extension online) instead of waiting through timeouts or trusting an action that did nothing.
- effort: Medium: typed readiness endpoint in relay/Mac agent, dashboard panel, queue expiry, and receipt schema/postcondition checks.  ·  risk: A stale heartbeat could temporarily hide a usable route; use freshness windows and a manual retry. A stricter receipt state may surface existing false-success histories as unverified rather than completed, which is safer and reversible.
- cost: Negligible runtime/API cost; one deterministic heartbeat aggregation and a few D1 fields per command. No additional model call required.  ·  latency: Improves latency by failing before dead-route timeouts; dashboard refresh can be 1–5 seconds.
- security: Reduces accidental actions by refusing to present unverified UI effects as successful; exposes only health metadata, not page contents or bearer tokens.
- depends on: Cross-surface typed readiness contract; Independent UI postcondition evidence; Browser queue expiry/quarantine policy


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: Mac bridge and relay are online, but Mac input is unusable (Accessibility false for the running binary; screen recording false), browser extension is offline with 3 pending commands, and repeated browser jobs failed after 45-second waits. Audio output is currently rendered at 24 kHz with no clipping, while capture remains 15.625 kHz; offline pendant alerts/bookmarks are being surfaced. Recorded these findings, informed judgement/action agents, and proposed a cross-surface truthful preflight plus dashboard readiness/receipt verification.

**Biggest unknown:** Pendant live diagnostics and continuity acknowledgement/retention semantics remain unavailable; the requested diagnostic tool/context has not appeared this round. I also cannot verify whether the Accessibility grant can be repaired without an owner-facing System Settings action.

