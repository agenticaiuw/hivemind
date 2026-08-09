# Harness derivation — relay-realtime — round 194

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If I say a long request, give me a quick, confidence-checked summary of what you’re about to do, and let me interrupt for a shorter plan."
- **useful because:** Reduces accidental misfires and keeps the owner in control while staying hands-free. It also fits the pendant’s limited audio channel.
- **path:** relay → mac-planner
- **model tier:** Realtime summarizes; mac-planner executes once confirmed.
- **latency:** Under 1.5s for a spoken summary; execution happens after confirmation.
- **cost:** Small additional cost for summarization; execution cost unchanged.
- **security:** Summaries should avoid exposing sensitive details aloud in public; offer a vaguer version when appropriate.
- **missing:** A structured plan preview endpoint that returns short and long summaries sized for speech, before execution

### "“Take care of this web task for me, but if the site asks a question you cannot infer, ask me through the pendant and continue when I answer.” The relay should carry an authenticated browser workflow across a Mac disconnect, pause at a genuine ambiguity, and resume without losing the page, fields, or evidence."
- **useful because:** Today a long task either assumes the owner stays at the Mac or fails silently when a human decision is needed. This would let the owner walk away while retaining control at exactly the points where judgment matters, rather than forcing them to repeat the whole task.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime relay only for the short clarification exchange; gpt-5.6-luna mac-planner for planning and state recovery; browser/UI model for locating controls; a cheaper background verifier for receipts and completion evidence.
- **latency:** Immediate acknowledgement under 1 second; clarification spoken within 2 seconds of the blocked step; resume within 10 seconds after the answer. Long navigation can run asynchronously.
- **cost:** About $0.03–$0.20 per workflow depending on planner turns and page inspection; clarification is dominated by realtime tokens, while browser actions and verification dominate wall-clock time.
- **security:** The workflow may touch authenticated sessions and personal data. Persist only an encrypted task state plus redacted screenshots/receipts, never raw credentials; pause before irreversible or legally consequential submission and say exactly what is waiting for the owner.
- **missing:** A durable, resumable task state machine shared by relay and Mac; A real browser-session lease and checkpoint protocol that survives Mac/browser reconnects; A bidirectional question/answer channel from Mac jobs to the pendant; Encrypted, redacted evidence storage and a user-visible audit trail

### "“When I say ‘log this’, preserve my exact words, when I said them, and what I was looking at; later answer ‘what exactly did I say about that?’ with the original clip and the surrounding context.”"
- **useful because:** A normal voice memo is difficult to search and easy to misremember. Provenance-preserving capture would turn fleeting thoughts, decisions, and observations into reliable personal recall without pretending a generated summary is a quotation.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime tier performs only capture acknowledgement and immediate transcript; a cheaper background model indexes entities and links the memo to Mac/browser context. Retrieval should return the source transcript/audio before any generated interpretation.
- **latency:** A capture acknowledgement in under 1 second; indexing within a minute; retrieval answer in under 3 seconds with an explicit ‘quoted’ versus ‘inferred’ distinction.
- **cost:** Roughly $0.005–$0.05 per memo plus storage; transcription and embedding dominate, not the live relay turn.
- **security:** Voice and browsing context are sensitive. Encrypt source audio/transcript, retain only explicitly logged utterances, expose deletion/export, and never silently attach unrelated screen content. The pendant must visibly confirm that ‘log’ was understood.
- **missing:** A provenance journal with immutable source spans and deletion semantics; A context snapshot API that records the active Mac app/browser tab at capture time; Semantic and exact-quote retrieval over the journal; A relay-to-pendant command for playing the source clip, not just a summary

### "“Tell me what changed since I last left my desk, and only mention things that require a decision.” The pendant should combine Mac state, browser-session changes, and queued task outcomes into a short spoken delta, with drill-down on a second press."
- **useful because:** The owner is often away from the Mac. Existing status checks answer isolated questions, but not the useful human question: what happened while I was gone, and do I need to act? This would reduce context switching and avoid reading bulk notifications aloud.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** A cheap background summarizer builds a change set from receipts and watched surfaces; realtime is used only to turn the already-ranked delta into a concise spoken response and handle ‘tell me more’.
- **latency:** Produce a first three-item answer in under 3 seconds when sources are cached; refresh remote sources asynchronously and push only material changes.
- **cost:** Around $0.01–$0.08 per briefing; ranking and source polling dominate, with low realtime cost for speech turns.
- **security:** The delta must not leak private content through an unattended pendant. Redact message bodies by default, classify urgency locally/server-side, expire snapshots, and require an explicit press for details or sensitive items.
- **missing:** A cross-surface change ledger with a durable ‘last seen’ cursor; Connectors that emit normalized change events from Mac apps and authenticated browser sessions; Decision/urgency ranking with deduplication across sources; A compact drill-down protocol and privacy-aware spoken rendering

