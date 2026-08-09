# Harness derivation — faculty-judgement — round 276

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Make my scheduled briefings self-checking: tell me only when the brief was actually downloaded and played, detect duplicate or stale runs, and leave an honest catch-up item when delivery failed."
- **useful because:** Today a routine can report completed after generation while the pendant is offline, and duplicate schedules already exist. This closes the gap between 'job ran' and 'I received it', without claiming an unheard brief was delivered.
- **path:** relay → mac-bridge → pendant → dashboard
- **model tier:** background for routine reconciliation and repair suggestions; realtime only for the owner's spoken catch-up question
- **latency:** under 10 seconds after a delivery ACK; under 2 minutes for the daily reconciliation
- **cost:** about $0.01-$0.05 per daily reconciliation; dominated by one background judgement over compact receipts, not audio generation
- **security:** Use opaque artifact IDs and authenticated device ACKs, never transcript or briefing text in the reconciliation record. Auto-repair may disable only exact duplicate routines after showing a draft; require confirmation before deleting or mutating schedules.
- **missing:** a durable routine-run to artifactId mapping; a routine delivery watchdog that consumes record_pendant_delivery_event and reconciles relay receipts; a safe duplicate routine repair flow using autonomy_policy_evaluate and explicit confirmation

### "While you are speaking a briefing item, let me say 'why?' or 'that's wrong' and have you pause that exact item, show the evidence and reasoning, then either correct the source, retract it, or resume without losing my place."
- **useful because:** A spoken briefing is currently a one-way stream: an owner cannot contest a claim at the moment it matters. This makes judgement accountable and turns an interruption into a bounded correction rather than restarting the whole conversation.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** realtime for binding the short utterance to the current item and answering why; background for evidence comparison and correction draft
- **latency:** pause within 300 ms locally; bind and acknowledge within 2 seconds; evidence comparison can take up to 15 seconds
- **cost:** $0.01-$0.08 per challenge, dominated by realtime transcription/judgement; no extra cost when the owner does not challenge
- **security:** Only operate on the active opaque item/cursor token; never expose secret source text over audio. Retraction or correction must be a reviewable draft unless the owner explicitly confirms. Preserve the original evidence and an immutable provenance receipt.
- **missing:** a challenge utterance classifier distinct from ordinary conversation; a typed correction/retraction draft that links an item to its evidence and downstream claims; a durable cursor-to-item binding shared by pendant and relay

### "Before any firmware or audio change reaches me, run a real pendant canary: exercise the USB-connected hardware, compare codec and delivery metrics to the last known-good run, and refuse promotion while producing a concise owner-readable failure report."
- **useful because:** The pendant is a physical product, so a green server job is not evidence that speech is intelligible or that playback reaches the owner. This turns measured hardware acceptance criteria into a judgement gate and prevents a regression from becoming my daily voice interface.
- **path:** mac-bridge → pendant → relay → dashboard
- **model tier:** background/cheap deterministic checks for packet, CPU, alias and drop thresholds; realtime is not needed unless the owner asks for the spoken explanation
- **latency:** 3-8 minutes per canary, with immediate fail-fast on serial/handshake failure
- **cost:** under $0.02 per canary if metrics are deterministic; dominated by optional model-written report, which can be skipped
- **security:** Run only signed test artifacts and allowlisted shell commands; do not upload microphone content. Store metric summaries and firmware hashes, not PCM. Promotion requires an explicit owner or maintainer confirmation; failure drafts never file externally.
- **missing:** a Mac harness route that flashes/runs the existing USB serial canary and captures scripts/audio-quality-probe.mjs output; a typed promotion gate comparing a named baseline to current metrics; a durable firmware-artifact-to-delivery-ACK linkage

