# Harness derivation — browser-extension — round 251

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “catch me up on the things I left open,” read my authenticated Safari tabs, identify only items that need action, and give me a short spoken triage with links and due dates; if I ask, prepare (but do not send) the next action."
- **useful because:** This is the highest-value browser-only experience: the browser reaches sessions no server or Mac shell can safely reproduce, the relay turns scattered tabs into a useful answer, and the pendant makes it available while walking. It converts abandoned tabs into an actionable queue rather than another unread digest.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Use a cheap background extractor per tab and a small realtime model only for the owner's final spoken triage. Persist only short claims with URL/host provenance, never page bodies.
- **latency:** 10–20 seconds for an on-demand scan of up to 10 tabs; stream “I found 3 candidates” quickly, then speak the ranked result. Background refresh can run on a routine without realtime inference.
- **cost:** Roughly $0.01–$0.08 per scan depending on page count and extracted text; browser navigation and Mac execution dominate wall time, not tokens.
- **security:** Authenticated content leaves Safari only to the local relay pipeline. Use an explicit per-origin configuration that ships empty, redact secrets before model input, retain only the existing short-lived browser findings (24-hour TTL, 200-character cap), and never read or send forms during triage. Show source URLs so the owner can verify.
- **missing:** A browser tab inventory plus stable tab IDs exposed to the planner (the live extension currently has tabs but the granted wrapper is ambiguous between browser_list_tabs and browser_list_sessions); A bounded multi-tab extraction/ranking job with duplicate suppression; An owner-configurable empty per-origin read/extract/redact/never-store policy UI; A spoken-result-to-pendant delivery path for browser findings

### "On an authenticated billing or account page, let me say “check this against my records.” Extract the page’s amount, date, and account label, find matching local receipts or mail on the Mac, report discrepancies, and draft a reminder or dispute note without sending it."
- **useful because:** A browser session alone can see the bill but not the owner's local evidence; the Mac alone cannot enter the logged-in account. Together they turn a vague “is this charge right?” moment into a grounded answer, with the pendant available when the owner is away from the desk.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic page extraction and local metadata search first; use the background model to normalize merchant/date/amount and a realtime model only to explain a detected mismatch. Do not send raw page text to the expensive tier.
- **latency:** 30–60 seconds per case, with a progress update after browser extraction and a final result once local records are matched.
- **cost:** About $0.02–$0.12 per case; local search and browser round trips dominate, while model cost is limited to field normalization and discrepancy explanation.
- **security:** This handles financial data. Keep extraction scoped to the active origin and requested fields, redact account numbers, retain only a short claim and provenance under the existing browser TTL, and stop at a draft. The draft must visibly show recipients, amount, and text; sending remains an explicit separate action.
- **missing:** A structured field extractor that returns typed amount/date/merchant evidence rather than a free-form page dump; A Mac-side read-only search adapter for Mail/files/receipts with matching confidence and provenance; A join record linking browser evidence to local evidence without storing either full document; A dashboard view that shows the proposed dispute/reminder and its source traces

### "Before I commit anything on a logged-in website, say “rehearse this.” Show me exactly what would change, compare it with my Mac calendar/files, flag conflicts or duplicate commitments, and leave the browser at the final review screen for me."
- **useful because:** The browser is the only node that can reach the authenticated transaction, while the Mac is the only node with the owner's surrounding commitments. A rehearsal catches the expensive mistake—booking over an existing event, accepting a changed price, or uploading the wrong file—without inventing a confirmation gate for ordinary work.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use browser DOM/state capture plus deterministic diffing; query calendar/files locally; reserve the realtime model for a concise explanation of conflicts and the spoken pendant summary. No model should infer a click is safe from prose alone.
- **latency:** Under 20 seconds for a single page and one local-calendar lookup; up to 90 seconds for a multi-step flow. Keep the tab parked at review while the owner decides.
- **cost:** Approximately $0.01–$0.10 per rehearsal. Browser action latency and local indexing dominate; token use is small because only structured before/after fields go to the model.
- **security:** Never submit, purchase, send, or upload during rehearsal. Keep full field values local where possible; redact tokens and account IDs; attach an undoable action journal and an exact diff to the review. The owner has maximum-access policy, so this is a visibility feature, not a silent refusal mechanism.
- **missing:** A browser action that snapshots typed fields and page state before/after each proposed step, with stable element references; A structured reversible plan and diff format shared by browser and Mac action runners; Local calendar/file conflict queries exposed as read-only planner actions; A pendant-readable summary containing the exact final values and URL

