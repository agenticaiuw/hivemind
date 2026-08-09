# Harness derivation — faculty-judgement — round 203

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me the top world and US headlines from the last 12 hours, in three short sentences I can play later.”"
- **useful because:** This exact request has been repeated and failed. It would produce a genuinely current, short, source-backed digest instead of silently giving stale or empty news, and leave an audio item the owner can replay without interrupting work.
- **path:** relay → browser → mac → pendant
- **model tier:** Use the cheap model for source clustering and compression; reserve realtime judgement for resolving contradictory headlines or deciding whether a story is safe and substantial enough to include.
- **latency:** 15–30 seconds for search, source checks, and synthesis; enqueue audio immediately after text is accepted.
- **cost:** Usually 3–8 web-search calls plus one cheap synthesis; roughly $0.01–$0.05, dominated by search and TTS/audio generation.
- **security:** Only public pages leave the relay. Do not read authenticated tabs for a public-news request. Store source URLs and short redacted summaries, not full article bodies; require no confirmation because there is no external mutation.
- **missing:** A freshness/source-quorum research coordinator that rejects stale, duplicate, or single-source headlines; A durable research-to-audio item link so the owner can replay the exact cited digest; A spoken format that includes source names without leaking article snippets

### "“What’s the battery percentage?”"
- **useful because:** The owner should get a precise paired-device answer rather than a fabricated pendant percentage. It should say Mac battery when that is the only measured value, and separately report that the pendant battery is unavailable because this hardware has no gauge, along with whether the audio bridge and relay are reachable.
- **path:** pendant → relay → mac
- **model tier:** Deterministic aggregation; no expensive model unless the owner asks for interpretation or troubleshooting.
- **latency:** Under 2 seconds for a live spoken answer.
- **cost:** Near-zero model cost; one Mac status read and cheap health/surface checks.
- **security:** Battery and connectivity are low sensitivity. Never collapse Mac charge into pendant charge, and never infer LTE registration from USB presence or a healthy Mac process.
- **missing:** A typed paired-device status adapter that exposes pendant charge as unknown, not zero, and distinguishes USB-attached from LTE-registered; A single owner-facing response schema for Mac battery, pendant battery, bridge state, and last authenticated delivery ACK; A live pendant status route or signed status packet for registration and charge when hardware eventually supports it

### "“Inspect this link” (or “why did that inspection fail?”)"
- **useful because:** The owner has repeatedly asked to inspect public and authenticated URLs and received failed/no-op outcomes. The system should classify the requested surface before acting: read public pages through the relay, use the browser only for authenticated content, and return a truthful, actionable reason when neither path is usable instead of retrying blindly.
- **path:** pendant → relay → browser → mac
- **model tier:** Cheap deterministic URL/surface classifier first; use realtime judgement only when the page’s access requirements or requested operation are ambiguous.
- **latency:** Public read: 3–10 seconds. Authenticated browser read: up to the extension result timeout, with a short spoken progress state.
- **cost:** Near-zero for classification; public reads use existing search/page retrieval; authenticated reads use one browser command. No model call for ordinary URLs.
- **security:** Never send credentials, page secrets, or authenticated content to the public relay reader. Public/authenticated classification must be conservative; clicking or mutation remains confirmation-gated. Persist only URL, access mode, and a digest of the result.
- **missing:** A typed handoff decision that chooses public reader versus browser session and explains the reason; A surfaced browser-bridge reachability/lease result before queuing a command; A single result envelope linking the spoken answer to the URL, access mode, and failure evidence

### "“Make your voice comfortable wherever I am.”"
- **useful because:** The owner should never get a painfully loud or unintelligible response because the pendant moved from a quiet room to a street, car, or kitchen. The pendant would locally estimate ambient level and speech audibility, then adjust gain and apply a hard hearing-safe limiter without sending room audio away.
- **path:** pendant → relay
- **model tier:** No model: local DSP and deterministic control are safer and cheaper than inference.
- **latency:** Adapt within 200 ms of an ambient change; never interrupt an utterance with a reset or click.
- **cost:** Negligible API cost. Firmware work; optional microphone calibration test, no recurring cloud cost.
- **security:** Ambient samples stay on-device and are reduced to short-lived level statistics. A conservative ceiling must win over intelligibility. The owner needs an explicit maximum-volume setting, not a model-chosen one.
- **missing:** A local ambient-level estimator and slow attack/release gain controller on the audio bridge/pendant; A persisted owner maximum SPL/volume ceiling and a calibration procedure for the actual ESP32 speaker path; A telemetry field in delivery ACKs for clipping/limiter activation so the system can diagnose poor environments without storing room audio

