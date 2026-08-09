# Harness derivation — faculty-perception — round 213

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser reachability** — At 2026-08-09T00:12Z the authenticated Mac agent reports Accessibility and Screen Recording granted, permissions.ready=true, browser extension online with two Safari tabs and zero pending commands; relay reachable with D1 store and mac bridge online. No pendant appears in the live snapshot.
  - evidence: read_continuity_snapshot(include relay,pipeline) invoked GET /ops/snapshot HTTP 200; body status.permissions and browser/relay fields.

## Capabilities it proposed

### "Tell me what is on my screen and what I can safely do next, then carry out the one option I choose."
- **useful because:** This is the first genuinely reliable hands-free computer interaction: the pendant supplies intent and confirmation, the Mac vision loop sees the actual screen, the browser bridge supplies session-aware DOM facts, and the relay preserves the turn if the Mac is briefly busy. It turns 'I am stuck' into a grounded answer rather than a guessed UI description.
- **path:** pendant → relay-realtime → mac-vision → browser-extension → mac-planner
- **model tier:** Realtime for the short spoken scene and confirmation; cheaper background model for OCR/DOM normalization and post-action verification.
- **latency:** 2-4 seconds for the initial scene; under 2 seconds after a choice; up to 8 seconds for a complex app.
- **cost:** About $0.01-$0.05 per interaction depending on screenshots and realtime audio; screenshots/vision dominate.
- **security:** Screen pixels and browser text leave the Mac only when explicitly needed for the turn; mask passwords and payment fields; require spoken confirmation before irreversible actions. Current Mac permissions are ready, but screen capture must still be visibly indicated.
- **missing:** A single scene contract joining screenshot, focused app, browser tab, and proposed reversible actions with timestamps; A relay-side short-lived scene reference so the spoken confirmation cannot apply to a stale screen; A policy gate that blocks destructive actions even when Accessibility is available

### "Mark this exact moment in the video, explain why I marked it, and remind me later with a link that opens at the same timestamp."
- **useful because:** A spoken bookmark preserves the owner's fleeting insight instead of a generic URL. The browser knows the authenticated tab and playback position, the pendant supplies the natural-language reason, the Mac stores verifiable provenance, and the relay can deliver the reminder when the browser is no longer open.
- **path:** pendant → browser-extension → mac-planner → relay-realtime
- **model tier:** Realtime only for capture confirmation; a small background model extracts a 1-2 sentence reason and tags the moment.
- **latency:** Under 1 second to capture URL/title/time; under 5 seconds to produce the spoken confirmation; reminder delivery is asynchronous.
- **cost:** Under $0.01 per bookmark; model summarization is the dominant cost, and it can be skipped for a literal note.
- **security:** Do not copy video frames or private page text unless requested; store URL, media timestamp, tab pseudonym, and owner note with expiry; require confirmation before sharing a bookmark externally.
- **missing:** A browser-extension result schema exposing media currentTime and a stable media identity, not merely tab URL; A Mac route that mints a timestamped evidence capsule and reminder payload atomically; A relay reminder payload that preserves the timestamp and opens the browser bridge session safely

### "Read the form I am looking at, tell me exactly what will be submitted, and let me approve only the safe fields before you send it."
- **useful because:** The owner gets a trustworthy voice-controlled form assistant for applications, purchases, and messages: it separates what is visible from what will actually be submitted, catches hidden or prefilled fields, and makes approval granular instead of a dangerous all-or-nothing click.
- **path:** pendant → browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** Realtime for the spoken field-by-field summary and approval; a cheaper structured extractor compares DOM values with the rendered screenshot; deterministic policy code decides whether submission is allowed.
- **latency:** 3 seconds to inventory a form, 1 second per approval response, and under 3 seconds for the final submit plus verification.
- **cost:** $0.02-$0.10 per form, dominated by one vision pass; deterministic field diffing is negligible.
- **security:** Never transmit passwords, payment numbers, health data, or one-time codes to the model; redact them before extraction. Submission requires an explicit spoken confirmation tied to a hash of the exact field set, URL, and tab, and a changed page invalidates approval.
- **missing:** A DOM-plus-screenshot field inventory with sensitivity classification and stable field hashes; A consent token bound to the browser tab, form hash, and approved field set, expiring after navigation or mutation; A post-submit receipt that records what changed without retaining secret values

