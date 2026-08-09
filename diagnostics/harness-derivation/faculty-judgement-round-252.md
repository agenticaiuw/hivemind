# Harness derivation — faculty-judgement — round 252

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When you do something for me, tell me whether it actually happened in the real app—not merely that the Mac accepted the command—and if it failed, leave me with the exact safe next step."
- **useful because:** Today a job receipt can mean generation or acceptance while the target may have rejected, changed, or silently ignored the action. A postcondition check spanning Mac/browser, relay, and pendant would turn trust from 'the agent said so' into 'the world now matches.' This is the single most useful capability in this round.
- **path:** relay → mac → browser → pendant
- **model tier:** Background/cheap model plans a typed postcondition from the intent; deterministic Mac/browser reads verify it; realtime is used only for the short spoken result. Escalate to the expensive model only when observed state conflicts with the intended state.
- **latency:** 5–12 seconds after a mutation; read-only verification should begin immediately and may complete asynchronously with a pendant alert. Never claim success before verification or explicitly label it unverified.
- **cost:** Roughly $0.002–$0.02 per action, dominated by one cheap planning call only for ambiguous intents; deterministic reads and receipts dominate latency, not token cost.
- **security:** Verification must not itself mutate. It should return only the minimum target fields, redact private page/mail contents, and carry evidence references. External or destructive actions still require the existing physical consent latch. A stale target must yield 'could not verify,' never success.
- **missing:** typed postcondition contracts for common Mac/browser actions; a durable relay-job↔Mac/browser action correlation key (currently only telemetry localJobId exists); a read-after-write verifier registry with bounded retries and stale-state detection; delivery of the verified result through the existing pendant artifact/ACK path

### "Learn how I actually consume my briefings—what I stop, replay, defer, or always miss—and suggest a shorter, better briefing plan, but never silently change what you tell me."
- **useful because:** A fixed urgency threshold cannot distinguish an item the owner repeatedly acts on from one they always skip. Playback starts/finishes, barge-ins, deferrals, and Mac/browser follow-through are behavioral evidence that can personalize ordering and length while keeping the owner in control.
- **path:** pendant → relay → mac → browser
- **model tier:** Use deterministic counters and recency decay for the first pass; a cheap background model summarizes patterns into a proposed policy delta. Realtime only speaks the current brief. The owner explicitly approves any change to /briefing/policy.
- **latency:** No added latency to a live brief. Update the recommendation after a day's events or on demand; delivery ACK ingestion is asynchronous and offline-safe.
- **cost:** Usually below $0.005/day; event aggregation is local/relay-side and the occasional small recommendation prompt dominates.
- **security:** Behavioral telemetry is sensitive. Store item IDs, action types, and timing rather than audio or raw content; link to evidence with revocable IDs. Never infer an owner's preference from one skip, and do not let engagement optimize toward more interruptions. Recommendations must show sample size, confidence, and the policy fields they would change.
- **missing:** a durable, source-linked preference writer (fleet memory has schema/routes but no production writer); a semantic briefing-item identifier shared by source, audio artifact, and owner action; a policy-delta/recommendation endpoint that requires explicit approval; delivery-event aggregation for interrupted/deferred items rather than only artifact completion

### "When I ask 'why didn't you tell me?' or 'why did you interrupt me?', give me a short, honest answer showing the source, freshness, policy rule, and whether the pendant actually delivered it."
- **useful because:** The system can now arbitrate attention and explain action provenance, but a suppressed or undelivered briefing has no durable explanation chain. This capability makes silence and interruption inspectable instead of mysterious, and catches failures such as an unauthorized calendar read being mistaken for an empty calendar.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic assembly should produce the explanation from the attention decision, source-health evidence, policy version, and delivery ACK. Use the expensive model only to turn that structured chain into one plain-language sentence when the owner asks conversationally.
- **latency:** Under 1 second when the decision ledger and receipts exist; up to 4 seconds for a fresh read-only source check. Never wait on a mutation or expose raw sensitive content in the spoken answer.
- **cost:** Near-zero for structured assembly; under $0.002 for optional phrasing. Storage is bounded decision metadata, not source bodies.
- **security:** Spoken explanations must name a source without reading its private subject/body. Include sensitive evidence only on the local dashboard, never via the relay voice path. A missing decision record must be reported as missing—not reconstructed as fact. Revocation must invalidate the cited source and any derived explanation.
- **missing:** durable attention-decision records including matched policy fields and source freshness; a join from attention event to briefing item/audio artifact and pendant ACK; a read-only suppression/explanation route distinct from action provenance; explicit distinction between 'not observed,' 'suppressed,' 'queued,' 'delivered,' and 'played'

