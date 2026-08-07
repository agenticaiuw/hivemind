# Harness derivation — faculty-judgement — round 128

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “I’ll handle that,” remember the commitment, watch the relevant calendar, mail, browser and local-file evidence, and nudge me only if it is still unresolved near the right time—with a one-tap pendant action to finish, defer, or dismiss it."
- **useful because:** People lose promises made in conversation, not tasks they deliberately entered. This turns an ordinary spoken intention into a quiet safety net without requiring a task app or constant notifications.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for extracting and reconciling commitments; realtime only for the spoken capture and final nudge wording
- **latency:** capture acknowledgement under 1 second; background evidence checks within 15 minutes of relevant changes; nudge under 2 seconds after its decision window
- **cost:** roughly $0.01–$0.05 per commitment per day; most cost is periodic reconciliation, not the short voice exchange
- **security:** Commitments may reveal health, work, or relationships. Keep raw audio on-device, send only structured commitment fields, cite evidence privately, and require confirmation before sending or deleting anything.
- **missing:** durable commitment graph with evidence links and expiry; cross-surface reconciliation scheduler; pendant offline capture and later sync; owner-configurable nudge quiet hours

### "When I ask “what should I do?”, combine what my pendant heard, what is open in my private browser tabs, and what my Mac knows locally; give me three options with consequences and confidence, remember which I chose, and carry out only that option."
- **useful because:** The system should help with judgement, not just retrieval or button pushing. The owner gets a grounded decision instead of a generic answer, while uncertainty and irreversible consequences stay visible.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model gathers and normalizes evidence; realtime model handles the owner’s final spoken tradeoff and choice
- **latency:** initial options in 10–30 seconds; evidence can continue gathering in background; execution starts only after an explicit spoken or pendant confirmation
- **cost:** roughly $0.05–$0.25 per decision, dominated by private-page extraction and synthesis; reuse unchanged evidence to avoid repeated context cost
- **security:** Private tabs and local files leave their respective devices only as cited excerpts. Never expose secrets in spoken audio by default; show provenance and redact sensitive fields in dashboard; confirmation required for external side effects.
- **missing:** decision workspace that joins pendant/relay/Mac/browser evidence; typed uncertainty and contradiction handling; choice-to-action transaction binding; cross-surface provenance receipts

### "Before I enter an important conversation, quietly assemble a private “what I need to remember” card from my calendar, recent mail, notes, and relevant logged-in pages; let me ask the pendant for one fact at a time, and capture the decisions and follow-ups afterward."
- **useful because:** Preparation and recall are hardest when attention is scarce. A conversational, source-backed memory card is more useful than a long briefing and keeps sensitive material off the room’s screen.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model prepares and ranks the card; realtime model answers short pendant questions and records post-conversation decisions
- **latency:** prepare 5–10 minutes before the event or on demand; each spoken fact under 2 seconds; post-conversation capture under 30 seconds
- **cost:** roughly $0.03–$0.15 per conversation; extraction and audio generation dominate, while repeated fact lookup is cheap
- **security:** Cards contain sensitive relationship and work context. Encrypt at rest, expire them after the event, use a spoken wake/gesture for playback, and never read names or amounts aloud unless requested.
- **missing:** event-scoped ephemeral memory card; calendar-triggered preparation hook; source-ranked fact extraction across Mail/Notes/browser; post-event decision capture and expiry

### "When I am weighing a consequential choice, let me ask “what happens if I choose this?”, and show me a private, source-backed rehearsal of the next month: calendar collisions, likely messages, commitments I would break, costs or deadlines visible on my Mac, and the assumptions that could make the forecast wrong."
- **useful because:** The owner needs help seeing second-order effects before committing, not just a list of facts after the decision. A grounded rehearsal would make judgment less impulsive while keeping the decision theirs.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model gathers evidence and runs scenario comparisons; realtime model conducts the short spoken tradeoff conversation
- **latency:** 30–90 seconds for an initial rehearsal; deeper evidence can continue in background; no external action without explicit approval
- **cost:** $0.10–$0.50 per rehearsal, dominated by multi-source extraction and scenario synthesis; cache unchanged evidence and assumptions
- **security:** Financial, work, and relationship data should remain on-device where possible; send structured excerpts, not whole mailboxes; clearly label speculation; never present a forecast as fact or contact anyone without confirmation.
- **missing:** scenario/evidence graph with assumptions and counterfactual branches; local adapters for cost and deadline sources; a private dashboard that distinguishes facts, inferences, and unknowns; decision history with owner corrections

