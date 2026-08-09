# Harness derivation — faculty-perception — round 187

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception state** — At 2026-08-08T22:23Z the live continuity snapshot reports AI Pendant Agent accessibility=true, screenRecording=true, automation grants present, permissions.ready=true; Safari extension online with 2 tabs and active DoorDash tab; Mac bridge and relay reachable; no pendant evidence is present in this snapshot.
  - evidence: read_continuity_snapshot include relay,pipeline invoked GET /ops/snapshot HTTP 200; returned status.permissions and browser/relay blocks.

## Capabilities it proposed

### "“Why didn’t that work? Show me exactly where it failed and what the owner or system actually saw.”"
- **useful because:** Today a Mac job can be marked complete while browser execution, relay delivery, or physical playback failed. This capability would produce an incident replay: one causal chain linking the spoken request, planner decision, browser command, Mac receipt, relay response, pendant capture/playback telemetry, and the first broken edge. It would explicitly separate 'action completed', 'page changed', 'relay accepted', and 'owner heard it', so the owner can retry the right layer instead of repeating the whole command.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic event join and failure classification first; a cheaper background model summarizes ambiguous evidence. Realtime only answers the owner's follow-up.
- **latency:** Initial diagnosis in 2–5 seconds from bounded recent events; a deep replay can run in the background and notify when ready.
- **cost:** Roughly $0.002–$0.02 per incident summary; event joining and hash comparisons dominate little, while model explanation dominates cost.
- **security:** Replays may contain page titles, typed text, screenshots, and audio quality metadata. Store redacted event envelopes, not raw audio or page bodies; require confirmation to reveal sensitive fields or transmit a replay to cloud relay.
- **missing:** A shared correlation ID propagated from voice turn through planner, browser command, relay job, and device artifact; A device-originated playback event (the accepted audio_delivery_ack_queue is the right firmware direction); A failure taxonomy and causal-graph reader rather than today's independent completion fallbacks; A bounded incident bundle endpoint on the dashboard

### "“Is anything private visible or being captured right now, and should you stop talking?”"
- **useful because:** The owner can wear the system while banking, messaging, or entering a password. This would continuously establish a privacy boundary across the Safari/Chrome tab, screen capture permission and active window, Mac microphone/capture pipeline, relay transmission, and pendant audio state. It would report a compact verdict such as private-page-visible, secret-input-in-progress, audio-uploading, or safe-to-speak, with the exact evidence and age. Judgement could then pause speech or refuse to quote page content before leakage occurs.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → dashboard
- **model tier:** Pure local rules and classifiers for URL/field/accessibility metadata; a small background model only handles ambiguous page semantics. No realtime model call for steady-state monitoring.
- **latency:** 250 ms for browser/window transitions and under one audio frame for capture-state changes; no cloud round trip required for the privacy verdict.
- **cost:** Near-zero ongoing API cost; occasional local classification. If ambiguous content needs a model, cap it at about $0.001 per transition and never upload raw secrets by default.
- **security:** This feature itself observes the most sensitive signals. Keep verdict inputs local, hash or classify URLs, never retain keystrokes or page bodies, and make the owner choose whether private-page metadata may reach relay. A false negative is serious: speech must fail closed when evidence is missing or stale.
- **missing:** A Mac event stream for active window and secure-text-field transitions that does not require scraping screenshots; Browser extension events for password/payment fields and page sensitivity classification; A relay speech gate that consumes the local privacy verdict before TTS/announcement bytes are emitted; Pendant mute/recording state telemetry, including the offline sentinel's unusable-capture verdict

