# Harness derivation — mac-terminal — round 208

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac hardware observability** — The newly granted mac_usb_serial_diagnostics and mac_read_diagnostics schemas still do not resolve to an implementation in the live inventory. The Mac has no callable serial diagnostic capability despite the physical USB paths being specified; broad Mac diagnostics likewise resolve only approximately to existing health/status routes.
  - evidence: mac_usb_serial_diagnostics returned unresolved (best action:get_mac_status 0.226); mac_read_diagnostics returned unresolved (best GET /health 0.390).

## Capabilities it proposed

### "When my Mac agent dies or the laptop reboots, resume the safe unfinished task automatically and tell me on the pendant exactly what was resumed, skipped, or needs me."
- **useful because:** Today a job can remain 'processing' forever after a crash, while its durable ledger is never closed and nothing resumes it. The owner should not have to reconstruct a half-finished task from logs, especially when away from the keyboard.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** background for boot reconciliation and replay classification; realtime only for the short pendant explanation
- **latency:** Reconcile within 10 seconds of local-agent boot; pendant status within 2 seconds after reconnect
- **cost:** Near-zero model cost for deterministic ledger reconciliation; one short realtime response only if the owner asks for details
- **security:** Only replay actions explicitly classified replay-safe and whose preconditions still match; never repeat unknown shell, email, delete, or external mutation automatically. Send only action summaries and hashes through relay, not shell environment or secrets. Owner confirmation remains available for ambiguous steps.
- **missing:** boot-time reconciliation that marks stale processing jobs honestly; orchestrator closeLedger on every terminal path; jobId propagation into planMeta and ledger; resume planner that checks preState/postState and emits a bounded safe action list; pendant push for resumed/skipped/blocked result

### "Did that actually happen? Give me one trustworthy answer that joins the Mac command result, the browser page it changed, and the relay delivery receipt, and point out any disagreement instead of saying 'done'."
- **useful because:** A completion message currently can omit the shell exit code, cannot join a job to its ledger, and browser provenance is separate from Mac receipts. The owner needs a verifiable answer when an external action matters, not a plausible model summary.
- **path:** mac-planner → browser-extension → relay-realtime → pendant → dashboard
- **model tier:** background deterministic receipt join plus cheap summarizer; realtime only when spoken through the pendant
- **latency:** Return a compact proof card in under 3 seconds for existing records; allow 10 seconds for a fresh browser verification
- **cost:** Mostly local JSON joins and hashes; one small summarization call only for spoken wording
- **security:** Redact command arguments, cookies, tokens, and page contents by default. Show source URLs and bounded field-level diffs, never wholesale authenticated page data. Require explicit owner request before opening a page to verify a mutation.
- **missing:** exit code, pid, argv/exec-vs-shell metadata and redacted environment fingerprint in shell receipt; stable jobId-to-ledger correlation and browser command/provenance correlation IDs; a verification action that reads only the claimed browser fields and compares expected postcondition; single proof-card schema exposed to voice and dashboard

### "Watch this signed-in page while I'm away, and interrupt me only if the exact thing I care about changes; when you alert me, include the old and new values and a button to take the obvious Mac action."
- **useful because:** The browser can hold sessions the relay and Mac cannot, while the pendant is the only always-with-owner alert surface. A change-triggered watch avoids periodic noisy briefings and turns a private authenticated session into a useful, auditable interrupt.
- **path:** pendant → browser-extension → relay-realtime → mac-planner → dashboard
- **model tier:** background watcher with deterministic DOM/field diffing; realtime only to phrase an urgent alert
- **latency:** Detect within the configured poll interval (15–60 seconds); alert pendant within 2 seconds of detection
- **cost:** Low: browser polling and field hashing dominate; use a cheap model only when a selector change needs semantic classification
- **security:** Watch only a URL and fields the owner explicitly names; store hashes and minimal before/after values, not full pages. Pause on authentication expiry or unexpected navigation. Any resulting Mac action is shown as a concrete action and logged with the triggering evidence.
- **missing:** owner-configurable page-watch records with field selectors and semantic predicates; browser-side authenticated polling with before/after evidence capsules; relay durable alert with deduplication and quiet hours; one-tap action binding from alert to a typed Mac action; expiry and re-authentication handling

