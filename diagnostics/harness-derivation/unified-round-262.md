# Harness derivation — unified — round 262

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live surface readiness** — Mac agent, browser bridge, relay, Accessibility, Screen Recording, and automation permissions are currently all healthy; the nRF9160 pendant is still offline. Workbench handoff is a live read-only route and returns known:false for an unknown job.
  - evidence: GET /ops/status returned ready:true, accessibility granted, screenRecording granted, browser online, relay reachable, pendant device discovery reports offline. GET /workbench/jobs/does-not-exist/handoff returned 200 readOnly:true.

## Capabilities it proposed

### "When I ask something through the pendant, make sure the answer I hear belongs to this turn—even if the link drops and reconnects—and tell me plainly if anything was skipped or replayed."
- **useful because:** Prevents the most confusing wearable failure: a late answer from an old turn speaking over the current one, or a response being played twice after reconnect. It requires the pendant, bridge, relay, and Mac to agree on one turn identity rather than each believing its own queue.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime for turn admission and short recovery wording; deterministic firmware/relay state machines for sequence validation; background model only for human-readable incident summaries.
- **latency:** No extra conversational latency on the healthy path; 1–2 audio frames to fence a reconnect. Recovery status within 2 seconds of link return.
- **cost:** Negligible model cost on healthy calls; roughly $0.001–$0.01 only when a background explanation is requested. Dominant cost is engineering and a few bytes of per-turn metadata.
- **security:** Never trust a client-supplied turn number alone: bind turn ID to a session epoch and authenticated device identity, reject stale epochs, and retain only hashes/counters rather than audio. Require confirmation before replaying any withheld audio.
- **missing:** A cross-surface turn-epoch contract spanning pendant, ESP32 bridge, relay WebSocket, and Mac handoff; Firmware/bridge enforcement that discards stale packets instead of merely reporting them; A durable, bounded turn receipt joining uplink acceptance, TTS generation, and physical playback

### "If the pendant is unavailable when I ask, keep exactly one pending answer for me and deliver it at the next safe conversation turn—without making me repeat myself or hearing an answer twice."
- **useful because:** The owner currently gets either silence or ambiguous retry behavior when the worn endpoint is offline. This creates a bounded, explicit handoff from pendant to relay/Mac and back: one answer, one expiry, one acknowledgement, with a spoken explanation if it could not be delivered.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic queue and deduplication for delivery; background model only to compress a long pending result into a short spoken recap. Realtime is used only when the pendant reconnects and playback begins.
- **latency:** Queue immediately; on reconnect, surface the pending item within 500 ms before accepting a new response. Expire or request re-ask within a configured TTL rather than silently replaying.
- **cost:** No model cost for queueing or deduplication; $0.001–$0.02 if summarization is needed. Storage and relay traffic dominate, bounded to one result per conversation and a small receipt.
- **security:** Pending results may contain private browser content. Encrypt at rest, bind to the authenticated device/session, redact browser tokens and page secrets, and never expose the item to a different browser tab. Physical playback should require the existing staged-reply/play confirmation semantics.
- **missing:** A product-level pending-answer record distinct from the existing generic job queue and audio delivery receipts; Relay lease/expiry and reconnect arbitration for one-answer-only semantics; A pendant inbox payload that can distinguish pending answer, expired answer, and already-heard answer

### "Before you send, submit, or upload anything for me, tell me exactly what information would leave this Mac, who would receive it, and which parts are inferred. Let me allow or refuse that data category once, without exposing the secret itself."
- **useful because:** The owner gets a meaningful privacy boundary for browser and Mac actions instead of an opaque approval prompt. It prevents accidental disclosure while still allowing useful automation, and it can explain refusals over the pendant in a few words.
- **path:** pendant → mac-bridge → browser → relay → dashboard
- **model tier:** Deterministic data-flow inventory and policy enforcement; realtime only for concise spoken disclosure; background model may classify sensitive fields locally but must not receive them merely to classify them.
- **latency:** Under 300 ms for known action types; up to 2 seconds for a new form or page requiring local inspection. No external action until the owner decision is recorded.
- **cost:** Near-zero model cost for typed fields and known destinations; occasional <$0.01 local/background classification. Engineering cost is the dominant expense.
- **security:** The inventory itself can reveal sensitive values, so speak labels and redacted shapes rather than contents. Bind consent to destination, field class, action digest, and expiry; never treat a prior consent as blanket permission for a changed form.
- **missing:** A Mac/browser data-flow inventory that identifies destination, field classes, and inferred versus literal values; A policy store for scoped, expiring owner consent and refusal; A pendant-readable disclosure frame and enforcement point before browser submission or Mac external-send actions

