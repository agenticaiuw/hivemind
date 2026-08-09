# Harness derivation — faculty-action — round 218

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **granted action verification and audio probes** — Both granted schemas remain non-callable in the live inventory. verify_operation_step is unresolved (nearest GET /workbench/contexts/:contextId, POST /browser/provenance/:recordId/check, GET /journal); audio_path_probe is unresolved and a call returned no implementation. Therefore I cannot honestly claim independent postcondition verification or fresh 24 kHz measurement from these tools.
  - evidence: describe(verify_operation_step), describe(audio_path_probe), and audio_path_probe(mode=capabilities) on Round 218

## Capabilities it proposed

### "“Do this browser transaction, but show me exactly what will happen first; I’ll approve it on the pendant, then tell me whether it definitely completed.”"
- **useful because:** This is the system’s most important end-to-end action: judgement can prepare a browser form, the browser can submit within its authenticated session, the pendant provides physical consent without receiving secrets, and perception independently verifies the postcondition. It turns a dangerous ‘agent did it’ into a bounded, truthful transaction.
- **path:** unified → faculty-judgement → mac-planner → browser-extension → faculty-action → faculty-perception → relay-realtime
- **model tier:** Realtime only for the short approval conversation; use the cheaper planner/action tier for preparation and execution, with deterministic verification afterward.
- **latency:** Preflight under 5 s; after the physical approval, submission under 10 s; verification within 3 s. If verification is unavailable, stop at unknown rather than claiming success.
- **cost:** Usually 1 planner call plus 1–3 cheap browser/action calls and one verifier call; expensive realtime usage is limited to the owner’s approval exchange.
- **security:** The pendant receives only an opaque transaction summary, digest, expiry, and nonce—not page contents, credentials, or form secrets. Require physical_transaction_approval_latch for irreversible actions. Never retry a non-idempotent submit after an unknown result; preserve the receipt and ask the owner.
- **missing:** A first-class transaction envelope shared by plan, browser execution, pendant approval, and verifier; A standard idempotency/retry policy per action risk class; Owner policy data for which transaction classes may be staged versus require approval

### "“When I tap the bookmark button during a call, save what I was hearing and what my Mac was showing, so later I can ask ‘take me back to that moment.’”"
- **useful because:** A bookmark currently risks being only a timestamp or audio artifact. Joining the pendant’s exact physical moment with the relay audio cursor and a read-only Mac/browser snapshot makes it a useful, searchable interruption marker: the owner can resume a thought, document, or conversation instead of merely knowing when they pressed a button.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → unified
- **model tier:** Cheap background indexing and deterministic correlation; realtime only when the owner later asks a natural-language question about the bookmark.
- **latency:** Record the bookmark locally in under 100 ms; capture Mac/browser state within 1 s; make it searchable within 5 s after connectivity returns.
- **cost:** One small event plus bounded metadata per bookmark; indexing can be batched and uses a cheap model only when needed.
- **security:** Store a digest and minimal locator by default, not screen pixels or full page text. Mark private/secret sources and require explicit owner request before revealing them. If the link is down, preserve the typed bookmark event in the existing OUTBOX and never duplicate it on retry.
- **missing:** A typed bookmark envelope that joins pendant monotonic time, relay audio artifact/cursor, and Mac/browser observation IDs; A correlation endpoint that resolves those IDs into a permission-filtered resume view; Firmware integration of the existing sw1 bookmark with a durable event ID if the current implementation does not already expose one

### "“Don’t interrupt me while I’m moving or presenting; queue only the alerts I need, then give me a compact catch-up when I’m free.”"
- **useful because:** A wearable that blindly speaks or vibrates at every event is not useful in real life. The pendant’s IMU, the Mac’s foreground/browser state, quiet hours, and relay-delivered alert inbox can jointly infer ‘safe to interrupt’ versus ‘queue,’ while retaining urgent alerts and explaining what was deferred.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-perception → unified
- **model tier:** Deterministic local motion classifier and policy router first; cheap background summarization for the deferred digest; realtime only for an urgent alert conversation.
- **latency:** Local motion/gesture decision under 100 ms; alert routing under 1 s; catch-up digest within 5 s when requested.
- **cost:** Near-zero inference for local features; occasional cheap summarization of queued notifications. No expensive model needed for routine gating.
- **security:** Do not infer sensitive activities from raw IMU beyond coarse states (walking, stationary, deliberate interaction). Keep raw motion local and transmit only state plus confidence. Emergency/owner-defined priority alerts bypass the gate. Never silently discard; queue with expiry and source provenance.
- **missing:** Motion-context safety gate (the pending request) integrated with IMU hardware; A shared interrupt policy schema spanning pendant, relay, Mac focus, and browser sessions; A bounded alert coalescer that preserves source IDs and supports owner-defined urgent classes

