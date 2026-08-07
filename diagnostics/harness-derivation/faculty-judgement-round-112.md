# Harness derivation — faculty-judgement — round 112

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Tell me when my commitments conflict, and give me the least-painful way out.”"
- **useful because:** Instead of separate reminders and briefs, the system would notice that a calendar promise, an email deadline, a travel reservation, or a logged-in task now makes another promise impossible. It would show the evidence and propose concrete options (move, delegate, decline, or ask for an extension), drafting messages but never sending them. The pendant can ask one short clarification at the moment a choice is needed; the Mac and browser do the evidence gathering that the pendant cannot.
- **path:** relay-realtime → pendant → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** Background/slow model builds a normalized obligation and conflict graph from Calendar, Mail, local notes/files, and authenticated browser pages; realtime model is used only to explain one conflict and collect a choice through the pendant. Deterministic rules handle overlap, travel-time, due-date, and dependency checks before any model judgment.
- **latency:** Nightly and event-triggered scans may take 1–5 minutes. A newly detected high-confidence conflict should produce a queued capsule, not an interruption; once the owner asks, the first evidence-backed answer should be under 3 seconds. Draft generation may take up to 20 seconds.
- **cost:** Roughly $0.02–$0.15 per daily scan depending on how many private pages and messages are extracted; most cost is summarization and reconciliation, not rule checks. One realtime clarification is a normal short turn.
- **security:** Private mail, calendar, files, and authenticated pages leave their surfaces only as bounded extracts with source, timestamp, and sensitivity labels. Never send, cancel, reschedule, purchase, or disclose without explicit confirmation. Conflicts involving secrets or health/financial data should be redacted in spoken output and linked to a Mac review workbench.
- **missing:** A durable obligation schema with source citations, confidence, due/temporal constraints, and expiry; A conflict detector that distinguishes true impossibility from merely adjacent events and accounts for travel/buffer time; A ranked option generator with reversible draft artifacts and an explicit approval boundary; Event hooks from Calendar/Mail/browser watches into the detector, plus deduplication and quiet-hour delivery

### "“Learn how I like things handled, but ask before you make a new rule.”"
- **useful because:** The owner repeatedly says the same things—never send without approval, keep spoken replies short, defer low-urgency items, prefer reminders over email—but today those choices are scattered across pendant turns, Mac receipts, browser approvals, and dismissed briefings. The hive would infer a candidate personal operating rule from repeated behavior, show three concrete examples, and let the owner accept, edit, or reject it. Accepted rules would then make every surface less annoying without silently changing autonomy boundaries.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** A cheap background model clusters decisions and dismissals; deterministic counters and policy constraints prevent overgeneralization. Realtime is used only when presenting a candidate rule or answering 'why did you do that?'.
- **latency:** Learnings can be computed nightly or after 10 relevant events. Candidate presentation should be a 20–30 second spoken interaction, with a Mac review page for details. Applying an accepted rule is immediate and must be reflected in the next task.
- **cost:** Usually under $0.01 per nightly update; dominant cost is embedding/clustering a small decision history. No model call is needed for every action.
- **security:** Behavioral history is highly personal. Store derived rules separately from raw transcripts, retain source references with short TTLs, and never infer sensitive traits or rules about health, relationships, or money. A candidate cannot widen permissions or authorize irreversible actions; owner confirmation is mandatory and revocation must be one utterance.
- **missing:** A versioned preference/policy registry with scope (surface/task), confidence, examples, expiry, and revocation; A decision-outcome event stream covering pendant acknowledgments, Mac receipts, browser approvals, and briefing dismissals; A conservative rule learner that distinguishes stable preference from one-off context; A spoken-plus-Mac review and rollback UI with exact before/after behavior simulation

### "“Help me negotiate this without committing me to anything.”"
- **useful because:** For an incoming request, bill, offer, scheduling demand, or support dispute, the owner would get a private negotiation packet: what the other party is asking, what the owner has already promised, hard constraints from calendar and account data, plausible concessions, a recommended position, and a ready-to-edit reply. The pendant can ask one focused question about the owner's priority; the Mac and authenticated browser can gather the surrounding evidence. Nothing is sent or accepted until the owner approves the exact wording and commitment.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-terminal → unified
- **model tier:** A background model extracts the request and generates alternatives from cited evidence; deterministic checks identify existing commitments and monetary/date changes. Realtime is reserved for the short clarification and spoken summary, not packet construction.
- **latency:** A packet from already-open sources should be ready in 30–90 seconds; broader research may take several minutes. Spoken clarification should be under 2 seconds after the packet is available.
- **cost:** Approximately $0.03–$0.25 per packet, dominated by reading private pages/threads and generating alternatives; deterministic constraint checks are negligible.
- **security:** The packet may contain private correspondence, account details, and negotiation strategy. Keep raw source material on its owning surface where possible, transfer only bounded excerpts with provenance, redact secrets in voice, and require explicit confirmation for every outbound message, acceptance, payment, cancellation, or changed promise. Never infer a reservation price or disclose one without the owner's statement.
- **missing:** A negotiation-specific packet schema for asks, constraints, concessions, authority, and commitments; Cross-surface extraction of the relevant thread/page plus the owner's existing commitments with stable citations; A consequence simulator that shows what each proposed reply would commit the owner to; A review UI and pendant interaction that supports edit, reject, or approve-exactly-this-text, with no implicit send


