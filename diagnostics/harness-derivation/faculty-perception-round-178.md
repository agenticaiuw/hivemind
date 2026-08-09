# Harness derivation — faculty-perception — round 178

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS reachability and live surfaces** — At 2026-08-08T04:47Z, the exact AI Pendant Agent binary has Accessibility and Screen Recording granted; /observe reports inputReachability.status=verified, uiActionsWillReachTheScreen=true, secureInput=false. Safari and its browser extension are online with two tabs; Mac bridge and relay are reachable. No pendant appears in the live device inventory.
  - evidence: GET /observe HTTP 200 and GET /ops/snapshot HTTP 200 at 2026-08-08T04:47Z; devices discovery lists Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline.

## Capabilities it proposed

### "Before you do anything consequential, tell me whether the world you are about to act on is still the world I meant: which app and browser tab are foreground, whether the browser session is fresh, whether the relay and Mac are reachable, and whether any required permission or device evidence is stale."
- **useful because:** Prevents the worst class of silent mistakes: sending or editing in the wrong tab, acting on a stale page, or treating a disconnected wearable's old state as current. It gives judgement a machine-readable precondition instead of a vague status page.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background for the bounded snapshot and contradiction checks; realtime only to explain a failed precondition in the owner's voice
- **latency:** Under 1 second when cached; under 3 seconds when browser and relay freshness probes are required
- **cost:** <$0.01 per check; dominated by no model call if the result is structured, with a small realtime explanation only on failure
- **security:** Must not expose page contents or secrets in the precondition; return origin, tab/session pseudonym, freshness, and permission booleans. Consequential actions require explicit confirmation if the foreground target changed or evidence is stale.
- **missing:** a signed/immutable precondition record joining /observe, /browser/status, /ops/snapshot, and relay device/job state; action-agent enforcement that refuses an execute unless the precondition still matches; a freshness policy per action class

### "Show me a causally ordered account of what happened across my devices, and flag contradictions instead of smoothing them over—for example, the Mac says a job completed while the relay lost contact or the browser changed tabs before the action receipt."
- **useful because:** A timestamp list is not an explanation. Causal reconstruction tells the owner which event caused which outcome, identifies races and clock uncertainty, and makes it possible to trust 'nothing happened' only when the evidence supports that conclusion.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → mac-terminal → faculty-judgement
- **model tier:** background deterministic event graph first; use the expensive model only to summarize unresolved contradictions in plain language
- **latency:** 2 seconds for the graph over recent events; 5 seconds for a human summary
- **cost:** <$0.02 per invocation; graph construction is local, with model cost only for the final explanation
- **security:** Persist event metadata and hashes, not page text or audio. Treat device clocks as untrusted; preserve source timestamps, monotonic sequence numbers, and observed-at times. Never infer success from a missing event.
- **missing:** a cross-surface event envelope with source, observedAt, sourceTime, monotonic/sequence key, causal parents, and uncertainty; relay endpoint to export its event/job transitions in that envelope; Mac and browser writers for action, tab, and receipt transitions; a contradiction classifier and owner-visible confidence grades

### "Is it safe to say this aloud right now? Classify the current target and nearby context as private, public, or unknown, then tell the action system whether spoken output may contain the requested details or must be redacted or withheld."
- **useful because:** A wearable speaks into the owner's physical surroundings. This prevents a calendar invite, bank page, message, or browser result from being broadcast merely because the request was valid. It also makes 'I can't safely say that here' a grounded device decision rather than a model guess.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic classifiers and explicit app/site policy first; background model only for unknown domains; realtime only for the short refusal or confirmation
- **latency:** Under 300 ms for known apps/sites; under 2 seconds for an unknown target
- **cost:** Near-zero for policy matches; <$0.01 for an unknown-context classification
- **security:** Fail closed on unknown or sensitive contexts. Do not transmit page text to the relay merely to classify it. Store only sensitivity class, host/app identifier, and decision reason. Require confirmation before speaking sensitive content even when requested.
- **missing:** a local sensitivity policy covering app bundles, browser hosts, and user-defined private zones; a perception route that joins foreground app, browser tab, requested target, and output channel; relay and pendant support for redacted/withheld speech with a reason code; action enforcement so a valid execute cannot bypass the privacy verdict

