# Harness derivation — faculty-judgement — round 250

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When you say you completed something, prove that the world changed — and if it did not, tell me exactly what is still pending and what I can safely do next."
- **useful because:** Today a receipt means the Mac or relay accepted work, not that the intended state changed. This would prevent false closure for reminders, browser edits, files, and cross-surface jobs, especially after a dropped link or stale page.
- **path:** relay → mac → browser → pendant
- **model tier:** gpt-5.6-luna for planning and interpretation; cheap deterministic checks for postcondition evaluation; realtime only for the concise spoken result
- **latency:** Under 2 seconds for local reversible checks; up to 10 seconds for browser or multi-step verification; never block the owner from seeing a draft receipt while verification continues
- **cost:** Roughly $0.01–$0.04 per verified multi-surface action; dominated by one planner call only when the postcondition cannot be generated deterministically
- **security:** Verification must be read-only by default and must not expose page contents in the spoken result. External mutations still require the existing policy/physical approval. A failed check must say 'not verified', never infer success from a receipt.
- **missing:** A typed postcondition field on plans/actions; Read-only verifiers for each mutation class (reminder/note, file, browser form, outbound draft); A durable link between relay job IDs, Mac jobs, action receipts, and the verification result

### "Give me the useful answer aloud, but put anything long or private somewhere I can inspect later; let me say 'continue' and resume the exact answer without starting over."
- **useful because:** A pendant is a bad place for long explanations and a risky place for private content. This creates one coherent conversation split across speech and a local written artifact, instead of truncating, leaking, or making the owner repeat the question.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic sensitivity/length/channel policy first; gpt-5.6-luna only to produce a short faithful synopsis and stable section boundaries; realtime for the spoken synopsis
- **latency:** Synopsis in under 1.5 seconds when the source text already exists; local note creation may finish asynchronously within 5 seconds; resume should start at the saved section within 1 second
- **cost:** $0.002–$0.01 per invocation when summarization is needed; storage and local note creation dominate neither latency nor cost
- **security:** Default full text stays on the Mac, not in third-party TTS. Existing redaction is insufficient for direct pendantSpeech callers, so the channel gate must run immediately before synthesis and fail closed for secret content. Browser URLs and note IDs should be spoken only as opaque references.
- **missing:** A single channel-policy enforcement point before every pendant speech path, including confirmations and audioBrief; A durable answer artifact with section/cursor IDs and source links; A spoken-resume command that maps to audio_brief_item_action without losing playback position

### "Notice when I keep postponing the same thing and ask me once whether to do it, reschedule it, delegate it, or drop it — don't keep nagging me with the same reminder."
- **useful because:** Repeated deferral is a hidden signal that the plan is wrong, not a reason to increase interruption frequency. This would convert reminder noise into a small decision at a calm moment and prevent stale obligations from surviving indefinitely.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic clustering of reminder/watch/task identities and deferral history; gpt-5.6-luna only to explain the conflict and draft four options; realtime for one short question
- **latency:** No added latency to ordinary reminders; evaluate during existing routine/triage runs; spoken prompt under 1 second once selected by attention_arbitrate
- **cost:** Typically under $0.01 per evaluation; model cost only when task identity is ambiguous or options need wording
- **security:** Never delete, delegate, or reschedule automatically. A dismissal is not consent to mutate the task. Show source IDs and the number of deferrals, avoid speaking private task text in public, and retain an undo path for any confirmed change.
- **missing:** A durable deferral/decision history keyed across reminders, browser watches, routines, and jobs; A task identity resolver that links equivalent items without copying sensitive text; A four-option confirmation executor with explicit mutation receipts and undo

### "Let the system earn permission gradually: for a new kind of action, show me what it would have done in shadow mode, learn from my approvals or corrections, and only then allow the narrow action class automatically."
- **useful because:** A single global approval policy cannot capture the owner's trust in a particular target, action, or context. This gives the owner a visible path from observe-only to draft-only to reversible execution without silently broadening autonomy after one approval.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic policy state machine and action fingerprints; gpt-5.6-luna only to summarize shadow outcomes and cluster owner corrections; realtime for a one-sentence approval request
- **latency:** Shadow evaluation adds no mutation latency; promotion decisions should be immediate after explicit owner review; every first-run action remains blocked until its verdict is durable
- **cost:** Under $0.01 per shadow evaluation when checks are deterministic; occasional model summarization costs $0.01–$0.03
- **security:** Never infer approval from silence or from a similar action. Scope trust by action kind, target/origin, sensitivity, spend, and expiry; destructive and external actions remain confirmation-only. Store only compact fingerprints and decisions, not private payloads, and provide instant rollback/revocation.
- **missing:** A durable per-action-class trust state with expiry and downgrade rules; A shadow executor that runs read-only previews and records the would-have-done result; A promotion UI/voice flow that names the exact scope and policy rule before granting it

