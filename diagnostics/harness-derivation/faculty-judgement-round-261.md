# Harness derivation — faculty-judgement — round 261

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Only interrupt me when something genuinely needs me; if a browser task is blocked on my login or a physical decision, put one concise request on the pendant and resume the task after I answer.”"
- **useful because:** This turns the hive from a collection of silent failures into a single, actionable queue: Safari can discover the block, the Mac can explain the smallest next step without exposing credentials, the relay can arbitrate timing, and the pendant can hold the request until the owner is ready. No single surface can both see the authenticated page and reach the wearer.
- **path:** browser → mac → relay → pendant
- **model tier:** Background model classifies a blocked step and drafts a 12-word request; realtime model is used only when the owner answers by voice. Deterministic policy handles whether to queue, speak, or wait.
- **latency:** Detection on the existing page-watch interval (about 30 seconds); under 2 seconds from a confirmed block to a queued pendant item; voice response should resume within 3 seconds after relay reachability.
- **cost:** About $0.001–$0.01 per blocked-task classification, dominated by page text sent to the model; normal heartbeat and policy decisions should be zero-model-cost.
- **security:** Never send page bodies, passwords, OTPs, or form values to the pendant. Browser provenance must retain only a redacted locator and a digest. Login-needed classification must fail closed to “owner action required,” and any submit/send/purchase remains behind physical consent. The owner should be able to inspect the source capsule and revoke it.
- **missing:** Mount the existing browserJobRunner/sessionNeedSignal path or implement its equivalent in production; it is currently unreachable.; A durable cross-surface task ID joining relay jobs, Mac jobs, browser commands, and pendant inbox entries.; A signed, opaque physical-consent response for the pendant item, bound to the exact browser step and expiry.; A resume executor that revalidates the page and plan after the owner responds, rather than replaying stale selectors.

### "“When you give me a briefing, tell me whether it was actually downloaded and played; if it was interrupted, resume at the exact item instead of making me hear it twice.”"
- **useful because:** Today the relay can accept generated audio while the owner may hear nothing. This gives the owner an honest distinction between prepared, delivered, started, finished, and unheard—and makes a dropped link recoverable without duplicate speech. It is the most valuable everyday behavior because every other proactive capability depends on the owner actually receiving it.
- **path:** relay → pendant → mac → browser
- **model tier:** No model for delivery state, deduplication, or cursor arithmetic. Use the realtime model only to produce a short spoken explanation when the owner asks; use a background model only to compress a missed multi-item brief.
- **latency:** ACK ingestion under 250 ms when connected; reconnect replay within one relay poll; owner-facing status in under 1 second. Resume must preserve the current item and cursor, not regenerate the whole brief.
- **cost:** Negligible API cost for ACKs and state transitions. A background compression call is roughly $0.001–$0.01 only when several items were missed.
- **security:** ACKs contain only opaque artifact/item IDs, monotonic sequence, checksum and playback position—not transcript or raw audio. Deduplicate by event ID and reject unauthenticated device sessions. A ‘played’ receipt must never be inferred from relay acceptance. Spoken status should pass through the existing redaction boundary.
- **missing:** Wire the firmware audio_delivery_ack_queue into the authenticated relay upload path; the skill is accepted but no live emitter exists yet.; Persist a semantic briefing manifest with item IDs, cursor tokens, and source evidence; current pipeline receipts do not expose an item-level cursor.; Add a relay-to-Mac delivery reconciliation route that can turn unheard/interrupted items into one durable inbox item without duplicating active playback.; Define the owner-visible policy for how long an unheard item remains eligible and whether a private item may be replayed aloud.