## Changes it proposed to its own stack

### `integration` — Create a durable obligation-and-conflict event layer between existing context graph/research/briefing routes: normalize commitments from Calendar, Mail, local notes, and authenticated browser extracts into typed obligations; emit idempotent conflict events with source citations, temporal/travel constraints, confidence, expiry, and a ranked set of reversible options. Persist a draft-only resolution packet that the Mac workbench and pendant queue can consume, with explicit owner approval required for any external mutation.
- **owner gets:** The owner gets an early, explainable warning that two promises cannot both be kept, plus a ready way out, rather than discovering the collision during a meeting or after a deadline. It turns existing disconnected reads and briefs into dependable life coordination.
- effort: Medium-high: schema and D1/R2 persistence, Calendar/Mail/notes/browser adapters, deterministic temporal rules, conflict deduplication, and a review/approval packet rendered by Mac and pendant. Start with calendar + browser deadlines, then add mail and local files.  ·  risk: False conflicts could create alert fatigue; mitigate with confidence thresholds, quiet-hour queueing, evidence links, and a dismiss/merge feedback loop. Never execute a cancellation, send, or reschedule from the detector. If a source is unavailable, mark the conflict incomplete rather than infer absence.
- cost: Low recurring storage and rule-evaluation cost; background model extraction is the dominant API cost, approximately cents per scan. No new hardware required.  ·  latency: Event ingestion is near-real-time where hooks exist; reconciliation is seconds to minutes. Spoken delivery waits for a stable packet and should remain under 3 seconds after it is queued.
- security: Sensitive source text stays bounded and provenance-tagged; spoken output uses redacted summaries. Approval packets must preserve the exact before/after effect and source evidence, and expired source extracts must be deleted on the retention policy.
- depends on: Durable typed context projection rather than hand-written fleetContext; Authenticated browser command/session reliability and truthful offline status; A durable review queue with acknowledgment, expiry, and approval gates; Calendar/Mail event or polling adapters on the Mac agent

### `integration` — Add a negotiation-packet compiler and consequence simulator that accepts a cited incoming request from Mail/browser, resolves only the owner's relevant calendar/account commitments, and produces three explicitly labeled reply variants (accept, counter, decline). For each variant, compute the exact new date, money, access, or communication commitments it would create, show source evidence and unresolved assumptions, and emit an immutable approval token tied to the exact text. Outbound adapters must reject any send or submit lacking that token.
- **owner gets:** The owner can respond confidently to difficult requests without manually reconstructing context or accidentally agreeing to something hidden in a polished draft. They see the consequences before committing and can approve only the exact reply they intend.
- effort: Medium: packet schema, evidence joiner, deterministic consequence rules, text/version hashing, and adapters for Mac Mail and authenticated browser forms; a Mac review surface and pendant summary are needed.  ·  risk: The model may miss an obligation or misread leverage; expose uncertainty and source excerpts, offer no-answer/ask-for-time variants, and fail closed when evidence is incomplete. Version hashes prevent a later edit from being sent under an earlier approval.
- cost: Small persistent storage and hashing cost; roughly cents per packet for extraction and alternatives, with no recurring cost after approval.  ·  latency: Compilation takes tens of seconds for local sources and minutes for multiple private tabs; exact-text approval and send can be immediate once the packet is ready.
- security: Sensitive negotiations stay scoped to the selected thread and sources, with redacted voice summaries and short-lived packet retention. Approval tokens are single-use, audience-bound, and cannot authorize unrelated actions.
- depends on: A stable cross-surface source citation format; Draft-only Mac Mail and browser form adapters; Durable versioned approval records and truthful send receipts; Owner-configurable retention and disclosure boundaries


## What it asked for

_Nothing._
## Its own summary

Round 112 produced two owner-facing additions beyond the existing brief/watch/action backlog: (1) conflict resolution that turns impossible combinations of calendar, mail, travel, local notes, and private browser commitments into cited, draft-only options; and (2) consent-based preference learning that turns repeated approvals/dismissals into reviewable, revocable personal rules without widening permissions. I also identified the concrete integration layer missing between existing context-graph, research, briefing, capture, browser, and job-receipt primitives.

**Biggest unknown:** Whether the current Mac agent can emit reliable Calendar/Mail/reminder/browser decision events with stable IDs and timestamps; without that event stream, both conflict detection and preference learning will be periodic, incomplete scans rather than trustworthy cross-surface behavior.

