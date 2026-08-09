# Harness derivation — faculty-judgement — round 169

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Before you start talking, tell me whether the pendant, USB link, and audio bridge are healthy enough for a real conversation—and if not, quietly choose the safest degraded mode and tell me what failed.”"
- **useful because:** Today a worn pendant can be physically connected yet have decoder starvation, UART loss, or an ESP32 playback fault; the assistant may still promise a conversation. This capability makes admission truthful, preserves a short spoken interaction when possible, and turns repeated failures into a reviewable local bug draft rather than a mysterious silence. It is genuinely cross-body: the Mac can inspect UART, the relay owns the conversation, and the pendant/bridge supply delivery evidence.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Cheaper background rules/model for health classification; realtime model only explains the already-computed verdict in one sentence. No expensive model call when metrics are clearly within thresholds.
- **latency:** Under 300 ms for cached health; at most 2 s for a fresh USB/UART probe before admitting audio. Never delay an emergency stop or owner button press.
- **cost:** Negligible per admission when rules use cached metrics; occasional small background classification call, dominated by UART collection and no external API.
- **security:** UART payloads may contain transcripts or tokens, so retain only metric summaries and hashes in the dashboard; local bug drafts stay on Mac. Never upload raw logs by default. A degraded-mode switch must be reversible and policy-evaluated.
- **missing:** A production USB-serial health adapter that identifies both /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA without assuming LTE registration; A typed health verdict schema and thresholds for packet loss, queue depth, underruns, and bridge reachability; A safe audio-mode fallback hook at the conversation admission boundary; A scheduler or boot hook to invoke the existing diagnostics tool before a session

### "“For every briefing, prove which sources were used, whether the audio actually reached the pendant, and whether I played it; if anything is missing, say ‘not verified’ instead of pretending I heard it.”"
- **useful because:** A generated briefing and a delivered briefing are different facts. The owner currently cannot distinguish cited-but-not-downloaded, downloaded-but-never-played, interrupted, or checksum-failed audio. This would make scheduled research and morning briefs honest, searchable, and recoverable: a one-sentence answer can say exactly what was verified and offer only the missing part.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background model or deterministic joins for source/artifact/ACK reconciliation; realtime model only compresses the verified status into the owner's requested one short sentence.
- **latency:** No added latency to generation; append delivery verification asynchronously. Status query under 500 ms from durable receipts.
- **cost:** Near-zero beyond storage and one small reconciliation pass; no TTS or research rerun unless the owner asks for repair.
- **security:** Store opaque artifact IDs, source IDs, checksums, and timestamps—not raw audio or source text in the delivery ledger. Spoken status must not reveal sensitive source titles unless policy permits. A repair/rerun is a new action requiring autonomy evaluation.
- **missing:** A durable join from research/briefing item to audio artifact and source evidence (current IDs are separate namespaces); A persistent delivery-verification projection that folds downloaded/playback ACKs with duplicate suppression and offline replay; A user-facing route showing missing verification edges and a repair action; A rule that prevents ‘heard’ claims when only server generation or download is known

### "“Let me ask ‘what would happen if I did this?’ and get a cross-surface, read-only rehearsal that shows the exact changes, stale assumptions, and irreversible boundary—without opening a tab, sending anything, or changing my Mac.”"
- **useful because:** Preview endpoints describe some plans, but they do not give the owner one coherent counterfactual across the Mac, authenticated browser, relay, and current evidence. A rehearsal is useful for unfamiliar or high-consequence tasks: it exposes stale tabs, missing permissions, spend or external-audience effects, and the precise point where owner confirmation would be required. It makes the assistant valuable before action, not only after a mistake.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic preflight, policy, and revalidation first; use a cheaper background model to summarize the typed diff. Reserve realtime only for the spoken answer after all read-only probes finish.
- **latency:** Return a concise rehearsal in 2–5 seconds for cached pages; up to 10 seconds for fresh browser reads. Hard timeout yields an explicit incomplete rehearsal, never a guessed outcome.
- **cost:** Low: read-only Mac/browser calls and one compact summarization; no mutation, TTS rerun, or external API spend unless separately approved.
- **security:** Browser page contents and mail can be sensitive; redact snippets by destination and retain only hashes plus field-level diffs by default. Rehearsal must not click, type, navigate away, submit, or create a draft. Every statement needs an evidence reference and freshness timestamp.
- **missing:** A typed counterfactual plan/diff schema spanning Mac actions and browser commands; A read-only observation adapter for each candidate action, with an explicit no-side-effect allowlist; A durable, expiring rehearsal record that can be revalidated but cannot silently become executable; A renderer that distinguishes observed facts, predicted effects, and unknowns in spoken output