### "“If my pendant is offline, keep important work moving on the Mac and browser, but don’t pretend I heard anything; when it comes back, give me one catch-up that says what changed, what was blocked, and what still needs my decision.”"
- **useful because:** The real device is currently offline, yet relay jobs and routines can continue. This prevents two bad outcomes: silently losing urgent work, or flooding the owner with duplicate alerts after reconnect. The Mac can observe and act, the relay can preserve ordering, and the pendant can receive one compact, physically durable catch-up.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic state aggregation and deduplication first; a cheap background model compresses only the final set of missed items. Realtime is reserved for the owner's spoken follow-up.
- **latency:** Offline detection within the existing device heartbeat window; Mac/browser actions continue immediately. On reconnect, produce the catch-up in under 2 seconds plus audio generation time.
- **cost:** Near-zero for state aggregation; roughly $0.001–$0.01 for a compressed catch-up when more than three items need summarization.
- **security:** Never equate generated, queued, or downloaded with heard. Include only redacted summaries and opaque provenance IDs in the pendant payload. Destructive or external actions remain staged and require the existing physical approval latch. Expired/private items must be withheld rather than replayed in public.
- **missing:** A durable device-presence record with conservative states (online, reachable-but-not-playing, offline, unknown) and timestamps.; A single ordered catch-up cursor spanning routines, jobs, browser reports, and pendant inbox items; current catchup has effectively empty pendant sources.; A relay-side coalescer that consumes delivery ACKs and attention decisions, eliminating duplicate announcements across Mac and pendant.; A reconnect trigger from the authenticated pendant session; LTE registration and production delivery are not live today.

### "“Before I commit to this, show me the likely consequences of doing it, postponing it, or dropping it—what deadlines move, who is affected, and which assumptions make the forecast uncertain.”"
- **useful because:** The owner currently gets ranked tasks and action plans, but not a consequence model. This would let him make life decisions with explicit trade-offs instead of asking the system to choose for him. It is uniquely cross-surface: calendar/mail reveal commitments, browser and files reveal project state, the relay preserves the question, and the pendant delivers a short decision-ready result.
- **path:** mac → browser → relay → pendant
- **model tier:** Background model builds a small causal graph and compares scenarios; realtime model only answers follow-up questions. Deterministic code computes dates, dependencies, and confidence bands; the model must not invent missing edges.
- **latency:** 30–90 seconds for a normal scenario over local sources; under 5 seconds for a follow-up against the already-built graph.
- **cost:** Roughly $0.02–$0.10 per scenario, dominated by extracting and comparing cross-source dependencies; follow-ups can use cached context at a few cents or less.
- **security:** Read-only by default. Do not contact anyone or mutate calendars/tasks. Show every asserted edge with its source and freshness, mark speculation separately, and omit private content from spoken output unless the owner explicitly requests it. Expire the scenario graph after 24 hours unless saved.
- **missing:** A typed dependency/causal-edge representation that can distinguish observed commitments from model hypotheses.; A join across mail, calendar, browser, files, and project state; current identifiers are surface-local and cannot reliably correlate entities.; A scenario evaluator that propagates uncertainty and refuses to forecast when evidence is stale or contradictory.; A compact pendant rendering for alternatives, confidence, and the one missing fact that would most change the answer.

### "“Prepare me for this conversation: reconstruct what we agreed, what each person may care about, the unresolved point, and let me rehearse both sides without sending anything.”"
- **useful because:** The owner can currently retrieve messages or make a plan, but not turn scattered correspondence, documents, and calendar context into a private rehearsal. This is a genuinely human capability: it reduces anxiety and improves a real conversation while keeping the final judgment and communication with the owner.
- **path:** browser → mac → relay → pendant
- **model tier:** Background model extracts a cited conversation brief and likely concerns; realtime model roleplays the other side with low latency. A deterministic redaction and no-send guard surrounds both.
- **latency:** 20–60 seconds to prepare; roleplay turns under 1.5 seconds after context is cached. A one-sentence spoken setup on the pendant, with detail available on the Mac.
- **cost:** About $0.03–$0.15 per preparation depending on thread/document volume; roleplay turns roughly $0.005–$0.03 each.
- **security:** Private-by-default and local-first. Never infer sensitive traits about participants, never present speculation as fact, and never send or draft into a live compose window without explicit request. Every claim needs a source link and date; participant names and quoted content should not be spoken in public mode.
- **missing:** A conversation bundle that joins mail threads, browser pages, local notes/files, and calendar events without copying raw bodies into long-lived memory.; A participant/claim model separating direct agreement, unresolved question, and hypothetical concern.; A rehearsal session surface with explicit ‘fact / inference / roleplay’ labels and a hard no-send execution boundary.; An owner-controlled retention and deletion cascade for the temporary bundle and generated transcript.

