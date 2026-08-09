# Harness derivation — faculty-judgement — round 227

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my morning brief self-healing: one canonical brief, no duplicate 07:00 jobs, and tell me if it was actually downloaded and played; if not, give me one catch-up instead of silently claiming success."
- **useful because:** The owner currently has multiple daily briefs and server-side completion is not pendant playback. This turns the brief from a generated file into a trustworthy, exactly-once experience.
- **path:** relay → mac → pendant
- **model tier:** Background model assembles and ranks the brief; deterministic relay/pendant delivery state handles dedupe and retry; realtime model speaks only the final short catch-up.
- **latency:** Routine check under 2 seconds; no owner-facing interruption unless the brief is urgent or the owner asks. Catch-up begins within 1 second after a deliberate request.
- **cost:** ~$0.01–$0.05 per daily brief depending on mail/research length; delivery verification and dedupe are negligible. Biggest cost is source reading, not arbitration.
- **security:** Do not infer playback from server generation. Store opaque artifact IDs and delivery ACKs, not raw audio in the relay. Calendar/mail content remains behind the existing redaction and owner policy; missing playback should produce a generic status unless the owner asks for details. Mutating/deleting duplicate routines requires confirmation.
- **missing:** A canonical routine identity and an owner-approved rule for which existing 07:00/07:30 routines survive; A durable relay-job lease/requeue so a crashed generation cannot create a second brief; A real writer for fleet memory or another durable cross-surface record of the canonical brief; A scheduler hook that consumes record_pendant_delivery_event and attention_arbitrate

### "When I come back after being busy or offline, give me one honest 'what I missed' handoff: group deferred alerts, stale page changes, unfinished jobs, and unheard audio into a short queue, with each item marked urgent, expired, or already played."
- **useful because:** Today deferred work is spread across browser reports, jobs, briefings, and pendant inbox state; the owner cannot tell what is still actionable versus merely generated. A single return-to-life handoff prevents both missed deadlines and repetitive nagging.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic attention arbitration and expiry first; a cheap background model compresses only the surviving items; realtime speaks the final digest on request.
- **latency:** Build the handoff in under 3 seconds after the owner asks; playback should start within 1 second. No unsolicited speech while the owner is speaking or in a quiet window.
- **cost:** ~$0.005–$0.03 per handoff; most runs need no model call if there are zero or one pending items. Costs are dominated by compression of multiple source excerpts.
- **security:** Never treat generated-but-unplayed as read. Use source IDs and evidence references, redact private content before audio, and expire sensitive summaries with the source. The pendant holds only opaque/short alert payloads and ACKs; external actions remain draft-only until physical consent.
- **missing:** A durable join between relay job IDs, Mac jobs, browser commands, and pendant artifact IDs; A production writer for deferred attention events and a replay-safe pending queue; A scheduler or return-presence hook using the existing idle/browser signals; A policy value from the owner for what may be spoken aloud; ship conservative non-content status by default

### "If a plan becomes stale while I am deciding, don't just fail: show me exactly what changed, withdraw unsafe steps, and offer a newly prepared reversible plan for the parts that are still safe."
- **useful because:** A browser page, calendar item, or file can change between preparation and approval. The owner gets a truthful recovery path instead of approving an action against yesterday's state or manually rebuilding the task.
- **path:** relay → mac → browser → pendant
- **model tier:** Typed revalidation, autonomy_policy_evaluate, and preflight make the safety decision deterministically; a background model explains the delta; realtime is used only for the owner's brief spoken choice.
- **latency:** Revalidation under 1 second for normal plans; regenerated draft under 5 seconds. No mutation occurs until the owner explicitly approves the replacement.
- **cost:** ~$0.002–$0.02 per stale-plan recovery; model cost is only the human-readable explanation. Browser/Mac state reads dominate latency, not tokens.
- **security:** Fail closed on missing provenance or changed sensitive fields. Never auto-approve the replacement. Keep old and new evidence references, redact snippets by default, and require physical approval for external side effects or spend.
- **missing:** A durable cross-surface plan identifier and relay↔Mac↔browser foreign-key mapping; A typed diff adapter for each plan step that returns changed fields without committing; A persistent approval decision on the relay, rather than Mac-local approval state; A user-visible recovery UI/audio contract for comparing old versus replacement steps

### "After I trigger the pendant privacy wipe, tell me what was definitely erased, what remote sessions were invalidated, and what cannot be verified yet—without replaying or exposing any erased content."
- **useful because:** A panic action is only trustworthy if the owner can understand its aftermath. This gives a bounded, content-free incident report across pendant, relay, Mac, and browser instead of a vague LED or false claim of total deletion.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic signed epoch and revocation accounting; no expensive model unless the owner asks for a natural-language explanation.
- **latency:** Local acknowledgement immediate; relay/Mac/browser reconciliation under 10 seconds after reconnect. Never delay the physical wipe for reporting.
- **cost:** Near-zero model cost; a few authenticated status reads and event writes. Storage is a tiny revocation epoch plus opaque session/artifact IDs.
- **security:** The report must contain no wiped audio, transcript, credentials, or sensitive snippets. Fail closed when a surface cannot confirm revocation; distinguish erased, revoked, pending, and unknown. Do not claim deletion from third-party systems without a receipt.
- **missing:** A cross-surface revocation-epoch protocol consumed by relay, Mac, browser, and pending jobs; A read-only endpoint that enumerates revocation coverage and outstanding acknowledgements; A durable mapping from device session/artifact IDs to remote jobs and browser sessions; Owner-approved policy for whether the local dashboard may show more detail than spoken output