### "“Don’t say private things out loud if someone else is nearby.”"
- **useful because:** Today a sensitive result can reach pendantSpeech directly without the briefing redaction gate. The owner should have a local, fail-closed bystander safeguard: if the pendant hears another nearby speaker or cannot establish a private acoustic context, sensitive content becomes a neutral alert and waits for a deliberate play action.
- **path:** pendant → relay → mac
- **model tier:** A tiny on-device voice-activity/overlap classifier for the immediate gate; server judgement only decides the content class. Never upload raw ambient audio for this decision.
- **latency:** Classify within 300 ms before playback; ordinary non-sensitive speech remains immediate.
- **cost:** No per-use model cost if using a compact DSP/VAD classifier; modest firmware RAM/flash work and bench calibration.
- **security:** This is defense in depth, not proof of privacy: headphones, distance, and quiet bystanders can fool acoustics. Fail closed for secret content, disclose the reason in provenance, and provide a physical override only through the existing consent latch—not voice.
- **missing:** A local bystander/overlap detector that can run within the pendant's remaining RAM and is tested against false negatives; A mandatory content-class handoff from every TTS caller, including pendantSpeech and audioBrief, not only briefingTriage; A policy field distinguishing neutral notification, queued private item, and physically approved replay

### "“Tell me when the conversation is actually over, even if the connection dies.”"
- **useful because:** A dropped link currently can leave the owner unsure whether an answer was sent, downloaded, or heard. They should get a tiny, durable end-state—heard, interrupted, not delivered, or cancelled—that survives reconnect and is tied to the exact spoken item, without replaying the whole answer.
- **path:** pendant → relay → mac
- **model tier:** Deterministic event reconciliation; use an inexpensive background model only to summarize a long list of unresolved items.
- **latency:** Local status immediately; reconcile queued events within one reconnect cycle.
- **cost:** Near-zero inference cost; small authenticated event records and normal relay storage.
- **security:** Use opaque artifact IDs and signed monotonic device events; do not persist spoken text in the delivery ledger. Duplicate and out-of-order ACKs must be harmless, and cancellation must not be mistaken for completion.
- **missing:** A durable cross-surface delivery state machine that joins relay job, audio artifact, and pendant sequence IDs; A reconnect UI/voice response that reports unresolved items without claiming the owner heard them; A retention rule for delivery metadata and a repair path for checksum-error or interrupted playback


## Changes it proposed to its own stack

### `integration` — Wire a ResearchAudioCompiler between POST /research and the existing audio brief queue: enforce a 12-hour freshness cutoff, require at least two independent source domains for each included claim, retain URL/title/time evidence, generate exactly three spoken sentences, and create one stable item_id/cursor_token for replay and ACK reconciliation. Route the resulting event through attention_arbitrate rather than speaking directly.
- **owner gets:** The repeated news request finally becomes a reliable, replayable answer rather than a failed search or an untraceable burst of audio.
- effort: Medium: adapter plus source normalization and tests; no new hardware.  ·  risk: Search outages or source disagreement could yield no brief; fail closed with a short explanation and preserve the sources for review. Do not silently substitute old news.
- cost: One cheap synthesis and normal search/TTS costs; no persistent raw article bodies.  ·  latency: Adds roughly 1–3 seconds for source quorum and validation.
- security: Public-only source allowlist for this intent; URL/title metadata can persist, article text cannot be forwarded to authenticated surfaces.

### `integration` — Add a paired-status reducer that calls get_mac_status and the live device/ops surfaces, emits separate fields mac_battery_percent, pendant_battery:{value:null,reason:'no_gauge'}, transport:{usb,lte}, bridge_online, and last_delivery_ack, then maps those fields to one short spoken sentence. Make null pendant charge impossible to serialize as 0%.
- **owner gets:** A one-sentence answer tells the truth about the device they are wearing and the computer it is attached to, instead of making them debug which battery was measured.
- effort: Small-to-medium adapter, schema, and endpoint tests; hardware charge telemetry remains a separate future change.  ·  risk: Stale health or ACK timestamps could look current; include observed_at and age, and say unavailable when stale. USB must never imply LTE registration.
- cost: Near-zero model/API cost; one status aggregation request.  ·  latency: Under 2 seconds when Mac and relay health are reachable.
- security: Low sensitivity, but authenticated session identifiers and detailed transport diagnostics should stay out of spoken output.
- depends on: A live device status source for pendant registration; until then the reducer must honestly emit unknown.

