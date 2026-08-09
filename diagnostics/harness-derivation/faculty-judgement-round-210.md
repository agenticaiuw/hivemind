# Harness derivation — faculty-judgement — round 210

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“What is the one thing I should do next?” and, when I mark a task done or switch context, keep me moving without making me manage a task list."
- **useful because:** The current day plan can describe a day but cannot notice that the owner is actually in a browser, on a call, or stalled. This would turn the pendant into a quiet executive function: one grounded next action, adapted to the owner’s real context, with no parade of notifications.
- **path:** pendant → relay → mac → browser
- **model tier:** Use a cheap background model to rank candidate actions and summarize context; reserve realtime for the spoken answer. A deterministic policy evaluator and attention arbiter decide whether to speak, queue, or do nothing.
- **latency:** Under 2 seconds for a spoken next-action answer; under 10 seconds for a fresh cross-surface context read. Never interrupt merely because the plan changed.
- **cost:** About $0.01–$0.04 per deliberate query; most context reads are local and the expensive model is only used when candidates conflict.
- **security:** Read calendar/mail/browser context only through existing least-privilege surfaces; never speak message contents by default. Any external or destructive action remains draft/physical-confirmation gated. Store only action IDs, state transitions, and short redacted rationales, not page bodies.
- **missing:** A live Mac route exposing owner-presence/foreground context without requiring Accessibility; A durable candidate/action state that joins a pendant marker to Mac and browser observations; A completion signal for actions that were done outside this system; An owner-configurable policy for work hours, interruption budget, and what counts as progress

### "“Tell me only when a news story I already heard has materially changed, and say exactly what changed and which source supports it.”"
- **useful because:** A news brief becomes trustworthy when it can correct itself instead of endlessly repeating a first snapshot. The owner gets fewer interruptions, explicit old-versus-new claims, and a correction trail rather than silently stale headlines.
- **path:** relay → browser → pendant → mac
- **model tier:** Use a cheap scheduled/background model to fetch and cluster public sources; use a stronger model only to adjudicate whether two versions are materially different. Realtime only speaks an approved correction when attention policy allows.
- **latency:** Background polling can run hourly or on a user-set cadence. A correction should be prepared within 15 minutes of a source change and spoken only in the next allowed briefing window unless urgent.
- **cost:** Roughly $0.02–$0.10 per monitored story per day, dominated by source retrieval and claim comparison; deduplication keeps stable stories cheap.
- **security:** Public-source URLs and extracted claims leave the device; private browser sessions must never be used for public-news monitoring unless explicitly selected. Every spoken correction includes source names and uncertainty. No automatic reposting or messaging.
- **missing:** A durable claim record with source URL, observed timestamp, claim hash, confidence, and supersession link; A scheduler/worker that re-fetches selected public sources and expires abandoned stories; A material-change threshold and owner setting for which topics may interrupt; A compact spoken correction renderer that can cite two independent sources

### "“When I press the marker button, remember what I was switching away from; later tell me where I left off and what the next small step was.”"
- **useful because:** A context switch is where intentions disappear. One press should create a durable, private handoff between the worn device, the Mac, and the authenticated browser without requiring the owner to dictate a note or reconstruct tabs later.
- **path:** pendant → mac → browser → relay
- **model tier:** Use deterministic capture and local metadata first; a cheap model compresses the observed app/tab/calendar state into a one-sentence handoff. Realtime is used only when the owner asks to hear the handoff.
- **latency:** Marker acknowledgement under 500 ms locally; Mac/browser enrichment within 5 seconds when online; offline markers sync and enrich on reconnect.
- **cost:** Usually under $0.01 per marker; model cost is only for compression, and no model call is needed for a marker with no online context.
- **security:** Persist opaque IDs, app names, URLs, and short redacted titles—not page bodies, form fields, or secrets. Authenticated pages require explicit allowlisting and provenance. Handoff deletion must revoke derived summaries and avoid retaining raw browser text.
- **missing:** A production writer for the already-granted offline_moment_bookmark payload; A cross-surface join from the marker ID to Mac job/browser command IDs; A readback route that can enrich a marker later without copying private page contents; A deletion cascade for derived handoff summaries

