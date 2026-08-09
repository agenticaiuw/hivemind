# Harness derivation — mac-terminal — round 196

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Handle this thread" — while I keep talking through the pendant, find the relevant authenticated browser page, extract the actual issue, make the needed Mac/browser change, and tell me exactly what changed or what is waiting on me."
- **useful because:** This is the system's defining cross-surface action: the pendant supplies an always-available conversational intent, the relay keeps the turn alive, Safari supplies authenticated context, and the Mac executes the fix. It removes the current failure mode where the agent can inspect or act in each surface but cannot carry one intent through all of them with a concise, truthful outcome.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime for the short voice exchange and intent disambiguation; background planner (gpt-5.6-luna) for page extraction and multi-step execution; cheap summarizer for the final one-sentence spoken result.
- **latency:** Acknowledge in under 500 ms; first progress beacon within 2 s; complete ordinary cases in 30 s, with progress updates every 5 s for longer work.
- **cost:** About 1 realtime turn plus 1–3 planner calls per task; roughly $0.03–$0.15 depending on page length and computer-use retries. Browser screenshots and repeated context are the dominant cost.
- **security:** Authenticated page text and screenshots leave Safari/Mac and reach the relay; redact tokens, passwords, and unrelated tabs before upload. Reading/clicking is owner-approved, but sending mail, purchasing, deletion, or irreversible edits must pause for explicit confirmation. Never claim completion without a browser/Mac receipt.
- **missing:** A durable cross-surface task state machine joining pendant turn ID, browser command IDs, Mac job IDs, and final receipt; A browser-to-planner structured extraction contract (not screenshot-only) with sensitive-field redaction; A single spoken progress/status stream that maps browser and Mac failures to truthful_action_status_beacon

### ""Keep the call intelligible" — automatically protect my speech while the agent is speaking, then restore 24 kHz superwideband playback when the link has room, without me changing a setting."
- **useful because:** The measured LTE-M failure is concrete: simultaneous 16 kbps uplink and 24 kbps downlink dropped 388 uplink packets (~7.8 seconds). A wearable conversation that loses the owner's words is unusable. An end-to-end governor can preserve speech first and opportunistically deliver the requested 24 kHz path, rather than pretending a fixed codec is reliable.
- **path:** pendant → relay-realtime → mac-planner → new-surface
- **model tier:** No LLM in the audio control loop. Use deterministic packet-loss/jitter/queue telemetry on the pendant and relay; use the cheap background tier only to summarize quality after a call.
- **latency:** Decisions every 100–250 ms; codec/bitrate changes at frame boundaries with no audible gap; recovery to 24 kHz within 2 s after sustained headroom.
- **cost:** Negligible model cost; modest LTE bytes when superwideband is active. Engineering cost is DSP testing and modem contention measurement, not inference.
- **security:** Audio remains the owner's voice stream; telemetry should be aggregate loss/jitter/codec state, never raw audio. The governor must fail toward intelligible narrowband and never replay stale microphone frames.
- **missing:** A negotiated audio profile message in the WebSocket protocol (24 kHz/60 ms, fallback profile, sequence and epoch); Relay-side congestion controller that measures uplink/downlink loss and sends profile changes; Pendant encoder profile switching with bounded buffers and a sequence-aware jitter buffer; ESP32 bridge support for profile metadata while preserving its fixed 44.1 kHz SBC output

### ""What exactly ran, and recover it if the Mac agent restarted" — show me the command's exit code, duration, changed paths, and whether it can be resumed, then continue safely from the last completed step."
- **useful because:** The current unrestricted shell is intentionally powerful, but its record is not trustworthy enough for long-running work: exit codes are discarded, environment is invisible, cancellation cannot stop a running command, ledgers stay open, job IDs do not join to ledgers, and a restart leaves jobs stuck as processing. This gives the owner confidence without adding gates or reducing capability.
- **path:** mac-planner → relay-realtime → dashboard → pendant
- **model tier:** Deterministic capture and reconciliation first; use the cheap planner only to interpret a failure and select a retry. Realtime is needed only for the owner's spoken status request.
- **latency:** Receipt emitted immediately after process exit; boot reconciliation under 2 s; status queries under 300 ms from durable files. Retry only after an explicit idempotency/replay classification.
- **cost:** Near-zero inference for receipts; one cheap planner call for ambiguous recovery. Storage is bounded JSON plus capped stdout/stderr, with optional artifact files for large output.
- **security:** Do not persist raw environment variables; hash or allowlist names and redact secret-like values. Keep the owner's unrestricted execution policy unchanged. Record the exact rewritten action when shell interception turns a command into an overlay/research action, and mark irreversible steps non-replayable rather than guessing.
- **missing:** execFile/argv-or-shell execution wrapper that captures pid, signal, exit code, timeout cause, and monotonic duration; Boot-time reconciliation that closes ledgers, marks orphaned jobs honestly, and exposes runnable versus non-runnable resume steps; Stable jobId-to-ledger/action receipt join plus idempotency key enforcement for /execute; Bounded stdout/stderr artifact storage with hashes and a typed receipt surfaced by dashboard and pendant status

