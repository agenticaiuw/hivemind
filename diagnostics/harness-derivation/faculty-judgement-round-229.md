# Harness derivation — faculty-judgement — round 229

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "After you do something for me, check whether it actually achieved the outcome—not just whether the Mac said it ran—and tell me if it quietly failed."
- **useful because:** A receipt saying 'click completed' is not the same as an email sent, a booking changed, or a page state updated. This closes the loop between intention and real-world result, especially when browser sessions drift or a site rejects a mutation.
- **path:** pendant → relay → mac → browser
- **model tier:** Use the cheap background model to formulate a verification check from the original intent; reserve realtime for the owner's brief spoken correction. Mac/browser perform read-only postcondition checks; relay stores the result and attention-arbitrates it; pendant speaks only a short discrepancy.
- **latency:** Initial action remains unchanged. Verification should begin 10–30 seconds after completion and finish within 60 seconds; if the site is unavailable, defer rather than interrupt.
- **cost:** About $0.005–$0.03 per verification, dominated by an extra browser read or Mac read and occasional background-model interpretation; no realtime call unless the owner asks why.
- **security:** Verification must be read-only and scoped to the original target, never infer success from a toast alone, and never expose message contents aloud by default. Require owner confirmation before any compensating mutation. Use explain_action_provenance for the evidence chain and autonomy_policy_evaluate for any proposed repair.
- **missing:** typed postcondition declarations attached to plans/actions; a durable relay↔Mac job correlation key (current localJobId is telemetry only); read-only verifier adapters for Mail/Calendar/web targets; a follow-up scheduler that survives an orphaned job (relay job leases are also missing)

### "When I approve or reject one of your suggestions, remember what that says about how I want you to decide next time—and show me the rule you learned before you use it."
- **useful because:** The system currently has an autonomy policy evaluator, but it cannot learn from the owner's actual corrections. This would turn repeated friction into fewer interruptions and fewer unsafe assumptions without silently changing policy.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime handles the one-sentence owner feedback; a cheaper background model clusters repeated feedback into a candidate rule. The relay keeps the immutable decision/evidence record; Mac/browser attach the action receipt and target context; the pendant displays the candidate rule for explicit approval.
- **latency:** Capture feedback in under 1 second after a spoken or physical response. Candidate rules can be compiled overnight or after five matching examples; never block an action on model-based learning.
- **cost:** Roughly $0.01–$0.05 per candidate-rule compilation, mostly background-model tokens; feedback capture and policy lookup are local/deterministic.
- **security:** A rejection is not automatically a global preference: scope learned rules by action kind, target, audience, and expiry. Do not infer sensitive preferences from a single event. Every learned rule must be inspectable, reversible, and evaluated fail-closed; explicit physical approval remains required for irreversible actions.
- **missing:** a durable decision-feedback record joined to each action (the current approval contract is not wired to the relay); policy versioning and owner approval for candidate rules; a compact feedback prompt/response path on the pendant; fleet-memory writer or another cross-body persistence path

### "Protect my attention for the whole day: batch low-value things, spend an interruption only when its value justifies it, and tell me when you deferred something important."
- **useful because:** Current triage scores each event, but it has no daily accounting for interruption cost, repeated context switches, or the fact that three individually reasonable alerts can ruin an hour. This makes the pendant feel like an assistant rather than another notification source.
- **path:** pendant → relay → mac → browser
- **model tier:** Use deterministic scoring for the daily attention budget, deduplication, quiet windows, and batching. Use a cheap background model only to summarize a batch. Realtime speaks the compact batch or the explicit 'deferred important item' notice.
- **latency:** Arbitrate each event in under 50 ms locally/relay-side. Batch ordinary items at the next scheduled boundary; urgent items can interrupt within 2 seconds. No model call for the decision itself.
- **cost:** Usually under $0.01 per batch, dominated by one short summarization call; single-event decisions are effectively free.
- **security:** The owner must set the budget, quiet windows, and what qualifies as urgent; ship conservative defaults but label them as defaults. Never use silence as proof that the source was empty or readable. Keep private content out of the spoken deferral notice, and make every decision explainable and reversible.
- **missing:** durable daily attention ledger with interruption cost, deferral, acknowledgement, and outcome; a real policy editor that extends /briefing/policy rather than inventing another policy store; source-health/permission evidence in each event so unreadable calendar/mail cannot be treated as clear; a single scheduler/arbiter ingestion point; current routines and triage jobs notify independently

