# Harness derivation — relay-realtime — round 98

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch this page for meaningful changes and tell me only when something important changed."
- **useful because:** The owner stops re-checking accounts and dashboards manually. The system quietly monitors and only speaks up when there’s a real change, which is perfect for a wearable.
- **path:** browser → mac-bridge → relay → faculty-perception → faculty-judgement
- **model tier:** Cheaper background model for extraction and change detection; realtime only for notifications.
- **latency:** Background checks can take seconds; notifications should be under a second once a change is detected.
- **cost:** Dominated by browser automation and extraction tokens; minimal relay cost for notifications.
- **security:** Authenticated pages contain sensitive data. Extract only necessary fields, store hashes/fingerprints, and avoid retaining full page content when possible. Require confirmation before submitting forms.
- **missing:** Durable authenticated page-watch service with cadence and quiet hours; Semantic fingerprinting to filter noise (timestamps, ads); Notification policy for pendant (rate limiting, do-not-disturb); Fallback between Safari bridge and server browser when Mac is offline

### "When I put the pendant back on, tell me what changed on my Mac and in my open browser work since I left."
- **useful because:** The owner is often away from the Mac and currently has no dependable way to recover the important deltas accumulated during that absence. A cross-surface departure snapshot plus a spoken return brief would turn the pendant into continuity for work, rather than merely a remote button. It can highlight changed documents, newly opened or closed work, browser-page changes, and pending Mac results without requiring the owner to remember where they left off.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheap background model to normalize and diff snapshots; use relay-realtime only for the short, low-latency spoken summary when the pendant reconnects or the owner asks. Escalate an ambiguous change to mac-planner for a cited explanation.
- **latency:** Capture snapshots opportunistically and on departure in under 2 seconds; on return, deliver a first spoken brief within 2 seconds, with deeper per-item explanations streaming afterward.
- **cost:** Usually one small background summarization/diff invocation per departure/return pair, roughly $0.001-$0.01 depending on captured text; realtime cost is limited to a few hundred summary tokens. Storage and polling dominate operational cost, not inference.
- **security:** Browser titles, URLs, snippets, and Mac activity can contain private work data. Keep raw snapshots encrypted and short-lived, redact secrets/forms, bind them to the owner's device/session, and expose deletion/history controls in the dashboard. Do not read page bodies or files unless the owner explicitly asks for the detail.
- **missing:** A durable departure/return snapshot store with retention and encryption; A reliable pendant connection/disconnect (or explicit one-button 'leaving/returning') event carrying a connection epoch; Mac collector for changed files, apps, windows, and completed job receipts; Browser-extension collector for authenticated tab identity and meaningful page-change fingerprints; Cross-surface diff/ranking and cited spoken-brief formatter; A relay endpoint that can push the brief after reconnect rather than waiting for a new utterance

### "That worked—turn what you just did into a reusable voice recipe I can run again, and show me exactly what it will touch before I use it."
- **useful because:** Today a successful pendant request disappears into a transcript and opaque job history. The owner should be able to convert a completed Mac/browser handoff into a parameterized, inspectable recipe—such as “prepare my weekly report”—without rebuilding the instructions from memory. This is specifically a hive capability: the relay contributes the spoken intent and context, Mac contributes actual actions and receipts, and the browser facet contributes session/tab targets and evidence.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use a background model to canonicalize a completed trace into a recipe and extract parameters; use relay-realtime only to confirm the recipe name and answer short spoken questions. Use mac-planner at execution time to fill parameters and re-plan if the environment differs.
- **latency:** Offer a draft recipe within 5 seconds after a completed job; dashboard inspection is asynchronous. A later run should acknowledge immediately and return a receipt when finished.
- **cost:** About $0.005-$0.03 per recipe extraction depending on trace length, then normal planner/action costs per run. Most cost is one-time trace summarization; storing structured traces is inexpensive.
- **security:** Recipes may encode private URLs, file paths, account names, and browser-session assumptions. Encrypt them per owner, redact tokens/cookies and page secrets, show every target and mutation in the dashboard, support revocation/versioning, and never silently broaden a recipe when a target changes. A preview is informational, not an execution gate, consistent with the owner's no-confirmation preference.
- **missing:** A trace normalizer that joins spoken transcript, planner plan, typed actions, browser command IDs, and receipts into one immutable provenance record; A recipe schema with named parameters, target selectors, preconditions, versioning, and rollback metadata; A dashboard editor/preview and a pendant command for save/list/run/disable; A rerun endpoint that resolves the recipe across the current Mac and authenticated browser session, reporting selector drift instead of guessing; Persistent per-owner recipe storage and deletion/export controls


## Changes it proposed to its own stack

### `relay` — Expose a relay-side capability inventory and intent-routing status endpoint (e.g., GET /v1/relay/capabilities, GET /v1/relay/intents/:id/status) backed by the same router used to serve requests. Include the granted-tool schemas, supported context fields, and any implemented intent handlers so relay-realtime can discover what it can actually do without guessing.
- **owner gets:** The pendant can give faster, more reliable answers like “I can do that” or “I can queue it for your Mac” without false promises. It reduces round trips and avoids confusing failures when a tool exists only as a schema.
- effort: Medium: define a small read-only API, add router registration, and wire it to the existing tool/intent registry. Add tests that the inventory matches the live router.  ·  risk: Low. Risk is exposing internal surface details; mitigate by returning a minimal, redacted list and omitting secrets, tokens, and implementation notes.
- cost: Small API cost per call; dominated by occasional discovery calls. No new external services.  ·  latency: Improves by preventing misroutes and failed attempts. Adds negligible overhead when used sparingly.
- security: Must ensure the endpoint is authenticated and only returns non-sensitive metadata. Avoid leaking internal paths that imply privileged actions.
- depends on: relay intent handler registry (or equivalent) being the source of truth for the inventory


## What it asked for

_Nothing._
