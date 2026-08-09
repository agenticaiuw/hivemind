# Harness derivation — faculty-perception — round 186

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac permissions and bridge health** — As of 2026-08-08T22:20Z, the live Mac snapshot reports AI Pendant Agent accessibility=true, screenRecording=true, requiredMissing=[], ready=true; browser extension online with 2 devices and zero pending commands; relay reachable and Mac bridge online. This supersedes the older denied-permission context.
  - evidence: read_continuity_snapshot include=['relay'] resolved to GET /ops/snapshot HTTP 200; status.permissions and status.browser/relay payload.
- **voice delivery reality** — Recent pipeline runs can render 24 kHz PCM successfully but still fail before relay result reporting; the live trace explicitly says heard=unknown and provesPlayback=false because no device_playback event exists. One run rendered 471,820 PCM bytes then failed reporting bridge work result with HTTP 500.
  - evidence: read_continuity_snapshot include=['pipeline'] resolved to GET /pipeline HTTP 200; first run job_560f7a08... events and delivery object.
- **vision preflight** — GET /vision-loop/preflight is now live and ready in accessibility mode for bundle com.aipendant.agent at the expected app and node paths; this is no longer blocked by TCC.
  - evidence: describe GET /vision-loop/preflight liveResponse HTTP 200, status=ready, checkedAt=2026-08-08T22:21:18Z, mode=accessibility.

## Capabilities it proposed

### "When you answer me, make sure I actually get it. If delivery fails anywhere, recover automatically and tell me exactly whether it reached the pendant, played, or is still unheard."
- **useful because:** The live trace shows the system can render 24 kHz audio and still fail reporting bridge work with HTTP 500; today 'completed' is not hearing. This would turn silent failures into recovery instead of lost conversations.
- **path:** relay-realtime → mac-planner → relay → pendant → unified
- **model tier:** Realtime only for the spoken answer; a cheap background watchdog classifies transport failures and schedules retry.
- **latency:** Initial speech remains realtime; detect failure within 2 seconds, retry within 5 seconds, and give a short status sentence only if recovery is needed.
- **cost:** Usually one realtime turn; retries are mostly transport and cached PCM, under $0.01 incremental API cost. Dominant cost is duplicate TTS only when PCM is unavailable.
- **security:** Audio and delivery receipts cross relay and Mac; bind every retry to an opaque artifact ID and device-originated playback events. Require confirmation before repeatedly speaking after an interruption.
- **missing:** Fix the observed POST /v1/bridge/work/:jobId/result 500 path; Use the accepted bounded playback ledger and make the firmware emit its played/interrupted event with the artifact ID; A relay-side retry state machine that distinguishes Mac-rendered, relay-accepted, device-received, playback-started, and playback-finished

### "Give me a morning briefing I can trust: show which browser sources you used, flag contradictions or stale pages, summarize them, and speak it only after the evidence is captured."
- **useful because:** The current relay browser reader returns untrusted text without an ID or hash, while the Mac already has content-addressed evidence capsules. This would make spoken news or shopping briefings inspectable instead of unverifiable prose.
- **path:** browser-extension → mac-planner → relay-realtime → relay → pendant
- **model tier:** Use a cheaper background model for source extraction, hashing, deduplication, and contradiction clustering; use realtime only to answer the owner's follow-up.
- **latency:** Capture and cluster within 10 seconds for a routine briefing; spoken response starts after the first reliable evidence set, with late sources clearly marked.
- **cost:** 2–6 browser reads and one small background synthesis, roughly $0.02–$0.10 depending on page count; no extra realtime call for routine generation.
- **security:** Never persist raw login pages or secrets; redact before capsule storage, retain URL/hash/provenance separately, and require confirmation before acting on a page-derived instruction.
- **missing:** Relay read_web_page must return a stable ID and content hash, then bridge that result to the existing Mac mintCapsule store; Mount the existing browser provenance routes and attach capsule IDs to the routine run and spoken artifact; A contradiction/staleness evaluator that refuses to present one source as fact when hashes or timestamps disagree

### "Do the task I describe on my screen, then tell me in one sentence what changed and let me ask the pendant to undo it if the result is wrong."
- **useful because:** Accessibility and Screen Recording are now live for the exact AI Pendant Agent binary, so the vision loop can finally inspect and act on the owner's real UI rather than stopping at a permission error. The owner gets an auditable result, not blind clicking.
- **path:** mac-vision → browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use the cheaper local planner/vision loop for observation and reversible actions; reserve realtime for concise confirmation and clarification.
- **latency:** Observe in under 2 seconds, perform reversible 1–3 step actions within 8 seconds, and speak the result immediately; complex workflows delegate locally.
- **cost:** Usually no external model cost for high-level actions; vision-heavy tasks may cost $0.01–$0.05. Browser actions and AppleScript dominate latency.
- **security:** Require confirmation for irreversible sends, purchases, deletes, or external messages. Record before/after state and a restore token; redact screen regions containing secrets from relay logs.
- **missing:** Wire the now-ready permission probe into vision-loop preflight instead of treating this machine as blocked; Expose a single owner-facing receipt that joins Mac action ledger, browser command result, and undo capability; A pendant command/receipt path that can request undo without pretending speech delivery proves the action

