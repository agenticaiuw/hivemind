# Harness derivation — faculty-action — round 173

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “do this” while I’m looking at a page or app, use exactly what is currently in front of me, carry out the multi-step task, and tell me whether it really finished—without making me describe the page."
- **useful because:** The owner can act on the thing already in context instead of translating visual context into fragile spoken instructions. It combines the worn trigger, relay reasoning, Mac foreground state, and browser session—none of the individual nodes can provide this reliably alone.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Realtime for the short utterance and confirmation; background/local planner for the multi-step workflow; faculty-perception for fresh foreground/browser state and faculty-action for execution.
- **latency:** Acknowledge in under 1 second; capture state in 1–2 seconds; workflow completion may take up to 30 seconds with spoken progress only on meaningful transitions.
- **cost:** Low per invocation after the initial realtime turn; local Mac/browser inspection and action execution dominate, not model tokens.
- **security:** Capture only active app/window URL/title and a bounded DOM or screen-derived summary, never full page secrets by default. Redact passwords, payment fields, tokens, and private text before relay/model exposure. Require the existing physical approval latch for consequential sends/purchases/deletions; verify postconditions before claiming completion.
- **missing:** A context-binding envelope that atomically records pendant utterance ID, active Mac app, active browser tab, and a short-lived state hash.; A perception endpoint that returns the foreground/browser context with sensitivity labels and a stable locator.; Planner support for resolving deictic phrases such as “this”, “that”, and “the form here” against that envelope.

### "If a computer task gets interrupted by a login prompt, confirmation dialog, network error, or the Mac going offline, keep my place and let me say “continue that” later; resume only from the last verified step and explain what changed."
- **useful because:** Long real-world tasks fail at the seams. A durable, verified continuation means the owner does not have to remember which emails were sent, which fields were filled, or whether a payment step already happened.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-action
- **model tier:** Cheaper background/local planner for checkpoint bookkeeping; realtime only for interruption notices and the owner’s resume command; faculty-perception independently verifies the checkpoint before resuming.
- **latency:** Persist a checkpoint immediately after every verified step; resume acknowledgement under 2 seconds and restart within 5 seconds once the needed surface is online.
- **cost:** Very low model cost; storage and fresh verification dominate. Avoid replaying the whole conversation by storing compact step metadata and hashes.
- **security:** Checkpoints must contain references, hashes, and redacted summaries—not credentials, page contents, or form secrets. Expire stale checkpoints and invalidate them when URL, account, or relevant file hash changes. Never infer that an irreversible step happened from an executor receipt alone; use verify_operation_step and report unknown when verification is unavailable.
- **missing:** A durable workflow checkpoint schema with step IDs, preconditions, postconditions, state hashes, expiry, and resume policy.; A resume coordinator that reconciles executor receipts with fresh Mac/browser verification and safely branches on changed state.; A user-visible list of paused workflows addressable as “that task.”

### "Tell me when two parts of my digital life disagree—for example, a calendar says I’m free but a booking email or browser reservation says I’m committed—and let me choose which source should win or fix the conflict."
- **useful because:** The owner gets a trustworthy answer about real commitments instead of a search result assembled from one surface. It catches silent contradictions across calendar, Mail, browser sessions, and local files, then makes the correction actionable from the pendant.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Background/local models extract normalized claims; realtime is used only when the owner asks or when a high-confidence conflict needs a short alert. Faculty-perception supplies fresh evidence and faculty-action applies only the selected repair.
- **latency:** On-demand answer in under 5 seconds; background reconciliation can run on a slower schedule and alert only for high-confidence conflicts.
- **cost:** Low: local extraction and hashes dominate; use a cheaper model for normalization and reserve the realtime tier for the spoken interaction.
- **security:** Keep full email and page bodies on the Mac. Send the relay only claim summaries, source labels, timestamps, and hashes. Never auto-delete or overwrite a source; repairs require explicit selection and postcondition verification.
- **missing:** A normalized claim schema for commitments, times, people, and source provenance.; A contradiction detector spanning Calendar, Mail, browser state, and local documents.; A repair planner that presents reversible alternatives rather than choosing a source silently.

