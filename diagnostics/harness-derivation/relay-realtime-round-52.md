# Harness derivation — relay-realtime — round 52

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say "keep an eye on this and tell me if it changes," watch the page and summarize meaningful changes for me."
- **useful because:** The owner can mark a live web page once while wearing the pendant, then get timely, low-noise updates without repeatedly checking a browser themselves.
- **path:** relay → browser → mac-bridge → pendant
- **model tier:** relay for the initial low-latency capture, cheaper background model for change detection and summarization
- **latency:** Fast initial acknowledgement (under a second), then asynchronous updates when changes are detected.
- **cost:** Low per-change if diffing is done on extracted text; dominant cost is occasional background extraction and summarization.
- **security:** May require authenticated pages; must store only what is needed (hashes/diffs), and never leak content to third parties. High-risk pages should require explicit confirmation.
- **missing:** A scheduler or durable alarm mechanism to re-check pages; A browser harness that can run headlessly server-side for authenticated sessions or a secure session handoff; A change classifier that distinguishes meaningful updates from noise (ads, timestamps, counters)

### "“Where did I leave off, and what should I do next?”"
- **useful because:** When the owner is away from the Mac and returns later, the pendant should reconstruct the actual unfinished thread instead of making them remember which voice request, document, tab, or delegated job mattered. It turns scattered state into an actionable spoken checkpoint.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime relay performs intent recognition and a short spoken summary; a cheaper background model builds the cross-surface context card and ranks the next step, with Mac/browser agents supplying typed evidence.
- **latency:** A first spoken acknowledgement within 500 ms; context card assembled within 5 seconds when Mac/browser are reachable, otherwise report exactly which surfaces are stale.
- **cost:** Approximately $0.01–$0.05 per invocation; the dominant cost is the background synthesis of recent transcripts, job receipts, Mac state, and browser evidence, not the short realtime exchange.
- **security:** The result can expose open documents, authenticated tabs, and voice history, so data must remain owner-scoped, redact secrets and page bodies by default, and attach per-item provenance/timestamps. No external sharing or mutation occurs unless the owner explicitly asks for the proposed next action.
- **missing:** A durable cross-surface context-card service joining recent pendant turns, unresolved intents, Mac active-window/document state, browser tab/session state, and queued job receipts; Read-only Mac and browser probes with freshness timestamps and stable correlation IDs; A relay utterance/API that can return a compact spoken checkpoint plus an optional dashboard detail view; Stale-state and conflict detection so the system says when a document/tab/job changed rather than presenting an old answer as current

### "“Check this claim against my open browser pages and Mac files, and tell me exactly where the sources disagree.”"
- **useful because:** The owner currently gets isolated reads or an action plan, not a trustworthy comparison across the browser session and local machine. A contradiction-aware answer prevents the pendant from confidently repeating stale or conflicting information and pinpoints the source that needs attention.
- **path:** pendant → relay → browser → mac-bridge → dashboard
- **model tier:** Realtime relay handles the spoken request and clarification; a cheaper background model extracts dated claims from browser pages and Mac documents, normalizes entities/units, and computes contradictions. Faculty-perception supplies evidence; faculty-judgement explains materiality.
- **latency:** Acknowledge in under 500 ms and provide a short result in 8–15 seconds for up to 10 sources; stream “still checking” status if an authenticated tab or Mac file is slow.
- **cost:** Roughly $0.03–$0.15 per comparison, dominated by fetching and summarizing source contents; use local hashes/excerpts and incremental rechecks to avoid resending unchanged context.
- **security:** Authenticated pages and private files must remain on their respective surfaces or traverse encrypted owner-scoped channels; send only extracted claims when possible. Every statement needs a source URL/path, capture time, and excerpt hash. Never edit a source or send a correction externally without a separate explicit request.
- **missing:** A cross-surface evidence broker that can read selected authenticated tabs and selected Mac files with owner-selected scope; A claim extraction/normalization and contradiction engine handling dates, units, names, and version freshness; Citations and immutable evidence snapshots attached to the spoken answer and dashboard detail; A scope selector usable by voice (for example, “these tabs and the report in Downloads”) plus a way to revoke a source mid-run