### "“Before you do anything consequential, verify that it is really me, that I can see the target, and that the requested change is still the one I intended.”"
- **useful because:** A spoken command can be stale, overheard, or aimed at a page that changed after the owner looked at it. This capability creates a perception quorum before judgement: pendant button/voice session proves local presence, browser evidence proves the exact current target, Mac state proves the intended account/app, and relay freshness proves the request has not been replayed. It would return proceed / ask-again / refuse with the missing evidence, preventing the worst class of silent wrong-account or wrong-page actions.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Deterministic freshness, identity-binding, and target-hash checks; background model only interprets ambiguous intent. Realtime handles a short confirmation exchange when quorum is incomplete.
- **latency:** 300–800 ms for checks already cached; at most 3 seconds if the browser must capture a fresh evidence capsule and the pendant must confirm presence.
- **cost:** About $0.001–$0.01 per consequential action; hashes and local checks are free, with model cost only for ambiguous intent or a confirmation question.
- **security:** The quorum must not become an authorization bypass. Never treat a browser session or Mac login as owner identity alone; bind a one-time nonce to a physical pendant interaction when available, expire it quickly, and show the target before action. Do not send secret form values into the quorum bundle.
- **missing:** A nonce-bearing physical-presence event from the pendant, with the pendant currently absent from the registry; A relay-to-Mac one-time challenge channel bound to the voice turn; Mounted browser provenance/evidence routes and a fresh target hash at the decision point; A policy declaring which actions are consequential and when explicit confirmation is mandatory

### "“Show me, in plain language, exactly what information is leaving each device right now, and let me allow or revoke one kind without shutting everything off.”"
- **useful because:** The owner cannot currently distinguish microphone audio sent for transcription, browser metadata sent for an action, page content sent to a model, and telemetry retained for diagnostics. This would provide a live data-flow ledger with per-stream purpose, destination, fields, retention, and owner consent state—and let the owner revoke only a stream such as page text, recordings, or location while preserving basic voice control. It makes the hive governable rather than merely powerful.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy and byte/field accounting; no model is needed except optional plain-language explanation of an already-structured flow.
- **latency:** Consent changes take effect within 250 ms locally and before the next network frame; the dashboard view should load in under 1 second.
- **cost:** Near-zero inference/API cost. Storage is a bounded local ledger of redacted flow metadata; implementation cost is instrumenting all egress paths.
- **security:** The ledger itself must not reveal the secrets it protects. Record schemas, classifications, destinations, and byte counts—not raw values. Revocation must fail closed at the source, survive relay reconnects, and require explicit confirmation to re-enable high-risk streams. An emergency physical mute on the pendant remains necessary.
- **missing:** A common egress-event protocol emitted by pendant, Mac, browser extension, and relay before transmission; Field-level redaction/classification and destination labels for every route, including model and durable-storage destinations; A signed, versioned consent policy replicated to the devices with offline-safe defaults; Relay and browser enforcement points that can drop a field rather than only disable an entire feature

### "“Forget this everywhere, and prove to me what was deleted, what was only made inaccessible, and what you could not reach.”"
- **useful because:** Today browser reads, announcements, audio, Mac ledgers, and relay jobs have different retention rules, some advertised expiries are not enforced, and there is no cross-surface deletion receipt. The owner should be able to select one utterance, page read, recording, or action and receive a deletion plan spanning browser, Mac, relay, and pendant storage, followed by independently checkable tombstones and explicit residuals. This is the difference between 'we stopped showing it' and actual control of personal data.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic content-address and tombstone propagation; a background model may resolve a vague reference like 'that DoorDash thing' only after presenting the matched records for confirmation.
- **latency:** Show the affected-record plan in under 2 seconds; local deletion immediate, relay confirmation within 10 seconds, and offline pendant deletion queued with a visible deadline.
- **cost:** About $0.001–$0.01 only when resolving an ambiguous reference; deletion and verification are API/storage work, not model work.
- **security:** Deletion requests are destructive and must require confirmation plus a clear scope. Tombstones should retain only opaque IDs, hashes, timestamps, and deletion status. Do not promise deletion from third-party browser/cloud history that the system cannot control; report unreachable replicas and legal retention honestly.
- **missing:** A shared artifact identity that joins utterance, page capture, audio, announcement, job, and derived summaries; Delete/tombstone endpoints on every store, including the currently unpruned relay announcements and opt-in-only relay audio sweep; A device-side erase queue that works offline without using the SD failure buffer for routine metadata; A verifier that samples each store and distinguishes body deletion, access revocation, and mere expiry

