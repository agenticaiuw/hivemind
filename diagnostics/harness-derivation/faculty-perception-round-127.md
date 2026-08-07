# Harness derivation — faculty-perception — round 127

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser perception boundary** — At 2026-08-07T18:24Z, home-macbook-bridge and Safari extension are online with 3 browser sessions (default Gmail plus two test forms), but AI Pendant Agent accessibility and screen recording are false; /observe reports synthesized UI events will not reach the screen. Relay is reachable and no pendant is registered.
  - evidence: GET /ops/status, GET /observe, GET /browser/status, and discover(devices) all returned these states in this round.

## Capabilities it proposed

### "“I’m back—what was I doing, and what should I do next?” (or press the pendant button twice)."
- **useful because:** This is the highest-value perception capability: after an interruption it reconstructs the owner's actual work from live evidence rather than guessing. The Mac contributes foreground app and recent action receipts, Safari contributes open private tabs and page state, the relay keeps the capsule while the Mac sleeps, and the pendant eventually provides the instant trigger and spoken answer. It should clearly separate observed facts, inferred intent, and unknowns, with links and a one-tap resume option.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model (GPT-4.1-mini or equivalent) builds/updates the capsule; realtime tier only handles the spoken request and reads the short result.
- **latency:** 5–10 seconds for a fresh capsule; under 1 second to answer from a capsule younger than 2 minutes. Current Mac-only prototype can be triggered from the relay/dashboard; pendant requires registration.
- **cost:** Roughly $0.01–$0.05 per refresh depending on page text and history; near-zero for cached reads. Dominant cost is summarizing changed page/app evidence, not the spoken turn.
- **security:** Private Gmail and other logged-in tab text must stay in the owner's relay/account boundary, with short TTL and explicit source URLs. Never capture passwords, full-screen pixels, or page text outside the active session. Resume actions must require confirmation. Accessibility/screen recording are currently false, so UI claims must be marked unavailable rather than fabricated.
- **missing:** A durable interruption capsule schema combining /observe, browser session/page state, and receipts; A relay endpoint to store and retrieve the latest capsule with TTL and provenance; Pendant registration and trigger delivery (currently no pendant is registered); Owner granting Accessibility and Screen Recording to the exact AI Pendant Agent binary if pixel/UI evidence is required

### "“Before I act, tell me what is actually true across my tabs, Mac, and recent jobs—and flag any contradictions.”"
- **useful because:** Perception should catch stale or conflicting reality before judgement/action: e.g. a calendar meeting moved while an open tab still shows the old time, a browser form changed after a job was queued, or a receipt says success while the page still shows failure. It returns an evidence table (source, observed time, exact excerpt/state, confidence) and stops downstream action when high-impact sources disagree. No single Mac, browser, or relay node can establish this reliably alone.
- **path:** relay-realtime → mac-planner → browser-extension → dashboard → pendant
- **model tier:** Cheap background model for extraction, normalization, and contradiction classification; realtime only summarizes the already-built evidence when asked.
- **latency:** Under 15 seconds for up to 6 active sources; cached sources answer in under 2 seconds. Never silently wait on an inaccessible source—report it as unknown.
- **cost:** About $0.02–$0.10 per check; page extraction and cross-source comparison dominate. Cached unchanged pages should cost pennies or less.
- **security:** Only inspect already-open authenticated tabs and explicitly permitted Mac sources. Store hashes/excerpts rather than entire pages, redact account identifiers, and retain evidence briefly. A contradiction is a warning, not an authorization to mutate anything.
- **missing:** Typed observation records with source URL/app, timestamp, field, excerpt/hash, and freshness; Cross-source field normalization (dates, amounts, statuses) and severity policy; A relay aggregation route that can request browser and Mac observations in parallel; A hard handoff so faculty-judgement receives 'blocked by contradiction' rather than a guessed value

### "“Why do you believe that?”—for any answer or proposed action, show me the shortest evidence chain and what could make it wrong."
- **useful because:** The system currently can observe Mac, private Safari, relay jobs, and historical audio, but those observations are easy to blend into an unjustified story. This gives the owner an on-demand audit of perception: each claim links to the live source, observation time, excerpt or structured state, transformations, and explicit unknowns/staleness. The pendant can speak a two-sentence explanation while the dashboard exposes the full chain. It makes the collective trustworthy without requiring the owner to inspect logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Cheap text model assembles and compresses already-collected typed evidence; no realtime reasoning unless the owner asks follow-up questions.
- **latency:** Under 3 seconds for cached evidence; under 12 seconds when it must re-read up to four open tabs and current Mac state.
- **cost:** $0.005–$0.04 per explanation; token cost is dominated by evidence excerpts. Hash-only or structured observations are nearly free.
- **security:** Do not expose secrets embedded in page text, cookies, or command output. Apply source-level sensitivity labels and redact before relay persistence. Explanations must be read-only; links to logged-in pages should be visible only on the owner's dashboard.
- **missing:** A claim/evidence graph with immutable observation IDs and transformation steps; A common API for faculty-perception to publish observations and faculty-judgement/action to cite them; Redaction and TTL enforcement before evidence leaves the Mac; A spoken follow-up protocol that can request one missing observation without rerunning the whole task