### "Answer this only from the sources I name—such as this browser tab and my calendar—and say 'I don't know' if those sources do not support it. Do not fill gaps from remembered facts or another app."
- **useful because:** The owner can make the system useful in sensitive situations without guessing: a spoken answer can be constrained to the page, account, app, or time window he names. This is stronger than showing evidence after the fact because unsupported claims are prevented before speech.
- **path:** pendant → browser → mac-bridge → relay → dashboard
- **model tier:** Deterministic source binding and retrieval first; a cheaper background model can summarize retrieved material; realtime is used only to speak the bounded answer.
- **latency:** 1–3 seconds for one bound tab or app; explicitly state when a source is unavailable rather than silently widening scope.
- **cost:** Typically <$0.01 per request for bounded retrieval/summarization; browser and Mac reads dominate latency, not inference.
- **security:** Bind the request to exact tab/session/app identities, reject navigation or account changes, redact credentials and hidden page state, and include the source scope in the spoken answer and receipt.
- **missing:** A source-scope object carried from the owner's utterance through planner, browser/Mac reads, relay context, and TTS; Enforcement that prevents fallback to general memory or unrelated tabs; A compact spoken and dashboard receipt showing which sources were actually used


## Changes it proposed to its own stack

### `integration` — Add an end-to-end conversation turn envelope: device_id, session_epoch, turn_id, packet_sequence, direction, content_hash, and monotonic deadlines. Make the relay and ESP32 bridge reject stale epochs and duplicate packet ranges; make the Mac handoff preserve the envelope; emit one compact receipt when a turn is accepted, played, interrupted, or abandoned.
- **owner gets:** Reconnects will stop producing ghost speech, duplicated replies, or an answer from yesterday's conversation. When something is lost, the owner gets an honest 'I missed that turn' instead of hearing a plausible but wrong response.
- effort: Medium-high: protocol changes in firmware, bridge, relay, and Mac handoff, plus fault-injection tests across reconnect, reordering, and duplicate delivery.  ·  risk: A clock or epoch bug could reject a valid response. Roll out behind a negotiated protocol version, retain the legacy path temporarily, and fail closed to silence rather than stale audio.
- cost: Tiny metadata overhead (tens of bytes per packet/turn); no ongoing model cost. Engineering and hardware test time are the main cost.  ·  latency: Zero on the steady-state path; at most one frame while a reconnect establishes a new epoch.
- security: Improves replay resistance and cross-session isolation, but requires authenticated device/session binding and careful nonces so metadata cannot be used to correlate conversations indefinitely.
- depends on: A durable relay job lease and requeue sweep; The existing audio_delivery_ack_queue semantics; The existing duplex_audio_congestion_guard profile transitions; A live hardware/bridge integration test rather than USB being treated as product transport

### `hardware` — Add a low-power haptic actuator and a small multicolor status indicator to the wearable revision, with firmware-owned patterns for privacy-latched, pending approval, recording, unread alert, link loss, and delivery confirmation. Keep the existing audio path and make all safety patterns work offline.
- **owner gets:** The owner can tell whether the pendant is recording, private, waiting for approval, or has a queued message without guessing from one overloaded LED or playing audio aloud. Privacy and approval states become unambiguous in a pocket or noisy room.
- effort: Medium hardware revision plus firmware pattern design, enclosure and battery testing, and accessibility testing for tactile distinguishability. Existing single-LED patterns need a migration table.  ·  risk: More power draw, false confidence if patterns are confused, and a new actuator failure mode. Use conservative pulse patterns, self-test at boot, and retain the current LED fallback.
- cost: Roughly a few dollars in components and PCB/enclosure revision; haptic pulses should be intermittent and low duty cycle, while the indicator adds small peak current. Exact cost depends on the owner's size and battery targets.  ·  latency: Immediate local feedback, independent of LTE, relay, or Mac latency.
- security: Improves privacy signaling but must not reveal sensitive alert content through patterns. Keep patterns semantic and authenticated state-driven; never let a remote party trigger arbitrary vibration sequences.
- depends on: A settled state-priority table shared by local_privacy_latch, physical_transaction_approval_latch, and offline_alert_inbox; A product battery/thermal/size decision for the wearable revision; Firmware acceptance tests proving safety patterns remain local during link loss

### `context` — Introduce a signed source-scope token that is created from the owner's utterance and travels through planning, browser/Mac reads, relay context, and TTS. Every retrieved fact must carry that token; the answer composer must refuse unsupported claims and emit a scope receipt. Navigation, tab identity, app identity, and account changes invalidate the token instead of widening the search.
- **owner gets:** When the owner says 'use only this page' or 'check only Calendar,' the system will actually honor that boundary rather than quietly consulting memory or another logged-in surface. It turns a spoken constraint into a guarantee he can rely on.
- effort: Medium: define the token schema, thread it through existing planner and retrieval calls, add refusal behavior, and test tab navigation, stale sessions, and missing sources.  ·  risk: Overly narrow binding could produce unnecessary refusals; silently widening scope is worse. Make widening an explicit owner choice and clearly report the reason for refusal.
- cost: Negligible storage and token overhead; no additional model cost beyond the original bounded answer.  ·  latency: Small signing and validation overhead; source reads remain the dominant latency.
- security: Reduces cross-tab, cross-account, and cross-app leakage. Tokens must omit page contents, expire quickly, bind to authenticated sessions, and be rejected after navigation or account changes.
- depends on: A planner/context schema that carries source scope end to end; Browser and Mac read receipts containing stable tab/app identity and navigation revision; A refusal path in spoken response generation that cannot fall back to unrestricted memory


## What it asked for

_Nothing._