### "“When I explicitly start a shared-conversation capture, remember the decisions and who owes what—but first show every participant a clear recording/processing signal, and let me prove later exactly what was retained or erased.”"
- **useful because:** The owner can leave a meeting with accountable decisions instead of a private note nobody else knew existed. Today the pendant can capture owner audio, but it has no participant-consent state, participant-visible signal, speaker/permission boundary, or end-to-end deletion proof for a shared conversation.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a local/cheap speech and extraction pipeline for a short decision transcript; invoke the realtime tier only for an explicit owner query about the meeting. Never send raw audio to a provider without the consent state allowing it.
- **latency:** Consent state and visible start acknowledgement under 1 second; extraction can finish asynchronously within minutes. The owner must be able to stop capture immediately offline.
- **cost:** Moderate transcription/storage cost per meeting, dominated by audio duration; default to short-lived derived decisions and delete raw audio after verified extraction or failure handling.
- **security:** Consent is a hard precondition, not a UI suggestion. Store per-session consent receipts, participant-visible start/stop events, source links, and deletion attestations. Never infer consent from calendar attendance; private or secret content must not be spoken back in public.
- **missing:** A participant-visible indicator or paired phone/web consent surface; the current pendant has only one LED and no haptic motor; A capture mode that binds audio, transcript, extracted decisions, and deletion state to one durable session; Speaker attribution and a policy for third-party data retention; A cryptographic deletion receipt that covers Mac, relay, browser cache, and any transcription provider

### "“When I ask whether I can make it somewhere on time, combine my actual location, the route, my calendar, and what I need to carry; warn me at the last safe departure time, and keep guiding me if the Mac link drops.”"
- **useful because:** A calendar reminder says an event exists, not whether the owner can physically reach it. Today the pendant has no trustworthy location or route progress, the Mac only knows its own timezone/location context, and a dropped link leaves no local navigation state. This would turn deadlines into actionable departures rather than late notifications.
- **path:** pendant → mac-planner → relay-realtime → browser-extension
- **model tier:** Background routing/geocoding and deterministic ETA calculations; realtime model only answers the owner's spoken question or explains a changed route. No model call for ordinary GPS updates.
- **latency:** Initial answer under 3 seconds; route refreshes asynchronous. Local pendant cues must continue within 200 ms after a position update even if the relay is unreachable.
- **cost:** Small recurring map/geocoding cost, dominated by route refresh frequency; cache routes and use coarse local updates to reduce it.
- **security:** Location is exceptionally sensitive. Keep raw coordinates on the Mac/pendant, send only coarse ETA/departure state to the relay by default, expire traces quickly, and require explicit enablement per trip. Never expose location in spoken output when the owner is in public unless asked.
- **missing:** GNSS hardware and antenna or a trusted location feed; the current pendant has no GNSS receiver configured; A local route cache and offline map/turn-cue representation that fits the pendant's storage and RAM; Calendar EventKit permission reconciliation before treating event destinations as known; A route provider integration and a typed location-retention policy; A local departure scheduler that survives a dropped Mac/relay link

### "“While I am wearing it, alert me if you hear a likely smoke alarm, doorbell, name being called, or other personally chosen sound—and tell me exactly what was detected without uploading a continuous recording.”"
- **useful because:** The pendant's microphone is currently useful mainly when the owner presses it. A local acoustic sentinel would help when the owner's hands and eyes are occupied or when they miss an important sound, especially with headphones or a noisy room. The owner gets event-level awareness without turning the device into a cloud microphone.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** A tiny on-device classifier for a fixed, owner-selected sound vocabulary; background relay model only clusters uncertain events after an explicit opt-in. Realtime is not needed for continuous listening.
- **latency:** Local detection and LED/audio cue under 500 ms; upload a compact event asynchronously. No continuous network stream.
- **cost:** Low recurring API cost if classification stays on-device; firmware/model work and a small event log dominate. Optional cloud confirmation should be rare and separately metered.
- **security:** Default to feature vectors/event labels, never raw PCM. Provide a hard physical disable that survives link loss, rate-limit repeated alerts, and distinguish ‘detected’ from ‘confirmed’. Do not identify people or record conversations by default.
- **missing:** An on-device acoustic event model and a measured false-positive/false-negative test set; A firmware local-listener mode with a strict no-audio-retention invariant; An owner-configurable sound vocabulary and alert policy; A signed event envelope that the relay/Mac can deduplicate and route without raw audio; A hardware microphone privacy indicator beyond the current single overloaded LED


## Changes it proposed to its own stack

### `integration` — Build a single verified-conversation admission record on the Mac: collect pendant_diagnostics_and_bug_draft metrics for both live USB serial devices, attach the result to the relay session, and make relay-realtime refuse to claim audio readiness unless the record is fresh. If unhealthy, select a signed degraded-mode envelope and enqueue one concise alert through the existing inbox rather than silently starting.
- **owner gets:** The owner gets an honest answer at the moment they press the pendant, instead of discovering after several seconds that the wearable or bridge could not carry speech.
- effort: Medium: USB serial parser, typed verdict, session attachment, and one relay admission check.  ·  risk: A false unhealthy verdict could delay a conversation; fail open only for text/stop paths, never for claims that audio is working. Expire the verdict quickly and provide a retry.
- cost: No meaningful API cost; local serial reads and a small durable record.  ·  latency: Approximately 100–300 ms from cached metrics, with a bounded fresh probe.
- security: Keep raw UART local; send only metric summaries and opaque session IDs.
- depends on: The existing pendant_diagnostics_and_bug_draft parser must expose structured metrics, not only a prose draft.; A new USB-tethered local voice feasibility result, which is still unknown in this round.