### "Let the pendant notice when I am in a real conversation and automatically keep private information out of its speaker until I am alone or explicitly unlock it—without recording or transcribing the other person."
- **useful because:** A calendar/Focus/idle signal cannot tell whether a stranger or colleague is standing beside the owner. Today the speech path can read sensitive text aloud whenever a caller bypasses the one briefing redaction path. This gives the owner a physical, context-sensitive protection against accidental disclosure while preserving ordinary hands-free use.
- **path:** pendant → relay → mac → browser
- **model tier:** A small on-device classifier should detect conversational turn-taking and nearby speech from short-lived PCM features only; it must discard audio locally. The relay applies the owner's disclosure policy to classify pending speech, while Mac/browser provide only the already-approved content class and destination. Use the expensive model only for policy explanation or ambiguous recovery, never for raw bystander audio.
- **latency:** The local gate must react within 200 ms to nearby speech and block before the next spoken frame. A transition to private output may be queued until the current sentence ends; unlocking or clearing the state should take under 1 second.
- **cost:** Low per-use API cost because detection and the first gate are local; occasional policy reasoning is under $0.01. Hardware/firmware work dominates: feature extraction, signed state transitions, and an output-side speech gate.
- **security:** Raw nearby audio must never leave the pendant or be persisted. The classifier must be conservative: false positives defer private speech, while false negatives are a privacy failure. Do not claim person identity or infer consent. Public-safe confirmations should reveal only that playback was withheld. The owner must define which classes are safe to speak and whether an explicit physical unlock is required.
- **missing:** an on-device turn-taking/nearby-speech classifier validated against real environments; a firmware output gate that can stop or replace an already-buffered private utterance before playback; an owner-configurable disclosure policy with a physical unlock/lock state, not merely a server-side preference; a signed privacy-state signal consumed by relay, Mac, and browser speech paths; hardware validation for microphone self-noise, wind, and speaker echo; a second microphone or proximity sensor may be needed for reliable detection

### "When I mark a moment, let me ask later 'what was I doing then?' and get a private reconstruction of the exact browser page, Mac app, conversation state, and unfinished intention—without saving a recording of anyone's speech."
- **useful because:** A bookmark today can preserve a timestamp, but not the context that makes it useful. The owner loses the thread between a physical moment and the work around it. Correlating a marker with short-lived Mac/browser state and the current relay session would make the pendant a reliable memory anchor rather than a timestamp graveyard.
- **path:** pendant → mac → browser → relay
- **model tier:** Deterministic correlation should gather timestamped foreground app, browser tab digest, session/job IDs, and the owner's own marker; a cheap background model summarizes the reconstruction. Realtime only answers the later question and must not synthesize missing facts.
- **latency:** Marker acknowledgment under 100 ms locally; background capture under 2 seconds when links are available; later retrieval under 3 seconds. If a source was unavailable, answer with an explicit gap.
- **cost:** Under $0.01 per reconstruction; local state digests dominate storage, with one small summarization call only when requested.
- **security:** Persist hashes, titles, and bounded redacted snippets—not microphone audio or third-party speech. The owner must be able to delete the marker and every linked digest. Never infer the content of an unavailable source or silently attribute another person's words to the owner.
- **missing:** a shared marker correlation protocol across sw1, relay session, Mac job, and browser command IDs; a short-lived, privacy-filtered Mac/browser state sampler keyed to the marker; a retrieval route that returns the evidence timeline and explicit gaps; cascade deletion from a marker through all linked digests

