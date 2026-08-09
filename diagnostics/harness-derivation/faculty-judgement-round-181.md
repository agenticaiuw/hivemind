# Harness derivation — faculty-judgement — round 181

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Before you act, show me the counterfactual: what each surface would do, what I would hear, what data would leave the Mac, and how I could undo it."
- **useful because:** Existing previews describe intended mutations, but they do not simulate the cross-surface experience or expose disclosure, interruption, and rollback consequences together. This lets the owner choose among plans before a browser, Mac, relay, and pendant diverge.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background model compiles the human-readable scenario; deterministic policy and preflight services decide permissions and effects
- **latency:** 3–5 seconds for a normal plan; never execute as part of simulation. Refresh automatically if the plan is older than the configured max age.
- **cost:** <$0.02 per invocation; mostly deterministic calls, with model cost only for concise explanation.
- **security:** Simulation must run read-only and redact sensitive snippets by default. It must show unavailable surfaces and stale inputs prominently, carry evidence references, and require a new confirmation after any state change. Do not imply browser or pendant success from a plan.
- **missing:** A typed counterfactual/impact schema that joins action effects, spoken output, outbound data classes, and undo coverage; Adapters that ask the pendant/audio policy what would be spoken without generating or playing audio; A dashboard renderer for per-surface timeline and stale-input warnings

### "Why did your answer change since yesterday? Compare the exact evidence and assumptions behind both answers, tell me what became stale or contradictory, and let me correct the right memory."
- **useful because:** The system can explain an action receipt and can read current evidence, but it cannot compare two judgments over time. This turns silent drift into an understandable conversation and prevents the owner from correcting the wrong fact.
- **path:** relay → mac → dashboard → pendant
- **model tier:** background model for diffing and plain-language explanation; deterministic freshness, provenance, and contradiction checks first
- **latency:** Under 5 seconds for a normal answer; stream a short spoken finding first and put the detailed evidence diff on the dashboard.
- **cost:** <$0.03; source reads and hashing dominate, with one compact model call for the explanation.
- **security:** Keep raw quotes off the pendant unless explicitly requested; show source IDs and redacted excerpts by default. A correction must be staged as a proposed memory change, never silently overwrite facts. Preserve the prior judgment and correction receipt.
- **missing:** A durable judgment record containing prompt intent, evidence references, policy version, and output digest; A comparator that can join old judgments to current evidence and classify stale, contradicted, or merely re-ranked; A correction workflow that updates facts and graph relations together while retaining an audit trail

### "Run a safe rehearsal of my whole pendant system: send synthetic audio over USB, interrupt it, queue a fake browser task, lose the link, reconnect, and prove nothing real was changed and every cancellation and playback receipt arrived."
- **useful because:** The hardware is physically testable over USB today, but there is no owner-facing end-to-end rehearsal. A staged canary catches broken audio, stale browser sessions, missing cancellation barriers, and false delivery claims before they affect a real request.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** deterministic test harness and receipt validator; use the realtime model only to narrate the final result if requested
- **latency:** 60–120 seconds for the full rehearsal; each phase has a hard timeout and leaves a complete pass/fail report.
- **cost:** <$0.01 when synthetic audio and local fixtures are used; no external model call required.
- **security:** Use an isolated namespace, synthetic URLs/text, and a browser profile or command mode that cannot submit forms. The harness must prove no external side effect, verify stop propagation before reconnect, and fail closed if the pendant session is not authenticated. Never call this a successful delivery without authenticated device ACKs.
- **missing:** A USB-serial test transport and a pendant test fixture mode that accepts synthetic artifacts without storing owner audio; An isolated browser/Mac dry-run namespace with explicit no-submit assertions; A correlation and assertion report joining pipeline IDs, Mac/browser jobs, stop tokens, and pendant delivery ACKs