### "Give me a temporary delegation window: for the next 20 minutes, handle only the routine, reversible things I name across my Mac and browser, then automatically revoke that authority everywhere and tell me what you left untouched."
- **useful because:** Today permission and autonomy are mostly per-action decisions, so the owner must repeatedly approve harmless work or risk leaving broad authority alive after the situation changes. A short, scoped lease would let them walk, drive, or focus while preserving a hard boundary around sending, deleting, spending, credentials, and other irreversible effects.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime parses the spoken scope and confirms the compact lease summary. A deterministic policy engine enforces target/action/audience/expiry constraints on every surface; a background model may classify ambiguous routine work but may not widen the lease. The relay is the expiry authority, Mac/browser enforce the lease token, and the pendant can cancel it with the existing stop/physical-consent mechanisms.
- **latency:** Issue or cancel the lease in under 1 second; enforcement adds under 50 ms per action. Expiry must work even if the pendant or Mac link drops, with all surfaces failing closed when the lease cannot be refreshed.
- **cost:** Usually below $0.01 per lease, dominated by one short realtime interpretation; enforcement and expiry are deterministic. No ongoing model cost for routine actions.
- **security:** Lease scope must be an explicit allowlist of action kinds, targets, and maximum spend (default zero), with a hard upper bound and nonce-based replay protection. It must never authorize send/delete/purchase/credential entry or silently convert a draft into a mutation. Every action records lease ID, matched rule, evidence, and expiry; the owner can revoke immediately and inspect the complete audit. Unknown or stale lease means ASK, not ACT.
- **missing:** a durable, relay-held delegation lease with monotonic expiry and revocation epoch; cross-surface lease propagation and enforcement in Mac and Safari before dispatch, not merely in the model prompt; a real relay↔Mac/browser correlation key (current IDs do not form a foreign key); an owner-facing lease editor and spoken readback that never reveals private target content; job leases/requeue so expiry and cancellation remain authoritative when a worker dies


## Changes it proposed to its own stack

### `integration` — Install a fail-closed 'blind-spot contract' between perception, judgement, and speech. Every answer that implies absence ('nothing waiting', 'calendar is clear', 'all done') must carry source-readability evidence and a freshness bound. If a permission, browser session, relay, or device feed is unreadable, the system must say what it could not inspect, suppress the all-clear claim, and offer a bounded fallback. Make this a shared enforcement point used by notifications, day-plan, briefings, catchup, and pendant speech—not another triage module.
- **owner gets:** The owner should be able to trust a quiet answer. Today an unauthorised EventKit read can look exactly like an empty calendar, and several speech paths have no confidentiality or uncertainty gate. This change prevents reassuring fiction and tells the owner precisely what remains unknown.
- effort: Medium: define a small typed evidence contract, thread it through existing readers and speech entry points, add regression cases for denied permissions/offline browser/stale relay, and expose a compact spoken/dashboard explanation.  ·  risk: Initially produces more 'I could not check that' responses and may surface false positives if freshness thresholds are wrong. Recover by keeping the old result internally, making the contract inspectable, and allowing an owner-set freshness policy; never downgrade unreadable to empty.
- cost: Negligible runtime cost; one deterministic validation per answer. A short fallback explanation may add a few realtime tokens only when a source is unavailable.  ·  latency: Under 10 ms for local validation; unavailable-source fallbacks should not wait on retries unless explicitly requested.
- security: Improves privacy by preventing sensitive fallback content from being spoken and makes source provenance explicit. It must not turn sensitivity labels into access permissions.
- depends on: A shared source-readability/freshness result from Mac and browser adapters; Threading evidence references through briefing, day-plan, notification, and pendantSpeech paths; Owner-editable freshness and disclosure policy with conservative defaults


## What it asked for

_Nothing._
## Its own summary

Discovered the live inventory and proposed three non-duplicate owner capabilities: (1) verify real-world postconditions after actions rather than trusting execution receipts, (2) learn scoped, inspectable decision rules from explicit owner approvals/rejections, and (3) a whole-day attention budget that batches and explains deferrals. The attention-budget capability is the strongest candidate for the system's most valuable everyday behavior. The Mac/browser are currently usable, but no pendant is present.

**Biggest unknown:** Personal policy values are still intentionally unset: the owner's interruption budget/quiet windows/urgency definition and disclosure boundary. I will not invent them; the system needs conservative labeled defaults plus an owner-editable policy. Technically, the missing pieces are durable cross-surface job correlation, a real relay-backed approval/feedback writer, postcondition verifier adapters, and one scheduler/arbiter ingestion point.

