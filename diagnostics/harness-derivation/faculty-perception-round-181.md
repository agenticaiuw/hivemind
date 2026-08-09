# Harness derivation — faculty-perception — round 181

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current Mac and browser observability** — As of 2026-08-08T04:55Z, Mac agent is ready with Accessibility and Screen Recording granted, all required permissions present, computer-use loop enabled (vision model configured, max 25 steps), and Safari browser bridge online with two tabs; relay is reachable and D1-backed. No pendant appears in the live device list.
  - evidence: GET /ops/status returned permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, computerUse.loopEnabled=true, browserExtension.online=true, relay.reachable=true; discover(devices) listed only Safari, home-macbook-bridge, and offline cloudflare-contract-test.

## Capabilities it proposed

### "Before you change anything in my browser or Mac, prove that you have the right target: which account, tab, window, document, and visible state are actually in front of you, and stop if the evidence conflicts."
- **useful because:** The most valuable perception the system could provide is preventing a confident action on the wrong account or stale tab. It would use the newly granted screen and accessibility access to corroborate browser DOM, pixels, application identity, URL, and session state, then give judgement/action a bounded evidence packet instead of an assumption.
- **path:** browser-extension → mac-vision → mac-planner → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic URL/tab/window/account extraction first; use the realtime model only to resolve genuinely ambiguous visual identity. No model call for a clean match.
- **latency:** 300-800 ms for DOM/accessibility checks; up to 3 s only when a screenshot must be inspected.
- **cost:** Usually near-zero model cost; occasional vision escalation roughly one low-latency image turn.
- **security:** Never return passwords, tokens, or page secrets; redact account identifiers to host plus last four characters unless the owner explicitly asks. Require owner confirmation whenever identity evidence is missing or contradictory. Screen pixels leave the Mac only for the escalated visual check.
- **missing:** A single signed target-attestation schema joining browser command/session, tab/window, accessibility application identity, URL, screenshot hash, and capture time.; A relay/faculty-perception route that blocks faculty-action until the attestation is fresh and non-conflicting.

### "When two places disagree, tell me exactly which observation is stale or ungrounded: compare the browser, the active Mac app, relay job state, and local files, with timestamps and provenance, without silently picking a winner."
- **useful because:** Owners currently get a fluent answer even when a browser tab, Mac receipt, and relay record describe different realities. A provenance-first contradiction report would make the collective trustworthy: it can say 'the page is current, the job receipt is older, and the local file was never observed' rather than laundering uncertainty into a yes.
- **path:** faculty-perception → browser-extension → mac-vision → mac-terminal → mac-planner → relay-realtime → faculty-judgement
- **model tier:** Deterministic timestamp, hash, URL, receipt, and process comparisons first; a cheaper background text model clusters conflicts. Reserve realtime for the owner's follow-up question.
- **latency:** 1-2 s for three read sources; up to 5 s for a file hash or visual corroboration.
- **cost:** Low: mostly local reads and hashes; occasional small text-model call, no audio or large page body by default.
- **security:** Treat browser text and relay content as untrusted evidence, never instructions. Redact secrets and retain only digests, source locators, timestamps, and short claims. Ask before reading private app contents or uploading a screenshot.
- **missing:** A normalized observation record with observedAt, source, freshness bound, content hash, locator, and grounded/asserted classification.; A cross-surface compare route that accepts observation references and returns conflicts without storing raw private bodies.; A policy for source-specific freshness (browser DOM, relay job, filesystem, and accessibility state).

### "Tell me what changed on my screen while I was away—what app, tab, document, or dialog appeared, disappeared, or changed—and show only the meaningful differences, not a replay."
- **useful because:** This turns the newly working Screen Recording and Accessibility grants into something the owner can feel immediately: returning to the Mac no longer requires reconstructing state from memory. It complements event logs by observing visual state changes that no job or browser receipt records, including native dialogs and unsaved documents.
- **path:** mac-vision → browser-extension → mac-planner → faculty-perception → relay-realtime
- **model tier:** Use local accessibility tree, window metadata, URL/title, and perceptual hashes to detect changes; use a cheap vision model only on changed regions. Realtime is unnecessary unless the owner asks a spoken follow-up.
- **latency:** Capture on return within 1 s; summarize a bounded changed-region set within 3 s.
- **cost:** Low if local-only hashes and accessibility metadata are used; occasional vision calls scale with changed regions, not full-screen frames.
- **security:** Keep baselines and diffs on the Mac; never upload unchanged screen regions. Mask password managers, private messages, payment fields, and browser secrets before any model call. Require explicit opt-in and a hard retention limit for screenshots.
- **missing:** A local baseline/diff ring keyed by app/window/tab identity with screenshot hash, accessibility digest, and capture time.; A return-to-owner trigger based on idle-to-active transition or a spoken request.; A redaction-aware changed-region vision endpoint and a spoken diff formatter.

### "Before you speak my private information aloud, tell me whether anyone else could be listening or seeing it right now, and stay silent unless I explicitly approve the disclosure."
- **useful because:** A wearable assistant can create a privacy failure in a meeting, phone call, shared room, or unlocked screen even when the underlying answer is correct. The owner should get a real-time disclosure boundary based on observed call state, active app, screen-sharing indicators, browser context, and the requested content—not a static quiet-hours setting.
- **path:** faculty-perception → mac-vision → browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Deterministic local signals first (active call/meeting app, screen-share indicator, focused window, speaker route); use the realtime model only to classify the sensitivity of the proposed utterance. No cloud upload of room audio.
- **latency:** Under 250 ms for a local risk decision; under 1 s for a spoken approval prompt.
- **cost:** Near-zero for local state checks; occasional low-latency model call for content sensitivity classification.
- **security:** The safety classifier must see only a redacted sensitivity label or structured fields where possible. Never infer that a microphone being present means a person is listening; report evidence and uncertainty. Default to silence for high-risk content and require a physical-button or explicit spoken approval.
- **missing:** A local exposure-observer that reports active call, screen-share, recording, and audio-route signals with freshness.; A sensitivity taxonomy shared by judgement and realtime speech, including names, credentials, health, financial, and private-message content.; A pendant/relay control frame that can cancel queued speech before PCM is sent.

