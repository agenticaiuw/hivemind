# Harness derivation — faculty-judgement — round 207

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Give me my morning brief" should produce one coherent, three-minute-or-less brief even though several daily routines, research jobs, calendar/mail reads, and audio deliveries may be running."
- **useful because:** The owner currently has overlapping 07:00/07:30 routines and repeated failed briefing/news requests. A single transaction would prevent duplicate speech, distinguish an actually empty calendar from an unauthorised read, and tell the truth if audio was not downloaded or played.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Background model composes and deduplicates; realtime model only handles a follow-up question or interruption. Deterministic policy and attention arbitration decide whether to speak, queue, or suppress.
- **latency:** Start speaking within 20 seconds of the scheduled window; assemble slower sources in parallel and append only before playback begins. If a source misses the deadline, say it was unavailable rather than inventing completeness.
- **cost:** Roughly $0.01–$0.04 per brief, dominated by one background synthesis and optional web research; deduplication and delivery verification are local/relay logic.
- **security:** Calendar/mail content must remain behind the existing redaction and provenance paths. Missing permissions must be an explicit 'unreadable' state, never 'clear'. External actions are not part of briefing. Require no confirmation for reading, but do not speak secret content.
- **missing:** A durable briefing transaction that claims each source/run exactly once; Routine-level deduplication and a single owner-facing run ID; Source-read status that distinguishes empty from unauthorised for every briefing input; Use the existing pendant delivery ACKs to report downloaded/started/finished truthfully

### "When I repeat a request that failed (for example a news brief or browser inspection), tell me the concrete failure and offer the smallest repair or a safe alternate route instead of producing another empty attempt."
- **useful because:** The owner has repeatedly asked for the same headlines and inspections, with failures and 'No actions provided' recorded. Repetition is a strong signal that the system failed the owner, not that they changed their mind. A failure-aware loop would save time and make the pendant trustworthy: 'Browser is offline; I can search public sources instead' or 'I need the page URL again.'
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic grouping of recent failed jobs and intent fingerprints; a cheap background model classifies likely repair. Realtime model speaks one short repair question only when needed.
- **latency:** Detect on the next utterance (<500 ms) and produce one repair choice within 3 seconds. Never auto-repeat a failed external mutation.
- **cost:** Usually negligible; under $0.005 for occasional repair classification, with no web/model call when the failure is unambiguous.
- **security:** Do not expose raw error payloads, URLs containing credentials, or private page text in the spoken diagnosis. Read-only retries may be offered; sending, deleting, purchasing, or other mutations remain confirmation-gated. Keep a bounded failure fingerprint rather than full transcripts.
- **missing:** A durable cross-surface intent fingerprint joining relay, Mac, and browser failures; A repair taxonomy mapping failures to safe alternate actions; A rule that repeated failure escalates to the owner instead of retrying indefinitely

### ""Give me the top world and US headlines from the last 12 hours, in three short spoken sentences" should return exactly three sentences whose sources are published inside the requested window, with a compact source trail available if I ask."
- **useful because:** This is the owner's most repeated unmet request. Current research can produce a briefing, but it does not guarantee a twelve-hour cutoff, world/US balance, exactly three spoken sentences, or an honest 'not enough verified coverage' result. The owner gets a concise answer rather than repeated failed or stale attempts.
- **path:** relay → browser → pendant → dashboard
- **model tier:** Background model gathers and clusters headlines from independent sources; realtime model only delivers the already-validated three sentences. Deterministic validators enforce timestamp cutoff, sentence count, duplicate-story collapse, and source diversity.
- **latency:** Under 30 seconds for a scheduled or explicit request. If validation fails, speak one sentence saying coverage is incomplete and offer a retry; never fill the quota with stale stories.
- **cost:** About $0.02–$0.08 per request, dominated by web retrieval and one synthesis call; validation is local.
- **security:** Public-source retrieval only by default. Preserve URLs and publication timestamps in a reviewable dashboard receipt, but speak no raw article text beyond the three-sentence cap. Treat quoted claims as unverified until two-source agreement or explicit attribution.
- **missing:** A freshness-and-coverage validator independent of the summarizer; A news-specific source ledger with publication timestamps, region labels, and duplicate-story fingerprints; A spoken contract test that rejects output not matching exactly three short sentences

