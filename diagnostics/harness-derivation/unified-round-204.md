# Harness derivation — unified — round 204

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **memory-and-job-evidence** — Live memory is not yet trustworthy as owner-facing truth: /memory/facts contains preference.timezone=America/Chicago from origin=machine, conflicting with the authoritative Mac timezone America/New_York; /context-graph contains Unknown entities and email drafts whose bodies include message content; /jobs exposes a completed browser_read_page result with extensive Discord page text. /workbench/contexts is currently empty.
  - evidence: Parallel GET /memory/facts, GET /context-graph, GET /jobs, and GET /workbench/contexts in round 204; all returned HTTP 200.

## Capabilities it proposed

### "“Did you actually finish that, or did you just say you would?”"
- **useful because:** Prevents the most damaging failure mode: the system claiming completion when a browser command, Mac action, relay delivery, or pendant playback stopped halfway. It waits for corroborating receipts and speaks uncertainty plus the next safe step instead of inventing success.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic receipt quorum first; background model only to summarize conflicting evidence; realtime only for the short spoken answer.
- **latency:** Under 2 seconds for an existing job; up to 5 seconds if browser and Mac evidence must be fetched.
- **cost:** Usually <$0.001 in API cost; dominated by zero-cost local/relay reads, with model spend only when evidence conflicts.
- **security:** Read-only by default. Bind evidence to the job/commitment and explicitly allowed browser tabs/apps; never infer success from an absent receipt. Do not expose page contents beyond the minimum evidence capsule.
- **missing:** A production policy that blocks completion language until a required evidence quorum is met; A small cross-surface correlation record linking relay job, Mac receipt, browser command, and optional audio-delivery receipt; A truthful spoken vocabulary for partial, unknown, and failed completion

### "“What is waiting for me right now? Give me one short answer, not a pile of notifications.”"
- **useful because:** The pendant becomes an attention surface rather than a dump: it combines held relay work, unfinished Mac/browser jobs, staged approvals, unread pendant inbox items, and evidence-backed commitments, then returns only the highest-value next item with an expiry and a safe action.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic inventory, deduplication, expiry, and urgency policy; background model compresses the selected item into one sentence; realtime speaks it.
- **latency:** Under 2 seconds from button press or spoken request; stale sources are labeled rather than blocking the whole answer.
- **cost:** <$0.001 per check; local and relay reads dominate, with a small background summarization call only when wording is needed.
- **security:** Read-only inventory until the owner deliberately approves an action. Respect quiet-hours and the owner’s conservative interruption default. Do not reveal browser titles/content unless the tab binding permits it; distinguish pending from failed and expired.
- **missing:** A single normalized pending-item schema with source, expiry, urgency, and safe-next-action fields; Cross-surface deduplication by commitment/job/receipt ID; A pendant delivery path that can surface the selected item on the next natural turn without interrupting active speech

### "“You have two different answers about me. Which one are you using, and ask me before choosing.”"
- **useful because:** Today a machine-derived timezone can conflict with the owner’s explicit timezone while both remain usable-looking facts. This capability detects contradictions before they affect routines, permissions, or spoken claims; it presents the competing values, provenance, and affected decisions, then records the owner’s choice as the authoritative resolution.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic contradiction detection and dependency blocking; realtime only asks the short clarification; background model may explain impact in plain language.
- **latency:** Detect during fact write or projection refresh; spoken clarification under 2 seconds.
- **cost:** <$0.001 per conflict; primarily local graph/fact comparison, with no model call for simple values.
- **security:** Do not expose sensitive source content merely to explain a conflict. Bind the resolution to a fact version and invalidate dependent routines or permissions when the chosen value changes.
- **missing:** A conflict index over facts, projections, context-graph entities, and routine parameters; Dependency links from each fact to decisions that consumed it; An owner resolution record with versioning and invalidation semantics

### "“Why do you believe that? Show me the shortest trustworthy chain from what happened to what you just said.”"
- **useful because:** The owner can currently hear conclusions without a compact way to inspect their provenance. This returns a bounded evidence chain—utterance or event, extraction, transformations, and the final claim—without dumping an entire browser page, conversation, or job log.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic provenance traversal and redaction; a background model compresses only the already-authorized chain into one sentence.
- **latency:** Under 3 seconds for a stored claim; stale or missing provenance must be reported explicitly.
- **cost:** <$0.002 per request; storage reads dominate and summarization is optional.
- **security:** Least-privilege evidence capsules only; source text remains on its originating surface unless the owner explicitly asks for it. Every hop must carry retention, sensitivity, and authorization metadata.
- **missing:** A stable provenance graph linking extracted facts and claims to evidence capsules; A redaction-aware evidence-capsule endpoint; A spoken/dashboard renderer that distinguishes direct evidence, inference, and machine metadata

### "“Give me an audit receipt, but do not copy the private page or message into every system that handled the job.”"
- **useful because:** Current job results can contain full browser page text even when later consumers only need to know that a bounded action succeeded. This creates audience-specific audit views: the pendant hears a minimal result, the relay stores a digest and status, and the dashboard can open sensitive evidence only under the correct binding.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic receipt projection, hashing, redaction, and audience policy; no model is needed for the security boundary.
- **latency:** Receipt projection under 500 ms after a result; sensitive evidence fetch under 2 seconds when explicitly requested.
- **cost:** <$0.001 per receipt; dominated by hashing and local storage.
- **security:** Never treat a digest as proof of content unless the source remains available and bound to the same job. Use separate audience scopes, expiry, revocation, and tab/app bindings; preserve immutable audit metadata without retaining page bodies by default.
- **missing:** Audience-scoped receipt schemas; Content minimization before relay persistence; Digest verification and expiry-aware evidence retrieval; A migration path for existing oversized browser results


## What it asked for

_Nothing._
