# Harness derivation — unified — round 174

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live pipeline reliability gap** — The live pipeline contains completed 24 kHz TTS and relay acceptance but no physical delivery/playback receipt, and it also contains a job waiting for approval with the spoken text 'Waiting for your approval on the dashboard.' while no dashboard approval path is exposed. A held-alert pipeline remains status processing.
  - evidence: GET /pipeline returned job_309f... with TTS done at 24000 Hz, relay_result done, no playback event; the same run has agent waiting approval. It also returned job_276... status processing with alert_delivered done.

## Capabilities it proposed

### "When I move from the Mac's USB-connected pendant to LTE (or back), keep the current conversation alive without repeating or losing a turn."
- **useful because:** The pendant is physically usable over USB today while LTE is unregistered, but a transport change currently risks duplicated audio, missing final frames, or a second conversation. The owner gets one continuous conversation regardless of where the link is available.
- **path:** pendant → mac-bridge → relay → mac-planner
- **model tier:** Realtime for the active audio session; deterministic code for cursor reconciliation and duplicate suppression.
- **latency:** Handoff at a turn boundary in under 500 ms; never interrupt an already-playing 60 ms audio packet.
- **cost:** Negligible model cost during handoff; roughly 1-2 KB of cursor/receipt metadata per turn, with audio remaining on the active path.
- **security:** Bind each handoff to a device session nonce and monotonic turn/frame cursor; reject stale transport claims and never upload a second copy of captured audio. Owner confirmation should not be needed for a normal transport fallback.
- **missing:** A production USB audio-session route that exposes the accepted usb_fallback_audio_session firmware behavior to the Mac bridge; Relay-side session cursor/epoch persistence and idempotent turn reconciliation; A bridge-to-relay acknowledgement that distinguishes accepted, played, and abandoned frames

### "Before I rely on an answer about something I promised or was supposed to do, tell me whether there is fresh evidence it was completed, and say what remains unverified."
- **useful because:** Commitments currently disappear into conversation even when the relevant browser tab or Mac app contains completion evidence. This gives the owner a concise spoken distinction between completed, partially evidenced, and unverified commitments without taking actions or pretending that a search is proof.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** Background model to cluster and summarize evidence; deterministic provenance and freshness filtering first; realtime only when the owner asks aloud.
- **latency:** On-demand response under 5 s for up to ten commitments; background refresh can run hourly or at conversation start.
- **cost:** Cheap background summarization, usually one small call for a batch; evidence queries and freshness checks are the dominant operations.
- **security:** Search only explicitly bound tabs/apps and return evidence candidates, not arbitrary browsing. Redact secrets and page content, preserve source URL/app binding and timestamps, and label absence of evidence as unknown rather than failure.
- **missing:** A durable commitment registry linking spoken commitments to an owner-approved browser/app binding and due window; A read-only aggregator that invokes commitment_evidence_query across those bindings and records provenance; A relay/pendant briefing envelope that surfaces only newly changed evidence and supports dismissal without mutation

### "If I missed your last spoken reply, replay exactly that reply once from the point it was interrupted, rather than making me ask the whole question again."
- **useful because:** A dropped link or privacy latch can leave the owner knowing a turn happened but not hearing it. The system already has artifact IDs and playback receipts in the audio-delivery path; turning that into a bounded replay makes the pendant dependable without repeating a model call or duplicating an action.
- **path:** pendant → relay → mac-bridge → mac-planner
- **model tier:** Deterministic artifact lookup and range replay; no model call unless the original artifact has expired.
- **latency:** Begin replay within 1 s when the artifact is retained; resume only at a frame boundary and never overlap current playback.
- **cost:** No inference cost; storage and egress for one bounded retained audio artifact are dominant, with a configurable short retention window.
- **security:** Replay only an owner-session artifact addressed by opaque ID and device/session nonce; require a local play press after privacy latch, enforce one replay per interruption event, expire audio promptly, and never regenerate a semantically different answer under the same receipt.
- **missing:** A relay audio-artifact retention/index route with frame-range reads and explicit expiry; A pendant/bridge replay command carrying artifact ID, interruption cursor and anti-replay nonce; A policy that records interruption cause and decides whether the owner may request replay after a privacy latch or transport handoff