### `interaction` — Implement a SurfaceHandoff decision before any inspect-URL job. It should classify public versus authenticated intent, preflight browser connectivity, dispatch public URLs to read_web_page/web_search and authenticated URLs to browser_run_actions, and return a durable failure envelope containing attempted surface, reason, and safe next option. Expose that envelope to the pendant as a short sentence and to explain_action_provenance as evidence.
- **owner gets:** “Inspect this” becomes one dependable action with a clear fallback, not a loop of failed browser commands or an unsafe attempt to send private pages to a public reader.
- effort: Medium: deterministic classifier, preflight wiring, and result normalization; no Accessibility grant required for public reads.  ·  risk: A public-looking URL may redirect into login; stop at the redirect and ask whether to use the authenticated browser. Never auto-click or mutate.
- cost: Near-zero classification cost; one existing read/bridge call per request.  ·  latency: Public path remains fast; authenticated path adds one preflight round trip.
- security: Conservative boundary: authenticated content never enters web_search/read_web_page; provenance records mode and URL but not page body.
- depends on: A typed URL access-mode classifier and a normalized cross-surface result envelope.

### `firmware` — Add a local acoustic safety loop: estimate RMS/noise floor from the existing microphone, run a bounded slow gain controller and brickwall limiter on downlink playback, and emit only aggregate limiter/clipping counters in the existing delivery event. Calibrate the ceiling on the actual ESP32 speaker and prove attack/release and peak limits with on-device measurements.
- **owner gets:** Speech stays understandable outdoors without sudden painful peaks indoors, and the pendant does not need to ship room audio to achieve it.
- effort: Medium firmware/DSP work plus bench measurements.  ·  risk: Bad calibration could make speech too quiet or pump; ship conservative ceiling, watchdog fallback to the known-safe profile, and an owner override bounded below the hardware limit.
- cost: No API cost; small CPU/RAM overhead and no new hardware.  ·  latency: Under 200 ms adaptation; no added conversational network latency.
- security: Room audio never leaves the device; only aggregate diagnostics are uploaded.

### `integration` — Make content classification a required typed field on every path into pendantSpeech/audioBrief, then run a local acoustic privacy verdict immediately before playback. Secret items fail closed when the verdict is unknown or another voice is detected; they become an opaque queued item requiring the existing physical transaction approval latch. Record only the policy rule and verdict, not ambient audio.
- **owner gets:** A private message cannot accidentally be spoken just because it bypassed the one briefing code path, while ordinary answers remain fast.
- effort: Large cross-cutting integration plus compact on-device VAD/overlap model and false-negative testing.  ·  risk: False positives delay private speech; false negatives remain possible, so the default is conservative and the owner gets a clear queued-state explanation.
- cost: No recurring API cost if the classifier is local; firmware flash/RAM and integration test cost.  ·  latency: At most a few hundred milliseconds before sensitive playback.
- security: Improves disclosure safety; no ambient recording or cloud inference.
- depends on: A content-class propagation contract for all TTS callers; Physical approval latch for releasing a queued secret item

### `relay` — Build one authenticated delivery ledger that joins relay job ID, opaque audio artifact ID, device session, monotonic device sequence, and playback state. Fold duplicate/out-of-order events, reject impossible regressions, expose a truthful owner-facing terminal state, and retain only metadata under a short TTL. Reconcile on reconnect before allowing a 'heard' claim.
- **owner gets:** They can know whether an answer was actually heard instead of confusing generated, downloaded, and played states—especially after a dropped link.
- effort: Medium relay schema/state-machine work plus pendant reconnect tests.  ·  risk: Clock skew and retries can misclassify events; use device sequence and event IDs as authority, with an explicit unknown state when evidence conflicts.
- cost: Small durable metadata footprint; no model cost.  ·  latency: Immediate local event status; server reconciliation on reconnect.
- security: Opaque IDs only, authenticated session binding, no audio text in the ledger.
- depends on: Authenticated pendant delivery event ingestion; A durable relay-to-Mac job/artifact foreign-key mapping


## What it asked for

_Nothing._
## Its own summary

Round 203 produced three owner-facing capabilities and implementation changes. The highest-value one is a freshness-bounded ResearchAudioCompiler: wire existing web search/research, source quorum, provenance, attention arbitration, and the durable audio item/ACK path so the owner's repeatedly requested three-sentence news brief actually arrives and can be replayed. I also proposed a truthful paired-device status reducer (Mac battery measured; pendant battery explicitly unknown because no gauge; USB never implies LTE) and a conservative public-versus-authenticated URL SurfaceHandoff that stops unsafe routing and explains failed inspections. All six existing building blocks are already present; what is missing is the typed connective layer, not another standalone tool. I still need three owner/system decisions before making stronger promises: the owner's actual timezone (memory says America/Chicago while the authoritative Mac routine zone is America/New_York), disclosure/trusted-destination policy, and eventual pendant telemetry for charge/LTE state. The reconciliation grant was invoked but resolved incorrectly to POST /briefing and did not perform a read, so it cannot currently settle those conflicts.

**Biggest unknown:** Whether the owner wants the Mac's America/New_York to govern routines or has explicitly chosen America/Chicago as their personal timezone; do not silently choose between them.

