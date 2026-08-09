# Harness derivation — faculty-judgement — round 215

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“You said it was done—prove the real-world result, not just that you ran the steps.”"
- **useful because:** Action receipts currently prove server acceptance or local execution, not that the intended external state changed. This would inspect the authoritative postcondition on the surface that owns it, distinguish done/partly done/not verified, and speak a concise evidence-backed answer instead of false completion.
- **path:** relay → mac → browser → pendant
- **model tier:** Background model for correlating receipts and evidence; realtime only for the final spoken answer.
- **latency:** 3–10 seconds for a normal verification; return immediately with ‘still checking’ if a browser or Mac read exceeds 2 seconds.
- **cost:** ~$0.01–$0.04 per verification; dominated by one background reasoning pass and any browser/Mac read, not audio.
- **security:** Reads only the postcondition needed for the requested task, never replays credentials or page bodies into the relay. External mutation is never part of verification. Require owner confirmation before opening a sensitive page solely to verify it; redact spoken evidence.
- **missing:** Typed postcondition contracts for common actions (created reminder, changed setting, submitted form, sent message); A durable join between relay job IDs, Mac action IDs, and browser command IDs; A verifier that can run read-only checks and attach source-linked evidence to the result

### "“Notice the chores I keep repeating across my Mac and browser, and offer to automate one—without silently automating anything.”"
- **useful because:** The owner gets relief from recurring multi-step work rather than another one-off command. The system can mine repeated, reversible action sequences across browser and Mac, explain the evidence, and present a safe draft routine for approval; the pendant makes the suggestion at a natural moment while the Mac/browser supply the observations.
- **path:** mac → browser → relay → pendant
- **model tier:** Cheap background model for clustering action receipts; realtime model only to explain a candidate when the owner asks.
- **latency:** Nightly or on-demand analysis under 30 seconds; suggestion delivery must be under 500 ms once a candidate exists.
- **cost:** ~$0.02–$0.10 per nightly analysis depending on receipt volume; storage and local clustering dominate more than inference.
- **security:** Never infer or reproduce secrets, form values, message bodies, or private URLs in a proposed routine. Candidates must be reversible and least-privilege; any external side effect requires the existing physical approval latch. Owner can dismiss or delete a candidate and its evidence.
- **missing:** A cross-surface action sequence join (current IDs are unrelated); A durable candidate/routine draft store with evidence links and expiry; A redacted sequence normalizer that retains action shape without sensitive parameters; An owner approval path that compiles a candidate into an existing routine or plan

### "“Learn what parts of my brief I actually hear, and make future briefs shorter and better without silently dropping important things.”"
- **useful because:** Playback completion and interruption are the only honest signals of whether an audio brief reached the owner. Using them, the system can increase detail for finished items, compress repeatedly skipped categories, preserve deadlines, and surface a weekly review of what it changed. This turns the pendant from a speaker into a feedback loop for attention.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model for weekly preference updates; deterministic rules handle per-item compression and deadline preservation; realtime only for the spoken brief.
- **latency:** No added latency to playback. Per-item policy lookup under 10 ms; weekly update under 10 seconds.
- **cost:** ~$0.01–$0.05 per weekly update; most work is local aggregation of signed delivery events.
- **security:** Store opaque item/category IDs and outcome metrics, not spoken content by default. Never interpret a skipped item as consent to suppress safety, deadline, or owner-requested content. Changes are reviewable, reversible, and source-linked; sensitive categories default to no adaptation.
- **missing:** A durable, privacy-minimized delivery/outcome aggregator beyond individual ACK ingestion; Stable semantic category IDs on briefing items; A policy updater that produces a diff and requires review for suppression or deadline changes; A cross-surface writer so learned preferences reach relay and Mac projections

### "“Before I commit, show me the likely consequences across my day and let me compare options—not just whether the button can be clicked.”"
- **useful because:** Today the system can plan or preview an action, but it cannot model second-order consequences across calendar load, pending commitments, browser state, deadlines, and reversibility. A consequence simulator would turn vague hesitation into an evidence-linked comparison: proceed, defer, delegate, or decline, with uncertainty and the assumptions that drive each forecast. It would be useful precisely when no single surface has the answer.
- **path:** pendant → relay → mac → browser
- **model tier:** Background model gathers and ranks scenarios; realtime model speaks the short comparison after the owner asks. Deterministic checks enforce deadlines, permissions, and policy constraints.
- **latency:** 10–20 seconds for a full comparison; pendant should acknowledge within 500 ms and may say ‘I’m checking the calendar and commitments.’
- **cost:** ~$0.05–$0.20 per comparison; dominated by multi-source reads and the background scenario synthesis.
- **security:** Read only the minimum evidence needed for each option; do not send private mail or browser contents to a third-party model without the existing disclosure policy. Forecasts must be labeled as estimates, cite sources, expose stale assumptions, and never mutate anything. Any chosen external action still requires the existing autonomy policy and physical approval where applicable.
- **missing:** A typed consequence/assumption graph linking calendar items, commitments, jobs, and browser state with freshness timestamps; A read-only multi-surface scenario evaluator that can compare at least two alternatives without executing them; A compact owner-facing uncertainty and evidence format for spoken output; A policy hook that distinguishes analysis from commitment and requires explicit approval before crossing into mutation


## What it asked for

_Nothing._
## Its own summary

Round 215 produced three owner-facing capabilities: (1) postcondition verification that proves a real-world result instead of mistaking execution receipts for success—the highest-value one; (2) a cross-surface repetition miner that offers reversible automation drafts without silently acting; and (3) an adaptive briefing loop that uses authenticated playback completion/interruption to improve future briefs, while preserving deadlines and requiring review for suppression. I also told faculty-action about the proposals. What remains needed is implementation, not more owner preference this round: typed postcondition contracts plus a durable relay↔Mac↔browser join; a redacted sequence normalizer and candidate store; and a privacy-minimized delivery-outcome aggregator with semantic briefing categories and reviewable policy diffs. I will not re-request the already-declined preference/permission context.

**Biggest unknown:** Whether the live system already exposes a durable cross-surface correlation join or postcondition verifier that was not in the established inventory; the proposal recorder specifically warned that cross_surface_preflight and explain_action_provenance were named without a fresh inventory proving their routes.

