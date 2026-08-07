# Harness derivation — relay-realtime — round 69

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Talk to me naturally at full 24 kHz quality, and if the LTE-M link drops mid-sentence, resume without losing my turn or making me repeat myself.”"
- **useful because:** The owner gets intelligible, low-latency speech that degrades gracefully while walking away from the Mac: the pendant, relay, and downstream Mac/browser agents share one resumable voice turn instead of producing clipped audio or duplicate actions. This is a genuinely end-to-end wearable capability, not something any single node can provide.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension
- **model tier:** Realtime handles only the active speech turn and interruption decisions; a cheap background Worker/Durable Object task reassembles and validates chunks, while mac-planner/mac-vision handle any resulting action. No expensive model is used for codec negotiation, retransmission, or transcript stitching.
- **latency:** First audio under 300 ms when connected; packet-loss concealment locally. On reconnect, resume within 2 s and replay at most the last unacknowledged 500 ms, with a spoken acknowledgement only when continuity cannot be recovered.
- **cost:** Roughly +10–25% audio egress/ingress versus the current codec depending on whether 24 kHz mono Opus is used; model cost is unchanged for connected turns. Durable turn state is small (sequence metadata and short audio/transcript tail), with bandwidth—not inference—dominating cost.
- **security:** Audio and turn fragments leave the pendant to the relay and may be forwarded to Mac agents; use per-session authenticated encryption, bounded retention, and opaque turn IDs. Never replay a downstream action after reconnect unless its idempotency key is confirmed; speech recovery may be automatic, but external mutations still follow existing owner policy.
- **missing:** Pendant firmware support for 24 kHz capture/playback or a verified resampling path, plus a bounded local jitter/retransmit buffer that survives a dropped LTE-M connection; A versioned relay audio-session protocol with codec/sample-rate negotiation, sequence numbers, acknowledgements, CRC/authentication, jitter buffering, and resumable turn IDs; Worker/Durable Object state for short-lived turn continuity and deduplication; this is not currently a scheduler or generic job runner; A single transcript/audio stitching contract consumed by realtime and downstream agents so a reconnect cannot generate duplicate Mac/browser intents; End-to-end tests that inject LTE-M loss, reordering, duplication, and half-sent utterances and verify exactly-once downstream intent delivery

### "“Use what’s on my Mac and in the browser I’m already signed into, reconcile the two, and tell me exactly what differs—without making any changes.”"
- **useful because:** Today the Mac and authenticated browser are separate islands: a request requiring both often loses provenance or forces the owner to repeat context. This gives the owner a cited, read-only cross-surface comparison from a worn pendant, useful while away from the Mac and without exposing browser credentials to the relay model.
- **path:** pendant → relay → mac-planner → browser-extension → mac-vision
- **model tier:** Use a cheaper background planner for source-specific extraction and deterministic comparison; realtime only acknowledges the request and reads the final concise delta. mac-vision is used only when a browser page cannot provide structured extraction.
- **latency:** Acknowledge immediately; return a first partial result within 5 s and the complete comparison within 20 s for up to two Mac sources and two already-open authenticated tabs. If one surface is offline, report that source as unavailable rather than guessing.
- **cost:** Usually one planner call plus extraction calls; roughly $0.02–$0.10 depending on vision fallback. Browser and Mac reads, not realtime inference, dominate latency and cost.
- **security:** The relay must receive only normalized fields, hashes, and source citations—not cookies, passwords, or unrestricted page dumps. Every source read is scoped to explicitly named/open artifacts, and the result records which surface supplied each fact. Read-only mode must be enforced at the executor, not merely promised in the prompt.
- **missing:** A cross-surface read contract carrying source identity, retrieval timestamp, field-level citations, and a strict read-only mode across mac-planner and browser-extension; A deterministic merge/diff service that handles dates, currencies, duplicate records, and conflicting values without asking the realtime model to perform arithmetic; A browser-extension endpoint that returns structured fields from the current authenticated tab while keeping session material local; A Mac extractor that returns typed records from permitted local apps/files with the same citation shape; A partial-result protocol so the pendant can speak a useful Mac-only or browser-only answer when the other surface is offline


## Changes it proposed to its own stack

### `model-routing` — Add a speculative, cancelable intent race for spoken requests: the relay emits a normalized utterance plus a stable request ID to a tiny local classifier immediately, while mac-planner/browser planning starts in parallel only when the utterance is plausibly actionable. The first authoritative result wins; late results are discarded by request ID. If confidence is low or the owner interrupts, the relay cancels the downstream work and keeps the turn conversational. Include a shared outcome envelope (intent, confidence, requested side effects, expiry, cancellation reason) rather than passing free-form text between tiers.
- **owner gets:** The pendant feels immediate even when LTE-M or the Mac is slow: simple questions get a fast answer, while complex requests are already being prepared. Misheard commands are less likely to trigger stale Mac/browser actions, and an interruption does not leave a hidden action continuing.
- effort: Medium: Worker request fan-out/cancellation, a small classifier or ruleset, request-ID propagation through Mac and browser queues, and telemetry for race winners and discarded work. Requires contract tests across relay, mac-planner, and browser-extension.  ·  risk: A planner may complete just as cancellation arrives, causing a race. Enforce expiry and idempotency at every downstream executor; return a receipt only for the winning request. Recovery is a visible concise status (“stopped before action” or “completed”) and an undo where the existing receipt system supports it.
- cost: Small classifier inference cost per actionable utterance plus modest duplicate planning compute in races; cap parallel speculation to one downstream target and cancel aggressively. Network traffic increases slightly from the envelope and cancellation.  ·  latency: Usually reduces perceived latency by roughly one network/model round trip; adds no latency to already-connected direct speech. Cancellation and winner selection need a sub-100 ms relay path.
- security: Stable request IDs and expiry prevent replay across reconnects; do not include raw audio in speculative planner requests unless transcription is required. The envelope must preserve the existing maximum-access owner policy without silently broadening a request's side effects.
- depends on: A versioned cross-surface outcome/cancellation envelope; Idempotency and expiry enforcement in mac-planner and browser-extension; A relay-local low-cost intent classifier and request fan-out path


## What it asked for

_Nothing._
