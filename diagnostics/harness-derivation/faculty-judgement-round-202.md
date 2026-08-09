# Harness derivation — faculty-judgement — round 202

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my scheduled briefings get smarter: only interrupt me when I actually need to hear something, remember what I heard, and roll anything missed into the next brief without repeating it."
- **useful because:** Today a routine can be marked completed even when audio delivery is unknown or playback never began, so the owner can silently miss decisions and receive duplicates. This would turn delivery evidence into a personal attention loop rather than a pile of successful server jobs.
- **path:** relay → pendant → mac → dashboard
- **model tier:** Cheap background model for item novelty/compression; realtime only for the spoken brief. Deterministic policy and delivery ACKs decide state without an expensive model.
- **latency:** Routine generation can take 1–3 minutes in the background; next spoken response must begin within 2 seconds once the owner asks. ACK reconciliation is sub-second.
- **cost:** About $0.01–$0.05 per daily digest depending on source count; dominated by research/summarization, not ACK or policy evaluation.
- **security:** Do not infer that generated means heard. Keep opaque artifact IDs and playback evidence; spoken content must pass the existing redaction path. Missing playback should create a quiet retry/draft, not an urgent interruption. Owner must be able to erase the hearing history.
- **missing:** A durable per-item briefing delivery state that joins routine/job/item IDs to record_pendant_delivery_event events; A background dedupe/novelty worker that updates the next briefing from heard/unheard state; A dashboard control to forget hearing history and choose retry versus queue

### "Give me a three-sentence world-and-US news brief that is genuinely new since the last one, says what changed rather than replaying headlines, and leaves cited sources I can inspect later."
- **useful because:** The owner's repeated headline requests indicate a high-value daily use, but a short spoken digest is easy to make repetitive or overconfident. Novelty tracking plus source citations gives the owner useful awareness without making them listen to a news dump.
- **path:** browser → relay → mac → pendant
- **model tier:** Cheaper background model clusters and compares headlines; realtime model only turns the selected three developments into a concise spoken answer when requested.
- **latency:** Precompute in 2–5 minutes on schedule; interactive playback starts under 2 seconds if the digest is cached, with a truthful fallback if sources were unreachable.
- **cost:** Roughly $0.03–$0.15 per digest, dominated by web retrieval and cross-source comparison; cached unchanged stories cost near zero.
- **security:** Public-source browsing only by default; never send authenticated tabs or private mail into news research. Every sentence carries source URLs and capture time; if sources conflict, say so rather than flattening it. No automatic posting or subscription changes.
- **missing:** A durable story identity/seen ledger with expiry so unchanged headlines are suppressed without retaining full article text; A research result schema that binds each spoken sentence to source URLs and retrieval timestamps; A scheduled audio artifact that can be played later and records downloaded/started/finished ACKs

### "Find my duplicate or misleading daily routines, show me one plain-English repair plan, and let me approve consolidating them without losing their history."
- **useful because:** The owner currently has two 07:00 morning jobs and two 17:00 jobs with overlapping purposes. That creates duplicate speech, wasted model spend, and uncertainty about which routine actually ran. A reviewable consolidation preserves intent while removing noise.
- **path:** relay → mac → dashboard → pendant
- **model tier:** Deterministic grouping by schedule/time/command similarity first; a cheap model explains the overlap and drafts one canonical routine. No realtime model unless the owner asks by voice.
- **latency:** Under 10 seconds for the conflict report; under 30 seconds to prepare a repair plan. Mutation only after explicit approval and should be reversible.
- **cost:** Usually under $0.01 per scan; dominated by one optional explanation call. No ongoing cost after consolidation.
- **security:** Read-only discovery must distinguish machine timezone from owner's stated timezone; use reconcile_personal_state before proposing changes. Never delete a routine silently: preserve disabled records, show exact schedule changes, require confirmation, and provide undo.
- **missing:** A typed routine conflict/merge planner that recognizes semantic overlap, not just identical names; A durable approval link between the displayed plan and the routine mutations, with expiry and undo; A post-change verification that checks nextRunAt and confirms only one canonical briefing will fire

### "When something I asked fails, tell me exactly what failed, what you did verify, and offer the smallest next step instead of saying it worked or silently retrying."
- **useful because:** The owner's history contains repeated failed headline, browser, and time requests. Trust is lost less by a refusal than by a confident-looking empty result. This would make the pendant a reliable partner under degraded links, permissions, and stale browser sessions.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic receipt/provenance classification first; a cheap model converts the structured failure into one short spoken sentence. Realtime is only needed when the owner is actively waiting.
- **latency:** Failure classification under 500 ms after a receipt; spoken recovery under 2 seconds. Background retries must never delay the truthful failure.
- **cost:** Less than $0.005 per failure; mostly deterministic. Optional model wording is the only recurring cost.
- **security:** Never expose raw errors, URLs, credentials, or page contents in speech. Distinguish not attempted, attempted-and-failed, and completed-but-unverified. Retrying external side effects requires autonomy_policy_evaluate and explicit confirmation for destructive actions.
- **missing:** A normalized failure taxonomy across relay jobs, Mac actions, browser commands, and pendant delivery; A response contract that requires attempted/verified/evidence fields before a success claim can be spoken; A compact owner-facing recovery UI that offers one safe next action and preserves the original receipt

