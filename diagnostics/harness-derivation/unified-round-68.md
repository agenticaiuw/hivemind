# Harness derivation — unified — round 68

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I’m listening to a briefing or answer, let me tap the pendant to bookmark the sentence I just heard; later, turn my bookmarks into a cited note with the source and a short follow-up list.”"
- **useful because:** A spoken answer often contains one actionable fact that the owner cannot safely remember while walking. A physical tap is faster and more private than dictating a note, and the Mac/browser can attach evidence that the pendant alone cannot reach.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to detect the active utterance boundary and acknowledge the tap; use a cheaper background model on the relay to normalize bookmarks and extract follow-ups. Mac/browser workers fetch source pages and citations, while the dashboard presents an editable note.
- **latency:** A local tap acknowledgement under 150 ms; bookmark persistence under 2 s. Citation enrichment may take 10–30 s in the background and must not block listening.
- **cost:** About $0.01–$0.05 per bookmarked utterance for background transcription/structuring; browser and Mac work dominate wall-clock time, not realtime inference.
- **security:** Bookmarks can capture private conversation or logged-in page content. Store the raw audio briefly, encrypt it, attach source URL/tab and timestamp, and require confirmation before sharing or sending any resulting note. Never expose secret page text to public web search.
- **missing:** A pendant-local moment-marker buffer with monotonic audio timestamps and tap debouncing.; A relay API that maps utterance IDs to retained audio/transcript segments and emits a durable receipt.; A Mac/browser citation worker that can re-open the exact source tab and preserve a quoted snippet/hash.; A dashboard review view for editing and confirming the generated note.

### "“If my connection drops while you’re answering, don’t lose the conversation—resume the exact sentence on whichever surface reconnects first, and tell me if anything was skipped.”"
- **useful because:** Today a dropped wearable link can turn a useful answer into an unexplained silence or force the owner to repeat themselves. A durable playback cursor would let the pendant, Mac, and phone act as one conversation instead of separate fragile sessions.
- **path:** pendant → relay-realtime → mac-planner → dashboard → iOS
- **model tier:** No expensive model is needed for continuity. The relay maintains packet and sentence boundaries; a cheap background worker only reconstructs a short missed-span summary when the original audio is no longer available.
- **latency:** Detect loss and persist the cursor within one audio frame (under 100 ms). Resume within 2 seconds of a surface reconnect. Summary fallback may take 5–15 seconds.
- **cost:** Near-zero inference cost when packets are retained; roughly $0.01–$0.03 only when a missed span must be summarized. Storage and heartbeat traffic dominate.
- **security:** A retained conversation fragment is sensitive. Encrypt per-session audio, keep a short TTL, never resume into an unlocked public surface without a local confirmation, and expose a clear “nothing was skipped” versus “summary substituted” status.
- **missing:** A cross-surface playback cursor protocol keyed by utteranceId and packet sequence, with idempotent resume requests.; Pendant firmware support for reconnecting to a specific utterance/sequence and reporting audible confirmation.; Relay-side short-lived encrypted audio segment retention and explicit gap receipts.; Mac/iOS handoff UI that refuses to claim continuity when packet ranges are missing.


## Changes it proposed to its own stack

### `hardware` — Replace the HUZZAH32 classic-Bluetooth audio bridge with a product bridge built around an nRF5340 Audio-class module (LC3/LE Audio, 24 kHz mono path) plus a small fallback classic-A2DP radio if the owner's headphones require it. Keep the nRF9160 for LTE-M/NB-IoT control, but move the 24 kHz packet decode/resampling and jitter buffering off the pendant's overloaded application core. Define a negotiated profile (24 kHz LC3/LE Audio preferred; 16 kHz Opus fallback) and expose packet loss, underrun, and clock-drift counters to the relay.
- **owner gets:** The owner gets intelligible, continuous superwideband speech instead of a 44.1 kHz SBC bottleneck and silence when the bridge buffer starves; older headphones still work through the fallback radio.
- effort: Medium-high: new bridge PCB/module, antenna and RF coexistence work, LE Audio firmware, headphone interoperability matrix, and an end-to-end audio test fixture. Prototype with an nRF5340 Audio DK before committing to enclosure power design.  ·  risk: LE Audio support varies by headphones and the dual-radio design adds pairing complexity; if the preferred path fails, automatically fall back to the existing A2DP path and preserve a wired/local playback test mode. RF coexistence and clock drift can still cause dropouts until soak-tested.
- cost: Roughly +$18–35 BOM in low volume for the LE Audio module, RF/layout, and fallback radio, plus ~20–60 mA during active playback depending on radio duty cycle; lower pendant CPU load may offset some system power.  ·  latency: LC3 framing and jitter buffer target <120 ms mouth-to-ear; profile negotiation adds <1 s only at session start. Removing the current 44.1 kHz resampling/starvation path should reduce sustained underruns.
- security: New pairing keys and radio firmware increase attack surface; store keys in secure hardware, never send them through the relay, and require explicit user action for pairing/reset.
- depends on: An end-to-end audio acceptance test that measures 24 kHz bandwidth, mouth-to-ear latency, packet loss, and recovery across pendant, relay, and bridge.; Owner decision on whether LE Audio-capable headphones are acceptable or classic-A2DP fallback is mandatory.

