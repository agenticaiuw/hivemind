# Harness derivation — unified — round 210

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I ask for the news, give me only headlines you actually verified, tell me when verification failed, and speak the result on the pendant."
- **useful because:** The live pipeline just produced a confident 'briefing ready' while reading zero sources and returning a null source URL. This capability prevents fabricated or empty briefings from being spoken as fact, and makes a failure audible and actionable.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use the background/planner tier for source collection and claim extraction; use realtime only for the owner's live follow-up. Deterministic validation should reject missing URLs, stale timestamps, and unsupported claims without an expensive model call.
- **latency:** 3-8 seconds for a verified briefing; under 1 second to say 'I could not verify that' when sources fail. Browser retrieval and deduplication dominate latency.
- **cost:** Roughly $0.01-$0.05 per briefing depending on planner tokens and number of pages; browser reads and macOS TTS dominate wall-clock time, not relay storage.
- **security:** Read only explicitly allowed news tabs/domains; never infer a headline from a search snippet alone. Show source titles/URLs in dashboard, bind each spoken sentence to evidence IDs, and require confirmation before opening or submitting anything.
- **missing:** claim-to-source evidence schema carried through research_brief and pendant speech; fail-closed validator that blocks audio when sourcesRead is zero or source URLs are null; browser retrieval policy for freshness and domain allowlists; compact spoken error and dashboard evidence view

### "If you tell me you completed something, let me ask 'did you really do that?' and get one answer that separates planned, executed, delivered, and physically heard."
- **useful because:** A successful Mac receipt is not proof that the browser changed, the relay accepted the payload, or the pendant speaker played it. The owner needs one trustworthy answer instead of optimistic status language, especially after a dropped link or interrupted job.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use deterministic joins and receipt validation first; invoke the background model only to summarize conflicting evidence in plain language. Realtime is needed only if the owner asks during a live conversation.
- **latency:** Under 2 seconds for existing receipts and browser results; up to 5 seconds if a bound browser tab must be inspected. Evidence lookup, not model generation, dominates.
- **cost:** Usually below $0.01; most calls are local/relay reads. A model summary is the only material variable cost.
- **security:** Require a commitment ID and explicit app/tab bindings; redact page contents and sensitive parameters; never turn absence of evidence into a claim of failure. Preserve immutable receipts and label stale or contradictory witnesses.
- **missing:** a cross-surface evidence join keyed by commitment/job/artifact IDs; explicit state vocabulary planned|executed|relay-accepted|device-received|playback-started|playback-finished|unknown; conflict resolution and stale-evidence rules; pendant-readable concise receipt response

### "Why didn't my morning briefing happen? Show me the exact scheduled time in the Mac's timezone, which stage failed, whether anything was spoken, and offer a safe rerun without duplicating it."
- **useful because:** The live pipeline has a failed routine run whose later stages still rendered and uploaded audio, while source collection returned zero sources. The owner needs causal truth and a non-duplicating recovery path, not a generic 'failed' badge.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic timeline and timezone calculations first; background model only summarizes the causal chain. Realtime is unnecessary unless the owner asks during speech.
- **latency:** Under 2 seconds for diagnosis; under 5 seconds for a dry-run rerun plan. Reads from local job/pipeline stores dominate.
- **cost:** Usually under $0.01; no model call needed for the common case.
- **security:** Use America/New_York for Mac-resolved routine times and label it; never substitute a pendant timezone. A rerun must inspect idempotency and existing artifacts, require approval if it can send or play again, and never claim audio was heard without a device receipt.
- **missing:** routine-run causal timeline joining scheduler, relay job, local job, pipeline and audio receipts; timezone-labelled owner-facing failure vocabulary; idempotent rerun planner that distinguishes no-op, retry, and duplicate side effect; dashboard drill-down and pendant summary

### "Before you speak a long answer, tell me how long it is and let me say 'shorter' or 'send it later'; never make me wait through audio I did not ask to hear."
- **useful because:** The owner wears a single-output device, and a 26.7-second briefing can be generated even when its content is unverified. A duration-aware preflight gives control over attention and data use without interrupting active speech or writing routine audio to SD.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** Deterministic duration/byte budgeting and queue policy; a cheaper background model makes a shorter rewrite. Realtime is reserved for the live utterance and cancellation.
- **latency:** Speak the duration estimate within one audio turn; shorter rewrite under 2 seconds after the owner's request. TTS rendering is the main latency.
- **cost:** About $0.001-$0.02 depending on whether a rewrite model is needed; TTS and Opus dominate compute.
- **security:** Cancellation must mute locally immediately and invalidate queued playback; preserve no discarded audio beyond existing failure-path rules. Never interrupt active speech unless the owner's runtime policy allows it; expose the chosen policy and exact duration.
- **missing:** audio-duration preflight before relay upload; pendant-local cancel/invalidate token tied to playback artifact; shortening endpoint that preserves evidence bindings; queue policy integrated with existing focus/notification modules

### "Tell me when two places disagree about something important—like my calendar, an email thread, and a browser page—and ask me which one should be treated as true before taking action."
- **useful because:** Today each surface can be queried independently, but the owner receives no warning when they contradict one another. Silent inconsistency can cause a missed meeting, duplicate payment, or an action against stale information.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic extraction and timestamp comparison first; use a background model only to classify whether two records refer to the same real-world item and summarize the conflict. Realtime is only for the spoken question.
- **latency:** Under 4 seconds for a conflict scan over explicitly bound sources; immediate spoken alert only after a high-confidence conflict is found.
- **cost:** Usually under $0.03 per scan; browser reads and background entity matching dominate.
- **security:** Read only user-authorized apps/tabs, show every conflicting value and timestamp, never silently choose a winner, and require explicit owner selection before any mutation. Redact unrelated page content.
- **missing:** cross-surface entity matching with provenance and timestamps; conflict severity and freshness rules; owner resolution record that binds the chosen source to subsequent actions; dashboard diff view and compact pendant prompt

