# Harness derivation — faculty-judgement — round 163

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Run this in shadow mode first. Show me exactly what would change across my Mac and browser, who it affects, what is reversible, and then—only after I approve—apply the same plan if nothing has changed.”"
- **useful because:** The owner gets a safe rehearsal for consequential multi-surface work instead of trusting a vague preview. It turns an ambiguous ‘yes’ into a bounded, stale-checked transaction and exposes side effects before they happen.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model compiles the plan and human-readable diff; deterministic policy/revalidation handles the final gate; realtime speaks only the compact result and waits for physical approval.
- **latency:** Initial shadow plan 5–15 seconds; approval and revalidation under 2 seconds when surfaces are online; no mutation while compiling.
- **cost:** About $0.01–$0.05 per rehearsal depending on browser/page context; most cost is one planning pass, not the deterministic checks.
- **security:** Shadow execution must use read-only adapters or isolated dry-run interpreters and never submit forms/send mail/spend money. Persist only action descriptors and redacted diffs. Require the pendant’s physical transaction approval for external side effects, then revalidate immediately; expiry or any changed field forces a new rehearsal.
- **missing:** A typed dry-run executor that can produce before/after diffs for Mac and browser actions without committing them; A durable cross-surface transaction linking relay job, Mac job, browser commands, and the approval nonce; A commit phase that accepts only the exact revalidated shadow plan

### "“For anything you tell me as a fact, say whether you observed it, inferred it, or don’t know—and tell me the one source that would settle it.”"
- **useful because:** This is the single most useful everyday behavior: it stops the pendant from confidently declaring an empty calendar, completed action, or healthy device when the underlying read was unavailable. The owner gets calibrated decisions rather than polished guesses.
- **path:** relay → mac → browser → pendant
- **model tier:** A cheap deterministic evidence classifier labels observed/inferred/unknown from route receipts and provenance; the realtime model converts that verdict into one short spoken sentence only when needed. Use the expensive model for ambiguous conflicts, not every fact.
- **latency:** Under 300 ms for known receipt/provenance cases; up to 3 seconds for a cross-surface evidence check; unknown should be returned immediately rather than waiting indefinitely.
- **cost:** Usually <$0.001 for deterministic cases; $0.005–$0.02 when a model must resolve conflicting evidence.
- **security:** Do not speak raw sensitive snippets by default. Return source names, timestamps, and failure reasons, with content redacted. Never convert an empty result into ‘clear’ unless the source explicitly reports readable=true. Keep observed, inferred, and unknown distinct in receipts and explanations.
- **missing:** A shared answer-envelope schema carrying epistemic status, source_refs, freshness, and failure reasons from Mac/browser to relay; A universal speech gate in pendantSpeech/audioBrief so non-briefing responses cannot bypass confidentiality and uncertainty labels; Adapters that normalize EventKit-empty/permission failures and browser-offline states into explicit unknown results

### "“Is the pendant actually working right now—did it download and play your last answer, or did it only look successful on the Mac?”"
- **useful because:** The owner can distinguish ‘the system generated audio’ from ‘I actually heard it’. This prevents silent failures, repeated requests, and false confidence during the daily USB-tethered setup; it also gives a concrete next step when playback failed.
- **path:** pendant → relay → mac
- **model tier:** No model for the primary verdict: reconcile authenticated delivery ACKs, pipeline receipts, UART metrics, and bridge connectivity deterministically. Use realtime only to explain an unusual failure in plain language.
- **latency:** Under 500 ms for the latest artifact; under 3 seconds for a diagnostic window such as the last conversation.
- **cost:** Near-zero API cost for the normal path; optional diagnostic explanation <$0.01.
- **security:** Expose only opaque artifact IDs, states, byte counts, timestamps, and aggregate metrics—not audio or transcript. Reject unauthenticated device events and deduplicate offline replay. Do not claim playback from a server-side generation receipt alone.
- **missing:** A live owner-facing status route joining relay generation, Mac pipeline, bridge, and pendant delivery/playback events; USB-serial ingestion of the authenticated ACK queue while LTE registration is absent; A small durable join between artifactId, pipelineId, and the spoken response without retaining audio content

