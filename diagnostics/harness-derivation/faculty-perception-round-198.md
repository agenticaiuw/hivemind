# Harness derivation — faculty-perception — round 198

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live cross-surface state 2026-08-08T22:58Z** — The Mac local agent is fully ready: Accessibility and Screen Recording are granted, requiredMissing is empty, browser extension is online with 4 Safari tabs and 0 pending commands, relay is reachable with D1 persistence and Mac bridge online, while no pendant appears in this snapshot. Active browser tab is an X.com post titled “Dermot McGrath（麦德蒙） on X: ByteDance has just released a fully featured phone as…”.
  - evidence: read_continuity_snapshot(include=['relay','pipeline'], maxItems=20) invoked GET /ops/snapshot, HTTP 200; body status.permissions.ready=true, browser.online=true, relay.payload.store='d1', relay.payload.macBridgeOnline=true, and no pendant device in returned status.

## Capabilities it proposed

### "“Give me a morning brief I can trust: what changed overnight, what needs my attention, and cite the exact pages or messages you used.”"
- **useful because:** The owner has repeatedly requested last-12-hours world/US headlines and already schedules briefs, but the current completed status does not establish freshness, source coverage, or whether a page was actually read. This would turn a recurring request into a compact, auditable spoken brief rather than another opaque summary.
- **path:** relay-realtime → browser-extension → mac-planner → relay-realtime → faculty-perception
- **model tier:** background for collection and clustering; realtime only to answer follow-up questions
- **latency:** Under 60 seconds at the scheduled time; under 5 seconds to answer “why is this in the brief?”
- **cost:** Roughly $0.03–$0.15 per scheduled brief, dominated by page retrieval and one cheap summarization pass; no realtime model for routine generation.
- **security:** Browser pages and mail/calendar excerpts leave the Mac only as redacted, source-linked extracts. Sending mail, changing subscriptions, or acting on a headline always requires confirmation. Login walls and unavailable sources must be reported, never silently filled.
- **missing:** A provenance-bearing relay-read contract that returns a stable read ID and content hash, then maps into the existing Mac evidence-capsule schema.; A brief-specific freshness/coverage receipt recording requested interval, sources attempted, sources succeeded, and local timezone.; A scheduler policy that marks a brief stale or partial instead of reporting routine completion as success.

### "“Remember this page for me: capture the exact passage I mean, save a short note in my workspace, and let me ask you later what the source said.”"
- **useful because:** A spoken “remember this” currently risks storing an untraceable paraphrase. The browser has the authenticated page, the Mac owns durable evidence storage, and the pendant is the only practical capture trigger. This gives the owner a retrievable, source-grounded memory instead of a confident but unverifiable fact.
- **path:** relay-realtime → browser-extension → mac-planner → faculty-perception
- **model tier:** realtime for the short spoken confirmation; background/local model for redaction, passage extraction, and indexing
- **latency:** Acknowledge in 2 seconds; capture and write the linked note within 10 seconds.
- **cost:** About $0.01–$0.05 per capture, dominated by one local extraction/classification pass; retrieval can be local and near-zero API cost.
- **security:** Never capture password fields, private-message bodies, or hidden page regions by default. Show the URL, selected region, redaction count, and expiry in the spoken/visual confirmation; saving a sensitive passage requires explicit confirmation. Revocation must remove the body while retaining a tombstone.
- **missing:** A browser-extension command that sends the user-selected region and tab identity to the Mac evidence-capsule writer from a pendant-originated request.; A durable note/index record that stores capsuleId and locator rather than duplicating page text.; A retrieval route that answers from the capsule and clearly says when it has expired, been revoked, or was never captured.

