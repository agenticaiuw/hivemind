# Harness derivation — mac-terminal — round 231

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“If a browser task reaches a point where it needs my eyes or a decision, tell me on the pendant and let me approve or reject it with one physical press; if I’m away, keep the request until I return.”"
- **useful because:** The browser can hold authenticated sessions the Mac and relay cannot, but today a long browser job can silently wait or finish without a wearable-level handoff. This turns the pendant into an attention bridge: the owner can safely complete visual or consequential steps without reopening the laptop, while stale requests remain visibly unresolved rather than being mistaken for completion.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap background classifier to decide whether a browser result truly needs human attention; realtime only to phrase the short alert and answer a button-driven follow-up. No expensive model is needed for the approval state machine.
- **latency:** Alert under 2 seconds after the browser command reaches a waiting state; button acknowledgment under 500 ms locally, with relay confirmation under 2 seconds when connected.
- **cost:** About $0.001–$0.01 per handoff, dominated by the optional realtime spoken alert; browser polling and state transitions are local.
- **security:** The relay must carry only a redacted task summary and opaque command ID, never page text, cookies, or screenshots unless the owner explicitly asks. Approval must be bound to the exact command ID, expire after a short TTL, reject duplicates, and record the page origin and evidence capsule. A rejection or timeout must leave the browser task paused, not guess.
- **missing:** A durable browser-awaiting-owner state with exact command ID, expiry, and idempotent approve/reject transitions; A pendant button mapping for approve versus reject that does not delay the sw0 active-edge recording path (likely use sw1 plus a short spoken confirmation if only one action is available); Relay push from browser/mac-planner to the pendant and a route that returns the physical decision to the browser command; A dashboard view of pending human decisions and their evidence

### "“Before I leave the desk, tell me whether the nRF9160 pendant and ESP32 audio bridge are both alive, exchanging sane frames, and ready for a conversation; if not, tell me exactly which cable, port, or chip failed.”"
- **useful because:** The hardware is physically present now but has no truthful, owner-facing bench readiness check. A single answer prevents discovering a dead audio path only after leaving Wi‑Fi or starting an important conversation. It also makes the Mac-attached pendant testable today without pretending USB is the eventual wearable transport.
- **path:** mac-planner → pendant → relay-realtime → dashboard
- **model tier:** No LLM for collection or parsing: a deterministic shell/serial harness should validate port enumeration, bounded UART health frames, counters, CRCs, and recent timestamps. Use a cheap model only to turn the structured failures into plain language.
- **latency:** Under 5 seconds for a bounded 1-second read from each chip; never wait indefinitely for a port or process.
- **cost:** Negligible API cost; roughly 1–2 seconds of Mac CPU and a few KB of captured UART data per check.
- **security:** Read-only diagnostics only. Never flash, reset, or transmit arbitrary bytes as part of a readiness check. Redact serial payload fields that could contain audio or credentials, retain only counters/error codes and port identity, and include a timestamp so an old healthy result cannot be presented as current.
- **missing:** A real host-side serial reader/parser for the two fixed USB ports (the granted serial diagnostic tool did not resolve; the existing dual_chip_autocapture.sh scripts are the nearest working substrate); A structured local-agent route or typed action that runs the bounded check and returns per-chip status, frame age, CRC/error counters, and port mapping; Firmware diagnostic frames with a stable versioned schema on both chips; A relay/pipeline status event so the pendant can say ready/degraded/offline when the owner asks away from the Mac

