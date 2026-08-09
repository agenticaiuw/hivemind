# Harness derivation — faculty-perception — round 219

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac and browser perception readiness** — At 2026-08-09T00:30Z the Mac agent is online with computer-use loop enabled, vision model configured, Accessibility trusted, Screen Recording granted, permissions.ready=true, and the Safari browser extension online with two tabs and zero pending commands. Relay is reachable and D1-backed; no pendant is registered.
  - evidence: GET /ops/status HTTP 200 and GET /browser/status HTTP 200; read_continuity_snapshot include relay/pipeline resolved to GET /ops/snapshot HTTP 200 and reported the same live status.

## Capabilities it proposed

### "When I say “watch this page,” tell me only when its meaning changes, with the exact before/after evidence and whether I need to act."
- **useful because:** The browser is live now, and this turns a vague recurring request into a trustworthy change detector instead of repeated noisy summaries. It can distinguish a real content change from a login wall, ad rotation, or layout churn and speak only actionable deltas.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheap background model to compare normalized page snapshots; reserve realtime for the spoken alert and judgement for whether it is actionable.
- **latency:** Initial capture under 3 seconds; scheduled checks every 15–60 minutes; alert within 10 seconds of a completed check.
- **cost:** About $0.001–$0.01 per check depending on page length; browser capture and hashing dominate latency, not model time.
- **security:** Page contents can include private logged-in data. Store hashes and short redacted diffs by default, never full pages; require confirmation before opening links or acting on a detected change.
- **missing:** A durable watch record with schedule, selector, and baseline capsule/hash; Semantic diff that ignores ads, timestamps, and layout-only changes; A relay-to-pendant alert that carries the diff ID and a real playback acknowledgement

### "Handle this private logged-in page for me, but do not send the page or screenshot off my Mac; tell me exactly what you changed and let me undo it."
- **useful because:** The browser is authenticated and online, while the relay is a different trust boundary. This gives the owner useful computer control without exporting account contents to the cloud, and makes the result auditable and reversible rather than merely saying “done.”
- **path:** browser-extension → mac-vision → mac-planner → mac-terminal → relay-realtime → faculty-perception → faculty-action
- **model tier:** Run perception, planning, redaction, and action locally on the Mac with a cheaper local/background model; use realtime only to clarify the owner's request or narrate a compact receipt.
- **latency:** Read-only tasks 2–5 seconds; one to three reversible edits under 10 seconds; pause for confirmation when the local classifier finds secrets or a destructive operation.
- **cost:** Near-zero cloud token cost for page content; local inference and screenshots dominate. A short spoken receipt is the only routine realtime cost.
- **security:** The Mac-local model still sees the logged-in page, so isolate its workspace and redact credentials, payment data, and message bodies from receipts. Relay receives only intent, status, hashes, and reversible operation IDs. Mail, deletion, purchases, and external sends require confirmation.
- **missing:** A hard relay contract that rejects raw page text and screenshots for this mode; Local-only browser/vision planner routing with a structured redacted-result schema; A reversible operation bundle that combines browser result, action-ledger step, and undo endpoint; A perception policy that labels every claim as observed locally versus asserted by the relay

### "Continue the task I was doing before the app or connection died, but first show me what state you recovered and ask only about steps that could have happened twice."
- **useful because:** Today the Mac ledger, browser spool, relay jobs, and pipeline traces are separate and completion is often inferred. A recovery capability would use the surviving evidence to distinguish committed, interrupted, and unknown steps, preventing duplicate sends or edits after a crash.
- **path:** relay-realtime → faculty-perception → mac-planner → mac-vision → browser-extension → mac-terminal → faculty-judgement → faculty-action
- **model tier:** Use a cheap deterministic state reconciler first; use a background model only to summarize ambiguous traces; reserve realtime for the owner's recovery question and confirmation.
- **latency:** Show a recovery map within 3 seconds for local state and 5 seconds when the relay must be queried; never auto-resume an ambiguous or irreversible step.
- **cost:** Usually under $0.01 because reconciliation is deterministic; model cost is limited to ambiguous summaries.
- **security:** Recovery state can expose private page titles, commands, and message targets. Keep raw evidence local, send only redacted step hashes to relay, and require confirmation for any non-idempotent operation. Never treat Mac completion as pendant playback.
- **missing:** A common event identity and idempotency key shared by relay jobs, Mac action-ledger steps, browser commands, and pipeline runs; A reconciler that models committed/failed/in-flight/unknown instead of one completed flag; A user-facing recovery map with per-step evidence and safe resume/undo choices; A lease/claim protocol so two agents cannot resume the same step