### "Show me where my attention went today: which interruptions reached me, which I actually heard, what I deferred, and what could have waited—and let me set a daily interruption budget by category."
- **useful because:** The system currently decides or queues attention without giving the owner an accounting of the cost. A transparent attention ledger would let the owner tune the system from lived outcomes rather than guessing at quiet hours, while exposing missed audio and duplicate notifications that ordinary job receipts cannot show.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic aggregation of attention decisions, delivery ACKs, focus/idle state, and owner acknowledgements; a cheap background model writes the daily narrative and suggests only reversible policy changes. Realtime is unnecessary.
- **latency:** Record each event in under 100 ms; dashboard query under 2 seconds; daily digest generated in under 30 seconds.
- **cost:** Near-zero for aggregation and storage; under $0.01/day for optional narrative generation.
- **security:** The ledger is sensitive behavioral data. Keep raw audio and message contents out; store event IDs, categories, timestamps, decision reasons, and opaque delivery evidence. Default to local Mac storage, encrypt/export only on request, and require confirmation before changing interruption policy. Never infer productivity or health claims from idle time.
- **missing:** A durable attention-ledger schema joining attention_arbitrate decisions, routine/job IDs, audio delivery ACKs, spoken acknowledgements, and deferrals; Owner-facing routes for daily totals, per-event provenance, deletion, and policy-budget edits; A policy evaluator extension that can enforce category budgets over a rolling day and explain when a budget caused deferral

### "When something is private, tell me that it is ready and show it on my Mac instead of reading it aloud; when I am away from the Mac, give me a safe one-sentence pointer and let me retrieve the full item later."
- **useful because:** The pendant currently has no general confidentiality gate: callers can hand arbitrary result text to speech, while the only robust spoken redaction lives in one briefing path. The owner needs privacy-preserving output routing, not merely shorter speech, especially when bystanders may hear.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic sensitivity classification and destination policy first; a cheap model may summarize only after the policy permits it. Realtime is limited to the safe pointer, never the private body.
- **latency:** Safe pointer under 1 second; local Mac display under 2 seconds; full content remains available on demand without repeating it over audio.
- **cost:** Near-zero when displaying an existing local artifact; under $0.01 when a safe summary is generated.
- **security:** Ship conservative defaults but do not invent the owner's trusted-destination policy. Private bodies should remain local, use one-time display tokens, expire after a short period, and be auditable through provenance. The pendant must never receive credentials or secrets merely to announce that a private item exists.
- **missing:** A single output-router policy mapping sensitivity and destination to speak, display, queue, or refuse; A local Mac display route with one-time retrieval tokens and an explicit 'owner viewed' receipt; A speech-layer enforcement hook before pendantSpeech/audioBrief, plus a safe-content test suite covering non-briefing callers

### "Let me ask 'where has this piece of my information gone?' and get a source-linked map of copies and derived claims across the Mac, browser, relay, and pendant, then approve one deletion that actually propagates everywhere it can."
- **useful because:** Today deleting a capture can leave its full text in the context graph, revoking evidence does not remove derived facts, and there is no global forget operation. The owner cannot honestly control their data without seeing those copies and the limits of deletion.
- **path:** dashboard → mac → browser → relay → pendant
- **model tier:** Deterministic lineage traversal and deletion planning; no expensive model is needed except optional plain-English explanation. Realtime only confirms the requested scope; destructive propagation always requires explicit approval.
- **latency:** Map a normal topic in under 5 seconds; prepare a deletion plan in under 10 seconds; apply and verify asynchronously with progress receipts.
- **cost:** Near-zero for local graph traversal; under $0.02 for optional summarization. Storage cost is bounded by retaining hashes/tombstones rather than raw copies.
- **security:** The map itself is sensitive and must be local-dashboard-only by default. Never reveal secret values merely to explain their locations. Show complete versus best-effort deletion, immutable audit receipts, and every surviving copy with a reason. Do not delete external mail/browser content without separate confirmation.
- **missing:** A durable lineage edge from evidence capsules to memory facts, context-graph entities, browser provenance, briefings, and relay events; A scoped cross-store forget planner with dry-run, approval token, idempotency, and verification of residual copies; Relay/device revocation and tombstone propagation, plus a local-only dashboard view that redacts values while preserving provenance


## What it asked for

_Nothing._
## Its own summary

This round produced four distinct owner-facing capabilities. The highest-value one is adaptive briefing delivery: a routine is not 'done' until the pendant's downloaded/started/finished evidence says what the owner actually received, and missed items are folded into the next brief without repetition. I also proposed novelty-aware three-sentence news briefs with citations, a reviewable duplicate-routine merger (the live state has overlapping 07:00 and 17:00 routines), and failure-aware spoken recovery that distinguishes not attempted, failed, and completed-but-unverified instead of claiming success. The proposals deliberately build on the new delivery ACK, attention, provenance, policy, and reconciliation primitives rather than inventing another queue.

**Biggest unknown:** I still need implementation answers, not more permissions: which durable store will join routine/job/briefing-item IDs to pendant delivery ACKs; whether the live relay has the /v1/routines and research/briefing routes assumed by the proposals; and the owner's actual timezone/quiet-hour and spoken-content policy. The machine reports America/New_York while owner memory says America/Chicago sampled from the Mac, so routine mutation or timed speech must remain read-only until that conflict is resolved.