### "“Take the exact item I’m looking at, turn it into the right action, and show me one compact confirmation with the source, recipient, changes, and undo before you do anything irreversible.”"
- **useful because:** This is the central failure mode of a wearable assistant: the pendant hears an underspecified command while the browser and Mac hold the missing context. A perception-led transaction would bind the spoken request to the active tab, extract the intended object, have the Mac prepare a reversible draft, and make the final confirmation inspectable instead of guessing.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** realtime only for disambiguation and confirmation; local/background models for extraction and draft preparation
- **latency:** Resolve context and present a confirmation in 5 seconds for a normal page; never execute an irreversible action merely to meet latency.
- **cost:** $0.01–$0.08 per prepared transaction, mostly local extraction and one planner pass; execution and undo are deterministic.
- **security:** The active tab is evidence, not authorization. Display recipient, exact object, diff, scope, and expiry before send/delete/purchase. Keep secrets on the Mac/browser; redact them from relay telemetry. Require a fresh spoken or button confirmation for irreversible steps and invalidate the plan if the tab, recipient, or content changes.
- **missing:** A cross-surface transaction envelope with immutable context references, preconditions, proposed effects, expiry, and an explicit reversible/irreversible classification.; A perception check that re-reads or hashes the browser object at execution time and refuses stale plans.; A single owner-facing receipt joining browser command, Mac action ledger, relay job, and final effect/undo handle.

### "“I’m walking away from my Mac—keep my request, and when I reconnect, tell me exactly what you understood, what changed while I was gone, and ask before acting.”"
- **useful because:** Today an offline or disconnected pendant can at best lose the interaction; the Mac and relay cannot distinguish an intentional deferred request from a failed one. An offline intent escrow would let the owner speak once, preserve the bounded request locally, then reconcile it against the live Mac/browser state on reconnect instead of silently dropping or prematurely executing it.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Small local classifier for capture quality and intent envelope; background model on reconnect for reconciliation; realtime only for the final spoken confirmation.
- **latency:** Local capture acknowledgement under 300 ms; reconnect reconciliation under 10 seconds; no action before explicit confirmation if state changed.
- **cost:** Under $0.02 per deferred request; local storage and hashing dominate, with one background reconciliation call on reconnect.
- **security:** Persist only a bounded, redacted intent envelope—not raw audio or secrets. Bind it to a monotonic device sequence, creation time, and intended scope. Expire ambiguous requests and require confirmation when the target, account, or page changed. Never replay a stale destructive command automatically.
- **missing:** A firmware-resident bounded intent-envelope queue with sequence numbers and a clear pending/expired state.; A relay sync protocol that deduplicates envelopes and reports acceptance without implying execution.; A Mac reconciliation endpoint that compares the envelope against current browser/Mac context and produces a confirmation diff.

### "“What did you change since I left, and put anything reversible back the way it was—show me the exact diff first.”"
- **useful because:** The owner can currently receive scattered completion claims from Mac jobs, browser commands, and relay routines, but cannot ask one trusted surface for a causal, reversible account of changes across all three. A time-bounded rewind would turn the action ledger and browser state into a practical safety net: identify effects, distinguish system activity from owner-approved activity, and offer targeted undo.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Local deterministic diff and rollback planner first; background model only to summarize the causal chain; realtime for the short spoken explanation.
- **latency:** Initial inventory under 5 seconds for a normal gap; rollback preview under 3 seconds; execution only after confirmation.
- **cost:** Usually under $0.03, mostly local reads and deterministic diffing; model cost only for ambiguous grouping or a natural-language summary.
- **security:** Never infer that a change is safe to undo from timestamps alone. Require provenance and preconditions for every reversal; exclude external sends, purchases, and destructive operations from automatic rollback. Keep private values redacted in spoken output and allow the owner to inspect the full local receipt.
- **missing:** A cross-surface causal change index joining Mac action-ledger steps, browser mutations, relay jobs, and routine runs by one owner-visible transaction ID.; First-class undo handlers and precondition checks for browser and Mac mutations, including explicit “cannot undo” records.; A perception query that can answer a time interval with complete/partial coverage and state exactly which sources were unavailable.