### "For sensitive questions, keep the words and answer on my Mac whenever possible, and show me exactly what—if anything—left the machine before I continue."
- **useful because:** The pendant, relay, browser, and Mac currently form a powerful path but not a user-visible data-boundary decision. The owner should not have to guess whether a private utterance became relay history, browser content, or persistent memory.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a deterministic sensitivity policy and local routing first; use a small local/background classifier for ambiguous utterances. Realtime may answer locally, but cloud realtime must be opt-in for classified-sensitive content.
- **latency:** Under 150 ms for known policy categories; under 1 second for an ambiguous classification prompt. Encryption and routing decisions must happen before transcription leaves the chosen boundary.
- **cost:** Low recurring model cost when classification is local; encrypted relay metadata and audit storage are the main costs.
- **security:** Never claim local-only unless the transport receipt proves it. Maintain a tamper-evident exposure receipt listing surfaces, data classes, retention, and deletion status; physical privacy latch remains an immediate hardware override, not a substitute for routing policy.
- **missing:** pre-transcription transport selection on the pendant; local speech-to-text or an explicitly bounded encrypted path; data-class policy with owner-editable categories; exposure receipt and retention propagation across relay, browser, and Mac

### "When I ask you to watch something over time, tell me only when the situation genuinely changed, show me the evidence for the change, and let me pause or end the watch from the pendant."
- **useful because:** The system can run routines and inspect browser tabs, but the owner cannot create a bounded, evidence-backed watch that coalesces repeated observations and remains controllable when the Mac or browser disappears. This would turn the hive into a useful long-lived observer without notification spam.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/scheduled model for normalization and change detection; deterministic hashing, timestamps, deduplication, expiry, and quiet-hour enforcement. Realtime only speaks a delivered alert or handles a live change to the watch.
- **latency:** Normal polling can be minutes apart; a confirmed change should reach the owner within one polling interval plus a few seconds. No foreground model call on every poll.
- **cost:** Low if pages are diffed and summarized only on change; browser polling and retained evidence capsules dominate.
- **security:** Require explicit target bindings, a maximum lifetime, pause/delete controls, and a visible list of watched sources. Do not retain full pages by default; store minimal redacted evidence and delete it with the watch. Alerts must respect quiet-hour policy and never imply the owner saw one without a receipt.
- **missing:** durable watch objects with lease, expiry, pause, and coalescing state; content-diff/evidence capsule service for bound browser or Mac sources; pendant inbox control verbs for pause/end; relay scheduler and delivery receipts for change alerts


## Changes it proposed to its own stack

### `integration` — Make research_brief a fail-closed transaction: require at least one successfully fetched, non-null URL source and attach evidence IDs to every sentence before allowing TTS or pendant upload. If validation fails, emit a spoken failure and a dashboard receipt instead of 'briefing ready'.
- **owner gets:** The owner will stop hearing confident audio that was generated from zero readable sources, as happened in the live pipeline.
- effort: Medium: validator, evidence schema, pipeline gate, regression fixtures for empty/null/ stale sources.  ·  risk: Some legitimate briefings will be blocked when publishers are temporarily unavailable; recover by offering an explicit unverified draft only after the owner asks.
- cost: Negligible storage; saves TTS and model spend on invalid briefings.  ·  latency: Adds tens of milliseconds for deterministic validation; no meaningful user delay.
- security: Improves provenance and prevents unsupported claims from leaving the Mac.
- depends on: research evidence IDs carried through /research and /research/briefings/:id/speech; source freshness and domain policy

### `integration` — Add a causal run ledger that joins routine fire time, relay job, local job, pipeline stages, browser commands, and audio delivery receipts into one immutable timeline with explicit terminal states. Close successful ledgers and mark partial runs rather than leaving every historical plan looking interrupted.
- **owner gets:** 'Why didn't it happen?' becomes answerable in one screen and safe reruns can avoid replaying a side effect that already happened.
- effort: Medium-high: correlation IDs across existing stores, terminal-state normalization, timeline endpoint and dashboard view.  ·  risk: A missing event could be mistaken for failure; label unknown explicitly and preserve raw receipts for audit. Recovery is rebuilding the projection from source stores.
- cost: Small local/relay index growth; no recurring model cost.  ·  latency: No hot-path impact; projection can update asynchronously.
- security: Redact sensitive params and keep action history immutable; do not use the projection as authorization.
- depends on: orchestrator closeLedger call; relay job lease/requeue prerequisite; cross-store correlation field

### `firmware` — Add a playback-intent token and local cancel path around the existing 24 kHz audio delivery ACK queue: before a queued artifact begins, the pendant accepts only the newest valid token; a local cancel immediately mutes and emits an interruption receipt, and stale relay packets are discarded without touching the speaker.
- **owner gets:** A long or obsolete answer cannot continue playing after the owner says stop or a newer response supersedes it, even when the relay is delayed.
- effort: Medium: token state machine in pendant playback, compact receipt fields, relay invalidation handling, and hardware test under packet reordering.  ·  risk: A lost invalidation could leave an old clip queued; local expiry and newest-token-wins recovery prevent indefinite playback. Must preserve the privacy latch's stronger guarantee.
- cost: A few hundred bytes of flash/RAM and tiny metadata messages; no routine SD writes.  ·  latency: Cancellation is local within one audio frame; no added start latency.
- security: Tokens must be opaque, monotonic/replay-resistant, and scoped to the paired device; do not include speech text.
- depends on: audio_delivery_ack_queue; duplex_audio_congestion_guard; local_privacy_latch


## What it asked for

_Nothing._
