# Harness derivation — faculty-judgement — round 149

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "While you're speaking a briefing, I can say “that's wrong” or “remember this instead,” and you will repair the exact item rather than making me repeat the whole request."
- **useful because:** The pendant is the only surface that knows which sentence I am reacting to. This turns spoken correction into a durable, source-linked repair: pause the sentence, capture my correction, retract or supersede the bad claim, and make later briefings stop repeating it. Today corrections either become ungrounded notes or are lost in conversation.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Realtime only for binding the utterance to the active audio item and extracting the correction; a cheaper background model normalizes the claim and compares sources. Deterministic policy and provenance code decide whether to supersede, flag, or ask.
- **latency:** Pause in under 250 ms; acknowledge in under 2 s; background reconciliation may take 10–30 s and must not block playback.
- **cost:** About $0.002–$0.01 per correction depending on transcript length and whether source comparison invokes a model; storage and local routing dominate less than model context.
- **security:** The correction may contain private information and must not be spoken back verbatim in public. Require explicit confirmation before it changes an external action. Preserve the original evidence and a revocable correction chain; never silently overwrite history. Sensitivity classification must be applied before TTS and outbound prompts.
- **missing:** An atomic claim-correction transaction linking audio item, evidence capsule, memory fact, and any fleet-memory event; A writer for shared fleet memory (the schema and routes exist but production has zero writers); capsuleId on derived memory facts and a real cascade when evidence is revoked; A production route that maps the active pendant audio cursor to the originating briefing item and source IDs

### "When the pendant reconnects after being away, tell me only what changed that I did not actually hear: unfinished jobs, new page-watch findings, and announcements, with each item marked heard, partially heard, or unheard."
- **useful because:** A normal catch-up repeats audio the owner may already have heard and misses device-local playback failures. This would make reconnection trustworthy: it joins relay/Mac/browser changes to authenticated pendant download and playback ACKs, then gives one compact delta instead of a noisy backlog. It is especially useful now because the pendant is physically testable over USB even though LTE registration is absent.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** No expensive model for the join or heard/unheard classification. Use deterministic event correlation and attention_arbitrate; use a cheap background model only to compress the final spoken delta. Realtime is reserved for a follow-up question about one item.
- **latency:** On USB reconnect, produce a first count in 1 s and a spoken digest in 3–5 s; full source refresh can continue in the background.
- **cost:** Typically under $0.001 for deterministic joins; $0.002–$0.006 if a model compresses more than a few items. USB/relay polling and event storage dominate operational cost.
- **security:** ACKs must contain opaque artifact IDs and positions, not transcript or private audio. Do not infer that downloaded means heard; only playback_started/finished establish those states. Deduplicate offline replay by eventId and device sequence, reject stale sessions, and suppress sensitive summaries unless the owner explicitly requests detail. Never mark an external action complete merely because its audio was played.
- **missing:** A durable cross-surface foreign key from relay job/briefing item to the audio artifact and from that artifact to source evidence; Wiring the pendant ACK queue into POST /pipeline/events with authenticated session and monotonic replay checks; A reconciliation service that joins ACKs, /catchup, relay jobs, browser-watch reports, and Mac receipts without treating empty sources as success; A reconnect trigger on USB serial attach (the current device is physically connected but not relay-registered)

### "Stop using anything from this site, sender, or browser account in my briefings and plans, and show me exactly what you stopped using."
- **useful because:** The owner can revoke one evidence capsule today, but derived facts, browser findings, prompt projections, and future reads continue because there is no source-level quarantine or propagation. A single spoken command should halt fan-out immediately across the browser, Mac, relay, and pendant, while preserving a reviewable list of affected claims and allowing explicit restoration later.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic matching, source filtering, and revocation should be local and cheap. Use a background model only to resolve an ambiguous spoken origin (for example, which of several similarly named sites); require confirmation before choosing among matches.
- **latency:** Local stop in under 500 ms and spoken confirmation in under 2 s. Rebuilding affected projections may run in the background, with a dashboard showing progress.
- **cost:** Under $0.002 for an exact-origin quarantine; $0.01–$0.03 only when ambiguity requires model-assisted entity resolution. Storage is a small durable policy plus tombstones.
- **security:** Fail closed on ambiguity: do not quarantine a broad domain or person without showing the match. Quarantine is not deletion; retain minimal tombstones and provenance IDs so the owner can audit and restore. Do not speak private source names in a public setting without a confirmation policy. Every blocked use should report the rule and source IDs, not silently produce an incomplete briefing.
- **missing:** A durable source-quarantine registry shared by Mac and relay, with exact origin/host/account selectors, expiry, and restore; Enforcement hooks in browser reads, memory projection, fleet projection, briefing triage, research, and action planning; A propagation job that links and retracts derived facts and graph copies; current facts lack capsuleId and context-graph copies have no TTL; An owner-facing preview of affected claims before broad quarantine, plus an idempotent restore operation

