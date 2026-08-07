# Harness derivation — relay-realtime — round 85

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “stay with me while I finish this website task,” have the pendant guide me through the authenticated browser session step by step: read the current page state aloud, let me answer ambiguities by voice, and resume exactly where we left off if the browser or Mac briefly disconnects."
- **useful because:** Today a spoken request can hand off a browser action, but the owner cannot conduct a live, hands-free dialogue over the private browser state or recover gracefully from a dropped Mac/extension link. This would make the wearable a genuine conversational front door to sessions that only the owner’s browser can reach, without requiring the owner to look at the screen for every branch.
- **path:** pendant → relay → browser → mac-planner → dashboard
- **model tier:** Realtime relay model handles short utterances, state summaries, and ambiguity questions; mac-planner handles multi-step planning; a cheaper background worker reconciles checkpoints and reconnects. Do not spend realtime tokens on DOM extraction or long plans.
- **latency:** Speak an acknowledgment within 500 ms; page-state summaries within 2 s; each browser action within 3–8 s. On disconnect, tell the owner immediately and automatically resume from the last verified checkpoint when the link returns.
- **cost:** Roughly $0.01–$0.05 per spoken turn plus browser/relay execution; the dominant cost is repeated page-state summarization and audio, so cache a compact state hash and only resend changed fields.
- **security:** Authenticated page contents leave the browser extension only as narrowly scoped extracted state, not arbitrary screenshots by default. Never read secrets or submit irreversible forms without an explicit spoken request; encrypt checkpoints, expire them quickly, and expose an audit trail in the dashboard. A malicious page must not be able to inject instructions into the spoken dialogue.
- **missing:** A bidirectional relay session protocol with event streaming, turn correlation, cancellation, and reconnect tokens; Browser-extension events for typed page state, focus/selection, action result, and DOM-change checkpoints rather than one-shot command responses; Durable checkpoint storage and a worker/alarm to reconcile interrupted sessions; Mac planner support for yielding a plan one safe step at a time instead of only returning a completed action list; A compact spoken-state renderer and dashboard transcript showing exactly what page data was disclosed

### "After any voice-driven Mac or private-browser task, let me ask “what did you actually do?” and hear a concise, trustworthy chain from my words to each action, the page/app state observed before it, the result afterward, and anything that was skipped or uncertain."
- **useful because:** The owner currently gets either a spoken completion or a queued-job status, not an end-to-end explanation they can audit from the pendant while away from the Mac. This is especially valuable when a private browser session, relay, and Mac planner each transform the request: it exposes silent omissions and makes failures understandable without opening a dashboard.
- **path:** pendant → relay → browser → mac-planner → dashboard → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use deterministic receipt assembly and small summarization on the relay; invoke the expensive realtime model only to answer a follow-up question about the receipt. Perception supplies evidence, judgement labels intent transformations, and action supplies execution receipts.
- **latency:** Basic spoken receipt under 1 s from cached records; detailed evidence under 3 s. Recording is asynchronous and must not delay the original action.
- **cost:** Near-zero additional model cost for structured assembly; $0.002–$0.01 only when a natural-language explanation is requested. Storage and browser evidence retention dominate cost.
- **security:** Receipts may contain sensitive URLs, page text, file paths, or dictated content. Encrypt them, redact tokens/passwords, retain only hashes plus short excerpts by default, and require a fresh button press or authenticated voice session to disclose private-browser evidence aloud. Untrusted page text must be marked as observed data, never treated as agent instructions.
- **missing:** A single immutable execution-trace schema linking voice transcript, planner decision, browser command, Mac action, evidence snapshot, and final result across request IDs; Relay endpoint that can retrieve and summarize a trace by natural-language reference such as “the thing I asked earlier”; Browser and Mac adapters that emit precondition/postcondition evidence and explicit skipped/uncertain outcomes; Retention, redaction, and per-surface privacy labels enforced before traces reach the pendant; Dashboard view that lets the owner replay the exact trace and export it for debugging


## Changes it proposed to its own stack

### `relay` — Implement the granted intent-routing schema as a real relay capability: accept an intent label plus utterance, resolve a target surface (mac-planner vs mac-vision vs browser-harness) using a minimal ruleset and live availability, create a relay job record, and return a jobId. Add a status read path that mirrors relay_job_status and a receipt trail so the user can ask what happened later. Keep the relay’s role conversational: it routes and reports, it does not plan multi-step work itself.
- **owner gets:** The owner can say simple things like “open Notes and remind me tomorrow” and reliably hand it off, then later ask “what happened?” without ambiguity. It reduces misroutes and makes the pendant feel dependable even when the Mac is asleep or busy.
- effort: Medium. Needs a small router module, job record persistence, and integration with existing mac_delegate/mac_run_actions/browser_run_actions calls.  ·  risk: Misrouting or duplicate execution if idempotency is missing. Mitigate with idempotency keys, target availability checks, and receipts. Recovery is to mark the job failed and report the error verbatim to the user.
- cost: Low per call. Main cost is storage of job metadata and occasional status reads.  ·  latency: Tiny routing overhead; most latency remains in downstream planning or browser automation.
- security: Sensitive utterances and targets become job metadata; must be stored with least retention and access controls. Do not log full transcripts unless needed.
- depends on: Durable job records at the relay surface (currently not exposable via a relay capability inventory).; A minimal capability inventory endpoint for the relay so routing can be audited.

### `integration` — Add a relay capability inventory endpoint and publish it to the commons, similar to the Mac agent’s /capabilities. Include routes, tools, and their schemas with versions. This makes the relay surface observable to other agents and prevents repeated proposals caused by unseen endpoints.
- **owner gets:** The system becomes easier to trust. Agents can discover what the relay can do today and stop guessing, which reduces errors and wasted budget, and makes new features ship faster.
- effort: Medium. Requires schema generation, versioning, and a read-only endpoint.  ·  risk: Schema drift if versioning is sloppy. Mitigate with automated checks in CI and a compatibility contract.
- cost: Low. Read-only endpoint; cost is mostly development time and small storage for schemas.  ·  latency: None at runtime; discovery happens out of band.
- security: Inventory could expose sensitive capabilities. Mitigate by redacting secrets and requiring authentication for introspection.


## What it asked for

_Nothing._
## Its own summary

Recorded two owner-facing gaps. First: a resumable, voice-steered conversation over the owner’s authenticated browser task, with typed page-state updates, reconnect checkpoints, and Mac/relay/browser turn correlation. Second: a spoken end-to-end provenance receipt explaining what the owner said, what was observed, which Mac/browser actions ran, what changed, and what was skipped or uncertain. Both explicitly require new connective infrastructure rather than pretending the existing one-shot job and receipt routes already provide it.

**Biggest unknown:** The existing backlog may contain a closely related “pendant steering while Mac work runs” proposal; the recorder flagged similarity. The genuinely unbuilt pieces remain the cross-surface event/trace schema, browser typed state events, reconnectable conversational session, privacy redaction, and durable checkpointing.

