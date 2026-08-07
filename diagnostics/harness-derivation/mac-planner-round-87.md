# Harness derivation — mac-planner — round 87

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner round 87 live readiness** — Relay and Mac bridge are online and macOS automation grants are present, but browser extension is offline with 5 pending commands; Accessibility and Screen Recording are still false. The newly granted mac_read_sources and mac_readonly_inspect tools exist only as schemas and return 'no implementation yet'.
  - evidence: GET /ops/status returned relay/macBridgeOnline true, browser online false pendingCommands 5, accessibility trusted false, screenRecording granted false; direct calls to mac_read_sources and mac_readonly_inspect returned schema-only implementation errors.

## Capabilities it proposed

### "“Use my private browser tabs and Mac files to answer this, but keep the private material on my Mac and tell me exactly what crossed the boundary.”"
- **useful because:** Today a cross-surface task can require sending browser content or local documents into server-side reasoning without a clear, per-field accounting of what left the Mac. The owner should be able to use authenticated tabs and files together while receiving a concise spoken answer plus a durable privacy receipt listing sources, redactions, derived facts, and outbound payload hashes.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → dashboard
- **model tier:** Use the cheaper background/task model for extraction, redaction, and hashing on the Mac; use gpt-realtime-2.1 only for the live pendant conversation and final short narration. The server-side planner should receive typed, minimized facts rather than raw page/file contents whenever possible.
- **latency:** Interactive answer in 2–5 seconds for already-open tabs and local files; longer research can run as a durable job and return a pendant notification. Redaction and hashing should happen locally in parallel with source reads.
- **cost:** Usually one inexpensive task-model invocation plus a small relay metadata write; realtime cost only for the spoken interaction. The dominant cost is any explicitly authorized raw-content analysis, which should be opt-in and visible.
- **security:** Raw URLs, mail, documents, and authenticated page contents are highly sensitive. Default to local extraction, field-level redaction, destination allowlists, short-lived encrypted receipts, and no raw-content relay. Show the owner a before-send manifest; store hashes and provenance rather than copies. Never infer that a source was consulted when it was unavailable.
- **missing:** A Mac-resident privacy broker that intercepts browser/file extraction and emits typed minimized facts; A field-level redaction and outbound-payload manifest format shared with relay and dashboard; A pendant-readable privacy receipt and a way to inspect or delete receipts; Working implementations of the granted read-only Mac source/inspection adapters; Browser extension reconnection for authenticated-tab access


## Changes it proposed to its own stack

### `integration` — Add a cross-surface action lease and reconciliation protocol shared by relay, Mac planner, and browser bridge. Every requested mutation gets one durable intent ID and semantic idempotency key before dispatch; relay owns the lease, Mac/browser claim it with a heartbeat, and receipts include precondition hash, effect summary, and terminal state. If the pendant retries after a dropped connection, the relay returns the existing receipt instead of dispatching a second action. If a worker disappears mid-step, mark the intent uncertain and run a read-only reconciliation probe before allowing continuation.
- **owner gets:** A spoken “send it,” “move that file,” or “book this” will happen once—not twice—when Wi‑Fi, the browser extension, or the Mac bridge drops at the worst moment. The owner gets a clear spoken result such as completed, not started, or needs review instead of guessing whether to retry.
- effort: Medium-high: shared intent schema and D1/local persistence, lease heartbeats, adapters for Mac job receipts and browser command IDs, plus reconciliation handlers for common actions.  ·  risk: A false precondition or incomplete receipt could incorrectly report an action as complete, while an overly cautious uncertain state may delay a legitimate action. Keep uncertain terminal states explicit, never auto-repeat high-impact mutations, and provide an inspectable receipt timeline and manual retry.
- cost: Low relay storage and a few metadata writes per action; negligible model cost. Reconciliation may add one local read or browser query, not a model call in the normal path.  ·  latency: Adds roughly one metadata round trip (tens to low hundreds of ms); retries become faster because they resolve from the receipt. Reconciliation is only on failures.
- security: Intent records contain sensitive targets and URLs; encrypt or minimize payloads, retain hashes rather than full contents, scope records to the paired owner, and do not expose browser credentials or message bodies to the relay.
- depends on: Existing Mac job receipts/undo records and browser request IDs/session affinity; A relay-side durable intent table and event stream; Typed result schemas from the Mac and browser adapters

### `context` — Create a Mac-resident privacy boundary between browser/file readers and every server-side planner. It should accept extraction requests, perform source reads locally, classify each field (safe derived fact, sensitive, secret), redact or aggregate locally, hash the original evidence, and emit a signed outbound manifest containing only the permitted facts and provenance. Relay and dashboard should render the manifest and hashes as a privacy receipt; raw evidence stays on the Mac and is deleted according to a short TTL unless the owner explicitly asks to retain it.
- **owner gets:** The owner can safely ask one mind to combine authenticated browser information with local documents without having to trust an invisible upload. They can hear exactly what was used and what crossed the Mac/server boundary, while still getting the benefit of unified reasoning.
- effort: High: local broker API and policy engine, browser/Mac adapter hooks, signed manifest schema, relay verification, receipt UI/audio, and deletion tests.  ·  risk: Misclassification could leak sensitive content or make an answer incomplete. Default-deny unknown fields, expose unavailable/redacted states, preserve local evidence hashes for audit, and allow a retry with a narrower or explicitly authorized scope.
- cost: Small local CPU/storage overhead and one compact relay receipt per task; raw-content model calls become less frequent and therefore cheaper.  ·  latency: Adds local classification and hashing, usually under 300 ms; parallel extraction keeps normal tasks interactive. Explicit raw-content escalation is slower and clearly marked.
- security: Reduces data leaving the Mac, provides tamper-evident provenance, and avoids copying credentials or full authenticated pages to the relay. Requires secure local key storage and careful receipt minimization.
- depends on: A shared typed extraction result format for Mac and browser; Local implementations of the granted read-only source and inspection adapters; Relay verification and dashboard rendering for signed privacy manifests


## What it asked for

_Nothing._
