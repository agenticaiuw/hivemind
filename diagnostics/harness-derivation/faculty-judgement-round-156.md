# Harness derivation — faculty-judgement — round 156

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What would have happened if you had waited, skipped that step, or asked me first?” — show me a counterfactual rehearsal of an action before it runs."
- **useful because:** The owner can inspect the consequences of autonomy without committing anything: alternate policy choices, which evidence would change the verdict, and where uncertainty comes from. This is the missing bridge between opaque explanations and safe delegation.
- **path:** relay → mac → browser → pendant → dashboard
- **model tier:** background for building the candidate simulations; realtime only to answer a spoken follow-up
- **latency:** 2–5 seconds for a rehearsal; never delays an already-approved action because it is a separate read-only operation
- **cost:** One small model call plus existing read-only probes, roughly $0.01–$0.05; dominant cost is assembling cited evidence, not audio
- **security:** No mutation, no form submission, and no sensitive snippets to the pendant by default. Each branch must be marked hypothetical and cite the evidence/policy fields it used. Dashboard may request detail; spoken output gets a redacted one-sentence result.
- **missing:** A durable counterfactual simulation route that accepts an action plus named branch overrides and returns predicted effects, blocked effects, uncertainty, and evidence refs; A common effect vocabulary across Mac and browser results so simulations cannot imply unsupported guarantees

### "“Tell me only what I actually missed while the pendant was offline, and do not replay anything I already heard.”"
- **useful because:** A dropped link currently leaves uncertainty between generated, downloaded, started, finished, and interrupted audio. A delivery-aware catch-up gives the owner a concise, trustworthy recovery instead of duplicates or silent loss.
- **path:** relay → pendant → mac → dashboard
- **model tier:** background for reconciliation and deduplication; realtime only when the owner requests playback
- **latency:** Under 1 second to answer from receipts; under 3 seconds to compose a short catch-up
- **cost:** Near-zero for receipt reconciliation; $0.005–$0.02 only when regenerating a missing spoken summary
- **security:** Use opaque artifact IDs and authenticated device sessions; never infer that an artifact was heard from download alone. Expired or private items should be summarized without replaying their content. Require owner confirmation before regenerating sensitive audio.
- **missing:** A durable catch-up projection joining pipeline generation receipts with pendant downloaded/playback ACKs and deduplicating offline replay; A route that asks the pendant for its last acknowledged sequence and returns only unfinished items

### "“Why did this happen twice, get stuck, or reach the wrong surface? Reconstruct the whole chain from my request to what the pendant, Mac, browser, and relay each did.”"
- **useful because:** Today the owner can inspect isolated receipts, but not understand a cross-body failure. A causal debugger would distinguish duplicate generation from duplicate dispatch, stale browser execution, audio replay, or a missing acknowledgement, then name the first broken invariant and the safe recovery. This is a new owner-facing ability, not another receipt or generic status page.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** background model over a deterministic event graph; realtime only for a short spoken diagnosis after the graph is built
- **latency:** 3–10 seconds for a diagnosis, with immediate acknowledgement that investigation is running
- **cost:** $0.01–$0.06 per investigation; most work is joining typed records and computing invariants, not generation
- **security:** Default output contains IDs, timestamps, surface names, and failure classes, not message bodies or page content. Evidence links must honor revocation and sensitivity. It must never retry or repair while diagnosing; any suggested repair is separately policy-evaluated and confirmed.
- **missing:** A durable cross-surface event graph with first-class foreign keys between relay jobs, Mac jobs, browser commands, action receipts, pipeline artifacts, and pendant delivery events; Invariant checks for exactly-once intent, at-most-once mutation, lease expiry, and generated-versus-heard audio; A read-only route returning a causal chain, broken invariant, confidence, and reversible repair candidates

### "“When I am wearing the pendant all day, learn whether I want a brief spoken, queued, shortened, or silent—without learning or retaining what the brief said.”"
- **useful because:** The owner gets an attention-aware assistant that adapts to interruption cost rather than repeating a fixed policy. It can learn from physical barge-ins, completed playback, deferrals, and missed delivery while keeping content out of the learning signal. This is useful across meetings, walking, and focused work, and no single surface can observe all of those signals.
- **path:** pendant → relay → mac → dashboard
- **model tier:** background statistical/rule model for preference updates; realtime only to apply the current decision
- **latency:** Decision under 100 ms from local state; preference updates batched daily or after 20 events
- **cost:** Near-zero for event aggregation; at most $0.01/day for a compact preference summary, with no content-bearing prompt required
- **security:** Persist only event features such as interruption outcome, duration bucket, surface, urgency class, and owner override—not transcript, headline, sender, or page content. The owner must be able to inspect, freeze, reset, or delete the learned policy. It must never silently promote sensitive content to spoken output.
- **missing:** A privacy-bounded preference learner keyed to policy dimensions rather than content; A durable owner-visible versioned policy with rollback and explicit distinction between learned suggestion and owner-set rule; A pendant event vocabulary for barge-in, finish, defer, unread, and physical stop that is joined to attention arbitration


