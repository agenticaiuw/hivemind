# Harness derivation — faculty-judgement — round 84

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Did that actually happen?” — after you do something across my Mac or logged-in browser, prove the resulting state changed, tell me what was verified and where, and flag any mismatch instead of calling it done."
- **useful because:** Today a job receipt proves that our agent emitted an action, not that the outside world accepted it. This closes the trust gap: the pendant can ask once, the Mac can act, the browser can reread the authoritative page or app state, and the relay can return a short spoken proof (or an honest unresolved status). It is especially valuable for reminders, uploads, reservations, and form submissions where silent failure is costly.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use the cheap/background model to compile a read-only verification plan and compare before/after evidence; reserve realtime only for the owner's spoken question and final discrepancy explanation.
- **latency:** Normal actions remain unchanged; verification should complete within 5–15 seconds, with a pendant answer immediately saying “action sent; checking.” Long checks continue as a durable relay job and notify only on mismatch or completion.
- **cost:** About $0.01–$0.04 per verification, dominated by model comparison of compact typed evidence; browser/Mac reads and relay storage are negligible.
- **security:** Verification must be read-only and scoped to the same tab/app/account that the action touched; never expose unrelated private page content in speech or dashboard. Keep before/after snippets or hashes with TTL and redact secrets. Irreversible actions still require the existing owner confirmation before execution; verification is not confirmation.
- **missing:** A cross-surface verification-plan compiler mapping an action receipt to an authoritative read-back target and success predicate; Typed before/after evidence records with source, timestamp, locator, and confidence, plus mismatch states in jobs/receipts; A durable retry/timeout policy and pendant wording for pending, verified, contradictory, and unverifiable outcomes

### "“Before I send this, make sure it is going to the right person and account.”"
- **useful because:** A confirmation gate answers whether the owner approved an action, but not whether the draft is addressed to the intended Alex, the correct work account, or the right thread. The pendant can notice the request in speech, the Mac/browser can resolve the visible recipient and account context, and the system can catch a near-match or cross-account mistake before anything leaves.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use a low-cost model for entity matching and deterministic account/recipient checks; realtime is used only to ask a short disambiguation question when confidence is below threshold.
- **latency:** 2–5 seconds for checks against already-open app/browser context; if ambiguous, pause before send and ask one spoken question. Never delay drafting or previewing when no send is requested.
- **cost:** About $0.005–$0.02 per check, mostly entity resolution; local deterministic checks should handle the common case without model cost.
- **security:** Read only recipient names, addresses, account labels, and thread metadata needed for the check; redact message bodies by default. Never infer permission to send. A mismatch or low-confidence match blocks the send and shows exact conflicting fields; the owner must explicitly choose the target.
- **missing:** A recipient/account identity resolver shared by AppleScript mail/calendar and authenticated browser sessions; A pre-send gate contract that accepts the chosen entity, confidence, and visible evidence, and blocks downstream execution on mismatch; A compact pendant disambiguation UI/voice grammar for selecting among two or three candidates

### "“Why did I agree to this, and are the reasons I had then still true?”"
- **useful because:** When a commitment feels wrong later, the owner cannot currently reconstruct the evidence and assumptions behind it without manually searching email, calendar, notes, and logged-in web threads. This would create a bounded, cited decision history across those surfaces, distinguish explicit facts from inferred assumptions, and identify which assumptions have since changed—without pretending to know the owner's inner motives.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → dashboard
- **model tier:** Use a cheaper background model to collect and cluster dated evidence and test assumptions; use realtime only to clarify the commitment the owner means and deliver a short spoken conclusion.
- **latency:** A first spoken answer in 5 seconds from cached indexes, followed by a deeper cited reconstruction in under 2 minutes. No unsolicited monitoring; run only when asked or explicitly scheduled.
- **cost:** Approximately $0.03–$0.15 per reconstruction, dominated by retrieval and synthesis across private sources; local indexing and cached evidence should reduce repeated costs.
- **security:** This is unusually sensitive personal history. Search only sources and date ranges explicitly authorized for the request, keep raw messages on the Mac/browser where possible, return citations and short excerpts rather than bulk content, and give the owner deletion and redaction controls. Never infer mental state or expose the reconstruction to another person without confirmation.
- **missing:** A cross-surface decision-history index linking commitments to the dated messages, calendar events, notes, and browser evidence that preceded them; An assumption ledger that labels each claim as explicit, inferred, or unknown and can re-check its current status; A privacy-scoped retrieval API with source/date limits, redaction, retention, and owner-visible provenance


## Changes it proposed to its own stack

### `integration` — Add a receipt-to-proof verifier between the existing executor and relay: every mutating action may declare a read-only verification target (Mac diagnostic, reminder lookup, browser tab/DOM locator, or app state) and a typed success predicate. Persist a compact before snapshot, action receipt, after snapshot, evidence hash/source/timestamp, and one of verified, contradicted, pending, or unverifiable. Re-run only idempotent reads; never retry the mutation. Expose proof in GET /jobs/:jobId/receipts and relay_job_status, and have the pendant speak the short result.
- **owner gets:** The owner stops hearing “done” when the system only knows “clicked” or “request accepted.” They get a truthful answer about the state that matters, with a precise reason when it cannot be proven and an opportunity to fix it.
- effort: Medium: typed verifier contracts in the relay plus adapters for existing Mac and browser result formats, receipt schema migration, and a small dashboard timeline.  ·  risk: A stale or wrong read target could falsely claim success. Require source affinity, freshness bounds, explicit predicates, and downgrade to unverifiable on ambiguity. Recovery is a read-only retry or owner review; the original mutation is never replayed automatically.
- cost: Low storage and read requests; roughly $0.01–$0.04 for model-assisted predicate compilation/comparison, preferably cached and using a cheaper model.  ·  latency: Adds typically 1–5 seconds for a read-back; long-running checks become pending jobs and do not block the initial action acknowledgment.
- security: Evidence is scoped to the originating tab/app/account, redacted, hashed where possible, and expires quickly. No new write authority; irreversible actions retain existing confirmation gates.
- depends on: Existing action receipts/jobs and browser tab/session affinity must expose an originating surface and action intent; Mac and browser adapters need stable typed read-only state responses; Owner confirmation policy for irreversible mutations remains authoritative


## What it asked for

_Nothing._
