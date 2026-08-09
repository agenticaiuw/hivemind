# Harness derivation — faculty-judgement — round 159

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me one morning brief, and prove whether I actually heard it; if the pendant was offline, leave exactly one catch-up note instead of speaking twice.”"
- **useful because:** Today several daily routines can generate overlapping briefs, and server-side completion is not proof of download or playback. A delivery-closed loop would make the morning brief dependable: one coalesced item, one spoken attempt, and an honest fallback when the worn device never received it.
- **path:** relay → mac → pendant → dashboard
- **model tier:** background for composing and deduplication; realtime only for the short spoken handoff
- **latency:** Compose within 10 seconds; delivery reconciliation may continue for 2 minutes without blocking the owner.
- **cost:** About $0.01–$0.04 per briefing depending on source reads; the dominant cost is composition, not ACK processing.
- **security:** Only opaque artifact IDs, checksums, positions, and delivery states cross surfaces; briefing text stays on the intended speech path. Replays must be deduplicated by eventId and an expired artifact must never be re-spoken automatically.
- **missing:** A durable coalescer that maps the daily routine outputs to one briefing item; A production writer for pendant delivery ACKs and a query that joins them to relay/Mac job IDs; A retry policy that creates a local note only after a bounded, provenance-backed delivery failure

### "“Before you blame the network, run a wearable link-and-audio health check and tell me which layer failed.”"
- **useful because:** The pendant is physically testable over USB today, but a generic failed conversation does not distinguish UART framing, radio/link absence, Opus starvation, bridge output, or playback delivery. A guided test would turn a vague failure into one actionable diagnosis and a repeatable regression check.
- **path:** pendant → mac → relay → dashboard
- **model tier:** background deterministic test runner; use the expensive model only to summarize anomalous measurements
- **latency:** A quick check in 15 seconds, with a full 60-second acoustic/transport test available on request.
- **cost:** Near-zero model cost for the deterministic run; under $0.01 for a concise anomaly summary.
- **security:** Generate synthetic tones and nonce-tagged markers, never record or upload conversational microphone content. UART logs should be locally redacted and drafts remain unsent until owner review.
- **missing:** A safe structured UART parser with frame counters and layer-specific classifications; A USB test protocol that requests nonce-tagged loopback/audio markers from both chips; A dashboard report correlating UART, pipeline, Opus, bridge, and pendant playback ACK timelines

### "“Never read private-looking content aloud by accident; give me a safe confirmation and put the detail in a reviewable note instead.”"
- **useful because:** The strongest redaction currently exists only in briefingTriage; pendantSpeech and audioBrief can speak arbitrary result text. A single cross-surface speech firewall would prevent accidental disclosure in ordinary confirmations, browser results, and job receipts while preserving useful short spoken feedback.
- **path:** relay → mac → pendant → dashboard → browser
- **model tier:** Deterministic classifier and policy engine; expensive model only when the owner asks to classify an ambiguous sentence
- **latency:** Under 100 ms for known sensitivity classes; ambiguous cases become a silent/short confirmation rather than waiting for a model.
- **cost:** Negligible per utterance; occasional ambiguity classification under $0.01.
- **security:** Default to no content for secret and private classes, and make destination policy owner-configurable rather than guessing trusted recipients. Use withheldOrEmpty, not the known-broken sentence masker. Every suppression should carry a policy rule and provenance reference; external mutations still require the existing physical approval.
- **missing:** A shared enforcement hook before every pendantSpeech/audioBrief synthesis; An owner-editable destination/data-class policy with conservative defaults; A real bystander/public-presence signal or an explicit owner-selected mode; idle time is not proof of privacy; A deletion/revocation link from derived facts and graph copies back to evidence

### "“Tell me what this pendant, Mac, browser, and relay could still reveal if my bag disappeared—and contain it without making me inspect every subsystem.”"
- **useful because:** A panic wipe is an emergency switch, but the owner cannot presently see the exposure surface before an emergency: queued audio, browser spools, cached credentials, evidence remnants, logs, and relay sessions have different lifetimes and deletion semantics. A loss-readiness audit would turn invisible risk into one bounded decision and verify containment afterward.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** Deterministic inventory and policy evaluation; use the expensive model only to explain the resulting exposure in plain language.
- **latency:** Under 15 seconds for a local audit; remote-session invalidation and verification may take up to 60 seconds.
- **cost:** Negligible API cost; dominated by local file and session enumeration.
- **security:** The audit must return classifications and hashes, never expose secret contents to the model or dashboard by default. Containment requires explicit confirmation except for the already-held physical panic latch. A failed verification must be reported as unresolved, not “secure.”
- **missing:** A cross-surface exposure inventory with common artifact classes and expiry state; A verified containment operation that rotates relay/Mac/browser sessions and confirms pendant wipe epochs; A provenance-backed report of what was found, what was removed, and what could not be reached

### "“Prepare this for another person without giving them my whole history, and let me see exactly what you chose to disclose before it leaves.”"
- **useful because:** The system can act across the owner's private browser, Mac, relay, and pendant, but it has no first-class human-to-human handoff. Today the owner must manually copy context, risking over-disclosure or omissions. A selective handoff packet would package only the relevant facts, evidence citations, open questions, and requested action for a named recipient, with a reviewable redaction diff.
- **path:** browser → mac → relay → pendant → dashboard
- **model tier:** Background model for relevance ranking and concise rewriting; deterministic redaction, provenance, and recipient policy enforcement around it.
- **latency:** Draft in 10 seconds; no external send until the owner reviews and confirms the disclosure diff.
- **cost:** Approximately $0.02–$0.08 per packet, dominated by source summarization; previews can be deterministic when no rewriting is needed.
- **security:** Recipient identity and destination must be explicit. Secrets, credentials, third-party personal data, and raw browser quotes default to withheld. The packet must retain source IDs and a non-repudiable record of exactly what was approved; sending remains destructive/externally visible and requires confirmation.
- **missing:** A durable selective-disclosure packet with recipient, purpose, expiry, and source links; A recipient-aware policy beyond the current three-way sensitivity classifier; A rendered side-by-side disclosure preview and approval record spanning Mac, browser, and relay

### "“When I am unreachable, keep the important part of this conversation alive—but do not keep the recording—and bring it back only when the right person or system can continue.”"
- **useful because:** A dropped link currently leaves the owner with fragmented jobs, audio, and notes. The owner needs continuity without routine speech retention: a compact, expiring handoff containing the unresolved objective, last verified state, next safe step, and evidence references, which can resume on the Mac, browser, or pendant when a surface returns.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic extraction of objective/state/evidence; background model for compression and ambiguity labeling; realtime only when the owner resumes speaking.
- **latency:** Create the handoff within 2 seconds of link loss; resume in under 5 seconds after a surface becomes available.
- **cost:** Under $0.02 per handoff; most packets should be deterministic and fit within existing context budgets.
- **security:** Never store raw PCM by default. Handoffs need short TTLs, explicit sensitivity, source references rather than copied secrets, and invalidation after a newer state supersedes them. Resumption must revalidate browser/Mac state and require confirmation before any external mutation.
- **missing:** A durable, typed interruption handoff distinct from ordinary context prompt caching; A link-loss detector that can seal the last verified conversational state without retaining audio; A resume chooser that presents competing stale handoffs and refuses unsafe automatic continuation


## What it asked for

_Nothing._
