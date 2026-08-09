# Harness derivation — faculty-judgement — round 148

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What was I doing around 11, and what did I leave unfinished?” Give me a private, source-linked timeline of my workday, with episodes rather than surveillance footage."
- **useful because:** The system currently stores fragments—foreground app, browser activity, calendar, jobs, audio playback—but cannot turn them into an owner-facing account of a day. A timeline would let the owner recover lost context, notice abandoned work, and ask follow-up questions without manually reconstructing tabs and receipts. Raw page text and audio stay on the Mac; the relay receives only a short, redacted episode projection when needed.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** background for episode segmentation and end-of-day summaries; realtime only for a query about a specific interval
- **latency:** Capture is append-only and sub-100 ms per event locally; a query should answer in under 3 seconds, with a 10-second background compaction budget.
- **cost:** About $0.01–$0.05 per generated daily summary, dominated by one background model call; interval queries can be local and cost $0 when no synthesis is needed.
- **security:** This is sensitive behavioral data. Keep raw URLs, page text, and audio markers local with a 24-hour default TTL and an owner-visible delete-by-episode action. Relay receives only redacted episode labels and source IDs, never raw browsing or microphone content. Dashboard must show every source contributing to an episode.
- **missing:** a durable local episode/timeline store with typed start/end, source IDs, confidence, and retention; adapters that emit foreground-app changes, browser tab transitions, calendar windows, Mac jobs, and authenticated pendant playback ACKs into that store; an episode segmenter that distinguishes active work from idle gaps without claiming presence during uncertainty; a query route and dashboard view with source-linked deletion

### "“I’m back. Catch me up on what changed while I was away, then put me back where I left off.”"
- **useful because:** Current catch-up is a pile of jobs and alerts, not continuity. This would use the pendant as the owner's explicit return signal, compare before/after Mac and browser state, explain only meaningful changes, and stage restoration of the last safe working context. It turns a dropped link, commute, or lunch break into a clean return instead of a forensic search.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** background for state diff and ranking; realtime for the short spoken return brief
- **latency:** A local snapshot on the return marker in under 500 ms; a spoken delta within 5 seconds; restoration remains staged until the owner confirms.
- **cost:** Typically $0.01–$0.04 per return, dominated by one compact diff-ranking call; all snapshots are local and bounded.
- **security:** A return brief must not read private page contents aloud by default. Store hashes, titles, app names, job IDs, and provenance rather than full snippets. Restoration is prepare-only until the physical transaction approval latch confirms; stale plans are revalidated before reopening or changing anything. If the pendant is offline, the Mac records the return marker and reconciles later.
- **missing:** a paired departure/return session record using the existing sw1 offline marker payload rather than a new gesture or queue; a local snapshot/diff engine for foreground app, browser tabs, pending jobs, watches, and staged audio; a typed restore plan with per-step preconditions and a single physical approval boundary; a compact return-brief route that uses the attention arbiter and exposes changed-only evidence

### "“Before I send this, show me exactly what the other person or site will receive, what came from my private data, and what could surprise me.”"
- **useful because:** A normal preview shows fields and syntax, but not the recipient's actual view or the provenance and sensitivity of each value. This capability would render the final email/form/browser submission from the authenticated session, annotate every field with its source and age, flag secrets or third-party data, and produce a concise spoken warning. The owner gets a meaningful last look before an external side effect, not a generic 'are you sure?'
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** realtime for the final explanation only; deterministic local rendering, provenance joins, and policy evaluation do the bulk of the work
- **latency:** Draft preview in under 2 seconds for Mac forms and under 5 seconds for browser forms; never submit automatically. A physical approval can remain valid only for a short, revalidated window.
- **cost:** Usually $0.00–$0.02; model cost is only for compressing a large field-level diff into spoken language.
- **security:** The preview must redact credentials and secrets from the pendant and relay while retaining local hashes and field labels. It must refuse to claim what a site will receive when the browser cannot expose the rendered request. No send/submit action is allowed from the preview; the existing approval latch signs a hash of the exact rendered payload, target origin, and expiry. Any DOM or draft change invalidates approval.
- **missing:** a recipient-view renderer that can derive the actual outgoing representation without submitting; field-level provenance links from memory/facts, browser extraction, Mac drafts, and form previews; a policy table for destination class versus data class, with owner-editable trusted origins and named block reasons; an atomic preview-hash-to-physical-approval binding and stale-plan recheck

### "“If I say yes to this, what else will have to move—and what is the smallest honest commitment I can make instead?”"
- **useful because:** The owner needs help with consequences before committing, not merely a reminder after the fact. This capability would model a proposed commitment against known calendar windows, reminders, active projects, browser work, pending jobs, and existing commitments; show conflicts and uncertainty; then draft a smaller alternative (shorter meeting, async reply, or a deadline) without sending or scheduling it. It is a counterfactual life-planning tool, not another task list: it tells the owner what accepting one thing costs.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background for gathering and constraint modeling; realtime only to explain the top two consequences conversationally
- **latency:** A read-only consequence model in under 6 seconds; draft alternatives in under 10 seconds; no external mutation without a separate owner-approved action.
- **cost:** $0.02–$0.08 per scenario, dominated by one reasoning call over compact, cited state; source reads and conflict arithmetic are local/deterministic.
- **security:** The model must distinguish observed commitments from inferred ones and expose stale or unauthorized sources instead of treating missing data as free time. Sensitive event titles and mail bodies remain local; the relay receives redacted constraints. Suggestions are drafts only. Any created reminder, reply, or calendar change requires autonomy_policy_evaluate, provenance, stale-plan revalidation, and physical approval.
- **missing:** a typed counterfactual scenario object that records proposed commitment, affected windows, assumptions, and expiry; a read surface for reminders and calendar that returns an honest unreadable/unauthorized state rather than an empty list; a constraint solver that can rank alternatives by time, deadline, and confidence; a dashboard and spoken explanation that cites each conflict and lets the owner accept only a draft


## What it asked for

_Nothing._
## Its own summary

Round 148 produced three new owner-facing capabilities: a private source-linked workday timeline, an explicit return-from-absence continuity brief with staged restoration, and a recipient-view preview that annotates exactly what an external site or person will receive before physical approval. The first two make the pendant a continuity device rather than merely an alert speaker; the third makes it a trustworthy boundary before consequential communication.

**Biggest unknown:** I still need owner decisions, not more infrastructure guesses: the retention window and deletion semantics for behavioral timelines, which destinations/data classes may be shown in a recipient preview, and whether return restoration may reopen apps/tabs automatically after physical approval. Technically, the largest missing pieces are the local episode/snapshot stores and the recipient-view renderer; I would keep raw data on the Mac and fail closed when a browser cannot reveal the actual outgoing payload.