### "Before I start talking, tell me whether the pendant, audio bridge, Mac agent, network, and browser session are all truly ready—and if not, fix only what can be fixed automatically and say exactly what is missing."
- **useful because:** Readiness is currently fragmented: the Mac health route can be green while the physical chips are absent, the browser session is stale, or audio acknowledgements are stalled. A single preflight prevents the owner from speaking into a dead path and gives a useful recovery plan.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → dashboard
- **model tier:** deterministic health aggregation; no expensive model unless explaining a compound failure
- **latency:** Complete in under 2 seconds on USB-connected bench hardware and under 5 seconds when checking LTE/browser session state
- **cost:** Negligible local checks; no model call for healthy or single-cause failures
- **security:** Expose only health, versions, counters, and ages—not audio, page content, tokens, or shell environment. Repairs are limited to restarting the local audio/relay transport and refreshing a browser session; never submit forms or mutate external data as part of preflight.
- **missing:** live serial health/counter reader for both connected chips; one authenticated aggregate preflight endpoint with freshness and transport identity; audio bridge frame-ack and encoder timing counters surfaced to the Mac agent; browser session freshness/auth-expiry probe; pendant-readable concise failure codes and recovery actions

### "Only interrupt me when something is worth breaking my attention for: combine the pendant's urgency signal, my current Mac activity, calendar focus, browser task state, and recent alerts into one ranked queue, then deliver each item on the least disruptive surface and explain why it crossed the threshold."
- **useful because:** Today each subsystem can notify independently, so the owner gets duplicate or badly timed interruptions. A worn device knows whether the owner is available, the Mac knows what they are doing, and browser/relay know what changed; none can arbitrate attention across all of them.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic urgency, deduplication, quiet-hours, and surface selection first; background model only for ambiguous priority classification; realtime only for the final spoken interruption.
- **latency:** Ingest and deduplicate events within 2 seconds; deliver urgent alerts within 3 seconds; nonurgent queue review can be delayed by 5 minutes.
- **cost:** Low: event joins and hashes dominate; use a small background model only for novel message classification.
- **security:** Keep page contents and message bodies local to their owning surface; send the relay only urgency, source, digest, and minimal excerpt. The owner must be able to inspect why an alert was promoted, suppressed, or merged. Never silently discard high-confidence safety or deadline alerts.
- **missing:** shared event envelope with source, urgency, deadline, digest, and deduplication key; presence/focus signal from the pendant and foreground-task signal from the Mac; cross-surface priority arbitration and suppression history; delivery receipts and escalation rules across pendant, Mac, and browser; owner-editable attention policy and an explanation view

### "Before you change anything, show me the likely consequences across my Mac, signed-in browser sessions, and pending relay jobs—including conflicts with work already underway—and let me compare two plans without executing either."
- **useful because:** Existing planning previews describe actions, but they do not model cross-surface interference: a browser download can race a Mac file move, a retry can duplicate a relay job, or a focus change can invalidate a plan. The owner needs a consequence map, not merely a list of commands.
- **path:** mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic snapshot/diff and dependency analysis; background model only to explain genuinely ambiguous consequences.
- **latency:** Produce two alternatives and a conflict map in under 8 seconds; never execute during analysis.
- **cost:** Low-to-moderate local computation; model cost limited to summarizing the resulting graph.
- **security:** Snapshots must redact credentials, cookies, message bodies, and unrelated page data. Treat authenticated browser state as opaque capabilities. Preserve the owner’s choice and ensure the comparison cannot enqueue or dispatch work accidentally.
- **missing:** cross-surface snapshot format for Mac state, browser state, and relay jobs; resource/dependency graph and conflict detector; two-plan counterfactual evaluator with explicit non-execution invariant; staleness markers showing which observations changed since the comparison; dashboard and pendant-readable summary of consequences

### "Take this goal, not just these steps: keep working across my Mac and signed-in browser until the stated result is true, stop when a boundary or uncertainty is reached, and come back with evidence—not a claim that the last command ran."
- **useful because:** The owner thinks in outcomes, while current execution is mostly a one-shot action list. A browser session may require several pages, the Mac may need local preparation, and relay delivery may fail between steps. A bounded mission would make the system useful for real unattended work without pretending uncertainty is success.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background planner/state machine for the long-running mission; cheap deterministic checks at every step; realtime only for a blocking question or final spoken result.
- **latency:** Start within 5 seconds, then progress asynchronously; heartbeat every 30 seconds and immediate escalation on a boundary, failed postcondition, or lost surface.
- **cost:** Moderate: mostly deterministic orchestration, with small background model calls only when the next step is ambiguous; avoid realtime for the mission itself.
- **security:** The mission contract must name allowed surfaces, data boundaries, time limit, maximum retries, and forbidden side effects. Browser credentials remain in the extension; shell secrets remain on the Mac. Stop before sending, deleting, purchasing, or submitting anything not explicitly covered. Every transition needs an evidence receipt and a revocation path.
- **missing:** goal contract with success predicates, stop conditions, budget, expiry, and allowed side effects; persistent mission state spanning relay, Mac, and browser; postcondition verifier rather than last-action success; interactive pendant question/answer checkpoints; mission-wide receipts, retry budget, and owner revocation


## What it asked for

_Nothing._