### "Help me preserve the meaning of a day, not just its files: when I say “save this moment,” combine a short pendant note with the nearby calendar event, open document or page, and my chosen feeling or lesson; months later I can ask what I learned and get a small, cited life story rather than a pile of transcripts."
- **useful because:** Important experiences disappear into screenshots, notes, and memory fragments. This gives the owner a private, searchable continuity of reflection without forcing them to journal at length.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** cheap background model creates and clusters private memory capsules; realtime model handles capture and later conversational recall
- **latency:** capture acknowledgement under 1 second; capsule assembled within 2 minutes; recall under 3 seconds for indexed material
- **cost:** $0.01–$0.08 per saved moment, mostly summarization and embeddings; raw audio can be deleted after transcription
- **security:** This is intimate data. Encrypt capsules, provide per-capsule expiration and deletion, keep private-page content as minimal citations, and require a deliberate gesture or phrase before spoken recall.
- **missing:** event-local context sampler across Mac and browser; private reflective-memory store with retention controls; semantic retrieval that preserves uncertainty and provenance; pendant capture mode that works while relay is unavailable

### "Before I share something with a person or group, ask “what is safe to disclose here?” and produce three versions—a private full version, a bounded version, and a minimal version—using my actual documents and messages while preserving secrets and showing exactly which facts were omitted or generalized."
- **useful because:** The owner regularly has to balance honesty, privacy, and usefulness. A disclosure assistant would prevent accidental oversharing without forcing them to remember every sensitive detail or manually redact documents.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model classifies sensitivity and drafts variants; realtime model explains the tradeoff briefly; no external send is automatic
- **latency:** 10–30 seconds for a short disclosure; up to 2 minutes for a document-sized one; explicit confirmation before copy, paste, or send
- **cost:** $0.05–$0.25 per disclosure, driven by document parsing and redaction review; local hashing and reuse reduce repeat cost
- **security:** The draft itself is sensitive. Keep source documents on the Mac, pass only selected excerpts, display recipient and audience assumptions, retain no drafts by default, and require confirmation before any browser or mail mutation.
- **missing:** field-level sensitivity and secret detection; recipient/audience context model; reversible redaction and provenance view; safe clipboard/browser insertion with a confirmation gate


## Changes it proposed to its own stack

### `browser-harness` — Add a tab-identity quarantine before any authenticated read or mutation: require a fresh extension heartbeat whose tabId, URL, title, session binding, and content hash agree with the durable session record; on contradiction, freeze commands, mark the tab orphaned, and ask the owner to choose the authoritative tab.
- **owner gets:** Prevents the system from reading or changing the wrong logged-in page. Today the live Safari tab says example.com/Failed to open page while the durable session says Gmail, so a confident action could target the wrong account context.
- effort: Medium: identity record, heartbeat comparison, quarantine state, and explicit recovery UI.  ·  risk: A stale heartbeat may pause legitimate work; recover by re-heartbeating and requiring owner selection. Never auto-rebind on URL alone.
- cost: Negligible API cost; a few D1/local records per heartbeat.  ·  latency: Adds under 300 ms to browser jobs when heartbeat is fresh; may require human recovery on mismatch.
- security: Strongly reduces confused-deputy risk and prevents cross-account tab mixups.
- depends on: authenticated browser session records; browser heartbeat and typed command queue; dashboard display of quarantined tabs