### "“When my meeting starts, keep a private running record of decisions and open questions, then give me a three-line debrief and draft—not send—the follow-ups when it ends.”"
- **useful because:** The owner has a calendar, Mac apps, browser sessions, and a wearable microphone, but no single capability can join meeting context to an end-of-meeting perception of decisions. This would eliminate the costly failure of remembering the conversation but losing who owes what, while keeping sending separate and confirmable.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → faculty-perception → faculty-judgement
- **model tier:** Local/on-device VAD and redaction during capture; background model for diarization, decision extraction, and draft generation; realtime only for start/stop consent and the concise debrief.
- **latency:** Start confirmation under 2 seconds; rolling notes within 30 seconds of speech; debrief and drafts within 60 seconds of meeting end.
- **cost:** $0.05–$0.30 per hour-long meeting, dominated by transcription and summarization; local redaction reduces uploaded audio and text.
- **security:** Recording must be visibly and audibly announced, with a hard stop and per-meeting consent. Default to local encrypted storage, upload redacted transcript segments only, expire raw audio quickly, and never send follow-ups without confirmation. Do not infer consent from calendar presence alone.
- **missing:** A consent-aware meeting session state shared by pendant, relay, and Mac, including a physical stop action that survives a dropped link.; A local encrypted transcript/decision store with participant-sensitive redaction and retention controls.; Calendar/browser context joins and a draft-only follow-up planner that cites the exact decision spans.


## Changes it proposed to its own stack

### `context` — Add a perception-side context lease for every browser-originated command: at utterance start, record tab/window ID, URL, title, content hash or selected-region digest, and timestamp; before any Mac or browser mutation, re-observe the same tab and invalidate the lease on navigation, tab replacement, or material content change. Surface the invalidation as a spoken “the page changed” rather than proceeding with stale context.
- **owner gets:** The owner can safely say “do that” while wearing the pendant without the assistant silently acting on a different tab or a page that changed underneath it. It converts active-browser context from an assumption into a checked fact.
- effort: Medium: wire browser snapshot/inspect and existing evidence hashes into plan/execute preconditions; add a small lease store and one invalidation branch.  ·  risk: False invalidations on dynamic pages may cause an extra confirmation; recover by showing the changed title/URL and offering to re-plan. A compromised extension could still lie about page state, so retain the browser trust boundary.
- cost: Negligible storage and local hashing; one extra browser inspection per mutation, with a small browser/API cost if remote retrieval is needed.  ·  latency: Adds roughly 200–800 ms locally, potentially 1–3 seconds for a remote page re-read.
- security: Improves authorization-context binding and prevents confused-deputy actions; does not grant new authority or bypass confirmation.
- depends on: Browser snapshot/inspect must expose stable tab/window identity and a content or region digest.; POST /plan and POST /execute must accept and enforce context preconditions.; Existing evidence capsule and browser provenance stores should be mounted for the receipt link.


## What it asked for

_Nothing._
## Its own summary

I discovered and recorded a new live fact: the previously blocked Mac permissions are now genuinely ready (Accessibility, Screen Recording, and automation all granted), the browser bridge is online with four Safari tabs and no pending commands, and the D1 relay is reachable; the pendant is still absent. I proposed three distinct owner-facing capabilities: an auditable fresh morning brief, browser-grounded “remember this” capture, and a cross-surface context-bound action transaction, plus a concrete context-lease change that invalidates stale browser plans. What remains needed is not another diagnostic: wire the existing evidence/provenance, browser, plan/execute, and receipt pieces into those flows; add relay-read IDs/hashes and freshness receipts; and enforce context preconditions before mutation. The owner should also decide whether a missing pendant is expected bench state or whether pairing/registration is now the next physical step.

**Biggest unknown:** Whether the current relay/browser infrastructure already has the exact /prepare and /approve semantics and browser inspection route needed for context leases; the snapshot confirms the surfaces are live, but not the detailed precondition/receipt contract. Pendant-originated behavior remains unverifiable until an nRF9160 actually registers.

