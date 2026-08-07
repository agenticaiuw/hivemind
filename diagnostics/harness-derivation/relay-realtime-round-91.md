# Harness derivation — relay-realtime — round 91

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Use the private detail I just spoke to complete this task, but do not let that detail appear in transcripts, logs, model prompts, browser-page captures, or Mac history.”"
- **useful because:** The owner can currently choose between getting useful cross-device action and keeping sensitive speech private, but not both. A pendant-marked private span would let them dictate a one-time code, health detail, or confidential note, have the relay orchestrate browser/Mac work, and receive a result while every other surface sees only a typed withheld handle.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime handles only intent boundaries and acknowledgement; a cheaper background worker performs redaction, handle expiry, and receipt reconciliation. Downstream agents receive task semantics, never the private payload unless the target operation explicitly needs it.
- **latency:** A short spoken acknowledgement within 300 ms; private-span sealing and task dispatch within 2 seconds. Completion can be asynchronous, with only a non-sensitive status spoken back.
- **cost:** About $0.002–$0.01 per invocation beyond ordinary transcription, dominated by encrypted temporary storage and one extra classification pass; no expensive realtime generation for the secret itself.
- **security:** The raw span must be encrypted at ingress, excluded from ordinary transcript/history/log projections, bound to one task and one target session, and destroyed on completion or a short TTL. Browser fill and Mac actions must expose only success/failure receipts, never echo values. Dashboard needs an auditable event that a withheld handle was used without revealing its contents; explicit owner gesture/button marks the private interval.
- **missing:** Pendant firmware support for a private-span start/stop gesture and local buffering of the marked audio; Relay privacy-envelope schema with encrypted payload, non-reversible handle, TTL, and redacted projections across voice runs, jobs, logs, and memory; Browser-extension and Mac planner APIs that consume a withheld handle for a single field/action without returning or logging its value; End-to-end tests proving secrets do not enter model prompts, receipts, screenshots, or analytics

### "“Before I join, tell me whether the meeting is actually ready here.”"
- **useful because:** Today each node can inspect only its own slice: the pendant knows the room’s immediate audio state, the Mac knows local apps/devices, and the browser holds the authenticated meeting page. The owner needs one answer that reconciles all three—whether the right meeting is open, audio output/input are usable, and the room is quiet enough—rather than a misleading single-surface status.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime asks one narrow clarification only if multiple meetings are plausible; faculty-perception/background models extract device and browser facts, while a cheap judgement pass reconciles them. No large model should inspect raw room audio: emit short local features such as speech/level/noise classification.
- **latency:** Initial spoken readiness verdict in 3 seconds, with Mac/browser probes parallelized; a changed-state recheck in under 1 second when the owner presses the pendant button.
- **cost:** Roughly $0.003–$0.02 per check, dominated by one browser extraction and lightweight reconciliation; local audio-feature extraction should be effectively free.
- **security:** Do not upload room audio or meeting content. Browser extraction must be limited to meeting identity and join/device status, with authenticated page text excluded from logs. The result should say which check failed and offer reversible fixes (select meeting, set volume, open join page), never auto-join or transmit audio without the owner’s explicit spoken request.
- **missing:** A typed readiness-check contract spanning pendant audio features, Mac device/app state, and browser session state; Pendant firmware event for a button-triggered local acoustic snapshot and a privacy-preserving feature payload; Parallel fan-out and correlation IDs in the relay so stale browser/Mac observations cannot be mixed; A reconciliation policy that distinguishes 'not observed' from 'failed' and speaks uncertainty clearly; Browser-extension endpoint exposing meeting identity and pre-join device readiness without page-content capture


## Changes it proposed to its own stack