### `integration` — Create an event-scoped evidence bundle that joins a pendant utterance/button timestamp, relay job ID, Mac job and receipt IDs, browser tab evidence, and final audio state into one immutable timeline; expose a plain-language outcome such as captured, planned, executed, rendered, uploaded, delivered, or played.
- **owner gets:** When the owner asks “did that happen?”, the answer should be a proof, not a hopeful status. It makes late/offline behavior understandable and lets them safely retry without duplicating actions.
- effort: High: shared correlation ID propagation, append-only event schema, and a small owner-facing receipt view.  ·  risk: Partial or duplicated events could produce misleading certainty; require explicit unknown states and idempotent event IDs, with raw event drill-down for recovery.
- cost: Low storage and background processing; no extra model call for normal events.  ·  latency: No meaningful hot-path delay if events append asynchronously.
- security: Receipts must redact utterance contents and private-page excerpts by default; retain only hashes and authorized summaries.
- depends on: pipeline event persistence; Mac/browser action receipts; relay job records; pendant delivery acknowledgements

### `interaction` — Introduce a truthful readiness contract for proactive work: aggregate Mac permission state, browser identity health, relay reachability, pendant registration, and audio capability into per-action preflight results; the voice agent must say exactly what it can do now, what will be queued, and what cannot be verified.
- **owner gets:** The system currently reports browser online while the active tab is broken and reports a relay-ready audio result even though no live pendant is registered. Honest preflight prevents wasted requests and false reassurance.
- effort: Medium-high: action-specific capability matrix, preflight route, and short spoken/UI explanations.  ·  risk: Overly conservative gates can frustrate the owner; allow reversible reads with warnings while blocking mutations or claims of delivery when prerequisites are unknown.
- cost: Tiny compute/storage cost; avoids expensive failed model/action loops.  ·  latency: Adds roughly 100–500 ms before actions, usually saving much longer failed runs.
- security: Makes missing permissions and device state visible without exposing tokens or sensitive content.
- depends on: GET /ops/status; GET /browser/status; pipeline telemetry; action policy and receipt layer

### `model-routing` — Add a values-and-uncertainty adjudicator between evidence gathering and action: it learns only explicit owner corrections and stable preferences, asks one clarifying question when sources conflict, and refuses to optimize for an unstated value (speed versus cost, privacy versus convenience, loyalty versus fairness). Persist the chosen tradeoff with the decision receipt.
- **owner gets:** Today a fluent agent can silently choose the wrong objective. The owner should feel understood in difficult choices and be able to see why the system recommended or declined an action.
- effort: High: preference schema, conflict detector, clarification dialogue, and receipt integration across relay/Mac/browser.  ·  risk: Inferred preferences could become manipulative or stale; never infer sensitive values, attach expiry and confidence, and let the owner erase or override them.
- cost: Small background-model cost for conflict checks; one extra realtime turn only when ambiguity is material.  ·  latency: Adds 1–3 seconds only on conflicting or high-impact requests; simple requests bypass it.
- security: Values are highly sensitive. Store encrypted, minimize projections to other surfaces, and do not expose them to third-party pages or prompts.
- depends on: cross-surface provenance receipts; typed uncertainty representation; owner preference and deletion controls; action confirmation policy


## What it asked for

_Nothing._
## Its own summary

Round 128 produced three owner-facing capabilities and three stack changes. The strongest is a spoken commitment safety net: turn “I’ll handle that” into a durable, evidence-backed promise checked across Calendar, Mail, browser and local files, then nudge only when it remains unresolved. Also proposed a cross-surface decision room and event-scoped conversation memory cards. Fresh live truth: relay and browser are reachable, but the active Safari tab is contradictory (example.com / “Failed to open page” while durable state says Gmail), Mac readiness is false despite automation grants because Accessibility and Screen Recording are still missing, and historical audio has rendered/uploaded states without proof of pendant playback. Changes proposed: quarantine contradictory tabs, join every action/audio path into an immutable proof timeline, and add truthful per-action readiness preflight. Still needed: owner manually granting TCC permissions if GUI automation is desired, real pendant registration/playback acknowledgement, and implementation of the missing commitment/evidence/decision storage—not another model prompt.

**Biggest unknown:** Whether the physically USB-connected pendant can now complete a real capture-to-playback round and emit a trustworthy delivered/played acknowledgement; current pipeline records historical nrf9160 activity but does not establish live end-to-end delivery.

