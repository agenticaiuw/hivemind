# Harness derivation — unified — round 258

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device and audio delivery state** — Mac bridge and Safari browser are online; nRF9160 pendant is offline. The newest pipeline run has 122,630 bytes of 24 kHz mono PCM accepted by relay but delivery state held_by_relay, awaitsDevice=true, and provesPlayback=false because no device_playback event exists.
  - evidence: GET /ops/snapshot and GET /pipeline responses in round 258

## Capabilities it proposed

### "“When I turn privacy mode on, prove that nothing is still listening, playing, queued, or exposed—and block any Mac/browser action until I physically clear it.”"
- **useful because:** The pendant latch already stops local capture/playback, but today that state is not an enforcement boundary for relay-held audio, Mac jobs, or browser commands. This would make the owner's physical privacy action apply to the whole hive, not just one chip.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime only for the immediate latch acknowledgement; deterministic relay/Mac policy for cancellation, blocking, and convergence checks.
- **latency:** Pendant mute within one audio frame; relay and Mac/browser quarantine within 1 s; authenticated convergence receipt within 3 s.
- **cost:** <$0.01 per latch event; dominated by one small realtime acknowledgement and one deterministic cross-surface read.
- **security:** Latch enter/clear events must be authenticated and monotonic; fail closed on missing or stale state. Do not transmit audio or page contents in the proof. Clearing requires the physical latch event, never a spoken command.
- **missing:** Relay enforcement hook that rejects new capture/playback and browser/Mac dispatch while latched; Mac/browser cancellation of already queued work with receipts; A durable latch-state binding shared by pendant, relay, and local agent

### "“When my pendant comes back online, show me the replies waiting to be heard, discard anything stale, and let me replay one deliberately—never surprise me with an old answer.”"
- **useful because:** The live relay currently records replies as held_by_relay and explicitly cannot prove playback; the pendant is offline while 24 kHz audio is already waiting. A reconnect handoff that distinguishes queued, stale, fetched, started, finished, and unheard prevents delayed speech from arriving out of context.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic queue aging, deduplication, and playback receipts; cheap background model only to summarize multiple stale replies.
- **latency:** Inventory on reconnect within 2 s; owner choice acknowledged within 1 s; no automatic playback of stale items.
- **cost:** <$0.01 per reconnect; storage/receipt traffic dominates, with optional summary costing a few cents only when many items accumulate.
- **security:** Use opaque artifact IDs and hashes, not transcript/audio in dashboard inventory unless requested. Retain audio only under the existing failure/ack policy. Require explicit physical play or discard for stale items and keep an audit receipt.
- **missing:** Relay-side age/expiry and owner disposition state for held audio; Reconnect inventory/fetch command that the pendant can acknowledge; Playback-start/finish events bound to the relay artifact ID

### "“Never play a reply from an old conversation in a new one—bind every audio artifact and device event to the turn that created it, and discard or quarantine anything that arrives out of context.”"
- **useful because:** The live pipeline already shows relay-held audio with no device playback proof, and a reconnect can otherwise deliver a valid but contextually wrong answer. A short-lived turn capability prevents cross-turn speech, duplicate replay, and late packets from becoming misleading conversation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic token validation, sequence checks, and quarantine; no expensive model required.
- **latency:** Validate each event/artifact in under 10 ms; quarantine on reconnect before any PCM reaches playback.
- **cost:** <$0.005 per turn; small D1 metadata and event receipts dominate.
- **security:** Use opaque per-turn tokens, monotonic sequence numbers, artifact hashes, and expiry. Do not put transcript or raw audio in tokens. Fail closed on missing binding, duplicate sequence, or clock ambiguity; allow explicit owner replay only through a fresh turn.
- **missing:** Relay schema and validator for turn-scoped capability tokens; Firmware/bridge event fields carrying turn token and sequence through fetch/playback; A quarantine/disposition endpoint and dashboard visibility for rejected late artifacts

### "“When I enter a private context—such as a meeting, banking site, or a chosen Mac app—silently keep the pendant and browser from capturing or exposing anything, and show me which boundary is active.”"
- **useful because:** A global privacy latch is valuable but requires a deliberate gesture. Owners also need predictable contextual privacy: the active browser origin or Mac application should be able to place the whole hive into a fail-closed, non-capturing mode without relying on the owner remembering a button press. This is an app/site policy boundary, not another mute latch.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy evaluation and signed state propagation; no realtime model call required.
- **latency:** Apply on active-origin/app change within 500 ms; pendant capture must stop before the next frame; dashboard status within 2 s.
- **cost:** Negligible per transition; bounded policy state and receipts, with no model cost.
- **security:** Policies must match exact origins/application identities, not titles or fuzzy strings. Fail closed on unknown identity, stale browser heartbeat, or relay disagreement. Never transmit page contents or microphone data to evaluate the policy. Exiting a private context must not itself authorize queued work.
- **missing:** Signed active-app and browser-origin identity events; A policy compiler shared by Mac, browser, relay, and pendant; A local pendant mode that receives and enforces a signed privacy-zone state while offline; Owner-facing policy editor and immutable enter/exit receipts


## Changes it proposed to its own stack

### `interaction` — Add a cross-surface 'state of the owner' panel and pendant query that answers four independent questions—what the system heard, what action ran, what audio the relay accepted, and what the pendant physically played—using explicit unknown states rather than collapsing them into success. Each answer should carry a timestamp, artifact/job ID, and the next available recovery action.
- **owner gets:** Today a successful Mac job and accepted TTS can sound like a completed request even while the pendant is offline and the response is merely held at the relay. The owner needs one truthful answer to 'did it happen, and did I hear it?' without inspecting pipeline logs.
- effort: Medium: define a join key across command, job, pipeline artifact, and playback receipt; implement deterministic projection and dashboard/voice rendering.  ·  risk: Incorrect joins could falsely claim completion. Require explicit unknown/unlinked states and never infer playback from relay acceptance. Recover by showing the underlying IDs and allowing replay or discard.
- cost: Low storage and computation; no model call for the base view, optional summarization only for long histories.  ·  latency: Under 2 seconds for current state; historical reconstruction can be asynchronous.
- security: Redact transcript, page contents, and audio by default; expose only status, IDs, hashes, and timestamps unless the owner explicitly requests evidence.
- depends on: A durable turn/artifact correlation ID across relay and device events; Device playback-start/finish receipts; A read-only projection endpoint joining jobs, pipeline events, and delivery state


## What it asked for

_Nothing._
