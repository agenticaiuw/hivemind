# Harness derivation — unified — round 70

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “continue,” resume the last unfinished task exactly where it stopped: replay its spoken intent, show what has already been done, and continue from the saved Mac/browser/pendant checkpoint without repeating completed or irreversible steps."
- **useful because:** Today a dropped link, leaving the Mac, or ending a voice turn loses the relationship between the pendant conversation, relay job, browser evidence, and local files. A single cross-surface resume capsule would make long tasks genuinely survivable and prevent duplicate submissions.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model to normalize and compact checkpoints; use realtime only to interpret the owner’s short “continue” and speak the capsule. Mac/browser agents execute only after the checkpoint is reconciled.
- **latency:** Resume acknowledgement under 1 second from the relay; capsule retrieval under 2 seconds; reconciliation can continue in background. Owner should hear a short status immediately, then details on request.
- **cost:** Usually <$0.01 per checkpoint/resume; dominated by one small summarization call. Store hashes and pointers, not repeated page text or audio, to control context and storage cost.
- **security:** Capsules may reference private tabs, mail, calendar, files, and audio. Encrypt or sensitivity-label each pointer, expire stale browser evidence, never persist secrets or raw microphone audio by default, and require confirmation before resuming send/delete/purchase or other irreversible actions. The spoken capsule must not expose private content in public mode.
- **missing:** A first-class durable checkpoint schema linking relay job, session, pendant audio pointer, Mac state, browser tab IDs/evidence, completed step receipts, and pending approvals.; Atomic checkpoint writes at every step boundary and a resume/reconcile endpoint that rejects stale or conflicting state.; A pendant-visible local marker for “checkpoint saved” and “resume available” when the link drops.

### "Let me teach you a recurring computer task once by doing it myself while I explain it, then later let me say “do the usual one” and have you reproduce the workflow with today’s values, showing me what changed before any irreversible step."
- **useful because:** The owner repeatedly has to explain workflows that are unique to their accounts and habits. A demonstrated workflow would turn the pendant, Mac, authenticated browser, and relay into a personal automation that no single surface can learn or safely replay alone.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to detect teaching boundaries and acknowledge the owner. Use a cheaper background model to convert the recording into a typed workflow with variables, preconditions, evidence requirements, and confidence; use the normal planner only for a later replay.
- **latency:** Teaching can process asynchronously after the session. On replay, acknowledge the request within 1 second, preview within 5 seconds, and pause before any send, purchase, deletion, or other irreversible action.
- **cost:** A few cents per newly taught workflow, dominated by one background transcription/normalization pass; replay cost is a small planning call plus ordinary Mac/browser actions. Store action structure and evidence hashes rather than full recordings.
- **security:** Demonstrations may expose passwords, private pages, one-time codes, or sensitive audio. Redact typed secrets and clipboard contents, do not retain raw screen/audio by default, bind workflows to the owner’s account/session, expire browser locators, and require explicit confirmation for irreversible steps. The preview must show substituted values and the source evidence for each one.
- **missing:** A first-class demonstrated-workflow format with typed variables, preconditions, safe/reversible classification, and evidence assertions.; A recorder that correlates pendant speech, browser command/result IDs, Mac typed actions, and before/after observations into one ordered trace.; A replay validator that stops when the page, account, or observed state differs from the taught preconditions instead of improvising.


## Changes it proposed to its own stack

### `integration` — Add a cross-surface Resume Capsule record and state machine. At each relay/job/pipeline step, atomically record capsuleId, owner intent, session and job IDs, step receipts, idempotency keys, Mac machine-context/file pointers, browser tab/session IDs plus evidence hashes, audio object pointer, sensitivity/TTL, and pending approval gates. Expose create/update/get/reconcile/resume operations; reconcile must compare the last receipt from GET /jobs/:jobId/receipts with Mac/browser acknowledgements and only enqueue the next uncompleted reversible step. Mark a capsule stale after TTL or browser-session loss, and make the pendant resume button speak a safe summary rather than guessing.
- **owner gets:** Long jobs can survive a dropped connection or walking away, and “continue” will not redo a form, duplicate a reminder, or silently cross an approval boundary.
- effort: Medium: D1 schema/API plus relay and local-agent adapters, then dashboard and pendant status UI; no Accessibility permission required for the first version because it can use existing typed Mac actions, AppleScript, browser bridge, and receipts.  ·  risk: A bad reconciliation could skip or duplicate work. Use idempotency keys, append-only receipts, explicit unknown/conflict state, and stop on any irreversible or stale step. Recovery is manual review from the capsule timeline.
- cost: Small D1/R2 growth from compact metadata; background summarization costs cents per hundreds of checkpoints. Do not duplicate page/audio payloads.  ·  latency: One small write per step (<100 ms target); resume adds one reconciliation round trip, while immediate spoken acknowledgement remains local to relay.
- security: Capsules are sensitive metadata. Encrypt private pointers, enforce per-session authorization, TTL-delete raw artifacts, redact secrets, and audit every resume/read.
- depends on: The durable job runner and browser command receipts already in progress; A stable audio object/pipeline identifier; A local-agent callback for typed Mac state and completion receipts

### `integration` — Add a Demonstrated Workflow compiler and replay validator between the pendant conversation, relay, Mac agent, and browser bridge. During a teaching session, assign one trace ID and collect timestamped spoken intent segments, typed Mac/browser commands, command results, page/state observations, and redacted before/after values. Compile them into a versioned workflow DAG whose nodes declare inputs, preconditions, evidence assertions, reversibility, and approval requirements. On replay, resolve variables from current authenticated state, run only validated nodes, compare each observation against its precondition, and halt with a concrete mismatch if reality differs. Show a dashboard preview with substituted values and evidence before gated actions.
- **owner gets:** The owner can automate personal routines without repeatedly explaining them, while the system refuses to blindly replay a stale or account-specific sequence.
- effort: High: trace correlation across relay, local agent, and browser bridge; a redacting compiler; durable workflow storage; replay validation; dashboard editing and preview.  ·  risk: A workflow could capture secrets or become unsafe as a site changes. Recover by defaulting to read-only teaching, redacting sensitive fields, versioning every edit, requiring confirmation for gated nodes, and stopping on any precondition mismatch.
- cost: One background compilation call per taught workflow and a small planning call per replay; compact typed traces are cheaper than retaining recordings or screenshots.  ·  latency: No impact on ordinary interactions; teaching compiles asynchronously. Replay adds validation before each action and should remain within a few seconds for short workflows.
- security: Highest sensitivity during teaching. Encrypt workflow definitions, isolate secret-like values as non-persisted placeholders, restrict replay to the same authorized browser/Mac identity, and provide immediate deletion of the workflow and trace.
- depends on: A durable cross-surface trace identifier and event envelope; Redaction of audio, clipboard, typed secrets, and private page content; Typed browser/Mac action results with stable evidence locators


## What it asked for

_Nothing._
