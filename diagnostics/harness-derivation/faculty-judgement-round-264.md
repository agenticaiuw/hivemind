# Harness derivation — faculty-judgement — round 264

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Make sure I actually receive my morning brief. If the pendant did not download or play it, recover it on the Mac or queue it for my next interaction, and tell me only once what was missed.”"
- **useful because:** Today generation/acceptance is mistaken for delivery. This would make scheduled briefings dependable across relay, Mac, and pendant rather than silently lost after a dropped link or playback failure.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Background model for delivery classification and concise fallback; realtime only when the owner asks what was missed.
- **latency:** No added spoken latency when delivery succeeds. Recovery should begin within one scheduler tick; fallback status under 2 seconds when asked.
- **cost:** Low: one event reconciliation and usually no model call; dominant cost is optional fallback synthesis only when the original artifact was not played.
- **security:** Use opaque artifact IDs and authenticated device-session ACKs, never raw audio in the delivery ledger. Do not replay private content aloud automatically; attention_arbitrate and the owner's policy choose pendant versus Mac display. Confirmation is required before any external resend or side effect.
- **missing:** A durable delivery-aware scheduler that joins relay jobs to artifact IDs and ACKs; A Mac fallback renderer that marks an item delivered only after display or playback confirmation; Relay job leases/requeue so a failed producer cannot remain processing forever

### "“When my Mac or connection dies during a task, recover it safely: tell me exactly what completed, re-check anything that changed, and continue only reversible steps without duplicating an action.”"
- **useful because:** An in-flight relay job currently has no lease and can remain processing forever after a crash. The owner gets neither reliable continuation nor a trustworthy boundary between completed and merely planned work.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic recovery and policy evaluation first; background model only to summarize the recovery receipt.
- **latency:** Detect orphaned work within one lease sweep; recovery decision under 1 second, with owner-facing explanation available immediately.
- **cost:** Very low: state reads and idempotency checks dominate; model is optional.
- **security:** Never replay an irreversible or externally visible action automatically. Revalidate source state, require physical consent for staged actions, honor the universal stop latch, and expose every skipped step with provenance. Browser commands must retain their existing lease/idempotency protections.
- **missing:** lease_until and requeue sweep for relay_jobs; A durable relay-job↔Mac-job mapping rather than telemetry-only localJobId; A recovery record that joins receipts, action-ledger idempotency keys, and revalidation results

### "“Is my pendant healthy right now? Run a safe end-to-end check of radio/link, audio quality, queue backlog, and last playback, then tell me the one thing I should fix—or say it is healthy.”"
- **useful because:** The owner currently has isolated diagnostics and job receipts, not a truthful end-to-end health verdict. This would catch the practical failures they feel—missing audio, stale queues, checksum errors, or a dead relay path—without making them interpret UART metrics.
- **path:** pendant → relay → mac → dashboard
- **model tier:** Deterministic probes and thresholds first; a cheap background model may turn evidence into one short spoken sentence. Realtime is unnecessary.
- **latency:** Local checks in under 5 seconds; remote checks may take 15 seconds and return a staged result if the pendant is offline.
- **cost:** Low API cost; device probe and metric aggregation dominate. No model call for normal/healthy results.
- **security:** Read-only by default. Do not expose auth material or raw microphone/audio; return counters, opaque IDs, and redacted reasons. Any firmware update, queue purge, or repair requires explicit confirmation and physical stop-latch state must win.
- **missing:** A typed aggregate health endpoint joining authenticated device telemetry, delivery ACKs, and Mac/relay reachability; A safe active audio loopback/test artifact with an owner-confirmed playback boundary; Threshold/version metadata so a health verdict is explainable and comparable over time

### "“When someone else is close enough to hear me, keep private details private: automatically switch to a neutral spoken response or route the detail to my screen, then restore normal speech when I’m alone.”"
- **useful because:** A pendant that speaks calendar, mail, browser, or memory content cannot know whether a bystander is present today. Timing suppression is not confidentiality. This gives the owner a practical physical-world privacy boundary instead of requiring them to remember to say ‘don’t say that’ every time.
- **path:** pendant → mac → relay → dashboard → browser
- **model tier:** Fast local classifier for acoustic/proximity state; deterministic policy evaluation for content routing. Use the expensive realtime model only to answer the owner, never to infer privacy from raw audio unnecessarily.
- **latency:** Privacy decision before any sensitive utterance starts, under 100 ms locally. State changes may be debounced for 2–3 seconds to avoid flapping.
- **cost:** Moderate hardware cost and low per-use API cost. The dominant cost is a second microphone or short-range proximity sensor and its always-on power budget; raw room audio should not leave the pendant.
- **security:** Fail closed: unknown presence means no sensitive speech. Never upload room audio or retain bystander features. The relay signs only a coarse state (`private`/`public`/`unknown`), and the owner can override it with a physical control. Sensitive content remains on the Mac/display unless policy explicitly permits speech.
- **missing:** A bystander/proximity sensor or microphone arrangement with local directional/voice-activity classification; A firmware privacy-state machine that can gate playback before PCM reaches the bridge; A signed, expiring presence state consumed by pendant speech, relay attention arbitration, Mac display routing, and browser-derived sensitivity policy; An owner-configurable rule table for which classes may be spoken in public


## What it asked for

_Nothing._
