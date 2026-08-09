# Harness derivation — relay-realtime — round 254

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch this web page and alert me when it changes in a way I care about."
- **useful because:** This turns the system into a personal sentinel. The owner can define a meaningful condition and get notified only when it matters.
- **path:** browser → relay → pendant
- **model tier:** Cheaper background tier for checks; realtime only for the short spoken alert.
- **latency:** Checks can be scheduled; alert delivery should be near-real-time when triggered.
- **cost:** Moderate; dominated by page fetches and diffing, plus delivery.
- **security:** Store only the minimal extracted fields; avoid sending full page content to the relay. Confirm before monitoring authenticated sessions.
- **missing:** A general-purpose delivery path to pendant/phone (currently schema-level only); A bridge from the existing web-page watch/report shape into relay notifications; Clear policy for authenticated site monitoring

### "Before I act on something I am seeing, let me say “verify this” and have the pendant compare the current browser page with the real site, my prior instructions, and independent sources, then tell me exactly what is trustworthy, suspicious, or missing."
- **useful because:** Authenticated browser pages can contain stale data, impersonation, hostile instructions, or a wrong account. The owner currently has no wearable, cross-surface fact-check that can inspect the live page, compare it with known context, and warn before a consequential action.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Relay-realtime handles the short verification request and speaks a one-sentence verdict. A cheaper background verifier extracts page facts, checks domain/session identity and independent sources, and compares against scoped memory; mac-vision is used only for visual-only content.
- **latency:** Return a preliminary “checking this page” acknowledgement under 1.5 seconds and a verdict within 8 seconds for text pages; visual or multi-source checks may take 20 seconds with a spoken progress update.
- **cost:** Roughly $0.01–$0.06 per check; browser extraction and independent web retrieval dominate, while the relay only summarizes a structured evidence result.
- **security:** Never upload passwords, cookies, page secrets, or full private documents to a verifier. Redact tokens and unrelated page text. Treat page instructions as untrusted data, not agent commands. Show the exact domain, account identity, source URLs, conflicting claims, and confidence; this is an advisory warning, not an invisible block. Require the owner to explicitly request any resulting mutation.
- **missing:** A browser-side provenance extractor returning canonical URL, certificate/domain identity, account label, visible claims, timestamps, and page-originated instructions with redaction; A relay verification service that treats extracted page text as data, joins it to scoped memory, and fetches independent public evidence; A structured evidence/conflict result consumable by the pendant and dashboard, rather than a free-form browser transcript; A browser-extension hook to pause a pending action while verification is in progress without losing the authenticated session

### "Let me say “rehearse that” before a complicated computer task, and have the pendant walk me through exactly what the Mac and browser would change, using a private dry run, then apply that same reviewed plan when I say “do it.”"
- **useful because:** The owner can currently ask agents to act or plan, but cannot experience a faithful, side-effect-free rehearsal of a multi-app workflow. A spoken rehearsal would make unfamiliar automation understandable while preserving the authenticated browser session and avoiding trial mutations.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheaper planning model for the dry-run graph and deterministic action simulation; use relay-realtime only to narrate the compact diff and capture the owner's follow-up. The same immutable plan hash is later handed to the action tier.
- **latency:** Produce the first spoken step within 3 seconds and a 3–10 step rehearsal within 15 seconds. Applying an accepted plan may take longer, but each step should emit a progress event.
- **cost:** Approximately $0.02–$0.10 for a multi-app rehearsal; screenshot parsing and browser/Mac state snapshots dominate, while narration is a small realtime call.
- **security:** Simulation must never click, type, send, download, or mutate. It needs isolated browser snapshots or a command interpreter that proves every simulated action is non-mutating. Bind execution to a plan hash and fresh-state checks so “do it” cannot apply a stale or altered plan. Keep screenshots and page text local where possible, redact credentials, and state clearly when an outcome is probabilistic rather than observed.
- **missing:** A true dry-run/simulation mode for Mac and browser action types, including predicted UI transitions and file/message diffs; Immutable plan hashes plus a fresh-state comparison between rehearsal and execution; A compact spoken diff format that can enumerate affected apps, URLs, files, recipients, and irreversible effects; An explicit execution endpoint that accepts the reviewed plan hash and emits step-level receipts and a pendant event