### "Let me hand you a task while I walk away, and have it finish safely across the browser, Mac, relay, and pendant—even through a connection drop—then tell me exactly which steps completed, which were rolled back, and what still needs me."
- **useful because:** Today the surfaces can each act, but a task has no end-to-end ownership: a browser action, Mac job, relay state, and wearable conversation can diverge. This would make the system a dependable assistant rather than several unrelated remote controls.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** background model for planning and reconciliation; deterministic local executors and the realtime tier only for the owner's live handoff and exception speech
- **latency:** Acknowledge handoff in under 1 second; execute ordinary steps within 30 seconds; reconcile after reconnect within 5 seconds
- **cost:** $0.02–$0.20 per task depending on browser vision steps; most cost is long-running computer-use inference, not reconciliation
- **security:** Requires a signed task lease, per-step target/effect, idempotency key, expiry, and explicit confirmation for irreversible steps. A disconnected Mac must not continue beyond the lease. Sensitive browser contents stay on the Mac; relay receives hashes, statuses, and redacted summaries.
- **missing:** a cross-surface task lease and step identity protocol; durable reconnect reconciliation that distinguishes committed, uncertain, and rolled-back steps; browser and Mac executors that report before/after evidence under the same task ID; pendant-visible approval and cancellation messages that survive a dropped link

### "When I ask what I missed, reconstruct the relevant moment from my Mac screen, browser state, spoken conversation, and pendant audio-quality signals, and show me the smallest evidence-backed explanation—not a guessed summary."
- **useful because:** The owner currently gets isolated logs and transcripts, not an account of a real-world episode. Joining visual state, browser provenance, speech boundaries, and relay events would recover what actually happened when a conversation was interrupted or an action became ambiguous.
- **path:** faculty-perception → mac-vision → browser-extension → relay-realtime → mac-planner → faculty-judgement
- **model tier:** deterministic alignment and redaction first; a slower model summarizes only the selected evidence window
- **latency:** Capture continuously with negligible interaction cost; answer a retrospective query in under 10 seconds
- **cost:** $0.03–$0.15 per retrospective query; storage and redaction dominate more than inference
- **security:** Default to event metadata and short redacted excerpts, never continuous raw recording. Explicit owner opt-in and per-app exclusion zones are required. Evidence must retain uncertainty and distinguish observed facts from model interpretation.
- **missing:** an owner-controlled multimodal evidence journal with bounded retention; a common clock/sequence alignment between browser, Mac, relay, and pendant; local redaction and consent controls for screen and audio evidence; a query layer that returns citations and confidence rather than free-form recollection

### "Pause yourself when I start talking to another person, and resume only when the conversation is over or I explicitly ask. Do not play queued announcements over my real conversation; preserve them with their urgency and explain any item that expired."
- **useful because:** A wearable assistant that speaks over a human conversation is socially and practically unsafe. Local speech detection can protect the moment even when the relay is unavailable, while the relay and Mac preserve and reprioritize what was deferred.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** on-device VAD and interruption classifier for immediate muting; background model for reprioritization; realtime only for resumed speech
- **latency:** Mute within 150 ms of detected competing speech; resume decision within 2 seconds after the conversation ends
- **cost:** Near-zero during the interruption because detection is local; <$0.01 for background reprioritization
- **security:** Audio should be processed locally and discarded after features are extracted. Never upload bystander speech. False positives should defer rather than speak; emergency alerts need an owner-configurable override and a distinct local signal.
- **missing:** a pendant-local competing-speech classifier beyond ordinary VAD; a persistent, bounded announcement hold state shared by pendant and relay; a resumable audio protocol that can stop and restart without marking bytes-to-socket as heard; owner-configurable urgency and emergency override policy


## Changes it proposed to its own stack

### `interaction` — Add a local, owner-editable 'speaking boundary' mode: a single pendant button press or Mac menu control toggles public/private/unknown output. Perception combines that mode with the foreground app and browser host; private or unknown blocks detail-bearing speech before relay synthesis, while still allowing a terse notification.
- **owner gets:** The owner gets a reliable physical way to say 'do not read this aloud here' without finding a setting, and sensitive pages stop leaking through an otherwise valid voice request.
- effort: Medium: local policy store, browser/app matching, relay reason-code propagation, and a pendant/bridge indicator; test with Safari, Messages, Mail, banking, and a disconnected pendant.  ·  risk: A stale mode could over-block or under-block. Default to private after restart and show the current mode visibly; require an explicit public toggle to loosen it. Recovery is a short button press or Mac control.
- cost: Negligible API cost; small local state. No new hardware required if the existing button/LED path is available; otherwise <$5 for an indicator component.  ·  latency: <100 ms locally; no model call on known apps/sites.
- security: Improves confidentiality by keeping classification and policy local; unknown contexts fail closed. Must avoid sending page text to the relay for classification.
- depends on: verified /observe input reachability; a local sensitivity policy for app bundles and browser hosts; relay/pendant support for a withheld or redacted speech outcome


## What it asked for

_Nothing._