### "Keep my private information from crossing the wrong boundary. Before anything from my browser, Mac, or voice reaches the relay or an external site, warn me about secrets and let me approve a redacted version once for this task."
- **useful because:** Today browser sessions, Mac automation, relay voice, and durable logs have different trust boundaries, but the owner has no single moment where he can see or control what leaves each one. A wearable confirmation plus automatic redaction would make powerful automation safe enough for daily use.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → pendant
- **model tier:** A local deterministic classifier handles known secret patterns and previously approved fields; use a cheap background model only for ambiguous semantic identifiers. Realtime speaks the short approval request.
- **latency:** Known patterns under 150 ms; ambiguous content under 2 seconds; never block ordinary non-sensitive actions.
- **cost:** Near-zero for deterministic redaction; occasional classification under $0.01 per approval. Storage and hashing dominate, not model calls.
- **security:** The classifier must run before relay logging and must fail closed for credentials, payment data, health data, and private messages. Store only redaction metadata and an expiring approval token; require fresh confirmation for a new destination or changed content.
- **missing:** A single cross-surface data-egress policy engine that runs before browser commands, Mac actions, relay tool calls, and logs; A pendant-originated approval token bound to task, destination, fields, and expiry; A way for the owner to inspect and revoke active approvals from the wearable

### "Watch a time-sensitive opportunity for me—like a price drop, appointment opening, or expiring reservation—and, when the exact condition is met, ask me on the pendant and complete the purchase or booking before it disappears."
- **useful because:** The browser can hold authenticated sessions and the Mac can act, but today they do not form a durable, owner-approved conditional agent. This would turn a spoken intention into useful action while the owner is away, without granting an unlimited standing mandate.
- **path:** browser-extension → mac-planner → relay-realtime → mac-vision → pendant
- **model tier:** Use a cheap scheduled/background model for polling and condition evaluation; use realtime only for the final pendant confirmation. Browser and Mac action execution remain deterministic where possible.
- **latency:** Poll on a user-selected cadence, wake within 30 seconds of a match, and finish a confirmed action within 10 seconds when the site is responsive.
- **cost:** Usually cents per day for scheduled checks; browser sessions and page loads dominate. Realtime costs only on a true match.
- **security:** Never store passwords or payment details in the relay. Bind each watcher to one domain, one maximum amount, one expiration, and one action; require fresh confirmation immediately before irreversible purchase or booking. Abort on page-shape or price mismatch.
- **missing:** Durable watcher records and scheduler leases spanning relay sleep and Mac offline periods; A browser-side condition evaluator that can prove the observed price/slot and detect page changes; A pendant confirmation protocol with a short expiry and an idempotent action receipt

### "When I lose connection or switch between speaking to the pendant and working at my Mac, continue the same thought without making me repeat it: tell me what was heard, what was decided, what remains unsent, and let me resume with one phrase."
- **useful because:** The system has separate voice sessions, Mac jobs, browser commands, and relay state. A dropped link currently leaves the owner to guess whether an instruction ran, while a resumed conversation has no compact, trustworthy handoff. This would make the hive feel like one persistent assistant rather than disconnected surfaces.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use a small background summarizer to maintain a bounded task handoff; realtime only interprets the owner's resume phrase and speaks the compact status.
- **latency:** Write a handoff under 1 second on every state transition; resume status in under 2 seconds after reconnect.
- **cost:** A few hundred tokens per transition, typically below $0.01 per interrupted task; the expensive part is durable conflict reconciliation, not generation.
- **security:** Handoffs must be encrypted and scoped to the owner's session, with sensitive browser text represented by capsule IDs rather than copied into relay summaries. Never infer completion from Mac execution alone; expose unknown explicitly.
- **missing:** A cross-surface task identity and causal event log joining relay turns, Mac jobs, browser commands, and pendant sequence numbers; Conflict resolution when both Mac and relay act while disconnected; A resume route that returns a bounded handoff with explicit states: heard, planned, executed, delivered, unknown


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the exact AI Pendant Agent now has Accessibility and Screen Recording, vision preflight is ready, browser extension has two online devices, and relay/Mac bridge are reachable. A recent run rendered 24 kHz PCM but failed bridge-result reporting with HTTP 500; playback remains unknown. Recorded three owner-facing capabilities: closed-loop delivery recovery with real playback state, evidence-backed source-grounded briefings, and permission-enabled reversible screen tasks with undo receipts. Sent the state change to all agents.

**Biggest unknown:** Whether the physical nRF9160 pendant is connected/registered and can emit the accepted playback ledger events; until that exists, no pipeline can establish that the owner heard audio.