### "“Fill this password or payment field for me, but never show the secret to the agent; tell me the exact site, account, and fields first, then let me approve it on the pendant.”"
- **useful because:** The browser can hold credentials the Mac agent and relay should never receive. This gives the owner useful authenticated web automation without turning the AI into a password exfiltration path, and makes domain/field mistakes visible before submission.
- **path:** browser-extension → mac-planner → faculty-judgement → faculty-action → faculty-perception → relay-realtime → pendant
- **model tier:** Cheap deterministic browser inspection and policy checks; realtime only to explain the proposed fill and collect the owner’s approval.
- **latency:** Inspect and present the target in under 3 seconds; fill after approval in under 2 seconds; verify that only the intended fields changed within 2 seconds.
- **cost:** A few browser inspection/result calls per use; no large-model call is needed after the initial explanation.
- **security:** The extension performs the fill locally; plaintext secrets never enter relay, planner, pendant, logs, receipts, or model context. Require exact origin, frame, field labels, and account identity; refuse redirects, lookalike domains, unknown fields, and password export. Payment submission remains a separate explicitly approved step.
- **missing:** A browser-native secret-fill primitive that returns only field metadata and a redacted result; Origin/frame binding and anti-redirect checks in the browser bridge; A policy store for allowed credential/payment domains and account labels; A read-only post-fill verifier that can prove field names changed without exposing values

### "“Before you act in a browser, prove that this is the tab and account I intended—not merely the URL—and stop if the page, login, or account changes while you work.”"
- **useful because:** A URL alone is not identity: redirects, multiple accounts, embedded frames, and stale sessions can make a correct-looking action land in the wrong place. This capability would make browser automation fail closed on identity drift instead of silently operating on the wrong account.
- **path:** browser-extension → mac-planner → faculty-perception → faculty-action → faculty-judgement → relay-realtime
- **model tier:** Deterministic provenance and policy checks; use a cheap model only to turn the owner’s natural-language target into structured account/site constraints.
- **latency:** Bind and attest the tab in under 1 second; re-check before each consequential action in under 500 ms; abort immediately on drift.
- **cost:** Small metadata-only browser calls, with occasional cheap parsing; no realtime model required for routine checks.
- **security:** Return origin, tab/session ID, account label, and authentication state as minimally as possible; never expose cookies, tokens, or page secrets. Treat an unknown account or cross-origin frame as a hard stop, not a guess.
- **missing:** Signed browser provenance assertions binding session, tab, top-level origin, frame origin, account identity, and observation time; A browser-bridge precondition hook that runs immediately before action execution; Account identity discovery that does not reveal credentials; A policy language for owner-approved site/account pairs

### "“Watch this browser page until the condition I described becomes true, then bring me a dated proof and ask before doing anything consequential.”"
- **useful because:** The owner cannot keep a tab open and repeatedly check a price, appointment slot, delivery status, or application state. The always-awake relay can monitor while the browser retains the authenticated session, but the system must present fresh evidence and never turn a watch request into permission to act.
- **path:** relay-realtime → browser-extension → mac-planner → faculty-perception → faculty-judgement → faculty-action → pendant
- **model tier:** Cheap scheduled polling and deterministic condition evaluation; use a background model only to interpret an ambiguous condition, and realtime only when notifying the owner.
- **latency:** Polling cadence chosen per site and rate limit (typically 1–15 minutes); notify within one cadence after the condition; no action without a new approval.
- **cost:** Low recurring browser/relay traffic; occasional cheap interpretation. Cost scales with watch duration and polling frequency, not conversation length.
- **security:** Store only the minimum locator and condition digest, not continuous page copies. Bind the watch to a specific origin/session and expire it. Respect robots/rate limits, stop after repeated failures, and treat evidence older than the cadence as unknown. A condition match is not authorization to purchase, send, or modify.
- **missing:** Durable watch jobs with expiry, backoff, rate limits, and cancellation; A condition evaluator over typed browser observations with provenance; A relay-to-pendant notification path that distinguishes match, stale, error, and expired; A fresh physical approval transaction if the owner later requests an action

