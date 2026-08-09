# Harness derivation — unified — round 188

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If the Mac or browser died halfway through that task, finish only the safe parts and tell me exactly what you skipped.”"
- **useful because:** Today interrupted ledgers are discoverable but never resumed, and ordinary plans remain falsely open. This gives the owner a truthful crash-recovery action across relay, Mac, Safari, and the physical approval latch instead of silently duplicating an email, write, or purchase.
- **path:** relay-realtime → mac-planner → browser-extension → unified
- **model tier:** background for ledger inspection and replay classification; realtime only to explain the result when the owner asks
- **latency:** 2–5 s to classify; execution proceeds asynchronously with a spoken completion receipt
- **cost:** ~$0.01–$0.05 per recovery, dominated by planner calls only for ask/blocked steps; deterministic steps are local
- **security:** Auto-rerun only replaySafety idempotent/additive with a fresh lease; unrepeatable/unknown and riskTier word-required steps wait for the physical approval latch or next conversation. Never infer completion from an open ledger. Requires closing completed ledgers, relay job leases/requeue, and the existing browser lease supervisor.
- **missing:** orchestrator closeLedger integration; relay_jobs lease_until and requeue sweep; startup recovery caller for planResume; relay persistence/delivery path for physical approval records

### "“Move this conversation from the pendant to the Mac USB link now, without making me repeat myself.”"
- **useful because:** The pendant and ESP32 are physically connected over USB today while LTE is unregistered. A turn-boundary handoff would let the owner keep talking through a reliable local path, then return to LTE without duplicated audio, lost turns, or an unexplained cold start.
- **path:** relay-realtime → mac-planner → unified
- **model tier:** realtime for the handoff decision and conversational continuity; deterministic firmware/bridge state machine for transport ownership
- **latency:** announce and switch within one turn boundary, target <500 ms after playback/capture quiesces
- **cost:** Near-zero model cost after the initial handoff decision; USB serial and bridge CPU/power dominate
- **security:** Only transfer sequence-numbered audio frames and turn metadata; do not copy raw audio to disk. Authenticate the USB session, pause LTE retries while USB owns it, and reject stale frames from the prior transport. Requires implementing the accepted usb_fallback_audio_session in firmware, Mac bridge transport binding, and a relay-visible transport state.
- **missing:** USB serial session protocol between nRF9160, ESP32 bridge, and Mac; Mac bridge audio endpoint and turn-boundary handoff hooks; relay transport-state/readback route

### "“Why didn’t you do what you said you would, and what would have happened if you had?”"
- **useful because:** A job status says queued/failed, but it does not explain the causal boundary across the owner’s utterance, relay receipt, Mac execution, browser evidence, and pendant delivery. This gives a trustworthy answer without pretending that absence of evidence is proof of completion, and can distinguish blocked approval, stale browser lease, transport loss, and an action that was never dispatched.
- **path:** relay-realtime → mac-planner → browser-extension → unified
- **model tier:** background for evidence join and counterfactual classification; realtime only to summarize the already-built causal report
- **latency:** <3 s for a bounded report over the last 24 h; long histories return a partial report with an explicit cutoff
- **cost:** ~$0.01–$0.04 per report; most work is deterministic joins, with model cost only for ambiguous natural-language commitment matching
- **security:** Search only explicitly bound tabs/apps and the owner’s own job/session IDs. Redact page contents, secrets, and unrelated browser tabs. Counterfactuals must be labelled hypothetical and never execute actions. Preserve immutable receipts and record which evidence was unavailable.
- **missing:** typed causal-report schema joining commitment, ledger, job, browser, and delivery events; route that binds a spoken commitment to its originating session/job without broad text search; counterfactual simulator for blocked/failed steps; owner-facing redaction and evidence provenance renderer

### "“Read this private page to me on the pendant, but guarantee that the page text, audio, and browser result disappear when playback ends.”"
- **useful because:** The browser can reach authenticated pages and the pendant can speak, but today there is no owner-facing ephemeral mode that binds browser extraction, relay/TTS processing, playback, and deletion into one verifiable lifecycle. This would let the owner consume private mail, documents, or dashboards without turning a reading request into durable memory or a lingering browser/result artifact.
- **path:** browser-extension → mac-planner → relay-realtime → unified
- **model tier:** realtime for low-latency extraction-to-speech; deterministic local cleanup and receipt verification afterward
- **latency:** Begin speaking within 3–5 s; cleanup and a signed convergence receipt within 2 s of playback completion or cancellation
- **cost:** ~$0.01–$0.08 per page depending on extraction length and TTS duration; TTS/audio transfer dominates
- **security:** Require an explicit page/tab binding and a one-request nonce. Never persist raw DOM, screenshots, extracted text, or generated audio beyond bounded buffers; redact credentials and form fields in the extension. If cleanup cannot be verified, say so and stop further exposure rather than claiming deletion. Browser history, server provider logs, and relay operational logs need separately documented retention limits.
- **missing:** ephemeral browser extraction contract with tab-scoped nonce and no-persist flag; relay/TTS transient object lifecycle with bounded TTL and deletion receipt; pendant playback-finished/interrupted acknowledgement tied to the artifact ID; cross-surface privacy convergence check for browser result, relay buffers, Mac temp files, and audio delivery


## What it asked for

_Nothing._