### "“Remember this exactly, but do not send it anywhere.” Then, when I ask later, find the exact moment and context—even if the pendant was offline when I said it."
- **useful because:** A genuinely personal memory primitive: the worn device can capture a short local audio/utterance with a monotonic timestamp, the Mac can later add the active meeting/app/tab context, and the relay can reconcile the record after reconnect. Today no node can preserve an owner instruction across an offline interval with verifiable ordering and exact context. The owner gets a trustworthy memory instead of a paraphrase that may have been lost during link failure.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** On-device buffering and hashing first; a cheap background model transcribes and links context after reconnection. Realtime is unnecessary unless the owner asks for it immediately.
- **latency:** Local acknowledgement under 200 ms; reconciliation within 30 seconds after the Mac/relay link returns; lookup under 3 seconds.
- **cost:** Low: a few cents per minute of audio for transcription, with most invocations using a short utterance. Storage is dominated by optional encrypted audio retention.
- **security:** The phrase must remain encrypted locally until the owner-approved sync policy allows upload. A physical button or explicit wake phrase should delimit capture. Never record continuously or infer other speakers without a visible/aural indicator; offer transcript-only deletion and cryptographic erasure.
- **missing:** An offline pendant capture queue with monotonic sequence numbers and authenticated replay protection; A reconnect reconciliation protocol joining pendant timestamps to Mac/browser observations without rewriting the original event; An owner-controlled encrypted memory vault with exact-audio versus transcript retention choices; A spoken retrieval command that returns provenance and uncertainty

### "“I’m in a private meeting now.” Make the whole hive go local-only until I say “private mode off,” and prove afterward that nothing left the device."
- **useful because:** The owner cannot safely use a cloud-connected collective in a confidential meeting today. This would coordinate pendant, Mac, browser, and relay: the pendant provides an unambiguous physical mode switch, the Mac blocks cloud uploads and pauses browser inspection, the relay rejects or quarantines incoming payloads, and a post-meeting report proves what was queued, discarded, or transmitted. This is an owner-visible safety boundary, not merely another permission setting.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic local policy enforcement; a cheap background model may summarize the audit after private mode ends. No realtime model is needed for enforcement.
- **latency:** Mode change must take effect within 300 ms locally and within 2 seconds across the relay/Mac; audit report within 10 seconds after exit.
- **cost:** Negligible model cost; the dominant cost is encrypted local queue storage if the owner chooses to retain observations for later processing.
- **security:** Fail closed if the relay cannot acknowledge the mode, and make the pendant LED/voice signal unmistakable. The relay must reject payloads rather than merely promise not to process them. Audit logs themselves may contain sensitive metadata, so encrypt them and keep them local by default. Emergency owner-approved calls must be a separate explicit override.
- **missing:** A signed privacy-mode state machine shared by pendant, Mac, browser extension, and relay; Relay ingress enforcement that cryptographically rejects uploads while private mode is active; Mac/browser hooks that stop observation and cloud-bound jobs, not just model calls; A tamper-evident local transmission ledger and post-session proof UI

### "“Turn the commitment I just made into a task, with the exact words, who it concerns, and a deadline—but do not contact anyone.”"
- **useful because:** The owner currently has to remember a spoken commitment, reconstruct it later, and manually connect it to calendar or reminders. This capability uses the pendant for an explicit utterance marker, the relay for a short local audio window, and the Mac for calendar/reminder context and a reviewable task. It preserves the exact source phrase and distinguishes an owner commitment from someone else's suggestion, preventing invented obligations.
- **path:** pendant → relay-realtime → mac-planner → dashboard
- **model tier:** Cheap background extraction/classification; realtime only acknowledges the capture. Any ambiguity in person, date, or obligation is surfaced for owner confirmation.
- **latency:** Acknowledge capture under 500 ms; draft task in under 10 seconds; never auto-submit messages or appointments.
- **cost:** A few cents per captured conversation snippet, dominated by transcription; negligible when the owner only marks text already in the live conversation.
- **security:** Capture only after an explicit button/phrase and indicate recording. Keep audio encrypted and short-lived, retain the exact transcript only with owner approval, and never infer or store third-party identities beyond what the owner confirms. Task creation is reversible; communications remain prohibited without confirmation.
- **missing:** A pendant-side utterance-marker and bounded pre/post-roll buffer; Relay support for encrypted, owner-scoped conversation clips with deletion and provenance; A commitment extractor that separates promises, requests, ideas, and quoted speech; A review card linking the exact words to proposed reminder/calendar fields


## Changes it proposed to its own stack

### `context` — Add a live, append-only perception ledger at the Mac/relay boundary. Every observation from /observe, browser inspections, job receipts, journal, and pipeline gets an observationId, source, timestamp, freshness deadline, sensitivity class, normalized claim, and redacted evidence hash. Expose a read-only claim query that returns supporting and conflicting observations; never let downstream planners consume an un-cited free-form fleet context.
- **owner gets:** The owner stops receiving confident answers built from stale browser tabs or historical pipeline data. They can ask “what do you know right now?” and get a sourced answer, while contradictions become visible before an action or spoken briefing.
- effort: Medium-high: schema, redaction, adapters for five existing routes, relay persistence/TTL, and planner integration; can ship Mac-only first while pendant is absent.  ·  risk: Ledger growth, accidental sensitive excerpts, and false conflicts from differing normalizations. Recover with hashes/short excerpts, per-source TTL, bounded retention, and a fallback that labels the claim unknown instead of blocking all work.
- cost: Low storage and API cost; roughly $0.01 or less per observation batch. Main engineering cost is adapter and redaction work, not model calls.  ·  latency: Adds <300 ms for cached structured reads; up to several seconds only when refreshing stale sources.
- security: Improves security if raw content never leaves the Mac and relay stores redacted excerpts/hashes. Requires explicit sensitivity policy and deletion propagation.
- depends on: A typed observation schema and redaction policy; Relay storage with per-observation TTL; A planner contract requiring citations for perception-derived claims


## What it asked for

_Nothing._
