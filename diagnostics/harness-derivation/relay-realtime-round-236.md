# Harness derivation — relay-realtime — round 236

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While I work in a selected Mac app, quietly watch the screen and whisper only actionable changes—like a build failure, a meeting starting, or a form error—and stop when I say “coach off.”"
- **useful because:** The owner gets an always-available second set of eyes without repeatedly asking what changed or sharing an entire desktop with a cloud service. The pendant is the private, low-friction output channel while the Mac supplies visual context.
- **path:** pendant → relay → mac-planner → mac-vision
- **model tier:** Use gpt-4.1-mini for frequent screenshot diffs and deterministic UI/error detection; invoke the realtime model only to turn a detected event into one short spoken sentence.
- **latency:** Screen-diff detection under 2 seconds; speech under 500 ms after a confirmed actionable change; no polling or speech when nothing changed.
- **cost:** Roughly $0.01–$0.05 per active hour depending on screenshot cadence and event density; most cost is vision frames, not realtime narration.
- **security:** The Mac must capture only the explicitly selected window/app and discard frames after comparison. Sensitive text could leave the Mac unless local OCR/redaction is added. Starting/stopping must be an explicit spoken command or button gesture; never monitor by default.
- **missing:** A Mac-vision loop that can subscribe to one window and emit semantic diffs (the current computer-use loop is disabled); A relay-side event throttle/deduplication stream that can send only actionable detections to the pendant; A local capture/redaction boundary and an owner-visible audit of which app was watched

### "Make me a temporary brief from these files and the authenticated pages I name, reconcile contradictions, and give me one spoken answer; keep the source bundle for 24 hours so I can ask follow-ups, then erase it."
- **useful because:** Today the Mac, browser session, and relay can each inspect sources, but the owner cannot ask for a bounded, coherent evidence packet spanning both without manually stitching results together. A short-lived bundle makes follow-up questions precise while limiting retention.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use a cheap background model for extraction, deduplication, and contradiction detection; use the realtime tier only for the owner’s final question and one-sentence spoken answer.
- **latency:** Acknowledge source collection immediately; first spoken synthesis within 10 seconds for up to 10 sources; follow-ups under 1 second from the retained bundle.
- **cost:** About $0.05–$0.30 per brief, dominated by document/page extraction and synthesis; follow-ups are cheap if the bundle is cached rather than re-read.
- **security:** Authenticated browser content and local files are high-sensitivity. The bundle needs per-source provenance, encryption at rest, a hard TTL, explicit source scoping, and no accidental injection of page instructions as commands. Never include full source text in spoken output unless requested.
- **missing:** A relay-owned ephemeral evidence-bundle store with TTL and deletion receipts; A cross-surface collector that can fetch Mac files and browser pages under one job and preserve provenance; A synthesis contract that distinguishes source facts, conflicts, and model inference

### "Watch me do this workflow once, turn it into a named command with the fields I should be asked for, and later run it from the pendant while checking that each step really succeeded."
- **useful because:** The owner repeatedly performs personal, multi-app sequences that are too specific for a generic command and too tedious to describe every time. Demonstration lets the Mac capture the real sequence; the pendant later supplies parameters and reports verified completion rather than merely claiming that clicks were sent.
- **path:** pendant → relay → mac-vision → mac-planner → browser-extension
- **model tier:** Use gpt-4.1-mini for action/DOM trace extraction and postcondition checks; use the background tier to normalize and version the playbook; reserve realtime for collecting the spoken name/parameters and reporting the result.
- **latency:** Recording adds no more than 100 ms to each observed action; replay begins within 2 seconds of the owner’s utterance; each step gets a bounded 3-second verification window.
- **cost:** About $0.02–$0.15 per replay, mainly screenshot/DOM verification; one-time playbook extraction costs under $0.50 for a typical 20-step demonstration.
- **security:** A demonstration may contain passwords, tokens, or destructive actions. Store selectors and parameter schemas rather than captured secrets, mark destructive steps, and provide a reviewable trace before publishing a playbook. Browser sessions remain on the owner’s Mac; do not upload raw screen recordings.
- **missing:** A Mac recorder that correlates UI actions, DOM changes, and resulting postconditions into a parameterized playbook; Versioned playbook storage with secret-field exclusion and migration when an app UI changes; A replay engine that pauses on failed postconditions and sends a concise needs-attention event to the pendant


## Changes it proposed to its own stack

### `relay` — Add a durable handoff inbox/outbox on the relay for post-session delivery, with explicit receipts. When a background job reaches a terminal state, the relay posts a typed notification into the owner’s delivery inbox; the pendant/phone pulls it with retry and acknowledges receipt. The relay keeps it until acknowledged or expired.
- **owner gets:** They stop babysitting tasks. The system can reliably deliver outcomes after the conversation ends, even across connectivity gaps.
- effort: Medium to high: needs new relay routes, storage, and a delivery protocol; also needs pendant/phone consumers.  ·  risk: Duplicate or missing notifications. Mitigate with idempotent message IDs, receipts, and expiry. If the pendant is offline, messages wait; if delivery fails, retries back off.
- cost: Low runtime per message; storage cost scales with undelivered notifications. Development cost is the bigger piece.  ·  latency: Adds minimal overhead to job completion; delivery happens when the pendant is reachable.
- security: Notification content may reveal sensitive activity; store minimal text and require confirmation for high-risk actions.
- depends on: Implement delivery endpoints on relay; Client support on pendant/phone to fetch and acknowledge notifications

### `integration` — Define a typed cross-surface event schema for job lifecycle and user-visible notifications, shared by relay, Mac, and pendant. Include fields for severity, redaction level, correlation IDs, and delivery targets. Replace ad-hoc strings with the schema so each node can safely transform and present messages.
- **owner gets:** Owners get consistent, understandable messages across devices. It reduces confusing mismatches like “queued” on one surface and “done” on another.
- effort: Medium: schema design, adapters in relay and Mac, and validation. Lower than building features twice.  ·  risk: Schema drift between components. Mitigate with versioning and validation.
- cost: Low per event. Most cost is implementation and testing.  ·  latency: Negligible.
- security: Schema-enforced redaction prevents accidental leakage of sensitive details.


## What it asked for

_Nothing._