### "Read the private page I am looking at and tell me the one fact I asked for, but do not retain the page, expose its contents to the pendant, or leave the fact in ordinary agent memory."
- **useful because:** The browser can reach private sessions that the pendant and relay cannot, while the pendant is the safest place for a short spoken answer. Today there is no end-to-end ephemeral boundary: a page read can create evidence capsules and ordinary job/memory records. The owner gets useful private-page answers without turning the agent into a second copy of their account.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** Realtime only for a spoken answer; deterministic redaction, minimization, and deletion enforcement around it.
- **latency:** Answer within 4 seconds for one bound page and one narrow question; erase transient page material immediately after synthesis and delivery.
- **cost:** One small inference call per request; deletion/index maintenance is the dominant engineering cost, not API usage.
- **security:** Require an explicit tab binding and narrow field query, prohibit arbitrary page dumps, redact secrets before relay transfer, encrypt the transient envelope, suppress ordinary memory updates, and emit a deletion receipt. The spoken answer itself must follow the owner's privacy latch and session policy.
- **missing:** A sealed ephemeral browser-result channel that bypasses ordinary evidence capsules, job history, and memory; A relay deletion/expiry primitive with a verifiable receipt across browser, Mac, relay, and pendant; A policy interpreter for the owner's still-unspecified retention and private-audio rules

### "For this session, let the browser read one approved page but forbid actions, forbid saving its contents, and forbid sending anything to the relay except the short answer I request."
- **useful because:** The owner needs a practical middle ground between full browser authority and a total privacy latch. Today permissions are broad and mostly credential-based: a browser session can be read or acted on, but there is no owner-visible, per-session data-and-action boundary spanning the browser, Mac, relay, and pendant.
- **path:** pendant → browser-extension → mac-planner → relay → dashboard
- **model tier:** Deterministic policy enforcement; a small realtime response model only for the requested answer.
- **latency:** Policy takes effect before the next browser command; answer under 4 seconds for a narrow read.
- **cost:** No recurring model cost beyond the requested answer; policy state is a small signed session record.
- **security:** Use a signed capability token carrying tab binding, allowed verbs, destination restrictions, expiry, and a no-memory flag. Enforce it independently in browser, Mac, and relay rather than trusting model instructions. A physical pendant gesture should be required to widen scope.
- **missing:** A cross-surface capability-token enforcement layer for browser commands, Mac jobs, relay persistence, and pendant delivery; A dashboard showing the active scope and a hard revoke path; A relay-side filter that proves only the requested answer crossed the boundary

### "Watch a specific private status page and tell me only if the condition I named changes by the deadline; otherwise stay silent."
- **useful because:** The owner should not need to repeatedly ask the pendant to check a delivery, reservation, account status, or application. A bounded watcher would use the browser's authenticated session, the Mac's schedule, and the relay's always-on reach while avoiding noisy alerts when nothing changed.
- **path:** browser-extension → mac-planner → relay → pendant
- **model tier:** Background/scheduled deterministic checks with a cheap summarizer only when the observed state changes; realtime for the final spoken alert.
- **latency:** Checks at the owner's chosen cadence, with an alert within one polling interval; no polling after expiry or explicit cancellation.
- **cost:** Browser polling and small state hashes dominate; model cost only on a detected change or ambiguous page transition.
- **security:** Bind the watch to one tab/URL pattern and a narrow extraction query, store hashes and redacted deltas rather than page contents, enforce expiry and cancellation, and require confirmation before any resulting action.
- **missing:** A durable conditional-watch record and scheduler that runs on the relay even when the Mac sleeps; A browser bridge lease/reconnect path that can safely revalidate the bound tab; A state-diff and alert policy that distinguishes changed, unavailable, and unknown without treating an outage as success


## Changes it proposed to its own stack

### `integration` — Make every relay_result audio artifact enter an explicit delivery state machine: accepted -> downloaded -> bridge-acknowledged -> playback-started -> playback-finished/interrupted, keyed by the existing artifact/event ID. Emit the state from the ESP32 bridge and pendant, expose it in pipeline events and job receipts, and close or mark stale processing runs when the terminal evidence arrives.
- **owner gets:** The owner will no longer hear 'response waiting for the pendant' as if it meant the answer was heard. They can know whether a reply reached the device, started playing, finished, or was interrupted, and recover a genuinely missing response.
- effort: Medium: bridge and pendant event plumbing, relay persistence, and a small reconciliation worker; validate with the existing pipeline validator and injected loss profiles.  ·  risk: A lost terminal event could leave an artifact pending; use idempotent event IDs, bounded TTL, and a conservative unknown state rather than claiming success. Existing jobs must remain readable during migration.
- cost: Small metadata writes and one compact event per state transition; no extra model calls and no routine audio copies beyond the existing artifact retention.  ·  latency: No added hot-path audio latency; receipt events are asynchronous. Playback-start may be reported within one frame.
- security: Opaque artifact IDs, per-session nonce and monotonic event sequence prevent forged or replayed receipts; retain no more audio than the configured replay window.
- depends on: ESP32 bridge acknowledgement and playback callbacks; audio_delivery_ack_queue (granted device behavior); POST /pipeline/events; GET /jobs/:jobId/receipts; GET /pipeline/:pipelineId/audio/:direction


## What it asked for

_Nothing._
