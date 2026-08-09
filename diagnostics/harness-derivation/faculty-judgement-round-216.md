# Harness derivation — faculty-judgement — round 216

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Give me a three-sentence world-and-US brief that is genuinely current, cite the sources, and tell me when the sources disagree.”"
- **useful because:** The owner has asked for this repeatedly, but a short spoken answer is not enough if it silently mixes stale or single-source claims. This would make freshness, source diversity, disagreement, and provenance part of the answer while keeping speech brief.
- **path:** browser → relay → pendant → dashboard
- **model tier:** Use the cheaper background model for source collection and clustering; use realtime only to answer a follow-up or handle barge-in.
- **latency:** 90 seconds for collection and synthesis; under 2 seconds for a spoken follow-up.
- **cost:** Roughly 6–12 public-page/search fetches plus one cheap synthesis call; dominant cost is fetched-page context, not speech.
- **security:** Only public URLs leave the device. Never read authenticated tabs for this job. Each sentence must retain source URLs, capture time, and an uncertainty/disagreement label; spoken output should say 'sources disagree' rather than resolve contested claims by confidence alone.
- **missing:** A news-source freshness/diversity policy the owner can edit (conservative default: at least two independent reputable sources per major claim).; A durable source-to-sentence citation bundle consumable by the dashboard and audio brief.; A live news brief scheduler that does not confuse the existing 07:00 research routine with the 07:30 Mac-status routine.

### "“Find duplicate or stranded routines, show me exactly what would happen, and ask once before disabling or repairing anything.”"
- **useful because:** The live owner state already contains overlapping daily briefs and routines can remain marked processing after a failure. The owner should not have to notice duplicate speech or silently missing work; this capability turns conflicts into a reviewable, reversible repair instead of autonomous deletion.
- **path:** relay → mac-planner → dashboard → pendant
- **model tier:** Deterministic reconciliation and policy evaluation first; use the cheaper background model only to summarize the conflict. Realtime is needed only for the final spoken question.
- **latency:** 2–5 seconds to scan and prepare a repair slate; no mutation until explicit confirmation.
- **cost:** Low: reads and policy evaluation dominate. One cheap summarization call for several conflicts; no cost for a no-op scan.
- **security:** Default to read-only preview. Never disable a routine, cancel a job, or alter a schedule without an explicit owner confirmation bound to the exact routine IDs and expected effects. Show provenance and a rollback path. Fail closed when timezone or permission evidence conflicts.
- **missing:** A routine-specific conflict/lease scan that distinguishes duplicate intent from intentionally separate schedules.; A durable repair plan with exact IDs, stale-state evidence, and one-click undo.; A single confirmation handoff shared by dashboard and physical pendant approval.

### "“Read this to me only when it is safe to say aloud; otherwise put it in my private review queue and tell me why you withheld it.”"
- **useful because:** The current strongest redaction path protects briefing triage, but direct pendant speech and audioBrief can speak arbitrary result text and do not consult sensitivity or bystander context. This capability makes disclosure a deliberate decision instead of assuming the wearer is alone.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic sensitivity and destination-policy evaluation first; use realtime only to explain a blocked decision or answer a follow-up. No model should infer privacy from prose when the classifier can fail closed.
- **latency:** Under 300 ms for an allow/block decision; under 2 seconds to queue a private review item.
- **cost:** Negligible for classification and policy; optional cheap summarization for a non-sensitive placeholder. TTS cost is incurred only after an allow decision.
- **security:** Ship with a conservative policy object whose fields are owner-editable: secrets never spoken, sensitive content requires explicit per-item permission, normal content may speak only when the pendant is actively worn/owner-present. Do not claim macOS Focus/DND exists; use the honest idle/presence signals and an explicit owner setting. Blocked content stays local and the spoken response contains no secret value. Log the policy rule, sensitivity class, and evidence refs for explanation.
- **missing:** A single enforcement hook in pendantSpeech.js and audioBrief.js before synthesis.; An owner-configurable disclosure policy and a real bystander/presence signal; current ioreg idle is not proof the owner is alone.; A private queue/review route that can hold the item without copying raw secret text into relay prompts.

