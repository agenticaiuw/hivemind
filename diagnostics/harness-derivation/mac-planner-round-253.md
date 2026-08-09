# Harness derivation — mac-planner — round 253

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **approval-handoff-live-state** — The discovered POST /approve and POST /prepare entries are not live Mac-agent routes: describe returns a 404 Cannot GET response for both. GET /workbench/jobs/:jobId/handoff is live but currently returns known:false for a placeholder job. Any pendant approval workflow needs a real server-side approval endpoint and job-bound execution primitive, not just these names.
  - evidence: describe POST /approve -> liveStatus 404; describe POST /prepare -> liveStatus 404; probe/describe GET /workbench/jobs/:jobId/handoff -> HTTP 200 with known:false.

## Capabilities it proposed

### "If a Mac job fails or is interrupted, put a compact recovery card in my pendant inbox saying what completed, what remains, and the exact phrase to resume it; when I say that phrase later, resume from the saved handoff instead of starting over."
- **useful because:** Long desktop tasks currently disappear into job logs. A wearable alert makes failure actionable away from the desk and gives the owner a safe, idempotent way to continue later.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** Cheap background model to compress receipts into a three-line card; realtime only when the owner asks to resume.
- **latency:** Failure-to-pendant alert under 15 seconds; resume acknowledgement under 2 seconds and execution starts only after the stored handoff is verified.
- **cost:** ~$0.005 per failure card; no model cost for receipt-only extraction, with one cheap call for natural-language compression.
- **security:** Cards must omit file contents, tokens, and full command lines. Resume must be idempotent, use the existing workbench job identity, and preserve the owner's policy for mutations; destructive steps should remain explicitly confirmed.
- **missing:** A relay-to-pendant inbox adapter for job failure events; A durable mapping from job_id to GET /workbench/jobs/:jobId/handoff and GET /jobs/:jobId/receipts; A voice intent that resolves the spoken resume phrase to one job without exposing other jobs

### "At the end of the day, ask me one question about each physical bookmark I made, then turn my answers into linked notes with the original Mac app/tab and timestamp attached."
- **useful because:** Bookmarks made in motion are valuable but otherwise become an unexplained pile. A short, bounded evening review converts them into decisions, follow-ups, or discardable moments with provenance.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime model for the interactive question loop only; background cheap model for clustering and note formatting.
- **latency:** Prepare the review in under 20 seconds; each question-answer turn under 1.5 seconds; finish within 5 minutes or pause safely.
- **cost:** ~$0.03 per daily review, dominated by realtime turns; metadata lookup is negligible.
- **security:** Only show cards made that day, redact page contents and URL parameters, and keep answers in the owner's notes workspace. The owner can skip or delete each card; no automatic external sending.
- **missing:** A daily bookmark index and review cursor; A pendant inbox action that starts a multi-card review and supports skip/delete; A note writer that preserves provenance links without embedding sensitive browser content

### "When a Mac action is waiting on me, send a short approval card to the pendant; I can approve or reject it by voice, and the Mac executes only that exact queued action and reports the result back to the pendant."
- **useful because:** The owner should not have to return to the Mac to unblock a useful task, but approvals must remain specific rather than becoming blanket automation. This creates a wearable control surface for the existing job queue.
- **path:** relay → pendant → mac-bridge → dashboard
- **model tier:** Realtime model only to resolve the owner's spoken approve/reject intent; deterministic server logic selects the pending job and emits the receipt.
- **latency:** Card delivery under 5 seconds; voice decision to execution under 3 seconds; receipt card under 10 seconds.
- **cost:** Under $0.01 per decision; mostly transport and receipt handling, with a short realtime intent call.
- **security:** Show app, action summary, and touched resources—not secrets or full command text. Bind approval to a nonce and job ID, expire it quickly, reject stale or changed plans, and preserve the owner's rule that mail sending, deletion, and purchases require confirmation.
- **missing:** A pendant inbox item type carrying a one-use approval nonce; A relay endpoint that binds voice approval to POST /approve or the existing approval handoff; A Mac-side atomic compare-and-execute check so the approved plan cannot be substituted

### "Let the pendant act as a physical presence key for sensitive browser sessions: when I walk away or press its privacy latch, pause/lock selected authenticated tabs, and restore them only when the pendant is present again and I explicitly unlock it."
- **useful because:** A browser session can remain authenticated while the owner is away. This gives the always-worn device a physical security boundary that the Mac and browser cannot establish from software alone.
- **path:** pendant → browser → mac-bridge → relay
- **model tier:** Deterministic firmware/browser policy; no model call except optional natural-language setup.
- **latency:** Lock selected tabs within 2 seconds of the pendant privacy state or link loss; unlock within 2 seconds after explicit local confirmation.
- **cost:** Negligible per event; implementation and browser-extension testing dominate.
- **security:** Never transmit passwords, cookies, or page contents. Default to locking only explicitly enrolled origins. Treat link loss as lock, not unlock; require a local button gesture plus browser-side nonce to restore. This must not pretend to replace OS account lock.
- **missing:** A secure presence/attestation channel between pendant and browser extension; An extension capability to suspend or redact selected authenticated tabs without destroying session state; A user-managed origin policy and recovery path when the pendant is unavailable

