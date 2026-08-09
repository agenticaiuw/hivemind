# Harness derivation — faculty-judgement — round 263

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run my morning brief once, and don't tell me it happened until the pendant confirms it actually started playing; if delivery fails, recover it or tell me plainly."
- **useful because:** The owner currently has two 07:00-ish morning routines plus a 07:30 routine, and server completion is not proof that anything reached or was heard by the pendant. This turns a scheduled promise into a truthful, deduplicated user-visible result.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** background for gathering and ranking; realtime only for the short spoken status
- **latency:** Schedule launch under 2 seconds; recovery on reconnect within one routine tick; spoken status under 3 seconds after an ACK or terminal failure.
- **cost:** Low: one background model call per brief (often already incurred); dominant cost is TTS/audio generation, not judgement.
- **security:** Only opaque artifact IDs and delivery states cross the relay; briefing text remains subject to existing redaction. Never claim heard from generated/accepted alone. Any retry must be idempotent and stop after expiry.
- **missing:** relay_jobs lease_until plus requeue sweep for orphaned jobs; routine-level dedupe key spanning the two 07:00 routines; wire record_pendant_delivery_event into the actual pendant ACK upload path; a small delivery-aware routine coordinator that maps routine/job/artifact IDs

### "When I come back, give me one honest 'what changed while I was away' card: unfinished work, new browser changes, messages that need me, and exactly what the pendant did or failed to play."
- **useful because:** Today catchup can read jobs and browser spool, but pendant-originated items are effectively always empty and server-side completion is conflated with delivery. A reconnect digest should reduce several silent queues to one actionable account, without pretending unreadable sources were clear.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background model for compression and ranking; realtime only to answer a follow-up question about one item.
- **latency:** Produce within 5 seconds of reconnect or explicit request; never block link recovery on model generation. If a source is unavailable, say so in the card.
- **cost:** Low-to-moderate: one short synthesis call per reconnect, dominated by context size; use deterministic filtering before model invocation.
- **security:** Source-linked snippets are redacted before speech; private/secret items become titles or counts unless the owner explicitly opens them. Include provenance and freshness per item, and dedupe replayed ACKs.
- **missing:** feed authenticated pendant delivery events and interrupted playback into catchupDigest; a durable relay-job-to-Mac-job correlation key rather than telemetry-only localJobId; source health/readability flags for calendar/reminders so empty is never rendered as all-clear; a single cross-surface catchup endpoint that merges jobs, browser reports, briefings, and delivery receipts

### "Before you act across my Mac and browser, tell me in one sentence what you can actually read, what you can draft, what needs my physical approval, and what will remain untouched; then carry out only the allowed part."
- **useful because:** The owner should not have to learn which body is online or discover after the fact that a browser session was stale, a permission was fake, or an action crossed from reversible draft into external side effect. This is the single most useful trust feature: truthful reachability plus bounded execution, not another clever answer.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** Deterministic policy/preflight first; cheap background model only to phrase the result; realtime model only for ambiguity in the owner's request.
- **latency:** Preflight under 500 ms when surfaces are healthy; one spoken sentence before mutation; no mutation if any required target is unavailable or stale.
- **cost:** Very low model cost because cross_surface_preflight and autonomy_policy_evaluate are deterministic; occasional model phrasing is the only variable cost.
- **security:** Fail closed on missing scopes, stale plans, unknown sensitivity, or changed evidence. Physical approval remains required for irreversible/external actions; never expose secrets in the spoken preflight. Every decision names the matched policy and evidence refs.
- **missing:** one orchestrator that composes cross_surface_preflight, autonomy_policy_evaluate, and revalidate_pending_plan before POST /execute; a typed result that distinguishes read/draft/mutate/destructive per target and carries freshness/provenance; enforcement hooks so Mac/browser executors cannot bypass the arbiter; durable approval decision handoff between relay and Mac


## Changes it proposed to its own stack

### `model-routing` — Add a mandatory claim-verification pass for every owner-facing spoken result that contains a concrete assertion: extract each claim, attach its source and freshness, classify it as observed/inferred/unverified, and block or qualify any claim lacking a current receipt. Use a cheap deterministic checker first and a background model only for ambiguous synthesis; realtime generation may not bypass the verifier.
- **owner gets:** The owner gets fewer confident falsehoods—especially about calendar, permissions, device state, and whether an action happened—and can hear a short honest qualification instead of a polished fabrication. This is different from an action receipt: it verifies the words about the world before they leave the speaker.
- effort: Medium: define a claim envelope, instrument Mac/relay/browser result producers, add a verifier middleware before TTS, and create regression cases for empty-calendar permission failures and stale job results.  ·  risk: Over-qualification could make speech tedious or suppress useful answers. Recover by limiting it to externally checkable claims, speaking only a compact uncertainty label, and retaining the full evidence view on the dashboard. If the verifier is unavailable, fail closed for high-impact claims and allow clearly labeled low-stakes summaries.
- cost: Small background-model cost only for ambiguous claim matching; deterministic extraction and receipt lookup dominate. No new hardware cost.  ·  latency: Typically 50–300 ms for deterministic checks; up to a few seconds for ambiguous multi-source synthesis, with a short 'checking' state rather than silent delay.
- security: Improves safety by preventing stale or unsupported private content from being spoken; claim envelopes must carry sensitivity and source IDs, and the verifier must never echo withheld snippets into logs.
- depends on: Wire GET /jobs/:jobId/receipts, GET /journal/:jobId, machine-context, browser status, and delivery ACKs into a common claim envelope; Fix the known unauthorised-calendar empty-result ambiguity before treating calendar absence as evidence; Ensure pendantSpeech and audioBrief pass through the verifier/redaction boundary rather than speaking raw result.message


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) a delivery-truthful, deduplicated morning brief that does not claim success until pendant playback is acknowledged; (2) a reconnect digest that says what changed, what remains, and what actually played; and (3) a single preflight sentence plus fail-closed execution boundary across relay, Mac, browser, and pendant. The third is the most valuable trust feature: the owner gets truthful reachability and bounded action instead of discovering surface limitations after the fact. I still need implementation of relay job leases/requeue, routine deduplication, real pendant ACK ingestion, cross-body job correlation, and enforcement hooks so executors cannot bypass policy. Owner preference decisions remain intentionally open: exact quiet hours, emergency categories, and which content may be spoken aloud or leave the machine.

**Biggest unknown:** Whether the owner wants the two overlapping 07:00 morning routines merged, disabled, or assigned different briefs; the current state proves duplication but not the intended replacement.