### "Before you do anything consequential, tell me when the Mac, browser, and pendant disagree about what is true; show me the smallest side-by-side conflict, let me choose which source wins, and carry that choice through the action and its audit trail."
- **useful because:** Today each surface can report a locally plausible state while the system silently proceeds with a stale or contradictory view. The owner should get a concrete disagreement, not a confident blended answer—especially before sending, buying, deleting, or changing a logged-in page.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** cheap deterministic comparison first; realtime only to explain the conflict and collect the owner's source choice; background model for normalizing unlike evidence
- **latency:** under 1 second for detecting a typed conflict; under 3 seconds for a spoken explanation; never block harmless read-only work longer than 5 seconds
- **cost:** $0.005-$0.03 per conflict, dominated by normalization only when sources disagree; zero model cost for equal canonical values
- **security:** Compare hashes, timestamps, permissions, and typed facts by default; redact sensitive snippets and require the physical approval latch for destructive or external effects. A source preference is scoped to this fact/action, expires, and is provenance-recorded; it must never silently become a global trust rule.
- **missing:** a typed cross-surface observation format with freshness, source, confidence, and conflict fields; a quorum/conflict evaluator that fails closed and returns the minimal evidence needed for the owner; an action-plan binding that makes the selected source and observation versions prerequisites for execution, with stale-plan rejection; dashboard and spoken rendering for a compact conflict card

### "After you act, tell me whether the result matched what you predicted, and learn which surfaces and kinds of evidence are reliable for me without turning one mistake into a permanent blacklist."
- **useful because:** The system currently records completion receipts, but not whether its judgement was right in the owner's world. A Mac action can succeed technically while the browser state, pendant delivery, or intended outcome is wrong. Outcome calibration would make future decisions more honest and improve source selection over time.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** background model over structured predicted-vs-observed outcomes; deterministic scoring for updates; realtime only when the owner gives a correction
- **latency:** record immediately; calibrate within 30 seconds of an outcome ACK; weekly review under 2 minutes
- **cost:** $0.01-$0.05 per nontrivial outcome; most updates are deterministic and free
- **security:** Store outcome metadata and source IDs, not page contents or audio. Keep calibration scoped by action type, source, and recency with decay and a visible undo; never let a learned score override a required confirmation or physical approval.
- **missing:** a typed prediction record created before execution and an outcome record after execution; a provenance-linked evaluator for expected versus observed state across Mac/browser/pendant; a bounded, owner-visible calibration store with decay and correction

### "When you decide not to act, keep a private, searchable explanation of what you considered, what rule stopped it, and what would change the decision—so I can ask 'what did you not do?' without guessing whether you forgot."
- **useful because:** Current receipts explain completed work, not suppressed or refused work. Silent non-action is indistinguishable from failure, especially when a browser is offline, a permission is ambiguous, or a plan went stale. A negative-action ledger makes restraint observable without encouraging risky retries.
- **path:** relay → mac-bridge → browser → pendant → dashboard
- **model tier:** deterministic policy output and compact background summarization; realtime only to answer the owner's query
- **latency:** write the decision synchronously with each suppression/refusal; answer a spoken query within 2 seconds
- **cost:** under $0.01 per decision; mostly structured storage, with model cost only for ambiguous explanations
- **security:** Store action classes, rule IDs, source hashes, and expiry—not rejected secrets or full page text. Hide sensitive candidates from spoken output by default. The ledger must be append-only, owner-readable, and separate from an executable queue so asking about it cannot replay anything.
- **missing:** a durable negative-decision ledger covering relay, Mac, browser, and pendant; policy-evaluation output with matched rule IDs and a stable decision reason; a query and spoken-rendering surface for suppressed/refused actions, with expiry and redaction


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) delivery-truthful scheduled briefs that count as complete only after authenticated pendant download/playback ACKs, (2) an evidence-bound “why?/that’s wrong” interruption that pauses the exact spoken item and supports correction or retraction, and (3) a hardware canary/promotion gate that exercises the USB-connected pendant and blocks audio regressions using measured codec, alias, drop, and delivery thresholds. The first two are built from the newly granted delivery, provenance, revalidation, attention, and audio-item primitives; the third is the most important long-term trust boundary because server success is not hearing success.

**Biggest unknown:** I still need the concrete Mac-side USB canary harness and a durable firmware-artifact-to-delivery-ACK mapping; neither is exposed by the discovered routes. I also still need the owner to decide disclosure and interruption policy, but those are explicitly open owner choices rather than assumptions I should invent. The nRF9160 remains offline from the relay, so LTE delivery cannot yet be validated; only the physically connected bench path can be tested today.

