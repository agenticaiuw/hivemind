# Harness derivation — relay-realtime — round 102

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Route this to my Mac and tell me when it’s done."
- **useful because:** It turns spoken intent into a consistent, low-latency handoff and status loop. The owner doesn’t have to remember which agent does what; they just speak, and the system routes and reports back reliably.
- **path:** relay → mac-bridge → mac-planner → faculty-action
- **model tier:** Realtime for intent capture; cheaper planner model for multi-step execution on the Mac; relay uses stored receipts for status.
- **latency:** Fast initial acknowledgement (sub-second) from the relay; longer execution happens on the Mac and can be summarized when receipts arrive.
- **cost:** Low per utterance at the relay; main cost is downstream planning/execution tokens and any receipts stored.
- **security:** Must not fabricate completion. Status must come from receipts/records. Avoid leaking sensitive context across sessions; only pass what’s needed.
- **missing:** relay_route_intent implementation; durable job runner / receipts pipeline wired end-to-end

### "Let me say “move this to my Mac” (or “bring it back to the pendant”) and continue the same conversation on the other device, without repeating the request or losing the in-progress task."
- **useful because:** The pendant is the always-with-owner front door, but the Mac has a screen, keyboard, and richer audio. Today a wearer must start over when they reach the Mac; seamless migration would make spoken work survive the physical transition between away-from-desk and desk contexts.
- **path:** pendant → relay-realtime → mac-planner → mac-vision
- **model tier:** Realtime relay performs the short handoff utterance, session-state packaging, and spoken/LED acknowledgment. mac-planner resumes the task and mac-vision can provide the Mac UI/audio endpoint; do not spend the expensive realtime tier on the continued desktop task.
- **latency:** Acknowledge the handoff on the pendant within 500 ms; establish the Mac endpoint and restore context within 3 seconds. If the Mac is offline, keep the pendant session active and report that it is waiting rather than silently dropping it.
- **cost:** One short realtime turn for intent detection and acknowledgment (roughly $0.01–$0.05 depending on audio duration), then ordinary planner/computer-use costs. The dominant cost is transferring enough recent transcript/task state, not the handoff phrase.
- **security:** The relay must bind the destination to the owner’s authenticated paired Mac, never an arbitrary nearby device, and expire handoff tokens. The transferred bundle should include only the active conversation and task state, with explicit indication of any browser session or private content being made available on the Mac. Returning to the pendant must not speak sensitive screen contents aloud without the owner asking.
- **missing:** A first-class session-migration protocol with resumable conversation/task checkpoints and endpoint identity; Mac audio ingress/egress or a clear UI takeover surface; current pipeline audio/events routes are not a migration contract; Pendant-side handoff acknowledgment and reconnect behavior in firmware; A state model that distinguishes active speech, queued Mac work, and completed receipts

### "If something I asked the system to do is still running, let me press the pendant button once and say “stop” (or press twice) to halt that specific operation immediately, then tell me what was stopped and what had already happened."
- **useful because:** A wearer may notice a mistake or unexpected side effect before a Mac/browser job finishes, while unable to reach the computer. Existing receipts or undo-after-completion are too late; a physical interrupt is the only dependable emergency control when voice, screen, or LTE timing is poor.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension
- **model tier:** No model should be required to recognize the double-press locally. Relay maps the authenticated interrupt to a job; downstream Mac/browser workers cancel cooperatively. Realtime is used only to explain the resulting receipt if speech is available.
- **latency:** Local LED acknowledgment immediately; relay cancellation request within 1 second of uplink; downstream workers must check cancellation between every action and report partial completion within 3 seconds. If disconnected, the pendant must retain the interrupt until it reconnects and must not claim success prematurely.
- **cost:** Negligible model cost for the interrupt; a small relay/worker implementation. Any later spoken explanation is one short realtime turn. Engineering cost is cancellation propagation and safe cleanup, not inference.
- **security:** Only the paired pendant and its current authenticated session may cancel jobs belonging to the owner; cancellation must never be a generic broadcast. Persist an immutable record of the interrupt, cancellation acknowledgment, and actions already executed. Stopping must not be implemented as an unsafe forced kill that corrupts files or transactions; workers need cooperative checkpoints and cleanup.
- **missing:** A pendant firmware double-press/interrupt event with offline latch and LED state; A relay cancellation endpoint and durable per-job cancellation state/idempotency; Cancellation propagation and checkpoints in mac-planner, mac-vision, and browser-extension workers; A typed partial-action receipt that distinguishes stopped, completed-before-stop, and unable-to-stop work


## Changes it proposed to its own stack

### `relay` — Implement relay_route_intent as the explicit routing entry point: normalize the utterance, select target agent (mac-planner vs browser when available), create a relay job record, and forward via existing plan/execute routes. Store a concise spoken acknowledgement immediately, then update with receipts as they arrive.
- **owner gets:** They can speak a command and get an immediate, consistent acknowledgement, plus a truthful follow-up about progress or failure, without the relay inventing status.
- effort: Medium: define a minimal intent envelope, map to existing downstream routes, and wire job bookkeeping to receipts.  ·  risk: Misrouting is the biggest risk. Mitigate with conservative defaults, fall back to mac_delegate for ambiguous tasks, and allow the owner to say "no, I meant…" to re-route.
- cost: Small runtime cost per utterance; main cost is storage of job records and receipts.  ·  latency: Improves perceived latency with immediate acknowledgement; downstream execution unchanged.
- security: Must minimize context passed; job records should avoid storing sensitive content beyond what’s needed for routing.
- depends on: durable job runner or equivalent storage for job records and receipts

### `integration` — Wire a durable job runner (or equivalent) so relay-created jobs can persist, retry, and deliver receipts even if the Mac is offline when the command is spoken. Use a single job id across relay, planner, executor, and receipts.
- **owner gets:** Commands spoken on the go don’t vanish. If the Mac is asleep, the task waits and runs later; the owner still gets a coherent status story.
- effort: High: needs a durable queue, retry semantics, idempotency keys, and receipt fan-in.  ·  risk: Duplicate execution if idempotency is wrong; mitigate with idempotency keys and executor-side de-dup.
- cost: Adds storage and compute cost for queue and retries; but reduces wasted re-tries by the owner.  ·  latency: No change for immediate tasks; big improvement for resilience when devices are offline.
- security: Stored jobs/receipts contain user content; encrypt at rest and restrict access by device/session.
- depends on: a stateful store (Durable Object or equivalent); receipt schema agreed across surfaces


## What it asked for

_Nothing._
## Its own summary

Recorded two owner-facing gaps. (1) Seamless “move this to my Mac / bring it back to the pendant” session migration, preserving active conversation and task state across pendant, relay, Mac planner/vision, and browser context. (2) A physical pendant emergency interrupt for in-flight Mac/browser jobs, with relay cancellation, cooperative downstream checkpoints, and a truthful partial-action receipt. Both require new connective protocols despite relevant individual routes already existing.

**Biggest unknown:** Whether the existing Mac audio surface can be extended for live endpoint takeover, and which downstream workers can currently checkpoint and cancel safely; I did not discover further this round per instruction.