### "“Why didn’t that thing I asked from the pendant happen?” Give me one causal timeline across the spoken request, relay delivery, browser or Mac execution, and the final acknowledgment—without making me know a job ID—and tell me the next recoverable action."
- **useful because:** Failures currently fragment across surfaces: a pendant request can be delivered, a browser command can be waiting, and a Mac job can fail or be cancelled while each surface looks locally plausible. The owner needs a human answer (“the Mac never received it”, “the browser was waiting for visual confirmation”, or “it ran and the reply was lost”), plus a safe resume option, not a pile of unrelated logs.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic correlation and state classification first; use a cheap model for the plain-language explanation. Realtime is only needed when the owner asks by voice. Do not resend full transcripts or page contents on every turn.
- **latency:** Initial answer under 2 seconds from durable records; if a live probe is needed, stream a first grounded status within 1 second and finish within 5 seconds.
- **cost:** Usually no model call if a known state maps to a template; roughly $0.001–$0.01 only for ambiguous explanations. Storage is a few hundred bytes per edge, not transcript-sized context.
- **security:** Correlate using opaque request IDs and store hashes/redacted summaries, not audio, cookies, or page text. Never automatically replay a side-effecting action merely because it appears missing; offer resume only for an explicitly idempotent step and preserve the original approval context. Distinguish “not observed” from “failed.”
- **missing:** A single cross-surface correlation ID minted at the pendant edge and propagated through relay, browser command, /execute job, pipeline event, and acknowledgment; A durable causal-edge record with delivery, start, finish, failure, and acknowledgment timestamps plus explicit unknown states; A read-only resolver that joins records without requiring the owner to know job IDs, then emits a resumable next-step descriptor; An exactly-once resume contract for browser and Mac actions, because current job cancellation and retry semantics do not guarantee safe replay

### "“Handle this wherever you can, and keep trying if one of my devices disappears—but never do the same side effect twice. When you’re done, tell me which machine actually did it.”"
- **useful because:** Today the wearable, relay, browser session, and Mac agent are separate execution islands. If the Mac sleeps or the browser loses its session, the owner must know which surface to retry and risks duplicating an email, purchase, upload, or file mutation. A leased, cross-surface handoff would let the system move observation or execution to the only reachable node while preserving one owner-visible operation and an exactly-once side-effect identity.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic lease and idempotency coordinator for routing, retries, and completion; a cheap model classifies whether a task is safely portable between surfaces. Realtime is used only for the final concise spoken outcome.
- **latency:** Detect a lost surface in under 3 seconds; hand off read-only work within 5 seconds. For mutations, wait for a durable lease decision rather than racing, even if that takes 10–20 seconds.
- **cost:** Usually no model call for routing; approximately $0.001–$0.02 when semantic portability classification is needed. The dominant cost is durable coordination state, not inference.
- **security:** A lease must be scoped to one exact intent and action fingerprint, expire conservatively, and be fenced so a late browser or Mac worker cannot perform a superseded mutation. Authentication/session cookies never cross surfaces. The relay stores opaque task IDs and redacted summaries; mutation handoff requires the original authorization context or an explicit new approval. Report “unknown” if completion cannot be proven.
- **missing:** A relay-owned operation ledger that assigns one fencing token/lease to an intent and records observed, claimed, committed, and unknown states across surfaces; Idempotency keys enforced by both /execute and browser commands, with late-result rejection after lease expiry; A portability contract distinguishing observations that may move from side effects that must remain on their original authenticated surface; Heartbeat and lease-loss callbacks from Mac and browser workers, plus a final completion receipt routed to the pendant; A recovery coordinator that can select an alternate surface without automatically replaying non-idempotent work

### "“Keep this task private: use my authenticated browser and Mac, but do not send its contents to the cloud or speak sensitive details aloud. Still tell me whether it succeeded.”"
- **useful because:** The owner currently has no single privacy mode spanning a browser session, Mac execution, relay, and pendant audio. This would make sensitive work usable in real life: local surfaces can act on private material while the relay receives only opaque progress and the pendant gives a redacted outcome.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → dashboard
- **model tier:** A deterministic privacy broker selects local-only versus relay-assisted routes; use no cloud model for private page/file content. A small local model may summarize a result after redaction, but only on the Mac.
- **latency:** Privacy mode should be acknowledged locally in under 300 ms and produce a redacted completion within the normal task latency; never delay execution waiting for a cloud policy decision.
- **cost:** Potentially lower API cost than normal operation because private content is processed locally and only status hashes leave the device. Main cost is local inference and encrypted metadata storage.
- **security:** The mode must be fail-closed: if the local planner, browser bridge, or Mac agent cannot guarantee locality, pause rather than fall back to cloud. Relay events contain opaque IDs, phase, success/failure class, and salted hashes only. Prevent sensitive stdout, screenshots, URLs, page text, filenames, and spoken synthesis from crossing the boundary; show the owner exactly which surfaces are trusted.
- **missing:** A cryptographically enforced locality policy shared by Mac, browser extension, relay, and audio response path; Local redaction and summarization for browser/page/file results before any event is emitted; A pendant-visible private-mode state that survives disconnects and cannot be silently cleared by a stale relay command; A test harness that proves no sensitive fields appear in pipeline events, job receipts, logs, or model requests

