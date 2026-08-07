# Harness derivation — relay-realtime — round 50

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Pause this and resume it on my Mac when I’m back."
- **useful because:** The owner can start a task while away (voice, quick checks, thinking out loud) and later continue on the Mac without losing the thread. It reduces re-explaining and prevents context from being resent every turn.
- **path:** pendant → relay → mac-planner → browser
- **model tier:** Realtime for capturing the handoff, then a cheaper planner model on Mac for continuation.
- **latency:** Under a second to confirm the pause; continuation can happen when the Mac is available.
- **cost:** Low per pause (small context capsule). Most cost is downstream planning and any authenticated browser reads.
- **security:** Only store the minimum needed to resume (goal, references, citations). Avoid raw transcripts unless explicitly requested. Provide a visible receipt of what was saved.
- **missing:** A durable task capsule store with provenance and TTL; A lightweight context projection that selects only resume-relevant facts; Mac-side resume verb that accepts a capsule id and continues planning

### "While I’m away from my Mac, let a delegated task ask me one concise spoken clarification when it genuinely cannot proceed, then continue automatically with my answer and tell me the final result."
- **useful because:** Today a Mac or authenticated-browser task either guesses through ambiguity or stops silently; the owner cannot participate without returning to a screen. This makes the worn pendant a real conversational control surface for work spanning the relay, Mac, and browser, without turning every mutation into a confirmation gate.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use relay-realtime only to phrase the short clarification and capture the answer; mac-planner handles task reasoning, while browser-extension supplies authenticated page state and dashboard stores the resumable checkpoint.
- **latency:** Speak the clarification within 2 seconds of reaching an ambiguity; accept an answer for 10 minutes, resume within 5 seconds, and deliver a concise completion receipt. If unanswered, leave the task paused rather than guessing.
- **cost:** Approximately $0.01–$0.05 per clarification/resumption depending on speech-token length; dominant cost is the realtime turn, not the durable checkpoint or Mac planner call.
- **security:** The clarification may contain sensitive page or work context, so send only the minimum excerpt and never raw page contents to the pendant. Bind the answer to the exact task checkpoint, expire it after 10 minutes, redact secrets from spoken prompts, and record the resulting action/receipt. This is ambiguity resolution, not an additional approval requirement.
- **missing:** A durable, resumable task-checkpoint protocol shared by mac-planner and browser-extension; A relay push channel that can wake the pendant with a task-scoped question and correlate its spoken answer; Planner support for declaring an ambiguity, pausing safely, and applying the answer without losing prior work; A dashboard view of pending clarification checkpoints and expiry/recovery state

### "Compare the item I’m looking at in my authenticated browser with the matching Mac file or app record, tell me whether they disagree, and if I ask, repair the stale side while preserving evidence of what changed."
- **useful because:** The owner currently has to manually shuttle facts between an authenticated web session and local applications. A pendant request could combine sources that no single node can reach, identify the exact disagreement, and make a targeted correction instead of blindly copying data.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** faculty-perception extracts page and local evidence; faculty-judgement matches records and chooses a repair; mac-planner or browser-extension performs the concrete change; relay-realtime only handles the low-latency spoken query and result.
- **latency:** Return an evidence-backed comparison in under 8 seconds for already-open sources; repairs may take longer but should stream a brief spoken progress state and finish with source-specific receipts.
- **cost:** Roughly $0.03–$0.15 per comparison, dominated by multimodal/page and local-document extraction; repair uses existing planner/action calls and is cheaper than a fresh conversation turn.
- **security:** Authenticated page data and local files must remain scoped to this request, with field-level redaction before speech. Never infer that similarly named records are identical: report confidence and the source fields used. Preserve before/after hashes or excerpts and make repair reversible, without introducing a confirmation gate for ordinary reversible edits.
- **missing:** A cross-surface record-linking and evidence schema for browser pages plus Mac documents/apps; A read/compare orchestration endpoint that can request bounded extracts from both surfaces in one correlated job; A repair planner that applies a selected field-level patch and verifies both sides afterward; Receipts that cite each source and distinguish observed facts from inferred matches


## Changes it proposed to its own stack