### "“For the next two hours, I’m in a client meeting: do not speak anything about personal mail or reminders, interrupt only for events that can expire during those two hours, and queue everything else for a private recap afterward.”"
- **useful because:** The owner gets a temporary, situation-specific boundary without permanently changing preferences or relying on an invented Focus-mode signal. It makes the assistant behave appropriately in the moments when context changes fastest, then automatically returns to normal and accounts for what it deferred.
- **path:** pendant → relay → mac → browser
- **model tier:** A deterministic mission-policy evaluator handles time window, source classes, urgency and expiry. The realtime model only summarizes queued items at the owner’s request; background work uses the cheaper scheduler. The pendant enforces the signed speak/queue decision while offline and the relay reconciles it when connected.
- **latency:** Policy evaluation under 100 ms; an incoming event should be classified within 1 second. Mission creation should be acknowledged immediately and expire exactly at its declared deadline.
- **cost:** Near-zero for policy evaluation and queueing; under $0.01 for an optional recap, dominated by summarization of deferred items.
- **security:** A mission must be scoped, signed, time-bounded, and visible in a receipt. Never infer that a meeting or public setting grants permission to speak sensitive content. Reject expired missions, fail closed on unknown source sensitivity, and do not let a browser or Mac override the pendant’s last valid signed policy. Deferred items need dedupe and an explicit expiry so private material does not accumulate indefinitely.
- **missing:** A durable mission object with start/end, source-class rules, urgency rule, deferred-queue identifier, and provenance; A precedence protocol between the mission, owner’s standing policy, attention_arbitrate, and the pendant’s offline alert inbox; A signed policy envelope and firmware verifier so the pendant can enforce the latest valid temporary rule while the Mac, browser, or LTE link is unavailable; A private recap route that reads only items deferred by this mission and records what was surfaced


## Changes it proposed to its own stack

### `model-routing` — Make every cross-surface result pass through a shared epistemic envelope before it reaches speech: {status: observed|inferred|unknown, source_refs, observed_at, freshness, failure_reason, sensitivity}. Route observed receipts through a cheap formatter, inferred conflicts to judgement, and unknown/failure states to a short explicit limitation. Reject raw strings from any route that lack the envelope unless the caller marks them as owner-authored text.
- **owner gets:** The pendant stops sounding certain when a permission failure, offline browser, or missing delivery ACK made the answer unknowable. The owner hears the truth about what happened, not merely the best-looking sentence.
- effort: Medium: define and adopt one response contract across relay, Mac bridge, browser results, and speech; update a handful of high-risk readers first (calendar/reminders, jobs, audio).  ·  risk: Some existing callers expect plain strings and may fail closed or become more verbose. Roll out in shadow mode, log envelope violations, and retain a compatibility adapter that labels legacy strings unknown rather than guessing observed.
- cost: Negligible runtime cost; lower model spend by formatting deterministic statuses without a model. A small one-time migration/test cost.  ·  latency: Usually improves latency; deterministic formatting is sub-100 ms. Ambiguous conflicts may add one judgement pass.
- security: Improves confidentiality by forcing sensitivity metadata to travel with content and preventing unreviewed raw route strings from reaching TTS. It is not a complete disclosure firewall until every speech path adopts it.
- depends on: A typed shared response-envelope module; USB pendant delivery ACK join for end-to-end playback status; Fixes to calendar/reminder readers so authorization failure is distinguishable from an empty result


## What it asked for

_Nothing._
## Its own summary

This round produced four non-duplicate directions: (1) cross-surface shadow execution with an exact diff, stale revalidation, and physical approval before commit; (2) an epistemically honest spoken mode that distinguishes observed, inferred, and unknown; (3) end-to-end pendant delivery truth joining generation, download, and playback rather than trusting Mac receipts; and (4) the model-routing change that enforces a shared evidence envelope before any speech path. I checked the live capability/device/route inventories first. The USB-tethered pendant and online Mac bridge are real; LTE registration is not assumed.

**Biggest unknown:** The remaining blockers are implementation gaps, not more conceptual design: a dry-run/commit transaction join across relay–Mac–browser, USB-serial ingestion and durable joining of pendant ACKs, and universal adoption of an evidence envelope (especially non-briefing speech). Owner policy values are still intentionally unset: which one-off external effects may be shadow-committed and which content may be spoken in public. I did not invent those preferences or re-request denied permissions.