### "When the system's perception and action planners disagree about something that matters, do not hide the disagreement behind one confident answer; give me the smallest useful uncertainty and ask only the question that resolves it."
- **useful because:** Today one model can turn stale, missing, or contradictory Mac/browser evidence into a single confident action. Exposing material disagreement would prevent wrong edits while keeping trivial uncertainty out of the owner's way.
- **path:** relay → mac → browser → pendant
- **model tier:** Cheap deterministic contradiction checks first; independent low-cost verifier for high-impact claims; gpt-5.6-luna only to compress a material disagreement into one owner question
- **latency:** No added latency for low-risk agreement; 1–3 seconds for a material read-only disagreement; mutation is blocked until the uncertainty is resolved or the owner explicitly chooses a branch
- **cost:** $0.005–$0.03 per escalated decision, dominated by the verifier; zero additional model calls for straightforward checks
- **security:** Show evidence references and freshness, not raw private content. Never manufacture numerical confidence from model votes. Keep disagreement records short-lived and scoped to the action; destructive or external effects remain blocked by existing consent policy.
- **missing:** A typed claim/disagreement envelope carrying source, freshness, consequence, and alternative interpretations; A deterministic materiality rule that decides when disagreement must interrupt; An owner response that selects or corrects a branch and records the decision for only the relevant scope


## Changes it proposed to its own stack

### `hardware` — Add a low-power second microphone or short-range voice-activity/proximity sensor and a hardware privacy-status input, then expose a signed local 'private-audio-safe / uncertain / public' signal to the relay. The classifier should detect nearby non-owner speech or an occupied room, not identify people, and fail closed to a non-speaking channel when uncertain.
- **owner gets:** The pendant would stop reading private mail, calendar details, or notes aloud when another person is likely nearby, without requiring the owner to remember a mode switch every time. It would still answer with a generic spoken cue and place the detail locally for inspection.
- effort: New board revision, acoustic enclosure/calibration, a tiny on-device voice-activity classifier, relay policy integration, and an owner-visible override with expiry. Validate false-safe and false-positive rates in quiet, street, car, and meeting environments.  ·  risk: A sensor can be wrong and a false public verdict could disclose content, so uncertainty must always suppress detail. Audio analysis must remain feature-level/on-device and never upload room recordings. Recovery is an explicit owner override or local privacy latch; no remote command may force private speech.
- cost: Approximately $3–$12 in board/BOM cost depending on the sensor and enclosure; tens of milliwatts during active listening, near-zero while asleep. No meaningful per-request API cost.  ·  latency: 100–300 ms to update the local safety state; speech gating adds at most one utterance boundary, never mid-word disclosure.
- security: Adds a local fail-closed disclosure boundary and signed state, but creates a new physical sensor attack surface. Do not retain raw microphone samples or expose the classifier's room inference to third parties.
- depends on: A policy table defining which data classes may be spoken in each safety state; A mandatory speech gate covering pendantSpeech, confirmations, and audioBrief; A firmware transport field carrying the signed state over the shipping LTE-M link


## What it asked for

_Nothing._
## Its own summary

Round 250 produced three non-duplicate owner capabilities: (1) postcondition verification so receipts never masquerade as real-world success; (2) channel-aware answer escrow, giving a short safe spoken synopsis and a resumable local written answer; (3) stale-obligation amnesty, detecting repeated deferrals and asking whether to do, reschedule, delegate, or drop the item. The attempted morning-brief proposal was correctly rejected as an existing duplicate, so I did not rephrase it.

**Biggest unknown:** I still need owner-set policy values, not more infrastructure: quiet-hour windows, what qualifies as an emergency, whether notification content may ever be spoken aloud, trusted destinations/data classes, and whether repeated deferrals should default to reschedule, delegate, or drop. Technically, the three proposals still need durable cross-surface IDs/postconditions, a final speech channel gate, and a task identity/deferral history; those are missing links rather than new owner decisions.