### "Watch me do this task once, then make it a reusable command I can invoke by voice, replacing private details with questions instead of saving them."
- **useful because:** The owner currently has automation primitives but cannot safely turn a demonstrated browser-and-Mac workflow into a reusable, parameterized routine. This would convert one-off computer use into a personal skill without storing passwords, message contents, or brittle screen coordinates.
- **path:** browser-extension → mac-vision → mac-planner → mac-terminal → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use local vision and deterministic action tracing during the demonstration; use a background model to generalize repeated steps; use realtime only for the spoken invocation and clarification.
- **latency:** Record the demonstration live; produce a draft routine within 15 seconds after completion; invocation should complete common tasks in under 20 seconds.
- **cost:** One background-model call per demonstration, roughly $0.02–$0.10 depending on trace length; later invocations are mostly local deterministic execution.
- **security:** Detect and discard secrets, credentials, payment data, and message bodies during recording. Require explicit approval before publishing a routine. Parameterize recipients, amounts, and destinations; destructive or externally visible steps always require confirmation.
- **missing:** A demonstration recorder that joins browser events, screen observations, AppleScript actions, and action-ledger steps; Secret-aware generalization that turns literal values into typed parameters or refuses to retain them; A routine compiler with replay preconditions and safe failure points; A routine review surface showing exactly what will be remembered and executed

### "When I press the pendant and say “save this,” save exactly what I am looking at and saying as a private, searchable bookmark I can resume later from the same page and context."
- **useful because:** A fleeting thought currently becomes a note detached from the browser state. This would join the pendant utterance, the authenticated browser tab, a redacted page region, and a resumable Mac/browser session so the owner can return to the precise context rather than reconstruct it.
- **path:** pendant → browser-extension → mac-planner → mac-vision → relay-realtime → faculty-perception → faculty-action
- **model tier:** Use realtime only to capture the short spoken intent; perform local page capture, redaction, hashing, and indexing with a cheaper background/local model; use the relay only for durable synchronization and eventual delivery.
- **latency:** Acknowledge the bookmark locally in under 500 ms; finish capture in under 5 seconds; resume in under 10 seconds when the Mac and browser are online.
- **cost:** A few cents at most per bookmark if transcription or summarization is needed; most work is local capture and storage.
- **security:** Logged-in page content must remain on the Mac unless explicitly shared. Redact credentials, tokens, payment data, and private messages. The bookmark should retain a revocable capsule and disclose when the original page or session is no longer available.
- **missing:** A pendant-to-browser correlation token that binds the press and utterance to the active tab; A local bookmark record joining capsule, spoken note, tab/session, and resume locator; A relay sync format for redacted bookmark metadata and offline retry; A resume flow that verifies the page still matches before navigating or acting

### "For anything risky, show me exactly what will happen on the Mac and require my physical pendant press to approve it; never accept approval from the browser alone."
- **useful because:** A voice command can be misheard and a logged-in browser can be manipulated by stale state. A physically bound approval channel would make sending mail, purchases, deletion, and account changes materially safer while keeping ordinary reversible work fast.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic policy and local diff generation; use realtime only to explain the pending action; no expensive model call should be needed for the approval decision.
- **latency:** Render the proposed diff within 2 seconds; accept or reject the physical approval within 1 second; expire approvals after 60 seconds or any observed state change.
- **cost:** Negligible model cost; implementation cost is protocol and firmware work, with a small per-approval relay event.
- **security:** Bind approval to a nonce, exact action hash, device session, and expiry so an old press cannot authorize a new action. Never speak secrets aloud. Require a second confirmation for purchases or irreversible deletion, and fail closed if the pendant is offline.
- **missing:** A cryptographically bound pending-action nonce shared by relay, Mac, browser, and pendant; A compact spoken/on-screen action diff format with preconditions and affected targets; Firmware support for displaying or acknowledging the nonce and emitting a one-shot physical approval event; Relay and Mac enforcement that rejects approvals for changed or expired state


## Changes it proposed to its own stack

### `mac-harness` — Turn on a permission-aware screen-grounded verification stage for every computer-use action: capture a redacted pre-state observation, execute the action, capture post-state, and require the observed postcondition to match the planned result before reporting success. Persist only hashes, action IDs, and a small failure crop; if observation is unavailable, report 'executed, unverified' rather than success.
- **owner gets:** The agent can now actually see and control the Mac: /ops/status reports Accessibility and Screen Recording trusted, computer-use enabled, and the browser extension online. The owner will stop hearing confident claims that a click or edit worked when the UI did something else.
- effort: Medium: wire the existing vision loop and action ledger together, add postcondition checks for the common action types, and expose a concise receipt.  ·  risk: Screenshots may contain secrets; redact and cap them, and never persist full frames by default. False mismatch could cause a harmless retry or pause; recovery is to show the owner the failed postcondition and offer a manual retry.
- cost: One extra vision observation per action; roughly $0.01–$0.05 for complex actions, negligible for simple DOM/browser actions.  ·  latency: Adds roughly 0.5–2 seconds per verified action.
- security: Improves safety by preventing unverified destructive actions from being reported as complete; needs strict crop/redaction and confirmation gates for mail, deletion, and purchases.
- depends on: Use the now-live permissions shown by GET /ops/status: Accessibility trusted, Screen Recording granted, permissions.ready=true; Existing computer-use loop and vision model; Existing action ledger and job receipts


## What it asked for

_Nothing._