### "Before you send, submit, delete, or change something important, read me the exact human-visible diff—what will change, where, and what cannot be undone—and let me approve that specific diff from the pendant."
- **useful because:** The owner can approve consequences rather than trusting a vague description of an action. This is especially valuable for browser forms and multi-app edits where the final state may differ from the original plan.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Local Mac/browser code computes structured diffs; a cheaper model summarizes them; realtime speaks only the compact summary. The existing physical latch authorizes the exact digest, while perception verifies the final result.
- **latency:** Generate a preview within 2 seconds after the action is staged; physical approval remains valid only for a short expiry window.
- **cost:** Low API cost; local DOM/file/calendar diffing and fresh verification dominate.
- **security:** Do not put secrets or full message bodies into the pendant. The approval envelope contains a digest and human-readable redacted summary only. If the final state differs from the preview, invalidate approval and require a new one; never silently fall back to the old authorization.
- **missing:** A typed mutation-preview protocol for browser fields, files, messages, calendar events, and settings.; Digest binding between preview, physical approval, executor attempt, and independent postcondition verification.; A compact spoken and LED representation for multi-field diffs.


## Changes it proposed to its own stack

### `integration` — Add a privacy firewall between faculty-perception/action and the relay voice transcript: before any browser or Mac evidence is sent upstream, classify each field as normal/private/secret, replace private values with typed placeholders plus stable hashes, and allow faculty-action to request only the minimum locator needed for the next verified step. Keep the complete evidence local for postcondition checks and audit it by hash.
- **owner gets:** The owner gets powerful “do this” automation on logged-in sites without handing passwords, payment details, message bodies, or unrelated open tabs to the cloud model. Failures become truthful (“I need you to handle the login”) instead of silently leaking context.
- effort: Medium: implement a shared redaction contract, field classifier, local evidence vault, and relay-safe summaries across browser and Mac action paths.  ·  risk: Over-redaction can make a task impossible; recover by requesting one narrowly scoped local interaction or explicit owner confirmation. Misclassification is the main risk, so default unknown fields to private and retain immutable local audit hashes.
- cost: Negligible API cost; modest local storage for short-lived encrypted evidence and hashes.  ·  latency: Adds roughly 50–200 ms per evidence bundle locally; avoids expensive retries and large model context.
- security: Strongly reduces secret and unrelated-tab exposure. Secrets never enter relay transcripts or model prompts; access to local evidence is step-scoped and expires.
- depends on: Context-binding envelope from the proposed foreground-context capability; GET /observe and browser inspection sensitivity labels; verify_operation_step as the sole postcondition evidence gate; Existing actionRisk.js, prepareApprove.js, approvalHandoff.js, and policyRouter.js

### `hardware` — Replace the prototype’s single LED with a tiny low-power status display or a two-color LED plus a capacitive/second approval control, and define a local display protocol for identity, expiry, conflict, preview, and verified-result states. Keep all sensitive content off-device; display only short labels, counts, and transaction digests.
- **owner gets:** The owner can distinguish “waiting for me,” “already completed,” “conflict found,” and “unknown result” at a glance—even in a noisy room or when audio is unavailable—rather than guessing from one blink pattern or repeating the request.
- effort: High: new wearable enclosure/PCB or display module, firmware state machine, power characterization, and relay/Mac rendering contract. This is intentionally a product-hardware change, not a refactor of the development kit.  ·  risk: More hardware increases size, power use, and failure modes. Recover with the existing audio/LED fallback and make display loss non-authorizing: a missing or stale display must never approve an action.
- cost: Roughly $5–20 in prototype components plus enclosure/PCB work; tens of milliwatts while active, near-zero in sleep depending on display choice.  ·  latency: Immediate local status feedback; no network latency for pending/expired/error states.
- security: Improves human-visible authorization state without putting credentials or page content on the pendant. Approval still requires the existing cryptographic transaction binding and deliberate gesture.
- depends on: A typed mutation-preview protocol and digest-bound approval envelope; Owner choice of wearable form factor and acceptable battery impact; Firmware support for richer local state rendering


## What it asked for

_Nothing._
