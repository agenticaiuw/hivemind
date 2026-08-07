# Harness derivation — faculty-perception — round 95

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device inventory** — Authenticated local agent currently reports home-chrome online and home-macbook-bridge online; cloudflare-contract-test mobile offline. No pendant/nRF9160 is present in the live device list.
  - evidence: discover(devices) at 2026-08-07T14:13Z returned exactly those three devices; GET /ops/status relay payload says macBridgeOnline=true.
- **Mac automation reachability** — AI Pendant Agent is not automation-ready: Accessibility trusted=false, Screen Recording granted=false, inputReachability.status=failed, and synthesized UI events are not accepted. AppleScript automation grants are present for listed apps, and browser extension is online with 9 pending commands.
  - evidence: GET /ops/status and GET /observe at 2026-08-07T14:13Z.
- **browser state** — Browser bridge home-chrome is online but has no active tab metadata (tabId/windowId/url/title empty); durable browser sessions count is 3, with sessions default (time.is/UTC), probe-form2 (selenium web form), and probe-form (httpbin 503).
  - evidence: GET /browser/status and GET /observe at 2026-08-07T14:13Z.
- **audio acceptance telemetry** — Recorded pipeline history contains a successful 24 kHz mono s16le TTS render: 75,734 PCM bytes, 1,578 ms audio, peak 65.2%, RMS 10.2%, clippedSamples=0, and relay accepted the response. This is historical, not live pendant telemetry.
  - evidence: GET /pipeline response, pipeline job_309f5663-e01a-4f8a-b798-319c7c18313f TTS and relay_result events.
- **Mac agent capability manifest** — The live Mac agent exposes 120 routes, including an evidence group for provenance capsules/revocation and an 8-route watches group; its ops status remains not ready solely because Accessibility and Screen Recording are missing, despite requiredMissing=[] and broad AppleScript grants.
  - evidence: GET /capabilities at 2026-08-07T14:13:56Z and GET /ops/status at 14:13Z.

## Capabilities it proposed

### "“I lost connection for a moment—catch me up on exactly what I missed and continue from there.”"
- **useful because:** A wearable conversation can fail between transcription, planning, relay delivery, and playback. Today the owner can see historical pipeline records, but cannot ask the system to distinguish an unanswered turn from a heard turn, summarize only the missing exchange, and resume without repeating or accidentally executing the interrupted request. This creates a true interruption-recovery experience spanning the pendant, relay, Mac planner, and private browser context.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Realtime for the short spoken catch-up only; a cheaper background model should reconstruct and summarize the interrupted turn, with deterministic receipt/state checks before any model call.
- **latency:** On reconnect, a concise catch-up should begin within 2 seconds; deeper reconstruction may take up to 10 seconds and should be clearly labeled as still preparing.
- **cost:** Usually under $0.01 using cached transcript and pipeline metadata; realtime cost dominates only for speaking the catch-up. No browser model call if no browser context was involved.
- **security:** Only use the owner's authenticated browser tabs when the interrupted turn explicitly depended on them; redact secrets from stored recovery summaries; never replay an action or submit a form automatically. If the interrupted request was destructive or ambiguous, resume in review mode and require confirmation.
- **missing:** A durable turn state machine shared by relay and Mac with states such as received, planned, acted, response-rendered, delivered, playback-started, and playback-finished; Pendant reconnect/button protocol that requests recovery by turn ID and acknowledges the catch-up; A browser-context snapshot reference (not copied page secrets) that lets Mac-planner reopen the same authenticated session when reconstruction needs it; A policy for expiry and deletion of unfinished-turn recovery data


## Changes it proposed to its own stack

### `integration` — Add an end-to-end delivery correlation protocol for every spoken response: the relay assigns a response nonce tied to pipelineId and intended device; the Mac bridge includes it in the PCM manifest; a connected pendant must emit signed lifecycle receipts (downloaded, playback-started, playback-finished, interrupted/underrun) with monotonic uptime and byte count; the relay stores the compact receipt and the local agent projects it alongside /pipeline. If no device ACK arrives before TTL, mark the response undelivered rather than successful. When no pendant is registered, automatically label all audio records historical.
- **owner gets:** The owner can finally know whether words were merely rendered on the Mac, accepted by the relay, or actually heard. It prevents a dangerous false success when the bridge is online but the wearable is missing or disconnected.
- effort: Medium: protocol/schema changes in relay, Mac bridge, and nRF9160 firmware, plus dashboard/pipeline projection and a simulator test harness.  ·  risk: Old firmware will not send receipts; the relay must treat missing receipts as unknown (never failure or success) and retain compatibility with current upload APIs. Lost final ACKs can produce unknown even after playback; add replay-safe receipt IDs and a short completion grace window.
- cost: Negligible storage (a few hundred bytes per response lifecycle); no additional model calls. LTE uplink adds roughly 2–5 tiny receipt packets per response.  ·  latency: No added speech-start latency; receipt writes are asynchronous. Final confidence is available within the playback duration plus a 2–5 second grace window.
- security: Bind receipts to a per-device rotating key/nonce to prevent forged 'heard' claims or cross-device confusion; do not include audio or transcript in receipts. Requires pairing/key rotation support.
- depends on: A live pendant registration and delivery-ack route in the relay; Firmware playback lifecycle telemetry skill on nRF9160; A compact pipeline receipt projection in the Mac agent/dashboard

### `context` — Create a durable interruption ledger that joins one owner turn across relay transcription, Mac planning/execution, browser evidence, pipeline rendering, and wearable delivery. Each ledger entry stores only IDs and compact state transitions (not duplicated audio/page secrets), has a TTL, and exposes a recovery projection: what the owner said, what the system actually did, what response was rendered, and the first unconfirmed boundary. Reconnection requests resolve against this projection instead of replaying the last transcript.
- **owner gets:** After a dropped connection, the owner gets an exact, non-repetitive explanation of what happened and can safely continue. They no longer have to guess whether an action ran, whether a reply was merely rendered, or whether a private browser lookup was still pending.
- effort: Medium-high: shared event schema and idempotent writes in relay and Mac agent, references from jobs/journal/pipeline/evidence, plus pendant reconnect protocol and dashboard recovery view.  ·  risk: Partial writes and clock skew could create contradictory states. Use monotonic sequence numbers per turn, append-only events, explicit unknown states, and never infer playback or action completion from timeout alone. Expire recovery records conservatively and provide a redacted audit tombstone.
- cost: Small D1/local JSON growth per turn; no routine model cost. A cheap summarizer is needed only when the recovery projection exceeds the spoken catch-up budget.  ·  latency: Normal turns add one asynchronous ledger write and negligible latency. Recovery adds one bounded read/aggregation, with model summarization only when necessary.
- security: Ledger must contain opaque references and redacted excerpts, not raw authenticated page content or audio by default. Enforce per-device pairing and owner-session authorization for recovery reads.
- depends on: A shared relay/Mac turn identifier and append-only event contract; Wearable reconnect and recovery request/ack messages; Stable job, journal, pipeline, browser-evidence, and delivery receipt references


## What it asked for

_Nothing._