### "“Stop every action you started, everywhere, right now.” Pressing the pendant’s emergency control should halt Mac commands, browser commands, and relay work, then tell me what was actually stopped and what may still be running."
- **useful because:** The owner currently has no single physical stop that reaches all execution surfaces. A Mac cancel can be cooperative and a browser command can be elsewhere, leaving uncertainty during an accidental or runaway action. A relay-wide stop fence gives the owner an immediate, embodied way to regain control without finding a screen or remembering a job ID.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Pure deterministic control path—no model call. The relay broadcasts a signed stop epoch; each worker fences new side effects and returns a truthful stop/unknown state. Realtime only speaks the resulting short report.
- **latency:** Local pendant indication under 100 ms; relay fan-out under 500 ms; each surface must acknowledge or declare unreachable within 2 seconds. Never claim a process was killed merely because a cancel signal was sent.
- **cost:** Near-zero API cost; a small durable stop record and one event per connected surface.
- **security:** Require a deliberate physical action distinct from normal recording, authenticate the pendant-to-relay channel, and make the stop epoch monotonic so delayed “execute” messages cannot revive work. Do not erase evidence or undo completed side effects; expose unknown/orphaned processes and preserve audit records.
- **missing:** A relay-wide monotonic stop epoch and signed broadcast consumed by Mac and browser workers; Hard cancellation/kill propagation from the Mac executor to child processes, not merely between sequential steps; Browser command fencing that rejects queued and late results after the stop epoch; A dedicated pendant control/firmware state distinct from the existing conversation and marker buttons; A final cross-surface stop receipt shown on the pendant and dashboard


## Changes it proposed to its own stack

### `model-routing` — Introduce an encrypted, content-addressed context capsule for each active owner task. Mac and browser surfaces keep large page/file/UI evidence locally and publish only a signed schema, digest, redacted claims, and byte-range handles; relay-realtime receives the capsule handle and asks the owning surface for only the exact span needed. Invalidate handles on session logout, browser navigation, or task completion, and make the router choose local retrieval before resending context to a model.
- **owner gets:** Long conversations and browser tasks would stop forgetting what was just established or repeatedly charging the owner to resend the same context. The owner gets faster, more coherent answers while private page and file contents remain on the machine that can actually access them.
- effort: High: define capsule schema and key exchange, add local retrieval endpoints to Mac/browser, teach relay and planners to request spans, add lifecycle invalidation, and test navigation/session changes.  ·  risk: A stale or incorrect capsule could cause the agent to act on old UI state. Every claim needs source surface, capture time, digest, and freshness policy; mutations must re-read the live target. If retrieval fails, report missing evidence rather than hallucinating from the digest.
- cost: Reduces repeated context-token spend substantially for long tasks; adds small local encrypted storage and occasional hashing overhead. No new hardware cost.  ·  latency: First capture adds tens to hundreds of milliseconds; subsequent turns should be faster because only narrow spans cross the model boundary.
- security: Improves data minimization, but compromised local key material could expose capsules. Use per-task keys, OS keychain storage, authenticated handles, and never put raw content in relay logs or job receipts.
- depends on: A relay-to-surface retrieval protocol with signed handles; Browser and Mac local evidence stores that support bounded span reads; Model routing that can declare which capsule fields it actually needs; Lifecycle hooks for browser navigation, logout, Mac sleep, and task completion


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities: (1) a browser task can pause for an exact human decision and notify/retain it on the pendant, (2) a pre-departure dual-chip audio-readiness answer, and (3) a voice-friendly causal explanation joining pendant → relay → browser/Mac execution → acknowledgment without job IDs. I also confirmed the newly granted serial diagnostic schema still has no live implementation: the resolver found no serial/USB capability, so the current practical substrate remains POST /execute with the existing dual-chip capture scripts. The recorder rejected my firmware heartbeat proposal as an existing backlog item, so I did not count it as new.

**Biggest unknown:** The system still lacks a real host-side bounded serial reader/parser and a durable cross-surface correlation/decision state. I still need those implemented capabilities (or a typed local-agent bench-health route and correlation route) before these can be run as first-class owner commands; no further tool rename or serial schema wording will make the unresolved diagnostic grant callable.