### "“Once a week, show me where you were wrong or overconfident, what evidence you missed, and which rule or preference should change—without quietly rewriting history.”"
- **useful because:** A personal AI should earn calibrated trust, not merely produce more outputs. This gives the owner an audit of false ‘all clear’ reports, stale plans, missed deadlines, and incorrect assumptions, with concrete corrections instead of opaque self-improvement. It spans the relay's history, Mac receipts, browser outcomes, and the pendant's delivery truth.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model clusters outcomes and proposes calibration changes; deterministic metrics calculate precision, stale-source rates, and delivery success. Realtime is unnecessary except for a spoken summary on request.
- **latency:** A weekly report can take 1–3 minutes; daily incremental scoring should be under 100 ms and require no model.
- **cost:** Roughly $0.02–$0.10 per weekly report, mostly summarization; metrics and ledger updates are negligible.
- **security:** Do not turn inferred errors into permanent facts automatically. Preserve immutable original decisions and evidence references, redact personal correspondence in the spoken summary, and require owner confirmation before changing an autonomy or disclosure policy. Reports must distinguish system error from changed external reality.
- **missing:** An outcome ledger linking each prediction/plan/triage decision to later evidence and owner correction.; Stable cross-surface IDs and immutable decision snapshots; current job, browser, and action IDs are unrelated.; A scoring vocabulary for calibration, stale evidence, missed delivery, and policy violation, with abstention rewarded.; An owner review route that can accept, reject, or defer a proposed rule change without mutating historical records.


## Changes it proposed to its own stack

### `relay` — Add a lease_until, lease_owner and attempt_count to relay_jobs; claim with compare-and-set, periodically requeue expired processing jobs with an explicit recovery receipt, and make completion/cancellation conditional on the current lease token. Surface recovered jobs to the Mac bridge as resumable context rather than silently running the full command again.
- **owner gets:** If the Mac or network dies halfway through a job, the owner gets a truthful recovered-or-needs-review result instead of a job that remains ‘processing’ for up to 24 hours and disappears from normal work. Morning briefs, research, and browser tasks stop becoming silent permanent failures.
- effort: Moderate: schema migration, D1 and memory-store parity, a short scheduler sweep, bridge claim changes, and tests for expiry races and duplicate completion.  ·  risk: A bad lease could cause duplicate work. Require a fencing token on every completion, use idempotency keys for reversible steps, and requeue only jobs whose action plan is explicitly resumable; otherwise mark them needs_review. Roll back by disabling the sweep and leaving existing processing rows untouched.
- cost: No model cost. A few D1 writes per claim/expiry and one low-frequency sweep; negligible storage growth from attempt metadata.  ·  latency: Adds one conditional write on claim and completion; recovery waits one lease interval (target 2–5 minutes), while normal work is effectively unchanged.
- security: Lease tokens prevent a stale Mac from completing a job after ownership moved. Do not put transcript or secrets in lease rows; retain only opaque IDs and provenance references.
- depends on: A migration applied to relay_jobs in the live D1 schema; The existing routine lease implementation as the compare-and-set template; A durable relay-job ↔ Mac-job correlation field, currently only telemetry localJobId; A resumable/non-resumable classification in the autonomy policy so irreversible actions never auto-replay


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: login/physical-decision handoff for blocked browser work; delivery-truthful briefings that distinguish generated/downloaded/played and resume by item; and graceful offline operation with one deduplicated reconnect catch-up. I also proposed relay job leases so Mac/network failure becomes recovery instead of a 24-hour stuck job. Live discovery confirms Safari and the Mac bridge are online, while the nRF9160 pendant is offline; therefore no claim of heard audio is currently valid.

**Biggest unknown:** The remaining decisive gap is not another model feature: whether the production relay has an authenticated pendant session/reconnect event and durable D1 schema available for presence, delivery ACKs, and job leases. Until those exist, I still need (1) live pendant-session registration and ACK ingestion, (2) a cross-surface correlation ID, (3) production mounting of the browser blocked-login detector/resumer, and (4) owner-set policy values for private speech, expiry, and what may auto-resume. I will not infer those from the Mac being online.

