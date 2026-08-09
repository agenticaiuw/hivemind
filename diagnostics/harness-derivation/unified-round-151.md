# Harness derivation — unified — round 151

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “fill this out but don’t submit,” inspect the current browser form, draft the fields without exposing secrets to the relay, and let me approve the final submission with the pendant."
- **useful because:** It turns the pendant into a safe boundary for browser transactions: the Mac/browser can reach the authenticated page, while the owner retains physical control over the irreversible submit. A draft can survive a dropped link without submitting twice.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** background for page/schema summarization; deterministic code for field mapping, digesting, and submission; realtime only for the spoken confirmation
- **latency:** Inspect and produce a spoken summary within 3–5 s; approval-to-submit under 2 s; no network round trip should be needed for the pendant’s cancel decision.
- **cost:** About $0.01–$0.04 per invocation, dominated by one planner/model call for ambiguous fields; deterministic forms cost near zero.
- **security:** Form values and page contents stay in the bound browser session; relay receives only a redacted field summary, plan digest, and receipt. Never autofill passwords or payment data without an explicit per-field policy. Submission requires the existing physical transaction nonce and a fresh owner approval; cancellation must be local and immediate.
- **missing:** Wire prepare/approve to the relay instead of its current schema-only contract; A browser action executor that stages field edits and returns a page/world digest without submitting; A secret-field policy and redacted preview renderer; A commit receipt binding the physical nonce to the exact browser tab and form digest

### "Tell me, in one sentence, what the pendant heard, what the Mac/browser did, and whether I actually heard the reply—not just whether the job completed."
- **useful because:** It closes the most important trust gap in a wearable assistant: relay acceptance is not physical playback, and a browser success page is not proof the intended action happened. The owner gets a compact, evidence-backed answer with uncertainty instead of a false “done.”
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic evidence join and confidence rules; cheap background model only to compress verified evidence into one spoken sentence.
- **latency:** Answer status queries in under 1 s from cached receipts; if evidence must be fetched, under 3 s. Never block the original action on the summary model.
- **cost:** Near-zero for deterministic joins; under $0.005 for optional wording. Storage is a bounded metadata ring, not audio.
- **security:** Return only evidence from explicitly bound tabs/apps and the matching conversation/job. Redact page text, secrets, and audio contents. Distinguish accepted, executed, playback-started, playback-finished, and unknown; never infer hearing from relay delivery. Owner confirmation is required before exposing sensitive browser evidence.
- **missing:** A single correlation ID propagated through capture, relay job, Mac/browser command, and playback receipt; Bridge-side playback start/finish receipts correlated to the existing audio_delivery_ack_queue; A typed read-only join route across pipeline, jobs, browser inspections, and pendant events; Retention/deletion policy for the metadata receipt ring

### "Before you click anything on this page, tell me what it will send, who receives it, and which parts are irreversible."
- **useful because:** The browser has the owner’s authenticated sessions, so ordinary webpage text can trick an agent into exfiltration or destructive actions. A preflight spoken risk card lets the owner use automation without needing to inspect every URL or understand the form themselves.
- **path:** pendant → relay → mac-bridge → browser → dashboard-ux
- **model tier:** Deterministic origin/action/data-flow extraction first; background model only for ambiguous page language and concise explanation; realtime only when the owner is actively asking.
- **latency:** Return a three-part spoken risk card within 2 s for a known page; up to 5 s for an ambiguous page. Do not execute anything while analysis is pending.
- **cost:** $0.002–$0.02 per check, dominated by optional model interpretation; known-origin and static-form checks are deterministic and nearly free.
- **security:** Inspection must be bound to the exact tab/session and must not submit forms, follow external links, or send page contents to the relay wholesale. Report destination origins, field sensitivity classes, and irreversible effects, redacting values. Treat page instructions as untrusted data, not agent policy. Any action after the card still uses existing physical approval for high-risk effects.
- **missing:** A typed browser preflight endpoint that returns origin, destinations, sensitive-field classes, and predicted effects without mutation; A maintained local origin/policy registry and suspicious-instruction detector; A pendant-friendly risk vocabulary and acknowledgement state; Tests covering cross-origin forms, downloads, navigation, and destructive buttons

### "Only execute a command if it came from my live pendant press and current voice turn—not from a replayed audio packet, stale browser tab, or another session."
- **useful because:** A bearer-token Mac agent and a relay job can otherwise accept old or cross-session instructions. The owner gets a command-origin guarantee: a remote page or delayed packet cannot cause an action merely because it resembles a previous request.
- **path:** pendant → relay → mac-bridge → mac-planner → browser
- **model tier:** Deterministic cryptographic verification and freshness checks; no model call for authorization. Realtime model handles speech recognition only after the envelope passes.
- **latency:** Verification under 20 ms on the relay and under 50 ms on the Mac; reject stale commands before any planner or browser action starts.
- **cost:** Negligible model cost; roughly 32–96 bytes of authenticated metadata per turn and a small key store on the pendant/relay.
- **security:** The pendant must sign a monotonic turn nonce and button-edge timestamp with a device key; the relay binds it to a conversation and transport epoch, and the Mac/browser reject replay, cross-session, and out-of-order envelopes. The private key must never leave the device. Key rotation and factory reset need explicit recovery, and this does not replace physical approval for irreversible actions.
- **missing:** Device identity key provisioning and protected monotonic counter on the pendant; Relay verification and replay cache bound to conversation and transport epoch; Mac/browser middleware that refuses unsigned or stale execute requests; A recovery ceremony for key rotation without silently widening authorization

