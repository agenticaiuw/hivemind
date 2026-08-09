# Harness derivation — faculty-perception — round 163

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility and screen recording live status** — The exact AI Pendant Agent binary is now verified ready: Accessibility trusted, Screen Recording true, input reachability verified, secure input false, automation missing none. The prior TCC blocker is resolved.
  - evidence: GET /observe at 2026-08-08T02:50:35.857Z reports accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, and uiActionsWillReachTheScreen=true; GET /ops/status reports permissions.ready=true.

## Capabilities it proposed

### "“What changed across my Mac, browser, relay work, and wearable since I last looked—only tell me changes that are real, and separate observed facts from unknowns?”"
- **useful because:** The existing catch-up feed is best-effort and mixes count-capped histories with delivery claims. This would produce a perception-first delta: foreground/app and permission changes from the Mac, tab/session changes from the browser, job/pipeline transitions from relay and Mac, and an explicit 'pendant unavailable' boundary instead of silently treating missing data as zero. It answers the owner's most important absence question without pretending completion means hearing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Use a cheap background model to summarize a deterministic snapshot/diff; reserve realtime for speaking the short result. No model should infer a success that the snapshot does not evidence.
- **latency:** Capture all read-only sources in under 2 seconds; speak a 2–3 sentence delta in under 1 second after the snapshot. A baseline must be stored locally with a bounded TTL and explicit observedAt times.
- **cost:** About $0.001–$0.01 per invocation depending on whether summarization is needed; most invocations are deterministic and incur no model call.
- **security:** The result can expose tab titles, foreground apps, job labels, and permission state. Keep it local by default, redact URLs/query strings and page text, and require confirmation before exposing private browser details over any remote voice path. Never convert absence of a pendant row into 'offline' without the registry caveat.
- **missing:** A durable, authenticated baseline/diff endpoint with source timestamps and per-field provenance; A pendant-originated liveness frame when the pendant exists; offline-reality-beacon is accepted firmware work but no device is registered today; A policy for which browser/app metadata the owner considers safe to speak aloud

### "“Before you act on something you read online, tell me whether the page is still the same page you read—and stop if it changed.”"
- **useful because:** A stale webpage is a perception failure that can cause the Mac or browser agent to send the wrong message, buy the wrong item, or edit the wrong record. This capability turns a reading into a verifiable observation: compare a content hash and capsule captured during reading with a fresh browser inspection immediately before mutation, report the exact drift, and require the owner to re-approve when the evidence no longer matches.
- **path:** relay-realtime → browser-extension → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** No expensive model for comparison: hash/capsule matching and locator checks are deterministic. Use a cheap model only to explain a small diff; realtime only speaks the concise warning.
- **latency:** Fresh inspection and comparison under 1.5 seconds for ordinary pages; if inspection is unavailable, fail closed and say evidence is stale rather than guessing.
- **cost:** Near-zero model cost for unchanged pages; roughly $0.001–$0.01 only when a textual diff needs explanation. Browser rendering and inspection latency dominate.
- **security:** Never persist or speak full private page bodies. Reuse the existing redaction and evidence-capsule rules, retain only hashes, locator, sensitivity classification, and a short redacted diff. A mismatch must block mutation until confirmation; a matching hash is evidence of content identity, not authorization to act.
- **missing:** Relay read_web_page must return a stable content hash/correlation ID, and the Mac must mint the existing evidence capsule for that read; A browser inspection API that can recapture the same locator and return a comparable redacted hash; An action-layer precondition that accepts an evidence capsule ID and refuses stale mutations

### "“If one part of you says an action is done but another surface still shows the old state, tell me plainly which claim is unverified.”"
- **useful because:** Today completion can mean a Mac-side execution receipt while browser state, relay state, or device playback remains unknown. A cross-surface contradiction detector would catch silent failures—wrong tab, stale session, interrupted relay work, permission loss, or an unplayed response—before the owner relies on them. It reports evidence per surface and never resolves disagreement by optimism.
- **path:** relay-realtime → mac-planner → browser-extension → mac-vision → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic rule engine for correlation, freshness, and state contradictions; a low-cost background model can turn a contradiction into plain language. Realtime only delivers urgent contradictions.
- **latency:** Evaluate after each job receipt or browser result within 2 seconds; urgent contradictions should be spoken in the next available turn, otherwise appear in the dashboard.
- **cost:** Usually no model cost; under $0.005 for occasional language rendering. Cost is dominated by read-only state probes and storing compact evidence references.
- **security:** Contradiction records may reveal private app/tab names and action targets. Store hashes, labels, timestamps, and redacted snippets rather than page bodies; enforce the existing bearer scopes and never let this read-only detector perform a repair. The detector must distinguish 'not observed' from 'false' and show freshness bounds.
- **missing:** A common correlation contract linking relay job IDs, Mac action receipts, browser command IDs, sessions, and evidence capsules; Fresh postcondition readers for important actions (current browser/app state, not only executor receipts); A monotonic contradiction ledger with expiry and explicit unknown states

