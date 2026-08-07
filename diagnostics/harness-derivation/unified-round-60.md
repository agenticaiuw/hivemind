# Harness derivation — unified — round 60

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac/browser observation trust** — Live /ops/status reports permissions.ready=false because Accessibility trusted=false and Screen Recording granted=false; browser extension home-chrome is offline with 5 pending commands. Any GUI or authenticated-page evidence must be treated as unavailable until the exact AI Pendant Agent identity receives TCC grants and the extension heartbeats.
  - evidence: GET /ops/status HTTP 200 at 2026-08-07 round 60; faculty-perception corroborating /observe and browser status.

## Capabilities it proposed

### "When I say “mark this for later” during a conversation, save the exact moment and context, then when my Mac/browser is available turn it into a review card with the relevant page or app, a concise summary, and a suggested next step—without acting until I approve."
- **useful because:** The pendant is present at the moment an idea or obligation occurs, while the Mac/browser may be unavailable. This creates reliable continuity instead of losing the thought or pretending a stale screen was seen. It only becomes an actionable draft after the private machine reconnects.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** gpt-realtime-2.1 only for the short capture acknowledgement and intent slotting; a cheaper background model on the relay summarizes and correlates context; mac-planner/browser-extension resolve the app or authenticated tab when online.
- **latency:** Acknowledge the capture in under 500 ms; background card enrichment within 30–90 s after Mac/browser heartbeat. No waiting on the live voice turn for private-page inspection.
- **cost:** About $0.01–$0.04 per captured item, dominated by transcription/context summarization; correlation and dashboard rendering are local/relay work.
- **security:** Audio and transcript leave the pendant to the relay. Secret-looking content must be redacted or marked private and never copied into the card by default. Authenticated page reads remain on the Mac/browser bridge; no send/submit action is allowed. Require explicit approval before creating reminders, sending messages, or changing a page.
- **missing:** A durable capture record with audio/time/active-conversation linkage and an idempotency key; A reconnect correlator that joins a capture to the next valid Mac/browser session and emits evidence citations; A review-card schema and dashboard queue with approve/edit/discard states; A local pendant failure spool and delivery receipt for captures made during LTE loss

### "When I press the pendant during a conversation and say “look that up,” use the few seconds immediately before the press to identify the person, product, place, or term being discussed, then quietly tell me what it is through my earpiece. If the answer depends on one of my private accounts, use the Mac/browser session and clearly label that source; otherwise use public research. Do not continuously record or save the surrounding conversation."
- **useful because:** It gives the owner an on-demand memory and research aid in the moment—at a meeting, store, lecture, or social conversation—without requiring them to repeat a name or pull out a phone. It uniquely combines a local wearable audio moment, low-latency relay interpretation, public research, and private browser reach.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime model only to detect the explicit trigger and extract a short candidate term. Use a cheaper background model for disambiguation and summarization. Use the Mac/browser only when private context is required or explicitly requested.
- **latency:** Trigger acknowledgement under 400 ms; public answer in 3–8 seconds; private-account lookup in 10–20 seconds. If confidence is low, ask one concise clarification rather than guessing.
- **cost:** Approximately $0.01–$0.06 per lookup, dominated by audio transcription and any background research; most routing and buffering are local or relay-side.
- **security:** The device must maintain only a short encrypted pre-trigger ring buffer and discard it after extraction or a short TTL. Never upload ambient audio without the explicit button press and trigger. Private-page content must be source-labelled, excluded from general memory by default, and never lead to an account mutation. Require a visible/spoken privacy acknowledgement when private lookup is selected.
- **missing:** A firmware-side encrypted pre-trigger audio ring buffer with strict byte/TTL limits and a button-triggered upload window; A relay endpoint that accepts the pre-trigger clip, trigger transcript, confidence, and deletion deadline as one idempotent request; A disambiguation/research orchestrator that can choose web_search versus an authenticated browser read and return citations to the earpiece; A private-source policy and dashboard setting controlling whether lookup transcripts may be retained


## Changes it proposed to its own stack

### `integration` — Add a hard “perception validity” envelope to every Mac/browser observation and action receipt. Before any GUI or authenticated-page task is planned, require /ops/status permissions.ready plus browser heartbeat/session freshness; if accessibility, screen recording, or extension polling is missing, return a typed unavailable state with the exact missing prerequisite and preserve the user request as a pending review item. Never let a failed observation be summarized as if it were current evidence.
- **owner gets:** The owner gets honest answers and recoverable pending work instead of an apparently successful automation based on an untrusted screen or an offline browser. Once permissions or the extension recover, the same request can resume with fresh evidence.
- effort: Medium: shared receipt schema, planner preflight, relay status propagation, dashboard state, and tests for stale/offline/permission-denied cases.  ·  risk: Some tasks will stop where they previously attempted best-effort execution; recover by offering a pendant acknowledgement and resumable queue. Avoid deadlocks with a TTL and explicit discard.
- cost: Negligible API cost; mostly local validation and a few status calls.  ·  latency: Adds roughly 50–200 ms for cached readiness, with no model call.
- security: Improves security by preventing actions or claims from untrusted GUI state; exposes only capability status, not page contents.
- depends on: macOS Accessibility and Screen Recording grant for the actual AI Pendant Agent identity; Browser extension heartbeat/reconnect behavior; Typed action receipts and durable job status


## What it asked for

_Nothing._