### "If I dictate a message while I am upset, warn me about what it could do, offer a calmer rewrite, and hold it until I explicitly approve sending."
- **useful because:** The owner gets a protective pause at the exact moment impulsive messages cause real damage. The pendant hears urgency and gives the owner a private escape hatch; the Mac/browser can inspect the actual recipient and message; the relay preserves the draft if the Mac or network drops. This is not a generic confirmation: it recognizes when the owner's state and the message's consequences call for a pause.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** Realtime only for the brief spoken warning and rewrite; a cheaper structured model classifies message risk and extracts recipient/action facts. Deterministic policy code owns the hold/release decision.
- **latency:** Under 2 seconds after dictation ends for a warning; under 5 seconds for alternatives; sending remains blocked until explicit approval.
- **cost:** Roughly $0.01-$0.05 per held message, dominated by speech and one text classification; drafts and policy checks are cheap.
- **security:** Emotion inference is sensitive and must remain local by default; do not retain raw audio or expose a mental-health label. Never silently rewrite or delay ordinary messages. The approval must bind to recipient, channel, exact final text, and a short expiry; payment, legal, employment, and public-post destinations require a stricter confirmation.
- **missing:** A local, transparent urgency/risk signal that reports observable cues rather than diagnosing the owner; A cross-surface outbox hold primitive that prevents the browser or app from sending until release; A final-content hash and recipient-bound approval token, with an undo window and durable receipt

### "Before I paste or send anything, tell me whether it contains a secret or personal detail that does not belong in this destination, and block it unless I approve the exact exposure."
- **useful because:** The owner gets a practical privacy boundary across authenticated browser sessions and Mac apps, where accidental pastes and replies are currently irreversible. It protects API keys, addresses, private messages, and health or financial details without requiring the owner to remember which app is trustworthy.
- **path:** pendant → browser-extension → mac-vision → mac-planner → relay-realtime
- **model tier:** Local deterministic scanners and destination policy handle common secrets; a small background classifier handles ambiguous personal data. Realtime only speaks the concise warning and approval request.
- **latency:** Under 300 ms for known-secret detection; under 2 seconds for an ambiguous-content warning; no network round trip for the initial block.
- **cost:** Near-zero for regex/policy checks; under $0.01 for an ambiguous classification, with the dominant cost being local OCR if the destination is visual-only.
- **security:** The scanner must not upload the very content it protects. Keep classification local, hash rather than retain blocked payloads, make false positives dismissible, and never let a relay or model bypass an owner block. Approval must bind to the exact destination origin, recipient, and content hash.
- **missing:** A Mac/browser interception layer for clipboard, typing, and submit events that can synchronously veto an action; A local redaction/classification engine with destination-aware policy and explainable matches; A short-lived approval token shared by the browser extension and Mac action executor

### "Give me one private phrase or button that immediately freezes every pending action, cancels anything not yet submitted, and tells me exactly what was stopped."
- **useful because:** When the owner realizes an instruction was misunderstood, one deterministic emergency stop is safer than finding the right app, tab, or job. The pendant can trigger it even while the Mac is locked; the relay can fan it out; the browser and Mac can cancel their own pending work and report the remainder honestly.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision
- **model tier:** No expensive model is needed for the stop itself. Realtime may summarize the stopped items afterward; deterministic cancellation and authorization must run independently of model availability.
- **latency:** Local pendant latch under 100 ms; relay propagation under 1 second when connected; every surface reports its stop state within 3 seconds. Offline devices retain the stop until an explicit owner reset.
- **cost:** Negligible per invocation; durable event fan-out and bounded cancellation ledgers dominate engineering cost, not API calls.
- **security:** The phrase must be locally recognized or button-triggered, rate-limited, and resistant to accidental activation. It must not erase evidence needed for recovery. Reset requires a second deliberate confirmation and should not resurrect an action whose destination already accepted it.
- **missing:** A shared emergency-stop epoch understood by relay, Mac jobs, browser commands, and pendant firmware; Cancellation hooks that distinguish queued, executing, submitted, and irreversible work and return per-item results; A pendant-local latch and reconnect replay protocol so the stop survives offline periods


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the Mac agent is now fully interaction-ready (Accessibility, Screen Recording, automation all granted), Safari's browser bridge is online with two tabs and no pending work, the relay is reachable on durable D1, and there is still no pendant. Recorded this finding and broadcast it. Proposed three owner-facing capabilities: grounded spoken screen-to-action guidance, voice-indexed exact video bookmarks, and field-level consent for browser forms. The first is the highest-value immediate capability because it combines the newly granted Mac vision reach with browser session state and pendant/relay confirmation; the latter two need new cross-surface contracts rather than new storage schemas.

**Biggest unknown:** The browser inventory does not yet expose whether the active YouTube tab reports media currentTime or structured form fields, and the pendant remains physically absent/unregistered. I still need a live probe or implementation of those two bridges before claiming either workflow works end to end.

