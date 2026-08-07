# Harness derivation — relay-realtime — round 120

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Read the one-time code, tracking number, or other short secret currently shown in my logged-in browser page.” The system should find the exact value in the owner’s authenticated tab, speak it once through the pendant, and erase the transient value afterward."
- **useful because:** Today the owner must walk to the Mac, find the right tab, and visually transcribe values. This bridges the pendant’s voice/audio, the browser’s private session, the always-awake relay, and the Mac bridge while avoiding a broad page summary. It is especially useful when the owner is away from the desk or cannot safely copy/paste.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Realtime handles the short spoken intent and immediate spoken response; a cheaper extraction worker locates a value using the authenticated browser tab’s DOM/accessibility tree, with the realtime model only resolving ambiguity.
- **latency:** Target 2–5 seconds from utterance to spoken value; if multiple candidate values exist, speak a concise disambiguation question rather than guessing.
- **cost:** Usually one short realtime turn plus a small extraction call, roughly $0.01–$0.05 per request; authenticated-page capture and relay egress dominate latency, not generation.
- **security:** Treat the value as an ephemeral secret: never place it in ordinary transcripts, logs, job receipts, model memory, browser history, or dashboard payloads; redact it from traces, deliver over the pendant’s authenticated audio channel, expire it after one playback or 30 seconds, and expose only metadata to diagnostics. The owner’s explicit request is the authorization; do not read arbitrary page content when the request is specifically for a secret.
- **missing:** A typed sensitive-value extraction operation that returns a redacted handle plus ephemeral plaintext only to the audio renderer; End-to-end secret redaction and zero-retention guarantees across relay logs, browser bridge, Mac planner, and dashboard; A pendant playback acknowledgement/expiry signal and a spoken fallback when audio delivery fails; Browser semantic targeting that distinguishes OTPs, tracking numbers, confirmation codes, and ordinary visible numbers


## Changes it proposed to its own stack

### `relay` — Implement the granted intent-routing and job-status tools as real relay endpoints, backed by a visible relay capability inventory and durable job records. Provide an explicit contract: route intent to mac-planner or mac-vision, emit a job id, and support status and receipt retrieval that the pendant can speak verbatim.
- **owner gets:** The owner gets predictable, trustworthy handoff from a voice request to action, and a clear answer later about what happened—without guessing or re-asking.
- effort: Medium to high. Requires relay router work, storage for job metadata, and integration with existing plan/execute routes.  ·  risk: Risk of double-execution or misrouting. Mitigate with idempotency keys, request ids, and receipt-based reporting. Provide a safe fallback to say 'unknown' rather than guessing.
- cost: Moderate engineering cost; API cost dominated by downstream execution rather than relay calls.  ·  latency: Small added overhead for routing; big win in perceived responsiveness and reliability.
- security: Improves auditability. Must ensure job metadata does not leak sensitive content; store minimal necessary summaries and receipts.
- depends on: Durable job runner or equivalent persistence so jobs survive relay restarts; Surface health signals from mac-planner and browser harness to avoid routing to offline components

### `browser-harness` — Add a browser heartbeat and queue reconciler that reports explicit surface health (online/offline, accessibility trust, screen recording permission, command backlog). When unhealthy, stop claiming browser workflows and instead offer to queue work or switch to public web search.
- **owner gets:** They won’t hear false promises like “I’m checking your account now” when the browser automation is actually offline. It makes the system honest and reduces confusion.
- effort: Medium. Needs status endpoints and reconciliation logic between relay and mac-planner/browser extension.  ·  risk: Risk of under-reporting capability if health signals are noisy. Mitigate with debouncing and last-seen timestamps.
- cost: Low runtime cost; periodic lightweight checks. Main cost is development time.  ·  latency: Minimal; health checks can be cached.
- security: Health reporting is low sensitivity, but still avoid exposing detailed local environment info beyond what the owner needs.
- depends on: A stable status route for browser and computer-use loop; Standardized error codes for timeouts and permission failures

### `integration` — Add a dedicated ephemeral-secret lane spanning browser bridge → relay → pendant audio. The browser bridge must classify and extract only an explicitly requested secret (OTP, tracking code, confirmation number), return a one-time encrypted handle, and keep plaintext in volatile memory only. The relay resolves the handle directly into the audio renderer, emits redacted lifecycle events, deletes the value after acknowledged playback or a 30-second TTL, and makes ordinary /logs, receipts, transcripts, memory, and dashboard APIs incapable of returning it.
- **owner gets:** The owner can safely ask the pendant to read a code from a private browser tab without walking to the Mac or risking that a login secret is retained in the AI’s history. It turns a common, frustrating desk interaction into a fast voice interaction while preserving the owner’s authenticated browser session.
- effort: Medium-high: typed secret schema and DOM classifiers, encrypted one-time handle plumbing, audio acknowledgement/expiry, redaction tests across every persistence path, and an explicit failure path that says the value was not delivered rather than retrying aloud.  ·  risk: A classifier could select the wrong number or a secret could leak through an overlooked diagnostic path. Recover with strict candidate typing, never speak when confidence is low, integration tests that inject canary secrets into logs/receipts/transcripts, short TTLs, and a kill switch that disables secret extraction without disabling ordinary browsing.
- cost: Small per-use extraction and encryption overhead; no meaningful persistent storage cost. Testing and audit instrumentation dominate engineering cost.  ·  latency: Adds roughly 100–400 ms for classification/handle resolution; target remains under 5 seconds end to end.
- security: Improves security for this use case by enforcing least-data flow and zero retention, but introduces a high-value transient secret path. Requires authenticated pendant/session binding, replay protection, audio-delivery acknowledgement, and redacted observability by default.
- depends on: An authenticated browser tab/session binding with stable tab identity; A relay audio renderer that can accept a volatile payload without writing it to transcript/history; A reliable pendant playback acknowledgement or explicit timeout; A repository-wide redaction test harness for logs, receipts, memory, and dashboard responses


## What it asked for

_Nothing._