### "“I’m leaving now—make sure my Mac is locked, pause anything playing, and tell me if there is an unsaved or failing task before I go.” The pendant should run a departure checklist against the live Mac, report exceptions, and let me say ‘leave it’ or ‘fix that’ for each exception."
- **useful because:** The owner currently has to remember several unrelated actions before walking away. A single spoken departure moment would prevent an unlocked machine, abandoned audio, or a half-finished automation from being left behind, while still exposing exceptions instead of making hidden changes.
- **path:** pendant → relay → mac-planner → mac-terminal → dashboard
- **model tier:** Realtime handles the short checklist dialogue; deterministic Mac probes do most work; gpt-5.6-luna is invoked only for interpreting an exception or carrying out a requested repair.
- **latency:** Checklist state in 2 seconds, first result in 4 seconds, and each repair under 10 seconds. If the Mac is offline, say so rather than pretending departure checks passed.
- **cost:** $0.01–$0.06 per departure, mostly planner calls for nonstandard repairs; deterministic status probes are cheap.
- **security:** Locking and pausing are reversible but can disrupt work. Never kill processes or discard edits; show the exact exception and preserve an audit receipt. Treat ‘I’m leaving’ as a trigger only after a clear button press or explicit phrase, not from ambient audio.
- **missing:** A departure-check action bundle with deterministic Mac lock/media/save-state probes; A way for the relay to query unsaved-document and active-job state without broad screen scraping; Per-exception spoken branching and a durable receipt of what was checked; A device-side explicit-trigger rule for this multi-action command


## Changes it proposed to its own stack

### `interaction` — Add a relay-owned conversation lease that can be transferred between the pendant’s live voice session and a paired phone/web audio client without resetting the session transcript, pending tool call, or spoken reply queue. The transfer should be explicit (‘send this conversation to my phone’) and reversible; the pendant announces the handoff and keeps a one-button return path.
- **owner gets:** When the owner’s hands or ears are occupied, they can continue the same task on a richer surface instead of abandoning it and repeating the request. This is especially valuable while away from the Mac, where the pendant is the only front door but cannot show long forms, receipts, or screenshots.
- effort: High: new authenticated phone/web surface, session lease and audio negotiation, reconnect semantics, and shared transcript/tool state across Worker instances.  ·  risk: A stale client could speak into the wrong session or expose private audio. Use short-lived device-bound leases, explicit handoff announcements, sequence numbers, and automatic revocation on disconnect. Recovery is to return to the pendant with the last confirmed state; never duplicate a tool call after reconnect.
- cost: Small ongoing storage and signaling cost; roughly $0.01–$0.05 extra per handoff for state and audio relay, plus implementation of a mobile/web client.  ·  latency: Handoff acknowledgement under 1 second; 1–3 seconds for audio renegotiation. Normal pendant turns unchanged.
- security: Adds another bearer of live microphone and conversation data. Require pairing, per-device keys, encrypted transport, visible active-surface indicator, and a one-button pendant command to revoke all other clients.
- depends on: A real paired phone/web surface; Durable session state and idempotent tool-call records; Authenticated low-latency audio transport beyond the current pendant path


## What it asked for

_Nothing._
## Its own summary

Recorded four owner-facing capabilities and one cross-surface interaction change: resumable human-in-the-loop browser work, provenance-preserving exact voice recall, decision-only away-from-desk deltas, a departure checklist, and explicit pendant-to-phone session transfer. The highest-value gap is durable cross-surface state plus a real clarification channel, so a task can pause for the owner and resume without repeating work.

**Biggest unknown:** Whether the existing /ops/memory, /ops/history, watches, and browser inspection records already expose enough source-level provenance and change cursors to implement the recall and decision-delta ideas without new storage.

