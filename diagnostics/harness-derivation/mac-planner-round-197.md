# Harness derivation — mac-planner — round 197

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I press the pendant's bookmark button, make a private 'pick up where I left off' card from the active Mac app and browser tab, save it in my AI-Pendant-Workspace, and speak a one-sentence receipt; later I can say 'resume my last bookmark' to reopen the exact page/file."
- **useful because:** A physical bookmark is useful only if it captures the digital state the owner was looking at. This makes the pendant's moment marker bridge into a durable, resumable desktop checkpoint without requiring the owner to narrate what they were doing.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use the realtime model only to interpret the short bookmark command and produce the spoken receipt; use a cheap background model to title and summarize the captured state. Mac and browser harnesses provide deterministic URLs, app identity, and reopen actions.
- **latency:** Bookmark acknowledgement under 500 ms locally; capture and write within 3 seconds; resume action within 2 seconds after the spoken request.
- **cost:** About $0.002-$0.01 per bookmark, dominated by optional summarization; deterministic capture and file writing are negligible.
- **security:** Authenticated URLs and selected page titles may be sensitive. Store a redacted card by default, never page bodies or cookies, and require the owner's existing destructive policy only for reopening or mutating actions. Browser reads are allowed; card files remain in ~/AI-Pendant-Workspace.
- **missing:** A serial/event bridge that delivers the already-shipped offline_moment_bookmark event while USB-connected; A structured active-window/document identity read beyond the current coarse observe snapshot; A resume-card schema and a browser command to reopen a recorded tab

### "Before I buy anything or send anything from the browser, have the pendant read me the merchant or recipient, exact amount or attachment, and destination, then let one deliberate button press authorize the already-prepared action."
- **useful because:** It puts a human-verifiable checkpoint on the one class of Mac automation that can cause irreversible external harm, without making ordinary browsing cumbersome. The pendant is harder to mis-click than a background browser tab.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Cheap deterministic extraction should identify amount, recipient, URL, and attachment; realtime is used only to phrase the short spoken confirmation. No model should invent missing transaction fields.
- **latency:** Read-back within 2 seconds of detecting a send/buy form; execute within 1 second after the physical press.
- **cost:** Under $0.005 per check; most work is browser DOM extraction and Mac action execution.
- **security:** A button press must be bound to a displayed transaction hash and expire after 30 seconds, preventing replay or confused-deputy actions. Never transmit passwords, cookies, or full message bodies to the relay. Destructive actions remain confirmation-required under the owner's policy.
- **missing:** Browser-side extraction of a normalized transaction summary for send/purchase forms; A relay nonce/transaction-hash handshake tied to the pendant button event; A Mac executor action that accepts only the exact preflighted browser command

### "If an overnight routine fails, tell me why in one spoken sentence and leave a redacted repair report in my workspace: which node failed, the last successful step, the affected app or browser session, and one safe next action."
- **useful because:** Today a failed routine is an opaque status. This turns relay, Mac, and browser evidence into an actionable morning answer instead of making the owner reconstruct logs and stale sessions by hand.
- **path:** relay-realtime → mac-planner → browser-extension → pendant
- **model tier:** Use a background model to correlate receipts and logs; use realtime only if the owner asks follow-up questions. Evidence collection and redaction must be deterministic before summarization.
- **latency:** Generate the report within 10 seconds of failure detection; spoken alert should be one sentence and under 5 seconds.
- **cost:** Roughly $0.01-$0.04 per incident, dominated by background correlation; routine successes cost nothing extra.
- **security:** Reports must redact tokens, URLs with query secrets, mail bodies, and file contents. Do not auto-retry destructive steps; offer only idempotent diagnostics or a dry-run repair. Keep reports local in ~/AI-Pendant-Workspace and expose only the one-sentence finding over audio.
- **missing:** A failure-event subscription from routines/jobs to the relay; A common receipt envelope linking routine, pipeline, Mac job, and browser command IDs; A deterministic redaction-and-correlation worker