### "“What could you not know about me today, and exactly what would have made it knowable?”"
- **useful because:** The owner should never mistake silence for safety or completion for success. This capability would generate a bounded, evidence-linked blind-spot report: unavailable pendant telemetry, stale or count-capped histories, inaccessible browser content, missing playback confirmation, expired relay records, and permission or freshness gaps. For each unknown it names the concrete missing observation and whether the owner can fix it, rather than inventing an answer. This is a different product from a catch-up digest: it reports the shape of ignorance itself.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Deterministic inventory and freshness rules should produce the facts; a cheap background model may compress them into a short spoken report. Realtime is only needed to interrupt when a requested conclusion is unknowable.
- **latency:** Under 3 seconds for a current blind-spot report, with every item carrying observedAt, source, retention bound, and required next observation. No report should be generated from stale data without saying so.
- **cost:** Usually below $0.005 because most output is structured rule evaluation; occasional summarization may cost $0.001–$0.01. The dominant cost is bounded cross-surface reads, not inference.
- **security:** A blind-spot report can reveal sensitive tab existence, app use, device absence, and retention policy. Speak only categories by default; require explicit confirmation for names, URLs, or private application details. Never treat an unavailable source as evidence of a negative event.
- **missing:** A signed, versioned observability contract for every surface that declares what it can observe, its freshness, retention, and failure semantics; A durable observation ledger that records both positive observations and explicit unknowns without retaining private content; Owner-configurable sensitivity rules for which blind spots may be spoken aloud and which require a dashboard view; A physical pendant telemetry and playback channel that can turn current 'unknown' delivery and hearing claims into device-originated facts

### "“Show me exactly what information left my Mac, browser, or wearable today, where it went, and what was withheld.”"
- **useful because:** The owner cannot currently audit the system's own perception boundary. Browser reads, relay prompts, audio captures, screenshots, and action metadata cross surfaces with different retention and provenance rules. A compact outbound-observation ledger would make privacy legible: destination, timestamp, source surface, redaction classification, content hash, byte/character count, and whether the owner approved it—without retaining the sensitive body itself.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception
- **model tier:** Deterministic event capture and redaction accounting; a cheap background model can group events into plain language. Realtime only answers a live privacy query.
- **latency:** Append a bounded ledger record synchronously or within 100 ms of each cross-surface transfer; answer a day's audit in under 2 seconds. If logging fails, mark the transfer unaccounted rather than claiming zero.
- **cost:** Negligible inference cost; bounded local storage and hashing dominate. A summarized audit should usually cost under $0.005.
- **security:** The ledger itself is sensitive. Keep bodies out, hash after redaction, encrypt at rest, cap retention, and expose only destination classes by default. It must cover failed and blocked transfers as well as successful ones, and distinguish owner-approved from implicit system traffic.
- **missing:** A cross-surface egress event protocol emitted by relay, Mac, browser bridge, and pendant for every prompt, page read, screenshot, audio, and action payload; A tamper-evident local ledger with per-event redaction classification and destination identity; A policy engine that attaches the owner's approval or purpose to each transfer and can fail closed when classification is unknown

### "“For any answer or action, show me the exact world-state you perceived at that moment—not the current page—and explain which observations were missing.”"
- **useful because:** When the world changes, today's logs cannot tell the owner whether the system acted on a stale tab, an old relay state, or an incomplete sensor view. A perception time capsule would freeze the structured observations that informed each decision, with content-addressed hashes, timestamps, locator/tab identity, model-input boundaries, and explicit unknowns. The owner could audit a surprising answer or recover context without exposing raw private bodies by default.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement
- **model tier:** Capture and hash structured observations deterministically at decision time. Use a cheap background model only for an owner-readable explanation of the capsule; realtime is unnecessary unless the owner asks during a live turn.
- **latency:** Capsule creation must add under 150 ms to a read/action path and never block an urgent action; body capture can be asynchronous, but the immutable metadata and hash must precede the action. Retrieval under 1 second for a recent capsule.
- **cost:** Near-zero model cost; bounded encrypted local storage is the main cost. Explanations may cost $0.001–$0.01 each.
- **security:** Capsules may contain extremely sensitive screen, browser, or audio context. Redact before hashing/storage, encrypt, enforce short body TTL with longer metadata tombstones, support immediate revocation, and require confirmation before rendering raw content. The capsule must preserve what was withheld, not only what was captured.
- **missing:** A universal decision-context envelope linking model turn, action/job, browser command, relay request, and device sequence; Capture hooks on relay voice reads and pendant audio, not just Mac browser evidence; A tamper-evident append-only index with owner-visible revocation and retention controls


