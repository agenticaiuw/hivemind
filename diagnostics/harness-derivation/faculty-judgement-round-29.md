# Harness derivation — faculty-judgement — round 29

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Don’t let me drop the promises I make.”"
- **useful because:** During ordinary pendant conversations, commitments disappear into memory. The system should turn an explicit promise into a small, reviewable follow-through loop: identify who/what/when, ask only when ambiguity matters, detect evidence of completion across calendar, mail, files, and authenticated browser pages, and nudge once at the right time. The owner gets closure rather than another task list.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** Realtime only for extracting a candidate commitment from the live utterance and asking a one-sentence clarification. A cheaper background model classifies commitment type, proposes due windows, and reconciles completion evidence; deterministic rules handle reminders, confidence thresholds, and state transitions.
- **latency:** Candidate extraction under 500 ms after the utterance; clarification in the next spoken turn. Background reconciliation every 6 hours and on relevant Mac/browser receipts. A reminder should take under 2 seconds to enqueue and be delivered when the pendant is reachable.
- **cost:** Roughly $0.01–$0.05 per commitment lifecycle, dominated by background reconciliation and authenticated-page reads; ordinary conversations incur only a small realtime extraction call. Avoid polling by triggering checks from receipts, changed-page watches, and calendar events.
- **security:** Commitments may contain sensitive people, health, work, or financial details. Store the minimum structured fields plus encrypted source pointers, separate secrets from text, and show provenance when a completion claim is made. Never send mail, submit forms, or alter external records automatically; creating a private reminder is allowed under the owner's stated policy. Require confirmation before sharing a commitment with anyone or inferring completion from ambiguous evidence.
- **missing:** A durable commitment entity with source span, owner/other party, due window, confidence, sensitivity, and lifecycle state; Cross-surface evidence adapters for calendar/mail/files/browser receipts with strict observed-vs-inferred completion states; A deduplicating reminder policy tied to pendant availability, quiet hours, and the owner's one-short-sentence preference; A review UI/audio affordance for correcting, snoozing, or resolving a commitment

### "“Before I commit to this, tell me what it will collide with—and help me make room if I still want it.”"
- **useful because:** Today the owner can ask for calendar or mail information, but cannot get a consequence-aware answer before making a promise. The system should combine the spoken intention with existing calendar commitments, travel, active browser workflows, unfinished Mac work, and the owner's normal time/energy patterns; identify the actual collision, quantify uncertainty, and offer a reversible plan or a prepared renegotiation draft. It should distinguish a hard conflict from a merely busy day and never silently reschedule anything.
- **path:** pendant → relay-realtime → unified → mac-planner → browser-extension → dashboard
- **model tier:** Realtime model extracts the proposed commitment and gives a short collision summary. A cheaper background planner computes availability, travel buffers, dependencies, and workload scenarios; deterministic policy enforces quiet hours, confirmation, and no-write defaults.
- **latency:** Initial answer in 1–2 seconds for known calendar/work items; deeper cross-account analysis may arrive asynchronously as a cited follow-up. Drafting a reschedule or message should take under 10 seconds, but sending or changing appointments always waits for confirmation.
- **cost:** About $0.02–$0.10 per analysis, dominated by cross-surface retrieval and one background planning pass; cache stable calendar and workflow facts and recompute only affected windows.
- **security:** This joins highly sensitive schedule, work, browser, and possibly health-like routine data. Keep the computation in the owner-scoped context projection, expose which sources caused each collision, redact unrelated private details, and never contact another person or alter a calendar without explicit approval. Do not infer availability from silence; report unknown when a surface is offline.
- **missing:** A typed cross-surface obligation/dependency and time-window model, distinct from a simple task list; A planner that reasons about travel/buffers, hard versus soft conflicts, uncertainty, and recovery options; Read-only adapters for calendar, Mac work state, browser jobs, and pending commitments with freshness/permission metadata; A confirmation-gated draft/reschedule workbench with a concise pendant explanation and cited dashboard detail


## Changes it proposed to its own stack

### `integration` — Add a Commitment Closure Graph spanning relay, Mac planner, browser bridge, and pendant delivery. On-device/relay extraction creates an immutable candidate event; a background worker canonicalizes it into a commitment entity and links only typed evidence (calendar event, sent message receipt, file change, browser transaction receipt). Each edge carries observed/inferred/contradicted, source, timestamp, and expiry. A deterministic reducer moves it through proposed → accepted → due → evidence_found → owner_confirmed/expired, with idempotent event IDs and a single pending reminder. Dashboard and pendant expose a compact correction action ('done', 'not that', 'snooze').
- **owner gets:** The owner can trust that “I said I’d do it” will not become invisible, while avoiding false claims that a file edit or page visit means the promise was fulfilled. It turns scattered activity into closure with one calm reminder instead of repeated nagging.
- effort: Medium-high: schema, event reducer, four evidence adapters, encrypted source pointers, reminder policy, and pendant/dashboard affordances; test with disconnected Mac/browser and duplicate receipts.  ·  risk: False-positive completion or reminder fatigue. Mitigate by never auto-closing on weak evidence, requiring owner confirmation for socially consequential commitments, expiring stale evidence, and making every state reversible. If a surface is offline, retain proposed/due state and say unknown rather than failed or done.
- cost: Small persistent storage and one background classification call per new commitment plus event-triggered reconciliation; substantially cheaper than periodic full account scans. No new hardware cost.  ·  latency: Live extraction adds <500 ms and does not block the response; closure updates are asynchronous. Pendant reminder delivery is next-connectivity, with no repeated network polling.
- security: Sensitive commitment text stays encrypted with least-privilege adapters; browser evidence is reduced to hashes/snippets and tab/session provenance. External side effects remain confirmation-gated.
- depends on: durable cross-surface event/persistence primitives; authenticated browser and Mac receipt streams; owner-approved reminder and quiet-hour policy; 24 kHz audio queue for concise pendant prompts


## What it asked for

_Nothing._
## Its own summary

Discovered the owner's durable preferences and live device inventory, then added a genuinely new cross-surface capability: commitment closure. The pendant/relay extracts promises from normal speech; background agents reconcile calendar, mail, files, and authenticated-browser receipts; deterministic state prevents ambiguous activity from being treated as completion; the pendant gives one concise, snoozable reminder. I also proposed the Commitment Closure Graph needed to make that reliable and told mac-vision the known action policy and current readiness blockers.

**Biggest unknown:** The implementation still lacks the durable cross-surface event/persistence primitives and the owner's pending audio acceptance criteria. Operationally, Mac Accessibility and Screen Recording remain disabled and the browser bridge is offline with three queued commands, so evidence reconciliation and GUI execution cannot yet be trusted.

