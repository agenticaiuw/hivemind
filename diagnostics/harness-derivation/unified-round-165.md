# Harness derivation — unified — round 165

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my speech stay intelligible when I move between a quiet room, a street, and the Bose bridge: 'calibrate the pendant for where I am now.'"
- **useful because:** The current 24 kHz path is technically healthy but a fixed gain/codec profile cannot distinguish room noise, wind, speaker leakage, and bridge playback. A short, deliberate calibration can improve recognition and prevent the owner from shouting or being surprised by loud playback.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Realtime only for the spoken calibration dialogue; deterministic DSP and a cheaper background model for scoring samples.
- **latency:** One 3–5 second calibration exchange, with a usable profile within 8 seconds; never run automatically during a conversation.
- **cost:** <$0.01 per calibration; dominated by one short realtime turn and optional background scoring.
- **security:** Calibration captures a brief acoustic sample and device telemetry; retain only aggregate noise/echo metrics, require an explicit button press, and never upload raw room audio after scoring.
- **missing:** A firmware calibration mode that emits a fixed test chirp and returns mic-noise, echo, and clipping metrics; Bridge-side speaker/mic loopback measurement with a signed result; A profile store keyed by environment class, with owner-controlled retention

### "Before you update the pendant or bridge, run a spoken go/no-go check that proves the 24 kHz path, USB transport, and recovery under packet loss still pass—and refuse the update if they do not."
- **useful because:** The owner gets a safety gate instead of discovering a broken wearable during a real conversation. It combines the shipped acceptance numbers with fault injection and the currently real USB-connected hardware, and produces a receipt that says exactly which threshold failed.
- **path:** mac-bridge → pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Deterministic tests and threshold evaluation; background model only summarizes failures in plain language.
- **latency:** A full gate in under 3 minutes; a quick smoke gate in under 20 seconds. No model call on the critical path.
- **cost:** <$0.02 per full gate; dominated by test audio transfer and optional summary generation.
- **security:** Use synthetic fixtures only, never owner speech; require physical transaction approval before flashing; retain hashes/counters rather than audio; make failed gates block the update.
- **missing:** A typed update/staging route that can consume a gate receipt; A hardware flasher action with rollback or a known-good image fallback; A deterministic mapping from audio_link_fault_inject and audio_pipeline_validate results to release thresholds; A pendant/bridge firmware version attestation in the receipt

### "If I say 'repeat the last sentence' or 'I missed the middle,' replay only that spoken sentence, not the whole answer, and do it even after a brief link drop."
- **useful because:** A wearable conversation fails most painfully when one clause is missed. Sentence-level replay turns the existing delivery receipts into a useful recovery action without forcing the owner to repeat the question or listen to an entire response again.
- **path:** relay-realtime → pendant → mac-bridge → mac-planner
- **model tier:** Realtime model identifies the requested segment; deterministic transcript timestamps and audio artifact ranges select and replay it. Use a background model only to repair missing sentence boundaries.
- **latency:** Acknowledge selection in under 300 ms and begin replay within 1 second; preserve the current conversation turn.
- **cost:** <$0.01 per replay; usually no additional generation, only indexed audio retrieval and a short classification turn.
- **security:** Keep replay artifacts encrypted and scoped to the active session; never infer or expose older conversations without an explicit session-bound request; expire audio indexes with the existing retention policy.
- **missing:** A sentence/time-range index attached to each generated audio artifact; A relay endpoint that can request an idempotent byte range or sentence range from the delivery queue; Pendant/bridge seek-and-replay support with sequence-numbered acknowledgements; A clear owner retention decision for replayable audio

### "Summarize the page I’m looking at, but prove that passwords, payment numbers, recovery codes, and hidden form values never leave my Mac."
- **useful because:** The browser can reach private sessions the relay cannot, but today the owner must trust that page inspection did not expose secrets. A local redaction boundary would make browser assistance safe enough for banking, health, and account-recovery pages while preserving useful visible context.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → dashboard
- **model tier:** Deterministic DOM/accessibility-tree redaction on the Mac first; realtime model receives only the redacted projection and summarizes it. Never ask the model to discover secrets and redact afterward.
- **latency:** Under 1 second for ordinary pages; show a blocking 'unredacted content detected' state rather than timing out or silently falling back.
- **cost:** <$0.01 per page summary; dominated by the redacted text sent to the realtime model.
- **security:** Treat redaction as a fail-closed capability: block submission on uncertain fields, include a content hash and redaction receipt, bind the projection to a tab/session, and never store raw DOM. The owner must explicitly opt in per site or domain class.
- **missing:** A browser-extension extraction mode that emits typed fields and DOM provenance instead of raw page dumps; A Mac-local secret detector/redactor with fail-closed confidence thresholds and tests against password managers and payment forms; A signed redaction receipt consumed by the relay and displayed in the dashboard; A site policy store for the owner’s allow/deny choices