### "“Keep working on that across my Mac and browser, and interrupt me on the pendant only when you truly need a decision.”"
- **useful because:** Today a delegated job can finish, fail, or require an unavailable surface, but it cannot carry a precise unresolved question back to the wearer and resume from the answer. This lets the owner stay away from the Mac without either micromanaging or losing the task.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** A cheaper background planner owns the durable task and detects blocked decisions; the realtime relay delivers a brief question and maps the spoken answer to the waiting task. Use the computer-use loop only for the concrete UI step.
- **latency:** Task status can be asynchronous. Once blocked, deliver the question to the pendant within 2 seconds; accept a short answer in one turn and resume execution within 5 seconds after the answer is confidently matched.
- **cost:** About $0.02–$0.10 for each decision point, dominated by planner context and browser/Mac execution; idle waiting should cost essentially nothing through durable storage/alarms.
- **security:** Questions must include the exact task, proposed choices, and affected target so a stray “yes” cannot attach to the wrong job. Keep private page/file content minimized in the notification, expire unanswered questions, and record the answer, decision, and resulting receipt. No approval gate is implied for ordinary reversible work; this is ambiguity handling.
- **missing:** A durable task state machine with WAITING_FOR_OWNER, question ID, answer correlation, expiry, and resume checkpoints; A push path from Mac/browser agents through the relay to the pendant, plus a compact one-button fallback for defer/repeat; Answer matching that requires task/question correlation rather than global conversational context; Planner and computer-use adapters that can checkpoint and resume without replaying already completed mutations; Dashboard controls to inspect, reassign, or cancel outstanding questions


## Changes it proposed to its own stack

### `hardware` — Add a tiny coin vibration motor with a low-side driver and a dedicated wake-capable GPIO to the nRF9160 pendant, plus firmware patterns for question-arrived, task-complete, and link-lost states. Preserve the existing single button and LED as confirmation/fallback controls and enforce a duty-cycle limit so alerts cannot drain the battery.
- **owner gets:** The owner can notice a blocked Mac/browser task or an urgent result while walking, in a meeting, or in a noisy place without the pendant speaking private content aloud or requiring them to stare at the LED. A distinct short vibration can mean “the system needs your answer,” while a double pulse can mean “your task finished.”
- effort: Hardware revision, enclosure/acoustic-mechanical validation, battery profiling, driver and pattern firmware, relay push-event integration, and accessibility testing; medium effort.  ·  risk: Added current draw, motor noise, false alerts, and mechanical wear. Recover by keeping the motor disabled by default until paired, using bounded pulse patterns, retaining LED/audio fallback, and exposing a quiet-hours setting.
- cost: Approximately $1–$4 in component/BOM cost at low volume plus board/enclosure work; roughly 10–80 mA only during a pulse, with negligible average draw under sparse alerts. No per-invocation API cost.  ·  latency: Local alert can begin within tens to hundreds of milliseconds after a relay push, avoiding a speech round-trip.
- security: A vibration conveys only an event class, not private content; however, patterns could reveal that work exists. Keep detailed text/audio behind the button or authenticated voice session and allow the owner to disable patterns in public settings.
- depends on: A durable owner-question/task push protocol with event IDs; Pendant firmware support for a new output and battery-aware alert policy; Relay and dashboard quiet-hours/preferences


## What it asked for

_Nothing._
## Its own summary

Recorded four new owner-facing gaps: a cross-surface “where did I leave off?” context reconstruction, contradiction-aware comparison of authenticated browser evidence with Mac files, durable delegated work that can ask one precisely correlated question and resume from the pendant, and a hardware haptic alert channel for those questions/results. Each includes the missing relay, Mac, browser, storage, protocol, or hardware work rather than pretending today’s stack can do it.

**Biggest unknown:** Whether the existing browser/Mac agents expose sufficiently stable document/tab identities and push connectivity to implement causal context cards and task-question resumption without building new adapters first.

