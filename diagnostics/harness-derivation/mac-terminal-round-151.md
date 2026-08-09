# Harness derivation — mac-terminal — round 151

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “don’t interrupt me unless it matters,” have the pendant and Mac decide what deserves an interruption, and give me one concise catch-up when I become available."
- **useful because:** The owner gets genuinely quiet computing: Calendar/mail/browser events can accumulate while the Mac knows the foreground app and the pendant knows whether a conversation is active. Only high-confidence urgent items break through; everything else is summarized at the next natural availability instead of competing with work.
- **path:** pendant → mac-planner → browser-harness → relay-realtime → dashboard
- **model tier:** Cheap background model classifies incoming events and drafts a digest; realtime is used only for the one urgent spoken interruption or the owner's catch-up question. Deterministic rules handle active recording, foreground app, and quiet windows.
- **latency:** Urgent classification under 2 seconds; a catch-up digest under 5 seconds. No model call at all for events filtered by deterministic quiet-state rules.
- **cost:** Usually <$0.01/day if event batching is used; cost is dominated by one small classifier/digest call per batch, not by the pendant conversation tier.
- **security:** Event titles, browser metadata, and foreground-app state leave the Mac only when needed for classification. Authenticated page contents stay in the browser harness; default to titles and sender/priority, redact secrets, and require explicit opt-in for page-body escalation.
- **missing:** A durable interruption policy with urgency, quiet-state, and expiry fields; An event-ingest bridge from Calendar/Mail/browser watches into one batched queue; A pendant availability signal distinct from merely being connected; A spoken catch-up endpoint and a way to mark items handled

### "When a Mac or browser task fails, press the pendant button once and say “fix that”; have the system capture what failed, repair it, and tell me exactly what changed or why it stopped."
- **useful because:** Today a failed shell/browser action leaves the owner to reconstruct the command, working directory, tab, and error. A physical request plus an evidence capsule turns failure into a recoverable interaction: the Mac supplies the trace and UI state, the browser supplies the authenticated tab context, and the relay can reason while the owner is away.
- **path:** pendant → mac-planner → mac-vision → browser-harness → relay-realtime → dashboard
- **model tier:** A cheap background model extracts the failure and proposes a bounded repair; realtime is reserved for an ambiguous repair question or spoken explanation. Deterministic retry is used first for known transient classes.
- **latency:** Capture under 1 second; first repair attempt within 10 seconds; a human-readable result within 20 seconds. Long repairs become a durable relay job with progress updates.
- **cost:** <$0.03 per incident in the normal case; the dominant cost is a single repair-planning call with a compact evidence capsule, not retransmitting full logs or screenshots.
- **security:** Capsules may contain command output, file paths, URLs, and authenticated page text. Keep raw evidence on the Mac, send only redacted excerpts and hashes to relay, and require explicit confirmation before destructive or externally visible repair. Never replay a shell action solely because it appears in a prior capsule.
- **missing:** A failure-capsule schema joining job, ledger, receipt, cwd, exit code, stdout/stderr excerpt, screenshot, and browser session; Boot-time reconciliation and real process cancellation for run_shell; Semantic postcondition checks before declaring a repair successful; A pendant button intent that references the last failed job without inventing completion

### "While I work, notice a repeated sequence I perform across Safari and Mac apps, and later ask me once whether to turn that exact sequence into a spoken command I can run from the pendant."
- **useful because:** The owner should not have to design automations. A browser login, file export, rename, and notification often spans surfaces no single recorder can see. Capturing the sequence as a reviewable recipe lets a worn-button command reproduce useful personal workflows without exposing credentials or silently automating surprising steps.
- **path:** pendant → mac-planner → browser-extension → mac-vision → relay-realtime → dashboard
- **model tier:** A cheap background model clusters action traces and names candidate recipes; realtime is only used for the short spoken proposal and the owner's yes/no. Replay uses deterministic typed actions, with vision fallback only when selectors drift.
- **latency:** Trace capture adds under 50 ms per action. Candidate detection runs in batches every few hours. Replay should begin within 2 seconds and report each step as it completes.
- **cost:** <$0.02 per candidate workflow; storage and clustering dominate, while replay is mostly local execution with no model call when selectors remain valid.
- **security:** Never record keystrokes, passwords, page bodies, or raw shell environment. Store redacted action schemas and selector hashes locally; show the complete recipe and affected domains/apps in the dashboard before enabling it. Browser recipes must bind to the originating authenticated session and refuse a different account.
- **missing:** A cross-surface trace recorder with secret/PII redaction and explicit start/stop boundaries; A recipe compiler that converts traces to stable browser selectors and typed Mac actions; A dry-run simulator and drift detector that pauses on changed page semantics; A pendant command registry with disable/delete controls and per-recipe receipts