### "When I am on a checkout or send form, say 'read back the transaction' and have the pendant give me a compact spoken receipt of the exact total, recipient, destination, and what will be sent; if I press the button, carry out only that exact prepared action."
- **useful because:** This is a concrete safety affordance for authenticated browser sessions: the owner can verify a transaction while looking away from the screen, while the Mac still performs the action in the session only after physical authorization.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Use deterministic browser extraction and a small formatter; realtime speech synthesis/turn-taking only. Never use a language model to infer totals or recipients from ambiguous text.
- **latency:** Receipt in 1.5 seconds; button authorization expires after 30 seconds and execution result returns in 3 seconds.
- **cost:** About $0.001-$0.01 per transaction, mostly speech generation; browser extraction is local.
- **security:** Bind authorization to a canonical summary hash, origin, tab ID, and action payload; reject any DOM change after read-back. Do not include card numbers or credentials in relay payloads. Sending mail, deleting files, and purchases remain explicitly confirmable.
- **missing:** A browser extension transaction-summary schema and DOM adapters; A one-shot pendant authorization event transport over the currently USB-connected setup; Mac/browser executor support for hash-bound prepared actions

### "Before I commit to a date, delivery promise, or reply in the browser, tell me if it conflicts with my calendar, recent mail, or another open commitment, and identify the exact conflicting item in one short spoken sentence."
- **useful because:** The owner currently has to remember commitments scattered across browser sessions, mail, and calendar. Catching a contradiction at the moment of commitment prevents missed meetings and impossible promises; it is more valuable than another retrospective brief.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic extraction for the proposed date, recipient, duration, and obligation from the browser form. A cheap background model compares it with bounded Calendar/Mail evidence; realtime is reserved for the one-sentence warning and does not decide whether evidence exists.
- **latency:** Warning within 2 seconds after the owner asks to check; never block ordinary typing. A background refresh can update commitments every 15 minutes.
- **cost:** Approximately $0.005-$0.03 per explicit check, dominated by the small comparison model; local browser and Calendar/Mail reads are negligible.
- **security:** Send only normalized dates, subjects, and redacted snippets to the comparison worker; never forward credentials or full mail bodies. Do not automatically reject or send anything. The owner can dismiss a warning, and all warnings expire with the browser tab.
- **missing:** A browser adapter that emits a normalized proposed-commitment object before submission; A bounded cross-source commitment index joining mac_read_sources results with browser observations; A relay command that asks the pendant for an explicit check and returns a confidence plus cited conflicts


## Changes it proposed to its own stack

### `integration` — Add a commitment-evidence graph that records each browser commitment check as a short-lived, redacted relation between the proposed obligation, the Calendar/Mail evidence consulted, and the eventual send/result receipt. Expose it to the pendant so a later question such as 'why did you warn me?' returns the actual conflicting event rather than a model recollection.
- **owner gets:** Warnings become trustworthy and explainable. The owner can correct a bad conflict, see whether it was resolved, and stop repeatedly rechecking the same promise across devices.
- effort: Medium: normalized browser form adapters, a bounded commitment index, expiry and redaction rules, and a result-linking hook in the Mac/browser job ledger.  ·  risk: A stale or over-broad relation could create false warnings. Expire commitments aggressively, show the cited evidence, and allow local deletion; never infer a commitment from private content without an explicit check.
- cost: Low ongoing storage and model cost; roughly 1–3 KB per check plus the comparison call already needed for the capability.  ·  latency: Adds under 100 ms for local relation lookup; initial evidence comparison remains within the proposed 2-second check budget.
- security: Stores sensitive scheduling metadata, so keep the graph local or encrypted, redact bodies and tokens, and give each relation a TTL. Do not persist full page contents.
- depends on: The commitment-conflict check capability and normalized proposed-commitment schema; A browser result receipt containing a stable tab/action identifier; A bounded Calendar/Mail evidence projection


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: a pendant-authorized browser transaction read-back, automatic redacted diagnosis of failed overnight routines, and a physical-button-bound prepared-action protocol (the latter was flagged as close to an existing prepared-form idea, so it should be treated as an extension rather than a separate product). I also learned that the current live stack already exposes the required observation, browser, pipeline, job, journal, and execution routes; the missing work is the contracts between them, not more endpoints. Accessibility and Screen Recording are now verified, so UI inspection is no longer blocked.

**Biggest unknown:** The granted mac_serial_exchange request is still unavailable. Without a live USB-serial event/command tool, I cannot test the pendant's physical bookmark/authorization events or prove the end-to-end Mac-attached workflow. The next concrete need is a typed serial exchange capability (read framed events, send a bounded command, timeout, and return raw plus parsed receipt), followed by browser transaction-summary and routine-failure event schemas.