### "After a meeting, give me a private decision record: distinguish what I said from what others said, list commitments I actually accepted, identify unresolved questions, and let me approve only the items that become reminders or drafts."
- **useful because:** Today the pendant can carry audio and the Mac can create reminders or drafts, but it cannot turn a real multi-person conversation into an attributed, uncertainty-aware record. This would prevent the common failure where an overheard suggestion becomes the owner's commitment.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background audio diarization and extraction model after the meeting; realtime model only for an owner-requested spoken summary
- **latency:** A 30-minute meeting processed in under two minutes after capture ends; no automatic interruption during the meeting unless the owner explicitly enables it.
- **cost:** Roughly $0.10–$0.50 per meeting depending on audio duration and diarization; storage and transcription dominate.
- **security:** Meeting audio is highly sensitive and must stay local by default or require explicit upload consent. Show capture state to participants where legally required, retain short-lived encrypted audio only until extraction is reviewed, and never create an external draft/reminder without physical or explicit owner approval. Speaker attribution must expose confidence and an unknown-speaker bucket rather than guessing identities.
- **missing:** A consented meeting-capture mode that uses the existing failure-path audio storage rule without silently retaining successful uploads; On-device or local-Mac speaker diarization and turn segmentation, with owner/other/unknown labels rather than face or identity inference; A review surface that binds each extracted commitment to timestamped audio evidence and routes only approved items to reminder, note, or draft actions

### "When something goes wrong, reconstruct the incident for me from the pendant press, audio delivery, link state, Mac/browser actions, and receipts—show the timeline, the first failure, what was cancelled, and what evidence is missing."
- **useful because:** The system currently exposes separate logs, jobs, pipeline records, and device diagnostics. The owner cannot establish whether a bad result came from capture, transport, model generation, browser execution, or playback. A single forensic timeline would make failures actionable instead of mysterious.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic event join and causal checks first; background model only turns the verified timeline into plain language
- **latency:** Under 10 seconds for a recent incident; older incidents may stream partial results while relay and Mac records are fetched.
- **cost:** <$0.02 per incident; hashing and event joins dominate, with optional short explanation generation.
- **security:** Use opaque IDs and redact audio/content by default. Do not infer causality when clocks or joins are missing; mark hypotheses separately from verified events. Incident exports require explicit approval and must exclude credentials, page bodies, and raw PCM unless expressly requested.
- **missing:** A durable cross-surface correlation key connecting relay, Mac, browser, pipeline, and pendant event IDs; Authenticated monotonic device event ingestion with clock-offset estimation and explicit missing-event markers; A causal timeline schema that distinguishes observed events, inferred links, and owner assertions

### "Did anything about this conversation leave my Mac? Show me every destination, what class of data was sent, what was redacted, and what you cannot prove because logging was absent."
- **useful because:** The owner has no end-to-end answer about disclosure. Existing origin policy and redaction are enforcement pieces, but there is no durable, queryable egress receipt spanning relay prompts, browser commands, model calls, TTS, and pendant transport. This turns privacy from a setting into an inspectable fact.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic egress ledger and redaction hashes; background model only summarizes the ledger in plain language
- **latency:** A current-session answer under 3 seconds; historical audit under 15 seconds. Missing telemetry must produce an explicit unknown result, never 'nothing left.'
- **cost:** <$0.01 per audit; storage and hashing dominate, with no model call required for the detailed view.
- **security:** Ledger entries must contain destination, policy rule, sensitivity class, byte counts, and content hashes—not raw secrets or full prompts. Protect the ledger itself, support owner revocation/retention, and distinguish blocked, sent, locally processed, and unobserved. The relay must not claim visibility into Mac-only traffic it cannot attest.
- **missing:** A tamper-evident egress event ledger shared by Mac, relay, browser extension, and pendant; Instrumentation at every outbound boundary, including model/TTS requests, browser results, USB serial, and relay context handoff; A verifiable attestation or explicit coverage report for surfaces that were offline or uninstrumented


## What it asked for

_Nothing._
## Its own summary

This round produced three non-duplicate owner-facing capabilities: a cross-surface counterfactual impact report before acting; a provenance-backed comparison explaining why an answer changed; and a full synthetic USB pendant rehearsal that proves audio, interruption, reconnect, browser isolation, and authenticated delivery receipts. I also tried a global erase capability, but the recorder correctly identified it as an existing proposal; I did not rephrase it.

**Biggest unknown:** Whether the live USB serial path already has a safe synthetic/test transport and isolated browser fixture. The pendant is physically connected, but without that boundary I cannot honestly promise a rehearsal that cannot touch real owner data. I still need the pending USB-tethered local-voice feasibility context and, separately, the owner's eventual disclosure/interruption policy values rather than inventing them.