### "When you summarize a private page or file, let me ask 'show me where that came from' and hear the exact source excerpt and whether it was redacted or transformed locally."
- **useful because:** A fluent answer is not enough for financial, medical, or work decisions. The owner needs a compact provenance trail that connects each claim to a visible source without exporting the private source itself.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → dashboard
- **model tier:** Deterministic source-span capture and hashing on the Mac; realtime model only explains selected spans in speech.
- **latency:** Attach provenance during the original summary in under 300 ms; answer a follow-up in under 2 seconds.
- **cost:** <$0.01 per follow-up; hashes and offsets are cheap, with no additional model call for simple excerpt playback.
- **security:** Store only source hashes, local offsets, sensitivity labels, and short owner-requested excerpts; require explicit confirmation before speaking sensitive text aloud; bind receipts to tab/file identity and expire them.
- **missing:** A unified provenance envelope shared by browser inspection, Mac file reads, and spoken pipeline artifacts; Local source-span capture that survives page updates by refusing stale hashes; A pendant/dashboard affordance for selecting and replaying one cited span; Redaction-aware citation rendering and audit receipts

### "Let me say 'this stays on my Mac' before you inspect a page or file, and prove afterward that no raw content, audio, or screenshot crossed to the relay."
- **useful because:** The owner currently has no meaningful per-task data-residency control: privacy latch stops capture but does not constrain browser/file context already being sent. A spoken, expiring residency contract would let him use local automation while keeping sensitive work local.
- **path:** pendant → mac-planner → browser-extension → mac-vision → relay-realtime → dashboard
- **model tier:** Deterministic policy enforcement and byte-level egress accounting; realtime model only parses the owner’s policy phrase and confirms it.
- **latency:** Policy acknowledgement within 500 ms; block any disallowed inspection before it starts, not after upload.
- **cost:** Negligible model cost for cached policy phrases; small local storage and hashing overhead.
- **security:** Fail closed on ambiguous policy, bind it to a job/session/tab and expiry, include content-type and byte-count receipts, and prevent relay-side fallback. The dashboard must show violations and make receipts tamper evident.
- **missing:** A first-class per-job data-residency policy carried through Mac, browser, relay, and pipeline code; An egress guard around browser inspection, screenshots, audio, logs, and model requests; A signed receipt proving allowed/blocked byte classes without retaining payloads; A local-only execution mode for actions whose inputs never need the relay


## Changes it proposed to its own stack

### `relay` — Add a session-scoped sentence index and replay-range protocol: when POST /pipeline/audio records an output artifact, persist only segment offsets, duration, hash, and turn/sequence IDs; expose an idempotent range request that feeds the existing audio delivery acknowledgement queue and rejects expired or cross-session ranges. Include a compact receipt linking requested segment to playback start/finish.
- **owner gets:** When the owner misses one clause, the pendant can replay that clause instead of the entire answer, even after a short disconnect, without duplicating or exposing unrelated audio.
- effort: Medium: index generation, D1/schema migration, range validation, and bridge integration; test with synthetic fixtures and packet loss.  ·  risk: Incorrect boundaries could replay a neighboring clause; mitigate with conservative padding, hashes, expiry, and a fallback to replay the full artifact. A schema migration must be backward compatible.
- cost: Small storage increase: tens of bytes of metadata per sentence; no model cost for deterministic ranges.  ·  latency: Adds under 100 ms lookup time; replay begins within one normal audio-buffer startup.
- security: Improves isolation if ranges are bound to session and opaque artifact IDs; never persist transcript text or raw audio beyond existing retention.
- depends on: audio_delivery_ack_queue; A retention/expiry policy for replayable output artifacts; Bridge support for sequence-numbered range playback


## What it asked for

_Nothing._
## Its own summary

Round 165 produced three new owner-facing capabilities: deliberate acoustic calibration across pendant/bridge, a pre-update spoken go/no-go gate using the shipped 24 kHz acceptance tests and fault injection, and sentence-level replay for “repeat the last sentence.” I also recorded a concrete relay change for session-bound sentence indexes and idempotent range playback. A USB↔LTE turn-boundary handoff was correctly rejected as an existing capability, so I did not rephrase it.

**Biggest unknown:** I still need the owner’s retention/deletion policy for replayable audio metadata and the owner’s personal timezone for routines; both context requests are already pending and should not be re-asked this round. The update gate additionally needs a real firmware staging/rollback route and hardware version attestation. macOS Accessibility/Screen Recording remain owner-granted TCC permissions, not something I can obtain here.

