# Harness derivation — mac-planner — round 68

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Finish the thing I started earlier, and tell me only if you’re blocked.” The system should reconcile my pending Mac and browser work, resume safe steps when the right surface returns, and give me one short pendant update."
- **useful because:** Today failed browser jobs remain as opaque failures, the browser has 3 pending commands, and Mac readiness is false despite the bridge heartbeat. A durable cross-surface reconciler would prevent duplicate work, explain the exact blocker, and automatically continue after Chrome/permissions recover—something no single node can do.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background planner for reconciliation and deduplication; realtime only for the one-sentence pendant status; cheap deterministic state machine for retries
- **latency:** Immediate blocker acknowledgement under 2 seconds; retry on heartbeat/permission transitions; completion receipt within 10 seconds after a surface returns
- **cost:** Usually <$0.01 per invocation; most runs use deterministic event processing, with a small planner call only for ambiguous job intent
- **security:** Persist only job IDs, typed action summaries, and redacted failure reasons in relay; never replay destructive actions automatically. Browser reads/clicks remain owner-authorized, but sending mail, deleting files, purchases, and irreversible actions require an explicit voice confirmation at execution time.
- **missing:** Durable cross-surface job state machine with idempotency keys and retry policy; A browser heartbeat-to-command-drain implementation; currently home-chrome is offline with 3 pending commands; A readiness transition stream from Mac bridge (Accessibility and Screen Recording are currently untrusted/missing); Read-only Mac inspection implementation: the granted mac_readonly_inspect tool currently returns “schema but no implementation”; Pendant notification route for concise blocked/resumed/completed status

### "“What do I need to know before my 2 pm meeting?” The system should privately join my Calendar, Mail, local notes/files, and authenticated browser pages on the Mac, return a concise answer through the pendant, and show exactly which sources were used without uploading their contents to the relay."
- **useful because:** The owner currently has separate source readers and browser access, but no trustworthy cross-source private join. They must either expose sensitive work data to a server model or manually search several apps. A local evidence join would make the pendant genuinely useful for context-heavy questions while preserving control.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Small background planner performs source selection and ranking; a local Mac model or deterministic extractor produces the joined evidence; realtime is used only to speak the final short answer.
- **latency:** Target 5 seconds for ordinary meeting preparation and under 12 seconds for browser-backed joins; return a partial answer with source status if one source is unavailable.
- **cost:** Near-zero relay token cost for local extraction; occasional small model call for synthesis, typically <$0.02. Dominant cost is local indexing/storage, not realtime inference.
- **security:** Mail, calendar, notes, files, and authenticated pages remain on the Mac. Relay receives only an opaque request ID, redacted answer, and source hashes/counts. The dashboard must let the owner inspect, exclude, or revoke each source class; never include secret values in spoken output unless explicitly requested.
- **missing:** A Mac-resident private evidence-join service with field-level redaction and source hashing; A browser bridge API that returns bounded structured page evidence rather than raw page dumps; A local synthesis/indexing model or deterministic ranking pipeline; Relay protocol for opaque requests and signed source manifests; Dashboard view for per-source inclusion, provenance, and revocation


## Changes it proposed to its own stack

### `integration` — Add a readiness-transition broker that continuously joins Mac permissions, bridge heartbeat, browser extension heartbeat, and relay reachability into one versioned surface lease. Every queued job records the lease it requires; on lease loss it pauses before the next step, emits a typed blocked receipt, and on lease restoration resumes only idempotent/read-only steps after verifying the prior receipt.
- **owner gets:** The owner stops hearing vague “failed” reports and stops wondering whether work ran twice. They get one accurate pendant sentence—blocked, resumed, or done—and work can continue after opening Chrome or fixing a permission without starting over.
- effort: Medium: new broker/state schema, event hooks in relay and Mac agent, browser heartbeat integration, dashboard visualization, and replay tests for crash/offline transitions.  ·  risk: A stale lease could incorrectly allow a step. Recover by requiring short TTLs, fencing tokens, and receipt verification before every resumed step; ambiguous mutations remain paused rather than replayed.
- cost: Negligible storage/compute; roughly one small event per heartbeat and one cheap planner call only for ambiguous recovery.  ·  latency: Adds under 100 ms to action dispatch; reconnection recovery depends on heartbeat interval, target under 5 seconds.
- security: Improves safety by preventing execution against an unverified surface; lease metadata must avoid exposing URLs, mail content, or secrets.
- depends on: Durable cross-surface job state machine; Browser heartbeat/command drain; Read-only Mac inspection implementation; Pendant status notification route

### `context` — Implement a cross-surface context-delta protocol: each relay, pendant, Mac, and browser response publishes a compact signed state vector (active task, source versions, unresolved questions, and action receipts). Subsequent turns send only deltas and references, while each surface can locally expand references it is authorized to see. Expire and garbage-collect deltas independently of transcript history.
- **owner gets:** The pendant can remember what matters across a long task without making every spoken turn slower, more expensive, or privacy-invasive. They can move from voice to Mac to a logged-in page and back while the system retains the task state, not a giant replay of their private transcript.
- effort: Medium-high: shared schema, signing/versioning, relay persistence, local expansion APIs, conflict resolution, and conformance tests across offline/reconnect cases.  ·  risk: A stale or mismatched reference could produce an answer based on old state. Recover with version checks, explicit “state changed” notices, and a forced local refresh; never silently merge conflicting action receipts.
- cost: Reduces repeated context tokens substantially; adds small D1/local metadata storage and hashing overhead. No new realtime call is required for ordinary turns.  ·  latency: Typically improves latency by shortening prompts; one extra local lookup per referenced source, with a bounded timeout and graceful omission.
- security: References and hashes cross the relay, but sensitive payloads stay on the originating device. Keys must be device-scoped and rotated; revoked references must fail closed.
- depends on: Private evidence-join service or equivalent local source manifests; Durable per-job receipts and source/version identifiers; Device identity and key rotation across pendant, relay, and Mac


## What it asked for

_Nothing._
## Its own summary

Discovered current blockers and proposed a new cross-surface capability: durable job reconciliation with readiness leases. Current live state is Mac bridge online but agent not ready (Accessibility trusted=false, Screen Recording=false), browser offline with 3 pending commands, and the newly granted mac_readonly_inspect tool has no implementation. The proposal pauses jobs on surface loss, prevents duplicate replay via fencing/receipts, resumes safe steps after recovery, and reports one concise pendant status. I also sent this gap to faculty-judgement.

**Biggest unknown:** Whether the owner will enable Accessibility/Screen Recording and bring the browser extension online; without those, GUI/browser execution cannot be verified. Engineering still needs to implement mac_readonly_inspect, durable cross-surface state, browser command draining, and the pendant status route.