### `relay` — Add a delivery-truth joiner that maps one briefing item to evidence refs, generated artifact ID, and pendant ACK sequence, then computes states generated/downloaded/started/finished/interrupted/checksum_error/unknown. Expose only the state transition and provenance refs to the voice agent; never let ‘generated’ or ‘downloaded’ render as ‘heard’.
- **owner gets:** Scheduled audio becomes trustworthy: a missed or interrupted briefing remains available, while a genuinely played item can be omitted from catch-up without guesswork.
- effort: Medium-high: durable schema migration, idempotent offline replay, and adapters at briefing creation and pendant ACK ingestion.  ·  risk: Incorrect joins could mark an item unheard or heard. Require stable artifact IDs and reject ambiguous joins; preserve raw receipts for repair.
- cost: Small durable storage growth per item; no recurring model cost.  ·  latency: Asynchronous; no impact on initial briefing generation. Status reads under 500 ms.
- security: Opaque IDs and hashes only in the join table; source content remains behind existing evidence policy.
- depends on: A durable relay-job/Mac-job mapping, currently absent.; The accepted audio_delivery_ack_queue and record_pendant_delivery_event path must be wired into the same store.; Briefing creation must emit a stable item ID rather than only spoken text.

### `context` — Create an expiring ‘rehearsal envelope’ rather than another planner: it stores read-only observations, predicted effects, evidence timestamps, policy matches, and an explicit irreversible boundary. On any later execution attempt, require revalidate_pending_plan plus autonomy_policy_evaluate against the current sources; expired or changed envelopes become explanation-only and cannot be promoted.
- **owner gets:** The owner can safely ask ‘what happens if…?’ and inspect a concrete answer without fear that a preview will mutate a tab or later execute from stale assumptions.
- effort: Medium: typed diff renderer, read-only adapters, expiry storage, and promotion guard.  ·  risk: A rehearsal can still be misunderstood as a guarantee. Label observed/predicted/unknown separately, show freshness, and fail closed when a source is unavailable.
- cost: Low storage and one compact summarization call; no mutation cost.  ·  latency: 2–5 seconds for fresh reads; cached rehearsals are immediate.
- security: Default to hashes and field names, with sensitive snippets only after explicit dashboard request; never send secrets to the summarizer.
- depends on: Existing POST /preview and browser inspect routes need a common typed output.; The approval handoff contract must be implemented on the relay if rehearsal promotion is ever allowed.; A cross-surface correlation ID is needed to join Mac and browser observations.

### `hardware` — Add a physically separate private-audio transducer to the next pendant revision: a low-power bone-conduction or near-ear transducer with a hardware mute switch, while retaining the existing open speaker for public replies. The firmware exposes two signed output classes (public and private); private audio is electrically impossible when the switch is open, rather than relying on a server-side redaction decision.
- **owner gets:** They could ask for names, reminders, or sensitive context while standing beside other people without either refusing useful help or broadcasting it. Today the single open speaker cannot provide a trustworthy private channel.
- effort: High: enclosure/acoustic redesign, driver and power budget, firmware routing, and measured intelligibility/leakage tests in a real room.  ·  risk: Bone conduction may be uncomfortable or unintelligible and a bad switch could create false privacy. Fail closed to silence on private output when the channel is unavailable; never silently route private text to the open speaker.
- cost: Roughly $15–40 in transducer, driver, and mechanical parts at prototype volume; additional tens of mW during private playback and likely a larger enclosure.  ·  latency: Negligible routing latency; acoustic calibration adds manufacturing/test work.
- security: Creates a hardware boundary stronger than the current sensitivity classifier. The private channel must have a physical mute and no fallback to public audio.
- depends on: A next hardware revision; the current board has one LED and an open audio path only.; A policy value naming which output classes are private; the owner has not supplied that policy yet.; Measured speech leakage and intelligibility acceptance tests.


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing directions and three concrete stack changes: (1) truthful conversation admission from live USB pendant + ESP32 health, (2) a briefing chain-of-custody that distinguishes generated/downloaded/played, and (3) a read-only cross-surface counterfactual rehearsal that expires and cannot silently become an action. The recorder correctly flagged that the primitives already exist; the new work is the missing joins, durable records, and enforcement between them—not another standalone tool.

**Biggest unknown:** USB-tethered local voice feasibility is still unresolved: I need an authoritative result on serial throughput, how the relay session can be bound to the Mac-attached pendant, and whether the ESP32 bridge exposes a trustworthy health signal. I also still need stable briefing-item/artifact correlation and a relay-job↔Mac-job mapping. Owner policy decisions (spoken sensitive content, trusted destinations, quiet/urgent rules) remain intentionally unset, so all proposals must ship conservative and policy-configurable rather than assume them.

