# Harness derivation — unified — round 223

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live pipeline delivery truth** — The newest pipeline run rendered 24 kHz mono s16le PCM and uploaded it to relay, but delivery state is held_by_relay with awaitsDevice=true, heard=unknown, and provesPlayback=false because no device_playback event exists. The same run's text says 42.7 seconds of audio while TTS metadata reports 9.723 seconds and 466,700 PCM bytes.
  - evidence: GET /pipeline response for pipelineId job_c8baaa61-212d-454a-bd4b-108d5bcb4990 at Round 223

## Capabilities it proposed

### "Before the pendant plays a briefing, tell me if the spoken claim and the actual audio agree — and refuse to deliver a malformed response."
- **useful because:** The live pipeline currently produced a response claiming 42.7 seconds of audio while its TTS event reported 9.723 seconds and 466,700 bytes. A deterministic gate would prevent truncated, mislabeled, or corrupt replies from reaching the owner's ear, and would expose the exact mismatch instead of claiming success.
- **path:** mac-planner → relay-realtime → pendant
- **model tier:** deterministic/background; no expensive model needed
- **latency:** Under 50 ms after TTS metadata is available; it should run before relay upload and never delay capture.
- **cost:** Negligible API cost; local arithmetic and metadata validation dominate.
- **security:** Do not transmit audio content beyond the existing relay path. Treat duration claims as untrusted metadata, cap tolerances, and quarantine rather than silently rewriting. Require confirmation only if an owner explicitly asks to play a quarantined artifact.
- **missing:** A canonical duration field and unit shared by research/briefing producers and TTS; A relay quarantine state and owner-facing diagnostic response; A test fixture covering PCM bytes = duration × sampleRate × channels × bytesPerSample and claimed spoken duration

### "When I ask a new question, do not play an old held reply first; show me the pending replies and let me choose which one to hear."
- **useful because:** The live relay currently reports a 24 kHz response as held_by_relay, rank 2, awaiting the device, with heard=unknown. Without supersession and explicit selection, a stale 42-second briefing can interrupt a later conversation or be mistaken for the answer to the new question. This makes queued speech predictable and owner-controlled.
- **path:** relay-realtime → pendant → mac-planner
- **model tier:** deterministic routing; background model only to summarize multiple pending labels
- **latency:** Selection and cancellation under 100 ms; pending-list summarization under 1 s when requested.
- **cost:** Near-zero API cost for state transitions; optional one short background summary call per pending batch.
- **security:** Expose only the owner's own pending artifacts, opaque IDs and short labels by default; never read private browser content to generate the queue label. A physical play/approval gesture is required for an old or externally generated item.
- **missing:** A per-conversation supersession token carried from relay job to pendant playback; An atomic claim/cancel/skip operation on held relay responses; A pendant-readable pending-list control frame and a bounded local queue policy

### "If my pendant is offline, do not spend time rendering a long spoken answer for it; give me a concise text/Mac fallback and keep the full answer queued until the device returns."
- **useful because:** The live system rendered 466.7 KB of 24 kHz PCM and uploaded it even though the relay had no device playback event and marked the response held_by_relay. An availability-aware response policy saves latency, bandwidth, and relay storage while ensuring the owner still gets useful information on the Mac, without pretending the pendant heard it.
- **path:** relay-realtime → mac-planner → pendant
- **model tier:** deterministic policy first; background model only for a shorter fallback summary
- **latency:** Detect stale/offline pendant state within 100 ms; deliver a short Mac fallback within 2 s; never block the eventual queued pendant artifact.
- **cost:** Usually lower than today: avoids TTS/Opus work when offline; at most one inexpensive background summarization call for a long answer.
- **security:** The fallback must not open or expose private browser material merely because the pendant is offline. Do not delete the full queued response automatically; apply a visible TTL and owner-controlled retention. Playback on Mac requires explicit policy/confirmation if content could be sensitive.
- **missing:** A reliable pendant presence/last-fetch signal distinct from Mac bridge health; A pre-TTS policy hook that chooses pendant audio, Mac-only text/audio, or defer; A durable response variant relation linking the concise fallback to the full queued artifact