### "When I say “I’m leaving” or “I’m home,” have the whole system update a short-lived presence context that changes what the pendant, Mac, browser, and relay do until I say otherwise."
- **useful because:** The owner should not have to repeat that they are commuting, at home, or in a public place to every surface. A single explicit context could defer nonurgent audio, prevent private speech in public, pause browser automation, and resume queued work on arrival. This is a user-declared mode, not an inferred location claim.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic state machine with realtime parsing of the owner’s short utterance. No background model is needed except optional summarization of what was deferred.
- **latency:** Apply the mode within one second and acknowledge in one short sentence. Expire automatically after an owner-selected duration or explicit return command.
- **cost:** Negligible model cost; durable state and propagation dominate implementation.
- **security:** Never infer or announce physical location. Store only the owner’s chosen context label and expiry. Private/public behavior must use the owner’s policy table, and an emergency action must not be suppressed by an ordinary mode.
- **missing:** A signed, expiring presence-context record shared by all surfaces; Mode transition receipts and a queue of work deferred because of the mode; A policy binding context labels to audio, browser, and Mac behavior

### "“What did you actually change today?” should return a complete, plain-language ledger of external side effects across the Mac, browser, relay, and pendant, including actions that failed, were cancelled, or were undone."
- **useful because:** Today receipts are fragmented by job and surface, so the owner cannot reliably answer whether an email was sent, a file changed, a reminder was created, or a browser action merely prepared. A single side-effect ledger restores trust after autonomous work and exposes silent partial completion.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** Deterministic aggregation and classification; a cheap model compresses the result into the owner’s requested level of detail. Realtime is used only for a spoken query.
- **latency:** Under three seconds for the last 24 hours, with pagination for longer periods. The ledger must show provisional results immediately and reconcile late receipts without rewriting history.
- **cost:** Low: local aggregation dominates; under $0.01 for optional summarization.
- **security:** Redact secrets and private payloads while retaining action type, target class, timestamp, outcome, and reversibility. Never claim an effect from a plan or acceptance receipt alone. Destructive actions require especially prominent provenance and confirmation evidence.
- **missing:** One append-only effect record with a shared cross-surface correlation ID; A distinction between planned, accepted, executed, externally observed, cancelled, and undone; A reconciliation job for late Mac/browser and pendant delivery events

### "“Don’t do that again” should turn a correction I make once into a visible, expiring rule that all surfaces obey, and later show me when that rule changed a decision."
- **useful because:** The owner currently has to repeat corrections after a failed or surprising action. A correction should become a testable behavioral constraint—such as never speaking a category aloud, never using a particular browser account, or always asking before a class of action—without becoming an invisible permanent preference.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime model extracts the correction; deterministic validation checks scope, expiry, sensitivity, and conflicts before publishing it. Background evaluation can test recent decisions against the rule.
- **latency:** Acknowledge the captured rule in under two seconds, with explicit scope and expiry. Enforcement must be synchronous before any affected action is executed.
- **cost:** Low per correction; one realtime extraction plus deterministic policy evaluation. Periodic compliance scans can use a cheaper background model.
- **security:** Never silently convert an emotional utterance into a permanent policy. Show the normalized rule, affected surfaces, expiry, and conflicts before activation; destructive or broad rules require physical confirmation. Keep rule history so the owner can revoke it.
- **missing:** A durable cross-surface policy-rule store with scope, expiry, provenance, and conflict resolution; A correction-to-rule confirmation interaction; Enforcement hooks that reject actions before Mac/browser execution and before pendant speech


## What it asked for

_Nothing._