### "After you say an action is done, verify the world—not just your own receipt—and tell me whether it was applied, merely submitted, contradicted by current state, or still unverified."
- **useful because:** A Mac receipt proves local acceptance, not that a browser site saved a change or an external service accepted it. This gives the owner an honest distinction between execution and effect, especially for consequential tasks.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic postcondition checks and provenance first; background model summarizes conflicts; realtime only speaks the short verdict.
- **latency:** Routine verification within 3 seconds after execution; long-running external effects become a pending status rather than blocking the owner.
- **cost:** ~$0.001–$0.02 per verification. Most cost is a browser/API read or Mac state read; model summarization is optional.
- **security:** Only perform read-only postcondition checks unless separately approved. Preserve before/after evidence with redaction, never infer success from HTTP 200 alone, and mark unsupported targets unverified. If the check would expose private content aloud, speak only the state label.
- **missing:** Typed postcondition declarations attached to prepared actions; A cross-surface receipt chain linking local action, browser command, remote acknowledgement, and observed final state; Read adapters for each external target with explicit freshness and confidence; Policy for what counts as sufficient evidence before the owner hears 'done'

### "When I am overloaded, quietly reduce the number of decisions I have to make: bundle reversible choices, defer low-value interruptions, and surface only the one decision whose deadline or consequence makes it worth my attention."
- **useful because:** The system should protect the owner's scarce attention, not merely rank notifications. Today it can see events and idle time but cannot recognize decision fatigue or change the shape of work accordingly.
- **path:** pendant → relay → mac → browser
- **model tier:** A small background model learns a personal decision-load signal from interaction timing, abandoned prompts, repeated deferrals, and active task count; deterministic policy enforces only owner-approved bounds. Realtime speaks one compact choice when necessary.
- **latency:** Continuous signals remain local/cheap; arbitration under 500 ms. The owner should never wait on a model to silence a low-value interruption.
- **cost:** ~$0.01–$0.05 per daily adaptation window; most decisions use cached features and deterministic rules. The expensive part is occasional calibration, not every interruption.
- **security:** This is behavioral profiling. Keep raw voice and message content out of the feature store; retain coarse counters with short TTLs and let the owner inspect, disable, or erase the profile. Never silently postpone a deadline-critical item.
- **missing:** An owner-visible decision-load profile with retention and opt-out controls; A policy language distinguishing deferrable decisions from deadline-critical decisions; Cross-surface features for unfinished Mac jobs, browser work, pendant interruptions, and speaking state; A learning/evaluation loop that asks for occasional correction instead of treating silence as approval

### "Let me run a personal experiment for a week—such as changing my morning routine or testing a focus habit—and have the pendant ask tiny check-ins, the Mac and browser observe the agreed outcome, and the system tell me whether it helped without pretending it proved causation."
- **useful because:** The owner gets a partner for changing real behavior rather than another reminder system. It turns vague intentions into bounded experiments with a baseline, a stop date, and an honest result.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model designs the experiment and summarizes results; deterministic scheduler and typed observations run it; realtime handles only short check-ins and end-of-experiment narration.
- **latency:** Check-ins must feel immediate; setup under 30 seconds. Weekly analysis can take up to a minute and should be delivered as a queued briefing.
- **cost:** ~$0.05–$0.30 per experiment, dominated by the final synthesis over several days. Device events and simple counts are negligible.
- **security:** Require explicit consent for every observation source and a clear end date. Store aggregates rather than raw transcripts or browsing history; never infer health or sensitive traits. The result must report uncertainty, missing data, and confounders.
- **missing:** An experiment schema with hypothesis, baseline, intervention, measures, consented surfaces, stop conditions, and expiry; A signed pendant check-in event that works offline and deduplicates on reconnect; Mac/browser observation adapters that emit aggregate measures rather than page contents; A statistical summary that refuses causal claims when adherence or data quality is inadequate

### "When I travel or cross time zones, ask me once which local clock should govern my routines, preserve the original deadlines, and explain every conversion instead of silently borrowing the Mac's timezone or the pendant's zoneless clock."
- **useful because:** A routine can be technically completed and still be wrong for the person if it fires at the wrong local hour. The current system has a machine timezone but no trustworthy owner-location timezone and the pendant cannot establish one.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic time conversion and conflict detection; realtime asks the one clarifying question; background model is unnecessary except for summarizing affected routines.
- **latency:** Detect a likely timezone conflict on reconnect or routine edit in under 1 second; ask only once per unresolved transition.
- **cost:** Negligible model cost. The main work is durable state and careful timestamp conversion.
- **security:** Location is sensitive. Store only the selected timezone and validity interval, not GPS or travel history. Never reinterpret an absolute deadline; show both source-zone and local-zone times before changing a scheduled action.
- **missing:** An owner timezone preference with explicit validity intervals, distinct from Mac system timezone; A pendant time-sync protocol that rejects zoneless timestamps rather than guessing; A routine migration preview and confirmation path for affected jobs; Cross-surface conflict detection when Mac, relay, browser, and pendant disagree


## What it asked for

_Nothing._
