# Harness derivation — mac-terminal — round 120

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **executor schema defect** — At 2026-08-07 14:42, executor receipts reject actions that visibly contain required fields: open_app with appName, run_shell with command, and run_applescript with script. Browser launch self-healing therefore loops on malformed dispatch/normalization.
  - evidence: GET /jobs and GET /logs returned failed jobs local_a35ac8bd, local_a65104d, local_7bad0b4b and local_7bad0b4b with these exact action objects and messages.

## Capabilities it proposed

### "“I got interrupted—what was I doing, what is still unfinished, and put me back where I left off.” The pendant should give me a short spoken reconstruction and, if I say ‘restore it,’ reopen the relevant Mac windows and reattach the browser tabs without submitting or sending anything."
- **useful because:** Today the pieces can report isolated jobs, sessions, apps, and browser tabs, but they cannot turn an interruption into a trustworthy, cross-device continuation. This would preserve the owner's working context across a dropped voice link, a sleeping relay, or moving between Mac and pendant without relying on memory.
- **path:** relay-realtime → pendant → mac-planner → mac-vision → browser-extension → unified → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic assembly for timestamps, active jobs, foreground app, browser tab identity, and receipts; use the background tier to summarize the interruption checkpoint. Escalate to planner only when the unfinished goal must be inferred from multiple artifacts. Use realtime only for the spoken request and concise answer.
- **latency:** Under 2 seconds for the first spoken checkpoint from cached observations; up to 8 seconds for a richer reconstruction. Restoration should stream progress and finish within 10 seconds when the browser bridge is online.
- **cost:** Low: deterministic reads dominate; roughly one background summarization call (about 2–4k input tokens) per reconstruction, with no model call for an exact active-job resume.
- **security:** Private tab titles/URLs, window identity, transcripts, and draft text leave the Mac only as a minimal redacted checkpoint. Never transmit page contents unless needed to explain the unfinished task. Restoration must be limited to reopening/focusing and browser reattachment; no send, submit, purchase, or destructive action. Require an explicit spoken ‘restore it’ after showing the proposed windows/tabs.
- **missing:** A durable interruption-checkpoint record that joins Mac observation, job receipts, session transcript, and browser tab/session identity with source timestamps and expiry; A cross-surface resume assembler that can distinguish an active unfinished task from stale background activity and cite each inference; A restore plan/action type for reopening or focusing a recorded app/window and reattaching a recorded browser session, with idempotency and truthful partial-failure receipts; Pendant/relay delivery of a compact checkpoint plus a confirmation turn, including behavior when the browser extension is offline

### "“What private information did you use for that, and what left my Mac?” Give me a plain-language data-flow receipt for the last request, including which browser pages, files, apps, model tier, and relay paths were involved."
- **useful because:** The owner has deliberately chosen maximum Mac capability, but today action receipts say what ran, not what sensitive context crossed from the Mac to the relay or model. A spoken, per-request data-flow receipt would make that trust choice legible after the fact without adding approval gates.
- **path:** mac-planner → mac-vision → browser-extension → relay-realtime → unified → faculty-perception → faculty-judgement
- **model tier:** Build the inventory deterministically from execution receipts, journal entries, browser evidence capsules, routing stats, and relay telemetry; use the background tier only to turn the inventory into a short explanation. Realtime is used only when the owner asks verbally.
- **latency:** Under 3 seconds for a completed request, using append-only event indexes rather than rescanning logs; partial receipts should state which node has not reported yet.
- **cost:** Very low: local indexing and deterministic formatting, with an optional 1–2k-token background summarization call. The dominant cost is one-time event plumbing, not per-request inference.
- **security:** This feature must not create a second leak: redact secrets, cookie values, full page bodies, file contents, and command output from the receipt by default. Keep raw provenance on the originating device; export typed categories, destinations, timestamps, and hashes. The owner can request a local-only detailed view.
- **missing:** A shared event envelope emitted by every node with data categories, source surface, destination/model, retention, and a content hash rather than raw content; Relay-side correlation of request IDs across pendant audio, Mac jobs, browser evidence, and model calls; A local and spoken renderer with configurable detail and automatic redaction of credentials and personal content; Retention/deletion controls for these data-flow receipts independent of ordinary action logs