### "“Move this exact document from my Mac into that web form, but show me the filename, size, hash, destination, and whether the upload really completed—without giving the document to the AI.”"
- **useful because:** Uploading the wrong version to the wrong destination is a common, costly failure. The Mac can select bytes locally and the browser can submit them, while the model sees only metadata and the owner gets a verifiable result rather than a vague ‘uploaded.’
- **path:** mac-terminal → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception → pendant
- **model tier:** Deterministic file hashing, destination binding, and upload; cheap language parsing for the owner’s reference to a document or form.
- **latency:** Hash and preflight under 3 s for ordinary files; upload follows site speed; verify within 3 s of browser completion.
- **cost:** Local hashing plus browser calls; no document bytes need enter model context, keeping inference cost and privacy exposure low.
- **security:** The model receives filename, size, type, hash, and destination metadata only. Require explicit approval for external upload, enforce allowed paths and origin binding, prevent silent replacement of an existing remote file, and retain a receipt without retaining the document.
- **missing:** A byte-stream handoff between Mac local file access and the bound browser tab that bypasses model context; A pre-upload manifest and post-upload server-side confirmation; Typed file provenance and destination policy checks; Independent verification of the resulting remote file identity


## Changes it proposed to its own stack

### `integration` — Make verify_operation_step resolve to a real read-only faculty-perception endpoint (prefer POST /browser/provenance/:recordId/check, with operation_id and step_id correlation), returning observedAt, source/session identity, postcondition results, evidence hashes/snippets, freshness, and an explicit unknown outcome when the browser state cannot be read. Do not let executor receipts close an operation.
- **owner gets:** After asking the pendant to send or change something, the system can tell the owner whether it actually happened instead of confidently repeating a receipt. This is the difference between an assistant that acts and one that lies about acting.
- effort: Medium: implement the endpoint adapter, persist correlation IDs, and add browser/file/app postcondition checks for each enum kind.  ·  risk: A stale browser observation could be mistaken for fresh proof; enforce max age and source/session binding. On adapter failure, return unknown and preserve the action receipt.
- cost: Negligible per action; one read-only verification request.  ·  latency: Adds roughly 0.5–3 s after execution, but prevents false completion claims.
- security: Evidence must be sensitivity-filtered; hash-only by default and never send credentials or secrets to the pendant.
- depends on: faculty-perception implementation of postcondition checks; operation/step correlation IDs in POST /execute and browser commands; owner policy for when unknown is surfaced versus retried

### `integration` — Now that GET /observe reports Accessibility, Screen Recording, and successful input reachability for AI Pendant Agent, add a guarded visual/browser execution path that uses the live Safari bridge and records a before/after observation for every UI action. Gate it on the exact host app identity and browser session binding, not merely a global permission boolean.
- **owner gets:** The owner can finally ask for real GUI work on this Mac and get a useful result even when a site has no API: the agent can see the current screen, act in the bound Safari session, and explain what changed.
- effort: Medium: connect the existing action planner to observation snapshots, add session-affinity checks, and test reversible actions before consequential ones.  ·  risk: Wrong-tab or wrong-window actions are the main failure mode. Require explicit session/tab locators, stop on ambiguity, and use the physical approval latch for consequential actions.
- cost: One observation and one verification call per action; modest API cost.  ·  latency: Adds 1–4 s for snapshots and checks.
- security: Screen content may contain secrets; redact or hash by default, never place page contents on the pendant, and honor secure-input state.
- depends on: GET /observe; GET /browser/status; GET /browser/sessions; browser command/result correlation; verify_operation_step implementation


## What it asked for

_Nothing._
## Its own summary

Round 218 produced three distinct owner-facing capabilities (verified browser transactions with physical approval, context-rich moment bookmarks, and motion/focus-aware interruption gating) plus two integration changes. Live discovery found Safari bridge online and, importantly, GET /observe now reports Accessibility, Screen Recording, and input reachability granted for AI Pendant Agent; that owner-side unblock is no longer needed. I also recorded that both supposedly granted verification/audio tools remain unresolved in the actual inventory, and did not claim measurements or verification.

**Biggest unknown:** Whether the pendant itself is currently registered/reachable for field execution; the live device inventory still shows only the Mac bridge and an offline mobile device. I still need a real implementation of verify_operation_step (or its concrete provenance route) and audio_path_probe, plus operation/step correlation IDs, before I can honestly close actions or report fresh audio-path results.