### "If your answer depends on an uncertain or conflicting fact, say so before acting, show me the two plausible interpretations, and let me resolve the ambiguity once so every surface uses the same answer afterward."
- **useful because:** The system currently has authoritative-looking but contradictory observations—especially calendar permissions, timezone, and scheduled briefings—and different modules can turn an unreadable source into a confident 'nothing is waiting.' The owner needs uncertainty to be visible at the moment it matters, not buried in logs.
- **path:** relay → mac → browser → pendant
- **model tier:** A deterministic conflict detector compares provenance, freshness, and authority first. The expensive model is used only to phrase the competing interpretations and ask one concise question; the resulting owner decision becomes a signed policy/fact consumed by all surfaces.
- **latency:** Under 2 seconds for known conflicts; no extra delay when evidence agrees. A pending ambiguity must prevent external mutation but may still allow safe read-only work.
- **cost:** Usually near-zero; one small clarification prompt under $0.01 per unresolved conflict. Storage is bounded to the decision and source references, not duplicated raw content.
- **security:** Do not expose private source snippets in spoken alternatives. Preserve both hypotheses and their provenance until the owner resolves them; do not let a stale answer overwrite a newer one. Destructive or externally visible actions remain blocked while ambiguity is unresolved.
- **missing:** a general contradiction record with authority, freshness, and affected intents; one cross-surface durable owner-decision store (not the currently local-only approval flag); policy hooks that make unresolved ambiguity fail closed for mutations; spoken and dashboard renderers that expose uncertainty without fabricating confidence


## Changes it proposed to its own stack

### `memory` — Make every derived memory fact carry its originating evidence capsule/source IDs, then implement an owner-visible 'forget this source everywhere' cascade: revoke the source, tombstone dependent facts and graph attributes, invalidate pending briefing items, and mark any already-generated audio as withdrawn. Return a bounded receipt listing what was removed, what could not be reached, and why.
- **owner gets:** If the owner revokes a page, note, or capture today, copied claims can remain in facts.json and the context graph indefinitely and may still be spoken. This gives the owner a real, comprehensible privacy boundary instead of a deletion button that only hides one copy.
- effort: Medium-high: add provenance fields and migration, dependency indexes, cascade handlers across Mac stores and relay memory, plus tests for partial failure and restart recovery.  ·  risk: A broad cascade could delete a useful fact or miss an unlinked copy. Default to preview, require confirmation for non-secret data, preserve tombstones and receipts, and fail closed on unknown lineage. Recovery is restoring only from an owner-confirmed export, never silently resurrecting revoked content.
- cost: Low API cost; mostly local disk/index work. Briefing/audio withdrawal may require one relay write and one bounded cleanup job.  ·  latency: Preview under 1 second locally; full cascade seconds asynchronously, with no claim of completion until all reachable stores report.
- security: Strongly improves deletion propagation, but provenance IDs themselves can reveal relationships; hash or redact them in spoken output and restrict full lineage to the local dashboard.
- depends on: memoryService fact schema gains capsule/source references; context graph records gain source linkage; relay fleet-memory migration and a production writer; durable cross-surface job correlation


## What it asked for

_Nothing._
## Its own summary

Round 252 produced four recorded proposals: verified real-world postconditions after Mac/browser actions (the highest-value proposal), behavior-informed briefing recommendations with explicit owner approval, an explanation trail for interruptions/suppression/delivery, and source-linked deletion propagation across derived memory and audio. I also confirmed the newly granted surfaces: Mac bridge online, Safari online, pendant still not registered. What remains needed from the owner is not another tool: explicit quiet-hour/urgency preferences and disclosure boundaries (what may be spoken aloud or leave the machine). Engineering-wise, the key missing joins are durable attention decisions, semantic item IDs, relay↔local action correlation, and provenance links through derived facts.

**Biggest unknown:** The owner's actual interruption and disclosure policy remains intentionally unset; without it, the system can only use conservative defaults and must ask before changing briefing behavior or speaking sensitive content.