## Changes it proposed to its own stack

### `integration` — Add a strict action-envelope adapter immediately before executor dispatch. It must accept both legacy top-level and canonical params forms, copy aliases (app↔appName, command, script) into one internal envelope without mutating the original receipt, validate required values, and emit a redacted `dispatch.inputKeys` diagnostic. On a missing-required-field error, perform exactly one local re-normalization retry; if it still fails, classify it as `schema_error` (not a user/action failure) and suppress planner self-healing loops. Add contract tests using the exact failing open_app, run_shell, and run_applescript payloads observed in /jobs.
- **owner gets:** Requests such as “open the browser bridge” will either work on the first attempt or explain a real wiring defect immediately, instead of silently spending several jobs failing and leaving the browser offline with 11 queued commands.
- effort: Small-to-medium: shared adapter, receipt diagnostic field, and executor contract tests; no policy or confirmation changes.  ·  risk: A bad alias could dispatch the wrong value. Keep the original action and normalized envelope in the receipt, validate non-empty strings, and cap retry to one; recovery is transparent failure with an actionable diagnostic.
- cost: Negligible API cost; saves planner retries and their prompt tokens.  ·  latency: Near-zero for valid actions; at most one in-process retry for malformed envelopes.
- security: No new authority; preserve FULL_CONTROL_MODE and existing owner policy. Redact secrets from diagnostics and do not log command output.
- depends on: mac-planner's non-blocking schema normalizer; receipt schema supporting diagnostics and failure classification

### `mac-harness` — Make action planning reachability-aware: inject the live /observe capability capsule into planning and receipts. When Accessibility is untrusted or Screen Recording is unavailable, mark ui_click/type_text/press_keys and vision steps as `unreachable` before dispatch, route equivalent intents to shell or AppleScript when a verified equivalent exists, and otherwise return a truthful unsupported result. Never report UI success when inputReachability.uiActionsWillReachTheScreen is false.
- **owner gets:** The owner will stop believing a task happened when the Mac agent's UI events actually did nothing; simple tasks can still complete through reliable non-UI paths, while impossible GUI work fails immediately with the exact permission needed.
- effort: Medium: planner context hook, action capability matrix, receipt status, and fallback mappings for common intents (open/focus app, volume, brightness, launch URL).  ·  risk: A fallback could have different semantics than the requested UI gesture. Restrict automatic fallback to equivalent, reversible intents and preserve the original planned action in the receipt; recovery is a normal retry after permissions change.
- cost: Saves vision-loop and planner tokens by failing or falling back before up to 25 useless steps; no new model cost.  ·  latency: Improves latency for unsupported UI tasks; adds a small local preflight read.
- security: No added authority or gates. /observe must redact command output and sensitive window contents; only capability booleans and app identity are passed to the planner.
- depends on: /observe read-only capability capsule; typed action receipts with truthful status categories


## What it asked for

_Nothing._
## Its own summary

Fresh discovery found a concrete Mac execution defect: /jobs and /logs show populated open_app, run_shell, and run_applescript actions rejected as if required fields were absent, causing repeated browser-bridge launch failures. I recorded the finding, notified mac-planner and browser-extension, and proposed an executor-boundary normalization/contract-test change plus reachability-aware UI planning. The Mac is otherwise online and relay-connected, but browser extension is offline with 11 pending commands; Accessibility and Screen Recording remain ungranted, so UI receipts are explicitly untrustworthy.

**Biggest unknown:** The exact internal executor envelope expected after planner normalization (top-level fields versus action.params) is still not exposed. I still need the adapter implementation or a confirmed dispatch contract; the owner also still needs to grant Accessibility to the actual AI Pendant Agent binary and Screen Recording if GUI/vision automation is desired.