### ""Check the private page and tell me only the answer" — answer questions about an authenticated Safari tab (orders, work portals, account status) without sending the page, cookies, or screenshots to the relay."
- **useful because:** Today the browser can inspect pages and the relay can converse, but private-page answers require exposing page material to the orchestration layer and there is no durable proof of which tab produced the answer. This would let the owner use authenticated browser sessions as a private sensor while the wearable remains the natural query interface.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Use a local Mac planner to interpret the page and emit a small typed fact capsule; use realtime only to ask a clarification or speak the answer. No raw page should be sent to the expensive model unless the owner explicitly requests it.
- **latency:** Acknowledge within 500 ms and answer ordinary pages within 5 s; wait up to 20 s for a dynamic page, reporting progress rather than guessing.
- **cost:** Usually one local extraction pass and one short realtime response, approximately $0.005–$0.03 per query. The main cost is local browser automation, not tokens.
- **security:** Cookies and page contents remain on the Mac. The extension must redact passwords, payment fields, tokens, unrelated tabs, and hidden DOM text; send only a schema-constrained fact capsule plus provenance hash. The owner must be able to inspect the source tab and invalidate capsules. Never perform a mutation from a read query.
- **missing:** A local-only browser extraction API that accepts a question and returns a typed, minimal fact capsule; A provenance format containing tab identity, URL origin, extraction timestamp, source-region hash, confidence, and expiry; Relay support for capsule-only answers and explicit refusal when the capsule is stale, ambiguous, or missing; Dashboard UI showing exactly which private tab and source region produced a spoken answer


## Changes it proposed to its own stack

### `hardware` — Replace the HUZZAH32 A2DP-SBC bridge with an ESP32-S3-class LE Audio bridge and a host stack that accepts 24 kHz mono LC3 (with SBC fallback for legacy headphones). Keep the pendant's I2S interface, but move resampling and packet pacing into a dedicated audio task with measured DMA watermarks.
- **owner gets:** They get genuinely clear, lower-latency 24 kHz playback instead of decoding 24 kHz and being forced through a fixed 44.1 kHz stereo SBC path that can starve into silence. Calls remain intelligible on legacy headphones and become substantially better on LE Audio devices.
- effort: High: new bridge board, LE Audio qualification, codec integration, RF/interoperability testing, and a wire-compatible firmware migration path. Prototype over the existing USB-connected boards before fabricating an enclosure.  ·  risk: LE Audio support varies by headphone and OS; failed negotiation must fall back to the current SBC bridge. Keep the old bridge firmware and a selectable transport profile so a bad update cannot strand audio. Test clock drift, underruns, and reconnects under simultaneous LTE traffic.
- cost: Prototype board and headphones roughly $30–$100; production BOM likely +$5–$15 over the current bridge. No meaningful model/API cost; power draw rises modestly during Bluetooth LE Audio.  ·  latency: Potentially 20–60 ms lower end-to-end latency than the current SBC path, but initial pairing and fallback negotiation may add 1–3 seconds.
- security: Bluetooth pairing keys and device identity remain local to the bridge; do not route them through the relay. Firmware updates require signed images and rollback.
- depends on: A negotiated audio-profile message between pendant and relay; An end-to-end 24 kHz test corpus with packet-loss and clock-drift measurements; A bridge firmware abstraction that can switch between current SBC and future LC3 transports


## What it asked for

_Nothing._
## Its own summary

Recorded a new private authenticated-browser fact-capsule capability and a hardware change to replace the fixed SBC bridge with an LE Audio/LC3-capable bridge for real 24 kHz playback. Both describe missing owner-visible abilities and the changes required without adding execution gates.

**Biggest unknown:** Whether the existing browser inspection implementation can expose structured source regions locally without first serializing page content through the relay.