### "Do this across my Mac and browser, and do not tell me it succeeded until you can verify the result I asked for; if verification fails, keep working or explain the exact blocker."
- **useful because:** A receipt saying an action ran is not the same as the owner's goal being true. This would make the system dependable: the pendant supplies intent, the Mac and browser act, and a second observation pass proves the postcondition before the spoken completion claim.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Cheap deterministic checks handle known outcomes (file exists, app state, URL/title, text present). A slower background model interprets visual or semantic postconditions; realtime only speaks the final verified result or asks one clarification.
- **latency:** Simple checks add under 1 second; visual checks under 8 seconds. If the postcondition cannot be observed, report “unverified” within 10 seconds rather than claiming success.
- **cost:** <$0.02 for most tasks; visual/semantic verification is the dominant model cost and should be invoked only when deterministic checks fail.
- **security:** Verification may read sensitive screen/page content. Keep snapshots local, send hashes or narrow excerpts to relay, and make the requested postcondition explicit so the verifier cannot broaden access. Externally visible actions still need the owner's existing policy treatment.
- **missing:** A required postcondition field on spoken and delegated intents; A verifier interface that can inspect Mac state and authenticated browser state without executing; A state-diff record linking precondition, action receipt, observation, and verdict; A truthful pendant completion state that distinguishes verified, executed-but-unverified, and failed

### "Keep working on this for me even when my Mac sleeps: monitor the authenticated browser page or Mac task I named, wake or reconnect when necessary, and tell me through the pendant only when the specific condition I described becomes true."
- **useful because:** Today the system can act through the Mac while it is reachable, or keep relay state while the Mac is unavailable, but it cannot make a durable promise across that boundary. The owner should be able to delegate a real outcome—such as waiting for a page change, a build to finish, or a file to appear—without leaving the laptop awake or repeatedly restating the request.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** A background model turns the spoken request into a compact condition and schedule. Deterministic polling, file checks, and browser assertions do the monitoring. Realtime is used only to notify the owner or resolve an ambiguous condition.
- **latency:** Reconnect or wake attempt within 30 seconds of a due check; simple conditions reported within one polling interval. The owner should never wait on a live model turn while the relay is monitoring.
- **cost:** Usually under $0.05 per day per active watch; cost is dominated by Mac wake/reconnect and authenticated browser polling, with model calls limited to setup and exceptional interpretation.
- **security:** The relay must never receive reusable browser cookies or shell credentials. The browser extension should issue a narrowly scoped, expiring watch capability whose checks execute locally on the Mac; transmit only condition results and redacted evidence. Require explicit setup for every watched origin and automatic expiry.
- **missing:** A durable cross-node watch lease with expiry, retries, and an owner-visible lifecycle; A Mac sleep/wake or launch-agent handoff that resumes the lease without duplicating actions; A browser-side scoped assertion worker that can inspect an already-authenticated session without exporting it; A relay scheduler and notification route that can distinguish condition-true, unavailable, and expired; A pendant command and truthful status indicating watching, paused, triggered, or unable to verify

### "When I walk away with the pendant, hide sensitive browser and Mac content, and restore it when I return; if the pendant link is uncertain, leave the screen protected and tell me why."
- **useful because:** The pendant is the owner's physical presence token, but today the Mac, browser, and wearable do not jointly enforce presence. This would protect authenticated tabs and private work during the ordinary moments when the owner leaves a laptop unlocked, without requiring them to remember a keyboard shortcut.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Firmware and Mac-side deterministic state machines do presence detection and protection; no model call is needed except optional natural-language explanation. Realtime can speak the reason only when the owner presses the button after a protected transition.
- **latency:** Protect within 2 seconds of confirmed departure or link loss; restore within 2 seconds of confirmed return. Require hysteresis so a brief USB/LTE packet gap does not flap the screen.
- **cost:** Near-zero API cost. The work is local event handling and browser/Mac control; the dominant cost is engineering and careful testing of false departures.
- **security:** A lost or cloned pendant must not become an unlock token. Use a rotating authenticated challenge, require local confirmation for first pairing, and make return unlock a short-lived presence assertion rather than a reusable secret. Never send screen contents to the relay.
- **missing:** Authenticated proximity/presence attestation over the real USB and eventual LTE transports; A Mac privacy action that locks or masks selected windows and restores them safely; A browser extension command to blur/replace sensitive page content without destroying session state; A fail-closed state machine with hysteresis, audit receipts, and recovery after Mac or pendant restart

### "Watch this authenticated checkout or booking page and complete it only if the final terms stay within the limits I said; otherwise keep the reservation or draft ready and ask me through the pendant."
- **useful because:** The owner can delegate a time-sensitive purchase or booking without handing over unrestricted authority. The browser contributes the logged-in session, the Mac verifies the final page, the relay waits while the owner is away, and the pendant provides a compact approval or refusal channel when terms change.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Deterministic extraction and arithmetic enforce price, date, quantity, and merchant constraints. A cheap model handles ambiguous page layouts; realtime is used only for the final spoken confirmation when the terms are within policy.
- **latency:** Evaluate a changed checkout within 5 seconds. Hold or submit within 15 seconds after an explicit approval. If the page cannot be verified, stop rather than improvise.
- **cost:** <$0.05 per monitored transaction; browser polling and visual fallback dominate, while model use is limited to layout ambiguity.
- **security:** This touches money, reservations, and authenticated accounts. Store no credentials or payment data outside the browser. Bind the policy to the exact merchant, item, currency, quantity, and expiry; show a final spoken/read-back summary and require explicit approval for any charge unless the owner separately enabled a narrowly bounded auto-complete policy. Record a receipt and proof of final terms.
- **missing:** A policy-bound transaction state machine spanning browser and Mac; Reliable extraction and cryptographic capture of final terms before submission; A browser mechanism to hold a checkout safely without losing the authenticated session; A pendant confirmation protocol with expiry, replay protection, and clear pending/approved/declined states; Post-submit verification and compensation handling when a site reports ambiguous success


## What it asked for

_Nothing._