### "I changed something fundamental—my address, employer, relationship, or daily routine. Show me every dependent reminder, browser account, saved fact, briefing rule, and pending plan that this change may invalidate, then let me approve the updates as one reviewable batch."
- **useful because:** Important life changes currently become isolated notes. The system continues acting on stale assumptions across the Mac, authenticated browser, relay memory, and pendant briefings. The owner needs consequences, not merely storage: one declaration should expose stale downstream state and offer a bounded, reversible migration without silently editing external services.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use the realtime model only to capture and disambiguate the owner's declaration. A cheaper background model can rank dependent records; deterministic provenance, policy, and precondition checks decide what is actually affected. No external mutation occurs during analysis.
- **latency:** Acknowledge the declaration in under 2 seconds. Produce an initial impact list in 10 seconds; deeper browser and Mac scans may continue for a few minutes. Applying a batch requires a deliberate owner confirmation.
- **cost:** Approximately $0.01–$0.05 per life-change scan, dominated by dependency extraction and browser/page analysis. Most graph traversal and stale-record detection should be local and deterministic.
- **security:** Life changes can reveal highly sensitive personal information. Keep the declaration local unless the owner approves relay processing; redact it in spoken confirmations. Never rewrite credentials, forms, financial records, or external accounts automatically. Each proposed update needs source evidence, an old/new diff, a precondition, an expiry, and an undo path. A failed migration must leave the original state intact.
- **missing:** A typed dependency graph connecting facts, context-graph entities, reminders, routines, briefing policies, browser origins/sessions, pending plans, and action receipts; A change-impact evaluator that distinguishes confirmed dependencies from model guesses and returns an explainable affected-set; A durable reviewable migration plan with per-item approval, atomic/idempotent application, and rollback across Mac and browser surfaces; Cross-store provenance and deletion/update propagation; current derived facts and context-graph copies are not reliably linked to their sources; A safe owner-facing dashboard and pendant summary that can handle dozens of proposed changes without speaking private values aloud

### "Why did you do that yesterday? Reconstruct exactly what you knew, what you did not know, which policy version you used, and what action followed—without replacing today's state."
- **useful because:** Current provenance explains an item or receipt, but it cannot answer the owner's real retrospective question when facts, permissions, browser pages, and policies have since changed. A temporal decision replay would make mistakes understandable, support disputes and recovery, and distinguish a bad judgement from stale or missing evidence.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic event reconstruction first. A cheap model can summarize the reconstructed timeline; realtime is only needed if the owner asks follow-up questions. Never let the summarizer invent missing events—unknown intervals must remain explicit.
- **latency:** Return a compact timeline in 3 seconds for a normal job; retrieve deeper evidence in under 15 seconds. Spoken output should start with the conclusion and offer dashboard detail.
- **cost:** Usually below $0.005 because receipts and event joins are local; $0.01–$0.03 for long evidence summarization.
- **security:** Historical views may expose private mail, browser content, or credentials that are no longer allowed today. Apply the historical policy and current disclosure policy separately, defaulting to metadata-only spoken output. Preserve immutable event hashes and mark gaps, clock uncertainty, redactions, and inferred joins. This is read-only unless the owner separately asks for repair.
- **missing:** An append-only, durable event ledger with common correlation IDs across relay jobs, Mac jobs/actions, browser commands, pipeline artifacts, policy decisions, and pendant playback; Versioned snapshots of autonomy, attention, disclosure, and source policies, rather than only current configuration; Timestamped evidence validity and revocation history that can distinguish what was available then from what is revoked now; A deterministic historical joiner that reports uncertainty instead of silently joining unrelated ID namespaces; A dashboard timeline and concise spoken renderer with metadata-only and owner-confirmed sensitive-detail modes


## What it asked for

_Nothing._