### "While walking, let me dictate a rough idea to the pendant and later say 'put that into my editor'; the Mac should open the correct workspace, insert a clearly marked draft at the right project location, and leave the original audio/transcript link beside it for correction."
- **useful because:** Voice memos and notes are easy to collect but hard to turn into usable work. This makes a spoken thought become an editable artifact in the owner's actual project without silently presenting a transcript as truth.
- **path:** pendant → relay → mac-bridge → mac-terminal → dashboard
- **model tier:** Realtime speech model for transcription only; cheaper background model to infer project/file placement and format; deterministic Mac actions for insertion.
- **latency:** Capture acknowledgement immediately; transcript available within 20 seconds; insertion preview within 5 seconds after the owner asks; never block capture on the Mac.
- **cost:** ~$0.02–$0.08 per memo depending on audio length; transcription dominates.
- **security:** Keep audio local/queued until upload policy allows it, mark every insertion as an untrusted draft, never overwrite existing text, and show the target path plus a diff before mutation. Project contents and voice leave the device only under the owner's configured policy.
- **missing:** A durable cross-node identity linking offline voice memos to their transcript and target workspace; A project/file resolver with a non-destructive insertion format and diff receipt; A spoken command that selects one memo unambiguously without exposing unrelated private memos

### "Before I send an email or submit a web form, let me ask the pendant 'what am I about to send?'; the browser extension should provide the draft, recipients, attachments, and destination, the relay should point out unexpected secrets or mismatches, and the pendant should read a short risk summary without sending anything."
- **useful because:** The owner can catch wrong recipients, accidental secrets, and stale attachments while mobile or distracted. It adds a comprehension step rather than another blind confirmation button.
- **path:** pendant → browser → relay → mac-bridge
- **model tier:** Cheap background classifier for secret/mismatch detection; realtime model only to answer follow-up questions in one short spoken turn.
- **latency:** Summary in under 4 seconds for a normal email/form; never hold or mutate the draft while analysis runs.
- **cost:** ~$0.01–$0.04 per check, dominated by redacted draft analysis.
- **security:** Perform redaction and recipient hashing locally before relay upload where possible. Never upload passwords or authentication fields. Make the summary advisory, preserve the draft unchanged, and require the owner's existing explicit send confirmation separately.
- **missing:** A browser command that returns structured draft/recipient/attachment fields rather than page text; A local secret detector and redaction layer for form fields and attachments; A relay analysis endpoint with a no-send guarantee and an auditable result tied to the exact draft hash


## Changes it proposed to its own stack

### `browser-harness` — Add a read-only, origin-scoped 'submission preview' command to the browser extension. It returns a normalized draft model (visible text, recipients, attachment names, destination, and field labels), a redacted preview, and a content hash; it refuses password, token, payment, and hidden-field values. The relay can analyze this model, but the command has no submit capability.
- **owner gets:** The owner can ask the pendant what a message or form will actually send and catch mistakes before committing, instead of relying on a vague confirmation prompt.
- effort: Medium: extension DOM adapters for email editors and common forms, local redaction, schema/versioning, and tests across Safari sessions.  ·  risk: Forms can be unusual or misleading; return an explicit unsupported/partial status and never claim completeness. A bad redaction could expose sensitive text, so fail closed for unknown field types and keep a local audit hash rather than raw content.
- cost: Low recurring API cost; one short analysis call only when requested. Engineering cost is the main expense.  ·  latency: Local extraction under 300 ms; relay analysis typically 1–4 seconds.
- security: Improves security by keeping secrets local and binding analysis to a draft hash; requires careful origin allowlisting and no page-script privilege escalation.
- depends on: A relay no-send analysis endpoint; Owner-configured browser origin policy; A pendant spoken query path


## What it asked for

_Nothing._
## Its own summary

Discovered the live inventory and verified the new-grant set. Recorded three distinct owner-facing capabilities: (1) job-failure recovery cards with resumable handoffs, (2) an end-of-day physical-bookmark review that turns answers into provenance-linked notes, and (3) wearable, nonce-bound approval/rejection of a specific queued Mac action. The first contextual-bookmark proposal collided with an existing capability and was not restated. I also verified that the advertised POST /approve and POST /prepare routes currently return 404, while GET /workbench/jobs/:jobId/handoff exists but reports unknown for an unrecognised job.

**Biggest unknown:** The missing approval and pendant-inbox adapters are the main blockers. I still need a live, job-bound approval/prepare API, a relay event bridge from Mac receipts to the pendant inbox, and a deterministic compare-and-execute/expiry rule. For bookmark review, I need the actual event consumer and retention/redaction policy. Accessibility/Screen Recording remains owner-blocked; I did not re-request it.