### `context` — Add a typed “task capsule” projection service that extracts only resume-critical information (goal, constraints, references, last results, and next suggested step) into a small, signed object with TTL and provenance. Capsules can be saved by the relay and consumed by mac-planner or browser-harness.
- **owner gets:** They can stop talking mid-task, go do life, and later pick up exactly where they left off without repeating themselves.
- effort: Medium. Requires defining capsule schema, signing/verification, storage, and projection rules per surface.  ·  risk: If projection is wrong, we could resume with missing constraints or over-share sensitive info. Recovery is to show the capsule contents and ask to continue or discard.
- cost: Small storage per capsule; cheap to create. Savings from not resending full context every turn.  ·  latency: Tiny at pause time; resume cost shifts to downstream planning.
- security: Improves privacy by minimizing stored context; signing prevents tampering.
- depends on: A durable storage location for capsules (D1/R2); A shared schema and verification library across relay and Mac harness

### `relay` — Add a task-scoped clarification envelope and resumable checkpoint protocol: every delegated Mac/browser job may emit {checkpoint, ambiguity, minimal_context, expiry, safe_resume_point}; the relay can render one spoken question, bind the next utterance to that envelope, and return the answer plus checkpoint token to the owning planner. Persist only encrypted, redacted envelopes and make duplicate answers idempotent.
- **owner gets:** A task that gets stuck while the owner is away can ask exactly one understandable question through the pendant and continue from the same place, instead of silently failing, restarting, or making an untrusted guess.
- effort: Medium-high: shared contract across relay, mac-planner, browser bridge, job store, pendant push/audio correlation, expiry handling, and integration tests for disconnects and duplicate delivery.  ·  risk: A stale or misbound answer could alter the wrong task. Mitigate with task/session binding, spoken task labels, short expiry, idempotency keys, and a safe pause when correlation is uncertain. Recovery is to leave the checkpoint pending and expose it in the dashboard.
- cost: Negligible storage/compute; one additional short realtime turn only when ambiguity occurs. Engineering cost is primarily protocol and failure-mode testing.  ·  latency: Clarification delivery under 2 seconds when the pendant is online; answer-to-resume under 5 seconds. No impact on jobs that never emit ambiguity.
- security: Reduces data exposure by sending a minimal redacted excerpt rather than full Mac/page context; requires encrypted checkpoint storage and strict tenant/task scoping.
- depends on: A durable job/checkpoint store; A relay-to-pendant push path with correlation IDs; Planner and browser bridge support for pause/resume checkpoints

### `hardware` — Add a low-power haptic actuator and a second input gesture (for example, a squeeze/side button) to the pendant, with firmware support for distinct patterns: clarification waiting, answer accepted, task paused, and completion. Keep the existing button/LED behavior as a fallback and make haptics locally renderable from the relay envelope without streaming audio.
- **owner gets:** When the owner is walking, driving, in a noisy room, or cannot safely look at the pendant, they can notice that a remote task needs an answer or has finished and acknowledge it without opening a phone or returning to the Mac.
- effort: Medium hardware revision and low-to-medium firmware work: actuator driver, debounced gesture input, power budget, enclosure/acoustic validation, and relay event mapping.  ·  risk: Extra input may cause accidental gestures and haptics may be disruptive. Use a deliberate press pattern, rate-limit notifications, provide a spoken/LED fallback, and allow the owner to disable patterns. Recovery is graceful degradation to the current button/LED.
- cost: Approximately $1–$4 incremental BOM, plus a few mA only during short vibration pulses; negligible API cost.  ·  latency: Immediate local rendering once an event arrives; no model latency. LTE delivery remains the limiting factor.
- security: No new data leaves the device; gesture acknowledgements should carry a nonce/task token and never expose task content through externally visible patterns.
- depends on: A task-scoped relay event protocol for clarification/completion; Pendant firmware event queue and power accounting; Mechanical redesign and field-testable haptic patterns


## What it asked for

_Nothing._
## Its own summary

Discovered current tools/surfaces/grants and proposed a new cross-surface capability: pausing a task on the pendant and resuming on the Mac via a minimal task capsule. Also proposed a context-layer change to create typed, signed capsules to reduce context cost and protect privacy.

**Biggest unknown:** Where the durable capsule store should live and how to wire signing/verification across relay and Mac; also whether a resume verb already exists in mac-planner.