### "“When a source cannot actually be read, tell me that it is unreadable—not that everything is clear—and let me retry only that source later.”"
- **useful because:** Today an unauthorised EventKit read can return an empty list, and some briefing routes turn that into a confident ‘calendar is clear.’ The owner needs absence, unreadable, stale, and genuinely empty to be different spoken outcomes.
- **path:** mac-planner → relay → pendant → dashboard
- **model tier:** Deterministic tri-state source contracts and corroboration; use realtime only to explain the result conversationally.
- **latency:** Under 1 second for a source-status verdict; retry may run in the background.
- **cost:** Minimal; one additional permission/read probe per affected source. No model call for the normal path.
- **security:** Never expose calendar or mail contents merely to prove readability. Return capability status, timestamp, permission provenance, and a safe reason. Fail closed on empty-plus-unauthorised combinations.
- **missing:** A shared SourceResult schema with readable/empty/unreadable/stale states and provenance.; Fixes in notificationTriage and dayPlan to consume that schema instead of treating [] as success.; A retry action that asks for no content and can be queued for the next permitted read.

### "“Keep my conversation usable when LTE is weak: shorten or defer nonessential speech, preserve the exact item I was hearing, and tell me plainly what was postponed.”"
- **useful because:** The owner should not lose the conversational thread to a marginal radio link or spend scarce bandwidth on low-value narration. This is an adaptive service-quality decision, not a second inbox: urgent short replies remain usable while long audio is deferred without pretending it played.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** Deterministic link/queue/audio metrics for mode selection; cheap background synthesis for a shorter substitute; realtime only for the live turn.
- **latency:** Mode decision under 100 ms; short reply under 2 seconds; deferred regeneration is background work.
- **cost:** Usually lower than today because deferred long audio is not regenerated repeatedly. Main cost is a small durable state record and optional short-form synthesis.
- **security:** Never silently drop content. Preserve item identity and expiry, expose the reason (radio, queue, codec, or policy), and require confirmation for sensitive content that would be replaced or re-spoken. Link metrics must be authenticated device telemetry.
- **missing:** A real-time quality profile spanning relay, radio, pendant queue, and ESP32 playback.; A policy that classifies items as essential, compressible, or deferrable.; A resumable audio artifact format with item-level checkpoints and an owner-visible postponement record.


## Changes it proposed to its own stack

### `hardware` — Add a low-power battery fuel-gauge IC with an authenticated state-of-charge/voltage/temperature measurement path, then expose those readings to the relay and Mac policy engine. Use them to select a safe audio budget, warn before a scheduled brief, and distinguish radio failure from power brownout in delivery receipts.
- **owner gets:** The owner should know whether the pendant is actually going to be available, rather than discovering after a missed conversation. The system can avoid starting a long brief that will die halfway through and can explain failures truthfully.
- effort: Board revision, I2C/ADC firmware driver, calibration across charge/discharge temperatures, signed telemetry schema, relay storage, and policy integration. Prototype on the live USB bench before a board spin.  ·  risk: Gauge drift or a bad calibration could create false alarms; recover with conservative voltage cutoffs, periodic calibration, and a ‘measurement unavailable’ state. Do not claim a percentage when only voltage is known.
- cost: Approximately $1–3 BOM increase plus board-layout work; tens of microamps to a few hundred microamps depending on gauge and sampling. Negligible API cost.  ·  latency: Telemetry arrives on the existing status cadence; policy decisions are local and effectively immediate.
- security: Battery data is low sensitivity but device identity and signed monotonic telemetry must be protected against spoofing. No audio or transcript leaves the device because of this change.
- depends on: A signed pendant telemetry envelope and relay ingestion path; A shared audio-budget policy consumed by relay and Mac; A delivery receipt that records power-related interruption reasons


## What it asked for

_Nothing._
## Its own summary

Round 216 produced three non-duplicate owner-facing capabilities: source-disputed current news briefs; a reviewable, confirmation-gated routine conflict/repair slate; and a conservative bystander-safe speech firewall. The delivery-ACK/replay proposal was correctly rejected as already covered by the existing delivery-event and audio-item primitives, so I did not rephrase it. I also asked faculty-perception for fresh evidence before the next judgement round.

**Biggest unknown:** I still need an owner-set disclosure policy (what may be spoken aloud and where), plus a stated morning-brief reliability preference. I will keep defaults conservative and fail closed rather than invent those preferences. Technically, the missing pieces are the speech enforcement hook, news citation/disagreement persistence, and routine repair/lease evidence—not another general-purpose arbiter.