### "“If my Mac, browser, relay, or pendant disappears right now, what can you still do—and prove it with a safe drill before I rely on you?”"
- **useful because:** The owner cannot currently know which promises survive a dead Mac, dropped LTE, stale browser session, or rebooted relay. A capability survival drill would run non-destructive synthetic probes across all four surfaces, verify offline queues and reconnect behavior, and return a per-function contract: works offline, degrades safely, waits for reconnect, or falsely appears complete. It would let the owner decide whether this is trustworthy outside the house rather than discovering the boundary during an urgent request.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic test runner and state machine; a cheap background model converts probe results into a human-readable contract. Realtime is only for announcing the result.
- **latency:** A standard drill under 30 seconds; a full fault matrix can run in the background and finish in a few minutes.
- **cost:** Under $0.01 per standard drill; synthetic payloads avoid model and browser-cloud costs. Main cost is engineering isolated fault injection and test fixtures.
- **security:** Drills must never send real messages, alter browser state, or expose page content. Use synthetic jobs, loopback audio, and a disposable browser session. Fault injection must be scoped and reversible; require confirmation before testing a live LTE disconnect or deleting a local queue.
- **missing:** A synthetic artifact/test mode shared by pendant, relay, Mac, and browser; Fault-injection controls for link loss, process restart, stale credentials, and offline queue replay; A verifier for the accepted audio_delivery_ack_queue and offline-reality-beacon semantics once a pendant exists; A dashboard contract format that records probe version, timestamp, and scope so results are not mistaken for a guarantee


## Changes it proposed to its own stack

### `integration` — Add a fail-closed privacy boundary service on the Mac agent. It consumes browser extension sensitivity transitions, active-window/secure-field events, pipeline capture state, and relay speech intent; publishes a signed, short-lived verdict {safeToSpeak, safeToTransmit, reason, observedAt, expiresAt} to the relay and dashboard. Relay TTS and announcements must refuse content-bearing output when the verdict is private, stale, or absent. Keep raw page text, keystrokes, and audio local.
- **owner gets:** The pendant will stop reading or transmitting content when a password, payment form, private message, or sensitive page is in view—even if the owner forgets to say 'stop'—and it will explain exactly why it stayed quiet.
- effort: Medium: local event adapters plus a small policy service, relay enforcement, and extension metadata; no new model required for the common case.  ·  risk: False positives make the device annoyingly silent; false negatives can leak private content. Recover by defaulting to silence, showing a local override button, and logging only redacted reason codes. Test against password/payment fields before enabling cloud relay enforcement.
- cost: Negligible API cost; local state machine. Engineering cost is integration and adversarial testing, not inference.  ·  latency: Sub-frame local updates; relay enforcement adds no model round trip.
- security: Improves security only if the relay treats verdict absence as deny and verdicts are nonce-bound and short-lived. Do not use URL alone as a sensitivity signal.
- depends on: Browser extension emits secure-field and sensitivity transitions; Mac agent exposes active-window and capture-state events; Relay speech/announcement path accepts and enforces a signed privacy verdict; Pendant playback/recording telemetry once a pendant registers


## What it asked for

_Nothing._
## Its own summary

Fresh live discovery: /ops/snapshot is reachable and reports the exact Mac agent now has Accessibility and Screen Recording granted, permissions.ready=true, Safari extension online with two tabs (active DoorDash), and relay/Mac bridge reachable. I recorded three new capabilities: cross-surface incident replay, privacy-aware capture/speech boundary, and physical-presence plus target-freshness quorum before consequential actions. I also recorded a concrete integration change: fail-closed local privacy verdicts enforced by relay speech. What I still need is not another diagnostic grant: a registered pendant emitting nonce/presence and playback telemetry, browser secure-field/sensitivity events, a shared correlation/nonce channel, and relay enforcement hooks. Until then, pendant receipt/hearing remains unknown and privacy decisions must fail closed.

**Biggest unknown:** The pendant is still absent from the live registry, so no current fact can establish physical playback, local presence, or device-side capture quality; all pendant-dependent proposals are specified but cannot yet be exercised.