### `integration` — Create a durable cross-surface utterance ledger: relay assigns every spoken turn and generated audio packet a monotonic utteranceId; /pipeline/events records start/end, source references, and playback state; /pipeline/audio carries the same ID; a pendant tap sends a marker against the currently audible ID; Mac/browser enrichment joins only by that ID and writes a receipt containing source URL, timestamp, transcript hash, and note status. Add retention/redaction controls so raw audio can expire while the citation receipt remains.
- **owner gets:** The owner can tap once and later trust that the note refers to exactly what was heard, even if the Mac reconnects, a job runs in the background, or audio packets arrive out of order. It turns a clever bookmark into a dependable memory aid.
- effort: Medium: schema and idempotent event API in relay, firmware marker packet, Mac/browser joiner, dashboard review state, and replay tests for disconnects and duplicate packets.  ·  risk: Clock drift, reconnects, and late packets may create ambiguous boundaries; use relay-issued IDs, monotonic sequence numbers, explicit unknown state, and never silently guess a citation. If enrichment fails, preserve the raw marker and tell the owner.
- cost: Negligible storage/API overhead per marker; background citation model roughly $0.01–$0.05 each, with raw audio retention configurable to zero after transcript verification.  ·  latency: Tap acknowledgement remains local/sub-150 ms; durable ledger write target <2 s after reconnect; enrichment is asynchronous (10–30 s).
- security: Ledger metadata can reveal listening history. Encrypt at rest, scope source snippets to the owner's authenticated session, redact secrets before model calls, and require confirmation before exporting notes.
- depends on: A pendant-local moment-marker skill (already requested but not yet delivered).; A relay schema and endpoint for utterance markers/receipts.; A browser citation worker that can reattach to the source tab without broadening browser permissions.

### `interaction` — Add a protocol-level continuity contract for every generated audio response: relay emits sentence and packet ranges with a signed playback lease; pendant, Mac, and iOS acknowledge the highest actually-heard range; on reconnect the next surface requests the missing range, and the relay returns either the exact encrypted audio or an explicit gap receipt. The UI and spoken response must distinguish resumed audio, replayed audio, and model-generated summary—never silently jump ahead.
- **owner gets:** A dropped link no longer makes the owner guess whether an answer finished, repeat a request, or act on an incomplete instruction. They can resume safely while walking and know exactly when continuity was impossible.
- effort: Medium: event schema, acknowledgement persistence, reconnect state machine on pendant and clients, short-lived segment cache, and fault-injection tests for loss, duplication, reordering, and surface handoff.  ·  risk: Incorrect acknowledgements could replay or skip speech; default to replaying a small overlap and report uncertainty rather than skipping. Expired audio must produce a visible gap, not a fabricated continuation.
- cost: Small D1/R2 and heartbeat overhead; no additional model calls for successful resume. Occasional summary fallback incurs background inference cost.  ·  latency: One-frame acknowledgement target under 100 ms; reconnection resume under 2 seconds when cached. A fallback summary is intentionally slower.
- security: Playback leases and cached audio must be encrypted and scoped to the owner/session; revoke leases on logout and require local confirmation before handing private audio to another surface.
- depends on: A durable utterance/packet identity shared by relay and clients.; A short-lived encrypted audio cache with deletion receipts.; Client and pendant firmware changes to report audible, not merely received, sequence numbers.


## What it asked for

_Nothing._
