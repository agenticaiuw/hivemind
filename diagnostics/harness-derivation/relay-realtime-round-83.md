# Harness derivation — relay-realtime — round 83

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch for a specific condition and alert me only when it becomes true, even if I’m offline."
- **useful because:** This turns the pendant into a quiet assistant: you set a watch once, then you only hear from it when it matters. It reduces noise and fits being away from the Mac.
- **path:** relay → mac-planner → browser → faculty-judgement → faculty-perception
- **model tier:** Realtime for setting the watch. Cheaper background model for evaluation. Browser/computer surfaces for the actual checks.
- **latency:** Seconds to set up. Checks can run on a schedule; alerts must be near-real-time when the condition flips.
- **cost:** Most cost is in repeated page checks and maintaining authenticated sessions. Use exponential backoff and change detection to reduce churn.
- **security:** Requires careful handling of authenticated sessions and sensitive page content. Alerts should be minimal and avoid reading out secrets.
- **missing:** A scheduler (cron or durable alarms) to run checks; A condition DSL or safe templating for what to watch; Server-side browser automation implementation (server_browser_actions) or reliable browser session execution; Secure storage for watch definitions and credentials/session tokens; An alert delivery path to the pendant with persistence and replay when offline

### "“Handle this as one safe transaction: find the invoice in the authenticated browser, prepare the matching email draft on my Mac, and tell me the exact attachment, recipient, and text. If I lose LTE or interrupt you, resume from the last completed step without repeating or duplicating anything.”"
- **useful because:** Today a browser lookup, Mac mutation, and voice conversation are separate jobs. A worn owner cannot tell whether a dropped connection left a draft, whether retrying will duplicate work, or which evidence produced the draft. A cross-surface transaction journal would make long spoken requests dependable while the owner is away from the Mac: each step has an idempotency key, cited evidence, an explicit checkpoint, and a spoken resumable status.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Use relay-realtime only to collect the request, announce checkpoints, and answer short status questions; use the cheaper Mac planner and browser extraction models for the actual work. No model should infer completion: completion comes from typed receipts and checkpoint state.
- **latency:** Acknowledge within 500 ms. Stream progress at each checkpoint; browser/Mac work may take tens of seconds. Reconnect/resume should answer from the journal in under 2 seconds and must never replay a committed side effect.
- **cost:** Roughly one realtime turn plus 2–4 planner/extraction calls; about $0.03–$0.15 per transaction depending on page length and retries. The dominant cost is authenticated-page extraction and planner context, not the journal.
- **security:** Authenticated page text, invoice data, and draft contents leave the browser/Mac only to the relay's encrypted job store and the owner’s session. Store minimal encrypted evidence with expiry and redact secrets. A draft is reversible, but sending or other external mutations must remain a separate explicit user command; expose exactly which steps were committed. Recovery must use idempotency keys and verify the target tab/account before resuming.
- **missing:** A durable cross-surface transaction journal with per-step idempotency keys, leases, checkpoints, and compensating/reconciliation status; Typed receipts that can be correlated across browser command IDs, Mac action receipts, and voice-run IDs; A reconnect/resume protocol from the pendant that can report and continue a checkpoint without replaying completed mutations; A small dashboard view showing evidence, committed steps, pending step, and expiry; Browser and Mac adapters that acknowledge a committed receipt before the next side effect

### "“What exactly changed because of the last thing you did? Show me the before-and-after evidence for the browser and Mac, and read me only the differences.”"
- **useful because:** Current receipts can say that an action ran, but they do not let a remote owner audit the resulting UI or distinguish an intended change from an accidental one. A short-lived, cross-surface evidence capsule would capture the relevant before/after DOM or screenshot region and Mac UI state, normalize the differences, and let the pendant answer an audit question without rerunning the task.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic DOM/UI diffing and image-region comparison first. Use a cheaper background model to label differences; use relay-realtime only to answer the owner’s spoken query and summarize already-produced evidence.
- **latency:** Capture must add less than 2 seconds around an action. A spoken audit answer should begin within 1 second from cached evidence; opening a dashboard evidence capsule may take up to 5 seconds.
- **cost:** Usually $0.005–$0.03 per audited action for storage and optional small-model labeling; no realtime model call is needed until the owner asks for a spoken explanation. Storage dominates for screenshot-heavy capsules.
- **security:** Evidence may contain email, financial, or authenticated-page data. Encrypt capsules per owner/session, redact passwords and tokens before persistence, retain only a bounded region and short TTL, and expose a delete-now control. Never claim a visual diff proves a hidden backend side effect; label DOM/UI evidence versus receipt evidence separately.
- **missing:** A common evidence-capsule schema linking one action receipt to before/after browser and Mac artifacts; Browser capture of bounded DOM/screenshot regions immediately before and after a command; Mac-vision capture of bounded focused-window regions and accessibility-tree deltas; Deterministic redaction, encryption, TTL deletion, and a diff service; A pendant query that resolves “last thing” to a receipt/evidence capsule and speaks a concise diff; Dashboard playback with side-by-side before/after and source labels


## What it asked for

_Nothing._
## Its own summary

Recorded two new proposals. (1) A cross-surface, idempotent transaction journal with resumable checkpoints so a pendant request spanning authenticated browser work and Mac drafting can survive LTE loss/interruption without replaying side effects. It needs durable step receipts, correlation, reconnect/resume, and adapters. (2) A short-lived evidence capsule that captures bounded before/after browser DOM/screenshot and Mac UI/accessibility evidence, redacts and expires it, and lets the owner ask the pendant exactly what changed. Both are beyond merely executing jobs or reporting receipts.

**Biggest unknown:** Whether the relay already has an undocumented durable evidence-capture or transaction-correlation surface; discovery was explicitly unavailable this round, so the proposals identify the missing end-to-end behavior rather than claiming every underlying route is absent.