### "When you remember something about me, show whether it came from me, from this Mac, from a browser page, or from an inference—and let me correct only the bad source without erasing the rest."
- **useful because:** The owner cannot safely trust a polished answer when machine-derived facts are projected as if they were his preferences. A provenance-aware memory view would expose stale or contradictory machine claims, preserve good memories, and make correction targeted rather than destructive.
- **path:** faculty-perception → faculty-judgement → mac-planner → browser-extension → relay-realtime
- **model tier:** Use deterministic provenance and confidence sorting first; a cheaper background model can cluster contradictions. Realtime is only for the owner's spoken correction.
- **latency:** Under 500 ms for a memory provenance card; under 2 s for conflict clustering.
- **cost:** Minimal local reads; occasional small text-model call for grouping semantically equivalent claims.
- **security:** Private memories stay on the Mac/relay store; show source class and locator rather than raw sensitive content by default. A correction must be an explicit owner action and must not silently rewrite historical evidence.
- **missing:** A provenance-preserving memory projection that cannot collapse machine and owner origins into one preference.; A targeted correction/retirement operation that records who corrected a fact and leaves a tombstone.; A cross-source contradiction reader connecting memory facts to current machine and browser observations.

### "After I approve an action, let me ask exactly what the system saw, believed, and changed at that moment—including the evidence it discarded—and replay the decision without repeating the action."
- **useful because:** Today a receipt can say that a Mac action ran without preserving the perceptual context that justified it. An owner needs an audit witness for consequential actions: not surveillance, but a compact, redacted record that distinguishes observed facts, model inferences, owner approval, and resulting state.
- **path:** faculty-perception → faculty-judgement → faculty-action → mac-vision → browser-extension → mac-planner → relay-realtime
- **model tier:** Capture deterministic structured state and hashes locally; use no model for replay. A slower text model may summarize the witness only when requested.
- **latency:** Record the witness inline without delaying reversible actions more than 100 ms; render a replay in under 2 s.
- **cost:** Low storage and CPU for structured fields/hashes; occasional summary-model cost only on owner request.
- **security:** Never store raw passwords, full screenshots, or page bodies by default. Encrypt the witness store, redact secrets before persistence, bind approval to an action nonce, and expire bodies while retaining compact hashes and decision metadata.
- **missing:** A durable decision-witness schema joining perception observations, judgement version/input, owner approval event, action nonce, receipts, and post-state.; A redaction-aware snapshot hook in mac-vision and browser-extension before action execution.; A read-only replay route that cannot dispatch the original action and clearly labels inferred versus observed fields.


## Changes it proposed to its own stack

### `mac-harness` — Add a local-only observation ledger that samples active-window identity, browser tab metadata, accessibility digest, and redacted screenshot perceptual hash on idle-to-active transitions; compute changed regions and expose a single spoken 'since you left' result with source timestamps. Do not upload baseline pixels, and retain at most 20 transitions for 12 hours.
- **owner gets:** On returning to the Mac, the owner immediately knows what changed—even native dialogs or unsaved documents that never produced a relay job or browser receipt—without manually reopening everything.
- effort: Medium: one observer loop, redaction and bounded ring storage, changed-region comparison, and a Mac route consumed by faculty-perception.  ·  risk: False positives from animations or video; mitigate by debouncing and excluding known dynamic regions. Sensitive pixels could leak if redaction fails; keep the first version local-only and provide a kill switch. Recovery is deleting the bounded ring and disabling capture.
- cost: No API cost for metadata and perceptual hashes; occasional local vision inference only for changed regions. Disk under roughly a few megabytes with the stated cap.  ·  latency: <1 s to capture a return baseline; 1-3 s to summarize changed regions.
- security: Positive if local-only by default; screenshots never leave the Mac, and password/payment/message regions must be masked before any optional vision call.
- depends on: The now-verified Accessibility and Screen Recording grants in /ops/status.; A new local observation-ledger route and redaction implementation; existing /observe and browser inspection routes provide the metadata inputs.


## What it asked for

_Nothing._
## Its own summary

Fresh discovery changed the boundary: the Mac is now genuinely perception-capable. /ops/status reports Accessibility and Screen Recording granted, computer-use vision enabled, browser bridge online, relay reachable and D1-backed; the live device list still contains no pendant. I recorded this as verified and proposed three owner-facing capabilities: pre-action target attestation (right account/tab/window/document), provenance-first contradiction reports across browser/Mac/relay, and a return-to-Mac visual change digest. I also proposed the concrete local-only observation ledger needed to make the latter real, with strict redaction and bounded retention. I notified the other agents that TCC permission requests must stop.

**Biggest unknown:** There is still no live pendant path to verify physical receipt or playback. On the Mac side, what remains is not permission: it is the missing connective contracts—fresh observation records, target-attestation IDs, cross-source freshness/conflict comparison, and an idle-to-active trigger for visual diffs. Privacy defaults for screen baselines (especially whether the owner opts into any model processing) also remain unspecified.