## Changes it proposed to its own stack

### `context` — Repair the granted read_continuity_snapshot resolver so it resolves to the authenticated GET /ops/snapshot plus GET /pipeline implementation it was designed for, with its include enum and maxItems bounds preserved. On failure, return a typed partial snapshot rather than an unresolved-tool error.
- **owner gets:** The owner currently cannot ask one mind what happened while away: the granted continuity tool fails resolution even though /ops/snapshot, /pipeline, browser, relay, and permission data are live. Fixing this makes the system able to state what it actually knows instead of silently falling back to guesses or forcing a model to scrape multiple routes.
- effort: Small resolver/manifest change plus contract tests for each include branch and partial-source failure. Verify against the live bearer-authenticated Mac agent.  ·  risk: A resolver could accidentally expose more fields than intended or label stale data as current. Enforce source timestamps, redact page content and tokens, cap records, and mark unavailable sources unknown. Roll back to the current direct routes if contract tests fail.
- cost: Negligible API cost; one bounded snapshot replaces several separate probes and may reduce context tokens.  ·  latency: Should be faster than multiple model-driven probes; target under 500 ms locally and bounded relay timeout.
- security: Read-only bearer-authenticated access only. Preserve existing scopes and do not include raw authorization, URL query secrets, or page bodies in the snapshot.
- depends on: A stable route mapping for /ops/snapshot and /pipeline in the capability resolver; A tested response schema distinguishing observedAt, freshness, unknown, and absent

### `context` — Make every faculty judgement and faculty action consume a signed Perception Context Envelope: immutable observation IDs, per-source observedAt/freshness, redaction class, content hashes, explicit unknowns, and the retention/permission basis. Persist only the bounded envelope and revocation tombstones; never require raw page/audio bodies to prove what was seen.
- **owner gets:** The owner would finally be able to ask “why did you believe that?” and receive the exact evidence boundary and unknowns that existed before an action, even after the current page or device state changes. It prevents a later snapshot from being mistaken for the perception that caused an earlier decision.
- effort: Large cross-stack protocol work: define the envelope, instrument relay voice/browser reads, Mac planner/vision/browser, and eventual pendant telemetry, then require action receipts to reference it. Existing Mac evidence capsule fields can seed the schema but do not cover relay or device observations.  ·  risk: Instrumentation overhead, sensitive metadata leakage, and failures that could incorrectly block actions. Start in audit-only mode, enforce size/TTL limits, and degrade to an explicit ungrounded action rather than fabricating context. Roll back by disabling enforcement while retaining captured envelopes.
- cost: Small hashing/storage cost per event; no required model cost. Context envelopes can reduce repeated raw context and therefore lower token spend.  ·  latency: Target under 150 ms metadata capture on the critical path; body capture asynchronous. Initial rollout may add latency until hooks are optimized.
- security: Improves accountability but creates a high-value metadata store. Encrypt at rest, bind records to capability scopes, redact URLs/secrets, support revocation, and make owner-visible audit access explicit.
- depends on: Stable cross-surface event IDs and clock/freshness semantics; Relay provenance transport for read_web_page and voice turns; Device-originated telemetry when a pendant is connected; A policy defining which observations may be retained versus represented only as a hash


## What it asked for

_Nothing._
## Its own summary

Established live facts this round: the exact AI Pendant Agent binary now has Accessibility and Screen Recording granted; /observe reports inputReachability=verified, secureInput=false, and /ops/status reports permissions.ready=true. Mac bridge and Safari browser extension are online, while no pendant is registered. The granted read_continuity_snapshot tool is not actually resolvable (its nearest live route is GET /ops/snapshot), although direct authenticated /ops/snapshot works. I recorded this finding, notified peers, and proposed four owner-facing improvements: evidence-bounded cross-surface absence deltas, stale-page precondition checks, contradiction detection across completion claims, and repairing the continuity snapshot resolver.

**Biggest unknown:** The system still cannot produce a single reliable, callable cross-surface continuity read: the implementation routes exist, but the granted tool mapping is broken. Until that is fixed, freshness and source-specific unknowns must be assembled manually. A physical pendant's liveness and playback remain unknowable because no pendant is registered and no device playback emitter exists.