## Changes it proposed to its own stack

### `interaction` — Add a tether-presence mode: when the nRF9160 and ESP32 are physically connected over the Mac's USB serial ports but LTE is unregistered, the Mac publishes a short-lived local session lease. The pendant can start a conversation through the Mac-local agent, and the relay is used only when reachable; on disconnect, the pendant refuses to imply cloud continuity and exposes a clear local/offline state.
- **owner gets:** The pendant is useful today on the desk instead of pretending it only works after cellular registration. The owner gets a working voice loop during development, travel without coverage, or relay outages, with honest boundaries about what local mode can do.
- effort: Medium-high: USB serial transport adapter, local model/STT/TTS routing, session lease and mode announcement, plus reconnect handoff tests across both chips.  ·  risk: A stale USB lease could make the pendant send audio to a vanished process; use a short heartbeat, explicit mode LED/state, and fail closed on lease expiry. Local transcripts must follow the same redaction and retention policy as relay transcripts. Recovery is automatic retry to relay only after a fresh authenticated lease.
- cost: No extra API cost for local inference if an on-device/Mac model is used; optional local model consumes Mac resources. Hardware cost $0 because both serial devices are already connected.  ·  latency: Potentially lower round-trip latency than LTE while tethered; mode transition on disconnect should be explicit rather than silently buffering.
- security: USB serial is a local trust boundary, not proof of owner presence. Authenticate the Mac session and rotate its nonce on reconnect; never expose local-mode transcripts to cloud without a separate routing decision.
- depends on: A real Mac USB-serial bridge for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A local speech/model path that can produce and consume the already verified 24 kHz Opus framing; A typed session-mode signal consumed by pendant, Mac, and relay

### `dashboard-ux` — Add a daily owner-facing trust report that measures the assistant's behavior rather than merely listing activity: requests completed, actions refused, stale plans prevented, duplicate work detected, audio actually heard, uncertainty/conflicts surfaced, and any content blocked by privacy policy. Every metric links to the underlying receipt or event and can be reset or exported.
- **owner gets:** They can tell whether this system deserves more autonomy. Instead of trusting reassuring prose, the owner sees where it failed, where it declined safely, and whether the pendant actually delivered what was promised.
- effort: Medium: define metric events and retention, build a deterministic aggregator and dashboard view, add spoken one-sentence summary, and test that sensitive payloads never enter aggregates.  ·  risk: A misleading denominator or missing event could create false confidence. Show coverage and unknown counts, never turn absent telemetry into success; label metrics provisional until all surfaces emit events. Recovery is to disable the report or rebuild from raw receipts.
- cost: Low storage and compute; aggregation can run locally once per day. No model call is needed except optional natural-language rendering.  ·  latency: No impact on live interaction; dashboard query should be under 500 ms from precomputed aggregates.
- security: Store only counts, classes, durations, and opaque IDs. Do not retain transcript, page text, sender, or secret values in metrics. Export requires dashboard confirmation.
- depends on: A shared event vocabulary and durable joins across relay, Mac, browser, pipeline, and pendant; record_pendant_delivery_event plus existing action and job receipts; A coverage report for surfaces that did not emit telemetry


## What it asked for

### `c21-l2hz` (context) — USB-tethered local voice feasibility
- why: The hardware is physically connected now, and my highest-value proposal depends on whether a Mac USB serial bridge and local STT/TTS/model path already exists or is entirely missing.
- would change: If a local path exists, I would narrow the proposal to session leasing and truthful mode transitions; if absent, I would treat the proposal as a new end-to-end capability with explicit model and transport work rather than imply it can run today.

## Its own summary

Round 156 produced three distinct items: (1) counterfactual action rehearsal so the owner can inspect alternate outcomes before committing; (2) delivery-aware missed-audio catch-up, explicitly flagged as close to an existing self-healing-brief idea rather than a new duplicate; and (3) a high-value USB-tethered local voice mode that makes the physically connected pendant useful while LTE is unregistered, with authenticated short-lived leases and truthful offline/cloud boundaries. I also requested context on whether a local USB/model path already exists.

**Biggest unknown:** Whether the Mac currently has a working USB serial + local STT/TTS/model loop. The owner still needs to decide the disclosure boundary (what may be spoken aloud), quiet/urgency policy, and whether local-mode transcripts may ever leave the Mac.