### "After I change something on a logged-in website, let me ask “did it really stick?” and have the system reopen or revisit the account, compare the resulting state with the intended change, and tell me what is still uncertain."
- **useful because:** A receipt saying that a click ran is not proof that the remote service accepted the change. This would close the dangerous gap between local execution and real-world outcome for settings, appointments, subscriptions, and account changes.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic state snapshots and field-level diffs first; use the cheaper background model to interpret ambiguous confirmation pages. Use realtime only for the owner's brief spoken explanation.
- **latency:** Verify immediately in 5–15 seconds when the page is responsive, or schedule retries over 1–10 minutes when the service is eventually consistent. The owner gets an early “not verified yet” result rather than a false success.
- **cost:** About $0.01–$0.06 per verification; most cost and latency come from browser reloads/re-authentication, not inference.
- **security:** Read-only after the original action. Never repeat the mutation automatically. Keep snapshots field-scoped, redact account identifiers, retain only the result and evidence capsule, and clearly distinguish confirmed, contradicted, and unknown outcomes.
- **missing:** A post-action verification job with retry/backoff and an expiration window; Stable semantic selectors or field extractors that survive page reloads; A result type distinguishing local receipt from remote confirmation; Pendant phrasing and dashboard UI for confirmed/contradicted/unknown states

### "If I say “freeze browser work,” immediately stop queued browser jobs, close or park automation tabs, revoke any resumable browser sessions, and tell me on the pendant exactly what was stopped and what might already have happened."
- **useful because:** The owner needs a physical, voice-accessible emergency brake when a page behaves unexpectedly, a session is left open, or a long-running browser job must stop while away from the Mac. No single browser tab, Mac process, or relay status page provides that cross-surface certainty today.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** No expensive model is needed for the stop path: deterministic cancellation and session revocation, followed by a tiny realtime summary only if the owner is speaking live. Background reconciliation can inspect receipts afterward.
- **latency:** Stop dispatch within 1–2 seconds; return a first pendant acknowledgment immediately and a complete receipt inventory within 10 seconds.
- **cost:** Negligible inference cost; the dominant work is browser command cancellation, tab cleanup, and receipt reconciliation.
- **security:** This is intentionally destructive to pending browser work, but not to remote account data. Preserve an append-only audit record, distinguish canceled from already-delivered commands, avoid pretending a remote mutation was undone, and require no network availability on the pendant for the local stop acknowledgment.
- **missing:** A relay-to-extension cancellation broadcast that can invalidate commands already polled but not completed; A browser-session revoke/park primitive with tab ownership tracking; A pendant emergency command and offline acknowledgment state; A reconciliation report joining canceled commands with execution receipts

### "Before I act on a logged-in page, let me ask “which account am I in?” Compare the page’s masked identity and organization with the account I meant to use and warn me if the tab is the wrong person, workspace, or environment."
- **useful because:** Wrong-account actions are a class of mistake that ordinary form previews do not catch: the fields can look perfectly valid while belonging to a personal, work, test, or family account. The browser has the session identity; the Mac and context graph can supply the intended identity.
- **path:** browser → mac-planner → relay → pendant → dashboard
- **model tier:** Use deterministic extraction of visible account/workspace markers and exact context-graph matching. Use a small model only when labels are ambiguous; realtime is needed only to speak the short warning.
- **latency:** Under 5 seconds on the current page, before any proposed click or fill. If identity cannot be established, return “unknown,” not a guess.
- **cost:** Typically under $0.01 per check; browser extraction and selector maintenance dominate.
- **security:** Never expose full email addresses, account numbers, or tokens in spoken output. Compare hashed or masked identifiers locally, retain only pass/mismatch/unknown plus host and provenance, and do not silently switch accounts or log anyone out.
- **missing:** A typed account-identity extractor for common page markers and masked identifiers; An owner-maintained mapping of purpose to expected account/workspace, empty until configured; A local-only comparison service joining browser identity to context-graph entities; A planner hook that runs this check before browser mutations


## What it asked for

_Nothing._
## Its own summary

Recorded three new, non-restatement capabilities: remote outcome verification after browser actions; a pendant-triggered cross-surface browser emergency freeze with reconciliation; and wrong-account/workspace identity checking before mutations. Each names the missing changes rather than pretending current wiring is sufficient.

**Biggest unknown:** Whether the existing browser command/session cancellation semantics can invalidate a command after Safari has already polled it; the proposed freeze therefore requires an explicit extension-side cancellation acknowledgment.