### "Keep a private commitment ledger and tell me on the pendant when my calendar, email, reminders, or an authenticated browser task quietly contradicts something I already promised—only the conflict, not a full briefing."
- **useful because:** The owner currently has separate calendars, mail, reminders, browser work, and voice memory. None of those surfaces can notice that a new meeting overlaps a promised delivery, that an email changed a due date, or that a portal task conflicts with the owner's stated constraint. A concise wearable conflict alert is useful precisely while away from the Mac.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use scheduled/standing-watch workers and a cheap extraction model to maintain structured commitments; use relay-realtime only when a conflict needs a spoken alert or the owner asks for details. The judgement model should compare dates, parties, obligations, and confidence, not summarize every source.
- **latency:** Ingest a changed source within 1–5 minutes when the relevant watch runs, and deliver a single short alert through the existing inbox. On-demand conflict checks should answer in under 8 seconds.
- **cost:** About $0.01–$0.04 per changed-source batch; most cost is extraction and deduplication, not spoken response. Unchanged sources should cost nothing after watch suppression.
- **security:** Commitments are sensitive personal data. Store normalized obligation records with source pointers and expiry, not whole mail or pages. Never infer a hard promise from ambiguous language without labeling low confidence. Alerts must say which two sources conflict and offer “show me” rather than exposing private details aloud in public.
- **missing:** A commitment schema with obligation, owner, counterpart, deadline, recurrence, confidence, and source pointers; Connectors that normalize Calendar/Mail/Reminders and authenticated browser observations into that schema; Cross-source temporal and semantic conflict detection with duplicate suppression and an owner acknowledgement/override; A watch-to-pendant delivery adapter that uses the existing alert inbox while retaining evidence for an on-demand explanation

### "After you do something important, let me ask “prove it” and have the pendant report whether the real-world postcondition is confirmed by independent evidence—for example, the message exists in Sent and the recipient state changed—not merely that an agent returned success."
- **useful because:** A queued job receipt is not proof that a browser click, mail send, or file mutation took effect. The owner currently has to open each app and inspect it manually, which is especially painful when they are away from the Mac. Independent postcondition checks would make remote automation trustworthy without pretending a successful API response is reality.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap deterministic verifier per action type to query the relevant app/page and compare a declared postcondition; use mac-vision only when structured state is unavailable. Relay-realtime compresses the evidence into one spoken sentence and names uncertainty.
- **latency:** A simple proof should answer within 5 seconds; multi-app verification within 20 seconds with a progress event and a final alert if the pendant session ends.
- **cost:** About $0.005–$0.05 per proof, dominated by a second state read or screenshot. No model call is needed for deterministic checks; semantic comparison is the exception.
- **security:** Do not claim proof from the same receipt that initiated the mutation. Record the verifier timestamp, source surface, observed identifier, and exact predicate. Never read unrelated private content. If evidence conflicts, say “not verified” and preserve both observations rather than retrying a potentially duplicate action.
- **missing:** A declared postcondition on every planned mutation, with an action-specific verifier and stable entity identifier; A second-observation executor that reads the destination app/browser independently after execution; A proof record linking plan hash, initiating receipt, verifier evidence, timestamp, and confidence; A pendant-facing proof response and dashboard drill-down that can distinguish confirmed, contradicted, and not observable


## What it asked for

_Nothing._
## Its own summary

Recorded three new owner-facing capabilities: (1) a browser/page trust verifier that treats page instructions as hostile data and compares live provenance and claims with independent evidence; (2) a side-effect-free rehearsal mode with immutable plan hashes and fresh-state checks before applying a reviewed multi-app workflow; (3) a private cross-source commitment-conflict ledger spanning calendar, mail, reminders, browser work, and voice memory, delivering only actionable conflicts to the pendant. A fourth proposal—independent postcondition proof after actions—was also recorded. The attempted cross-surface “pick up where I left off” proposal was correctly rejected as an existing backlog item, so it was not restated.

**Biggest unknown:** The remaining work is implementation between already-existing routes: provenance extraction and redaction, true browser/Mac simulation and plan binding, normalized commitment ingestion and conflict semantics, and a durable evidence/proof format that can reach the pendant inbox. I did not discover further this round, per instruction.