### "When my pendant link drops during an answer, continue the same conversation on my Mac without restarting or repeating it, then hand the next turn back to the pendant when it reconnects."
- **useful because:** Today the pendant, Mac, and relay can each hold pieces of a turn, but there is no owner-visible live handoff. A dropped link should not make the owner hear a clipped answer, receive a duplicate, or have to restate the question. Exact audio sequence and conversation state continuity would make the system feel like one device rather than several unrelated endpoints.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** Realtime for the active turn; deterministic state transfer, with no extra model call unless a short handoff summary is needed.
- **latency:** Detect loss in under 250 ms; Mac takeover under 1.5 s; reconnect handoff at a turn boundary without interrupting speech.
- **cost:** Small relay state and optional one short summary call only when raw turn state cannot be retained; otherwise no additional inference cost.
- **security:** The Mac fallback must obey the same privacy latch and sensitivity policy as the pendant. Encrypt turn state in transit and expire abandoned handoff state. Never play private audio on the Mac merely because the pendant disappeared without an owner-configured fallback policy.
- **missing:** A duplex session state machine with monotonic audio sequence numbers across relay and Mac; A relay handoff lease preventing both endpoints from speaking simultaneously; Mac audio output/input as a first-class continuation surface rather than only a planner action; A reconnect reconciliation message that reports the last heard sequence

### "For any action you take in my browser or Mac, let me ask for a privacy-preserving proof that the intended state changed, without exposing the page contents or private files."
- **useful because:** Receipts today can say an action completed without proving the resulting state. The owner needs an independently checkable witness for actions such as changing a setting, submitting a form, or creating a file, while avoiding a second copy of sensitive page text. This is stronger than an execution receipt and safer than sending screenshots or full DOM dumps to the relay.
- **path:** browser-extension → mac-planner → relay-realtime
- **model tier:** Deterministic selectors, hashes, and signed attestations; use a background model only when an owner asks for a human explanation of the proof.
- **latency:** Under 500 ms for a bound-state check; under 2 s for a multi-step proof bundle.
- **cost:** Near-zero inference cost; hash and selector evaluation dominate.
- **security:** Proofs must be scoped to the exact tab/app binding, redact values by default, include freshness and nonce, and never claim success when only an action receipt exists. Sensitive proof disclosure requires explicit owner request.
- **missing:** A browser/Mac witness schema with before/after state hashes and freshness; Signed or authenticated proof capsules joined to action receipts; Safe redacted assertions for common states such as URL, title, selected option, file existence, and message sent

### "Let me define which kinds of information may leave my Mac, and enforce that boundary before a request reaches the relay, browser, or pendant."
- **useful because:** The current system can route browser, Mac, relay, and wearable work, but the owner has no single enforceable data-boundary control. A local policy firewall would prevent credentials, financial pages, private notes, or selected applications from being copied into relay prompts or spoken aloud, while still allowing harmless automation.
- **path:** mac-planner → browser-extension → relay-realtime → pendant
- **model tier:** Deterministic policy and local classification first; background model only for ambiguous content, with ambiguity defaulting to deny.
- **latency:** Under 100 ms for application/domain and known-field rules; under 1 s for local content classification. A denied request should fail closed immediately.
- **cost:** Low ongoing API cost; local rules dominate. Ambiguous classification may use a small background call, never the realtime tier.
- **security:** The classifier itself must not upload the data it is deciding about. Store only policy decisions and redacted audit records. Deny by default for secrets and require explicit confirmation to relax a boundary. The relay must cryptographically receive the policy verdict, not merely trust a Mac-generated label.
- **missing:** A local preflight interception point before prompt construction and audio rendering; Owner-editable data classes and destination policies; Secret/credential detection that operates locally on browser DOM, Mac files, and clipboard; Relay enforcement of a signed allow/deny/redaction verdict


## Changes it proposed to its own stack

### `integration` — Make one canonical responseId mandatory from POST /pipeline/events through TTS metadata, relay upload, pendant fetch, and device playback events; reject or quarantine any artifact lacking it. Derive it from the existing relay job ID when present, otherwise mint a UUID at pipeline creation, and expose a correlation view in the pipeline response.
- **owner gets:** Today the pipeline explicitly says it cannot prove playback because the live duplex path holds no job ID. The owner should be able to ask about one reply and get one truthful chain, rather than a relay receipt that cannot be joined to what the pendant heard.
- effort: Medium: schema and event propagation across Mac agent, relay, and pendant telemetry; add migration handling for old runs.  ·  risk: Old clients may emit events without the field; quarantine them as unknown rather than dropping audio. Recover by accepting legacy records with an explicit uncorrelated state.
- cost: Negligible storage and bandwidth increase (roughly one 36-character ID per event).  ·  latency: Sub-millisecond local overhead; no additional model call.
- security: Opaque IDs only; do not put transcript or URL data into correlation tokens. Improves auditability without expanding content exposure.
- depends on: A pendant playback event reporter that actually emits fetch/start/finish/interruption; Relay schema support for responseId and an index; A canonical duration/integrity gate before upload


## What it asked for

_Nothing._