### "When I put the pendant on or move to a noisy room, calibrate the microphone, speaker, and bridge together so my speech stays intelligible without sudden loudness or clipping."
- **useful because:** The owner should not have to tune gain, distance, or playback level by trial and error. A joint calibration uses the wearable’s real acoustic path and the ESP32 bridge’s speaker/mic geometry, improving everyday intelligibility while preserving the shipped 24 kHz codec path.
- **path:** pendant → relay → mac-bridge → mac-planner
- **model tier:** Deterministic signal analysis and calibration tones; a cheap background model may label the environment (quiet, speech-noise, wind) but must not control safety limits.
- **latency:** A brief 2–4 s calibration on explicit request; adapt gain within 100 ms during a call, with hard peak and rate-of-change limits. Never inject calibration audio during an active response without consent.
- **cost:** Near-zero model cost; a few seconds of local PCM and metadata. Firmware work is the main cost; no routine audio persistence.
- **security:** Run analysis locally on the pendant/bridge where possible; do not upload room audio. Calibration tones must be clearly announced and cancellable. Keep safe maximum output independent of model decisions, and disable adaptation while the privacy latch is set.
- **missing:** Bridge firmware endpoints for loopback/tone generation and measured RMS/peak/noise-floor reports; Pendant-side short-window AGC/noise metrics and a bounded calibration profile in nonvolatile settings; A Mac/relay calibration command that coordinates both chips over USB today and LTE later; Acceptance tests for clipping, echo, latency, and preservation of 24 kHz framing

### "Give me a private, local-only way to say “what did you just hear?” and replay or discard the last turn without sending that transcript or audio to the relay."
- **useful because:** Speech recognition can be wrong and a wearable response can be missed in noise. The owner gets an immediate correction path that works during link loss and does not create a new cloud copy of a sensitive conversation.
- **path:** pendant → mac-bridge → mac-planner
- **model tier:** Local deterministic ring-buffer indexing; optional on-device or Mac-local speech decoding only when explicitly enabled. No cloud model is required for replay.
- **latency:** Button-triggered replay/discard feedback under 150 ms; the last-turn index should be available offline. Any local transcription may take up to 2 s but must not delay replay.
- **cost:** No per-use API cost; bounded RAM/flash metadata and, only under explicit local policy, a short volatile PCM buffer. Hardware/storage cost depends on the owner’s chosen retention window.
- **security:** Default to no persistent raw audio and no relay upload. The privacy latch must clear the volatile buffer immediately. Replay must not become an accidental upload, and any local transcript needs an explicit retention/deletion policy. The device should expose only the selected turn, not an ambient pre-roll.
- **missing:** A post-turn volatile audio/sequence buffer that starts only after deliberate capture and is wiped at turn close or privacy latch; A dedicated offline query/replay button mapping that does not delay the existing recording edge; USB-local control messages for replay/discard and explicit no-upload status; Owner choice of whether local transcription is allowed and how long a turn may remain volatile


## Changes it proposed to its own stack

### `integration` — Add a correlation envelope shared by pendant turns, relay jobs, Mac jobs, browser commands, and audio delivery receipts: conversationId, turnId, transportEpoch, actionDigest, and parentReceiptId. Propagate it through POST /pipeline/events, POST /execute, browser result callbacks, GET /jobs/:jobId/receipts, and the pendant’s audio_delivery_ack_queue; expose one read-only join response that labels each stage accepted/executed/played/heard-unknown.
- **owner gets:** The owner can ask “did it happen?” and receive a truthful one-sentence answer tied to the exact turn and tab, instead of a relay job marked complete when the browser or speaker failed.
- effort: Medium: shared schema plus adapters in relay, Mac executor, browser bridge, and firmware receipt emission; add fault-injection tests for duplicate, late, and out-of-order events.  ·  risk: Incorrect propagation could merge two turns or falsely claim completion. Reject missing/invalid parent IDs, use monotonic epochs, and default to unknown rather than success. Recover by keeping existing per-surface receipts when the envelope is absent.
- cost: Negligible storage and bandwidth for roughly 100–250 bytes of metadata per stage; no model cost for the join.  ·  latency: Under 10 ms for propagation; cached status lookup under 1 s. It must never wait for the speech model or block playback.
- security: Redact payloads and page contents; only opaque IDs, digests, and bounded status leave each surface. Bind browser evidence to an explicit tab/session and enforce the owner’s existing destructive-action confirmation.
- depends on: Define the correlation envelope and versioning; Implement relay persistence for the approval/receipt contract; Wire bridge playback receipts to the existing audio_delivery_ack_queue; Add a typed read-only cross-surface join route


## What it asked for

_Nothing._
## Its own summary

Round 151 produced three new recorded capability directions and one integration change. The strongest is a cross-surface correlation envelope and truthful completion answer: bind one turn across pendant capture, relay job, Mac/browser action, and physical playback, then report accepted/executed/played without claiming “heard” unless the pendant can prove it. I also recorded a browser preflight risk card and a staged browser-form workflow using the existing physical approval latch. The USB/LTE conversation migration proposal was correctly rejected as a duplicate of the existing transport-handoff capability, so I will not rephrase it.

**Biggest unknown:** The remaining blockers are implementation seams, not reconnaissance: relay persistence for the approval contract, typed browser preflight/staging results, and correlation propagation into playback receipts. Owner policy is still needed for transport preference (LTE-only vs USB/phone fallback), browser secret-field handling, and the conflict between the Mac’s authoritative America/New_York zone and the owner memory saying America/Chicago. Retention/deletion policy remains pending from the earlier request and should not be guessed.