### "“Notice the workflows I keep struggling through, figure out the smallest safe improvement, and show me the change before you make it.”"
- **useful because:** The system can execute individual Mac and browser steps, but the owner still pays the recurring cost of badly designed personal workflows. This capability turns repeated friction—reopening the same pages, copying the same fields, recovering from the same failure—into a reviewable improvement rather than another reminder or generic automation.
- **path:** pendant → relay → mac → browser
- **model tier:** A background model clusters action receipts and failure traces; a stronger model is used only to infer a proposed workflow change. Realtime speaks a short proposal, while deterministic policy and physical approval gate any mutation.
- **latency:** Observe passively; produce a proposal after three or more comparable friction episodes or on explicit request. Proposal generation may take 30 seconds, but applying it must remain an explicit owner action.
- **cost:** Approximately $0.05–$0.25 per proposal, dominated by summarizing several traces; routine clustering is local and inexpensive.
- **security:** Logs must be reduced to action types, domains, and outcomes before model use. Never infer or retain form values, credentials, private message bodies, or page screenshots. Proposed automations must be least-privilege, reversible, and previewed step by step.
- **missing:** A durable cross-surface action-trace join rather than separate relay, Mac, and browser IDs; A friction classifier that distinguishes owner error, network failure, and product/UI change; A safe workflow-diff format with replay tests and rollback; A review surface where the owner can accept, reject, or permanently suppress a proposed improvement

### "“When my surroundings make speech hard, adapt the conversation automatically—shorter replies, stronger repetition, or a visual handoff—and return to normal when it is safe.”"
- **useful because:** A wearable assistant that speaks identically in a quiet room, on a street, and beside a running machine is unusable exactly when the owner needs it. This would make the interaction resilient to acoustic conditions without requiring the owner to repeatedly manage settings.
- **path:** pendant → relay → mac → browser
- **model tier:** Use local signal metrics and deterministic thresholds for noise, packet loss, underruns, and owner barge-in. Use the realtime model only to reformulate the current response; no background model is needed.
- **latency:** Adapt within one utterance boundary, under 500 ms after a reliable local signal. Never wait for a cloud classification to protect intelligibility.
- **cost:** Near-zero additional API cost when selecting a shorter rendering; occasional reformulation costs under $0.01 per affected turn.
- **security:** Acoustic metrics, not raw microphone audio, should leave the pendant. The system must not claim to know whether bystanders are present. Sensitive content remains suppressed under the existing disclosure policy even when repetition is requested.
- **missing:** A signed audio-quality and acoustic-context signal from the pendant delivery telemetry; A shared response-rendering contract supporting concise, repeated, screen-readable, and deferred variants; Mac/browser visual fallback that is addressable by the same utterance/item ID; A hysteresis policy so noisy conditions do not cause rapid mode oscillation

### "“Give me a private rehearsal before I have a consequential conversation: what am I trying to achieve, what am I conceding, and what should I not accidentally promise?”"
- **useful because:** The owner currently gets help executing messages and browser tasks, but not a structured pause before a high-stakes conversation. A rehearsal can expose ambiguity and accidental commitments while there is still time to change course, without sending anything or pretending to know the other person’s intent.
- **path:** pendant → relay → mac → browser
- **model tier:** A stronger reasoning model prepares the rehearsal from owner-provided goals and explicitly selected source material; a cheaper model compresses it into a spoken practice card. Realtime is used for interactive rehearsal only.
- **latency:** Initial rehearsal in under 15 seconds; follow-up turns conversational. No unsolicited interruption—only on explicit request or a user-created preparation trigger.
- **cost:** Approximately $0.05–$0.30 per rehearsal depending on source length and adversarial scenarios; raw sources should be locally filtered first.
- **security:** This is highly sensitive interpersonal material. Default to owner-provided text and metadata, not autonomous mailbox scanning. Never send, save, or share rehearsal output without confirmation. Store only an expiry-bound summary and provenance references, with an immediate discard option.
- **missing:** A high-stakes conversation preparation mode distinct from mail triage or message drafting; A source-selection and redaction UI that lets the owner choose exactly which messages/pages are included; A structured rehearsal schema for goals, boundaries, concessions, uncertainties, and forbidden promises; A short-TTL private workspace with explicit discard and provenance explanation


## What it asked for

_Nothing._