### `relay` — Implement the granted intent-routing schema as a real relay feature: a thin, explicit router that accepts an intent label and utterance, validates a small set of targets (mac-planner, mac-vision), persists a relay job record, and forwards to the appropriate downstream tool (mac_run_actions for 1–3 reversible actions, mac_delegate for multi-step goals). Attach a stable job id and status updates consumable by relay_job_status, including failure reasons and last known step.
- **owner gets:** They can say something like “open my calendar and draft a reminder” and the relay can route it reliably without guessing or inventing a protocol. It also enables consistent status updates through the pendant if they walk away.
- effort: Medium. Needs relay-side implementation, job bookkeeping, and a small intent-to-tool mapping; no new model behavior required.  ·  risk: Misrouting could trigger unintended actions. Mitigate with conservative mappings and defaulting to mac_delegate when intent is ambiguous. Keep actions reversible by default; rely on receipts for audit.
- cost: Low per request. Dominated by downstream Mac agent planning/execution when used.  ·  latency: Low added latency. Routing is lightweight; most time is downstream.
- security: Moderate: relay becomes an action initiator. Requires strict auth, logging, and minimal payloads. Avoid embedding secrets; pass references when possible.
- depends on: relay_job_status implementation and relay job persistence

### `integration` — Wire a durable, cross-surface job runner that the relay can enqueue into and the Mac/browser harness can drain when online. Jobs should support: intent + normalized payload, target surface, idempotency key, retry/backoff, receipts, and cancellation. Use Durable Objects or D1 to persist, and a queue/worker to execute. Provide a status API that relay_job_status can read without waking the Mac.
- **owner gets:** They can ask for something that takes time, then walk away. The system keeps working and can later tell them exactly what happened, even if the Mac was offline when they asked.
- effort: High. Requires new infrastructure and coordination across relay, Mac harness, and browser harness.  ·  risk: Queue bugs could duplicate actions or run out of order. Mitigate with idempotency keys, receipts, and undo where possible.
- cost: Moderate ongoing cost for storage and worker execution; dominated by downstream work volume.  ·  latency: Improves perceived latency by acknowledging quickly and completing asynchronously.
- security: High: introduces a new persistence and execution path. Needs careful auth, payload minimization, and audit trails.
- depends on: No scheduler exists today; needs queue/worker plumbing; Relay job persistence and status visibility

### `relay` — Add a cross-surface temporal-coherence layer to every spoken answer and delegated action: attach monotonic observation timestamps, source surface, session affinity, and freshness bounds to Mac, browser, and pendant facts; reject or explicitly label a result when the facts were gathered from different tabs/sessions or have gone stale. Before claiming success, the relay should perform a cheap state re-read for volatile facts (active tab, call status, volume, network) and speak 'last observed' when revalidation is impossible.
- **owner gets:** The owner will stop hearing confident but wrong answers caused by a browser tab changing, the Mac going offline, or a delayed job receipt arriving after the world changed. They get a trustworthy answer such as “the meeting page was ready 8 seconds ago, but I can’t verify the microphone now,” instead of a false assurance while away from the Mac.
- effort: Medium: shared observation envelope, correlation/freshness logic in relay and adapters, plus simulator tests with delayed and reordered events.  ·  risk: A strict freshness bound could turn a useful answer into an unnecessary 'unknown'; recover by returning the last cited observation and offering a recheck. Clock skew and retries could create false mismatches, so use relay-issued sequence numbers and source monotonic counters rather than wall-clock time alone.
- cost: Negligible API cost; one extra lightweight read only for volatile operations. Small durable metadata overhead per observation and receipt.  ·  latency: Adds about 100–500 ms for revalidation when needed; no extra latency for stable informational answers.
- security: Improves isolation by preventing facts from one authenticated browser session or owner/device from being accidentally attached to another task. Do not persist page content—only typed source, session, timestamp, and freshness metadata.
- depends on: A common typed observation envelope across relay, Mac planner, browser extension, and pendant events; Correlation IDs and session affinity for delegated jobs; A per-field freshness policy distinguishing volatile state from durable facts


## What it asked for

_Nothing._
## Its own summary

Recorded three new items: (1) a privacy-envelope capability so a pendant-marked secret can be used across browser/Mac without entering transcripts, prompts, screenshots, or logs; (2) a cross-surface meeting-readiness check reconciling pendant acoustics, Mac device state, and authenticated browser state; and (3) a relay temporal-coherence layer that prevents stale or cross-session facts from becoming confident spoken answers. The owner still needs the privacy-envelope protocol and firmware gesture, typed readiness fan-out, and shared observation/freshness envelopes across all surfaces.

**Biggest unknown:** Whether the existing pendant firmware and browser-extension implementations already expose private-span markers, acoustic features, or typed session/freshness metadata; no further discovery was permitted this round.

