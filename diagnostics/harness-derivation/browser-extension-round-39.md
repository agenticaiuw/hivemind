# Harness derivation — browser-extension — round 39

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser-extension live connectivity** — GET /browser/status currently reports Safari extension offline, only the never-used home-chrome device registered, and 3 pending browser commands. Mac ops status independently reports browser online=false and ready=false due missing Accessibility/Screen Recording.
  - evidence: GET /browser/status HTTP 200: online=false, home-chrome tabCount=null, pendingCommands=3; GET /ops/status HTTP 200: browser online=false, accessibility trusted=false, screenRecording granted=false.

## Capabilities it proposed

### "If a private-site task hits a login or 2FA wall, pause it safely, tell me which site needs attention, and resume the exact task automatically after I re-authenticate—without repeating already-completed steps."
- **useful because:** Authenticated browser work currently fails opaquely or risks replaying actions. This turns a common interruption into a recoverable handoff: the pendant can alert me, Safari can retain the session, and the relay/Mac can continue later without me restating the goal.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Background planner for detection, checkpointing, and resume; realtime only for the short spoken re-auth prompt.
- **latency:** Detect within the current browser action (under 2 seconds); resume within 5 seconds after the extension reports successful re-authentication.
- **cost:** Usually one cheap classifier/planner call per blocked task and one resume call; roughly $0.01–$0.05 per interruption, dominated by page extraction context.
- **security:** Never transmit passwords, OTPs, cookies, or page contents to the relay. Browser reports only origin, auth-state reason, checkpoint ID, and coarse page metadata. Re-authentication is performed by the owner in Safari; resume must revalidate origin, tab identity, and page fingerprint before any mutation.
- **missing:** Browser extension auth-wall detector and re-auth event (login/2FA/expired-session taxonomy); Per-task checkpoint/lease store with completed-step hashes and safe resume points; Relay-to-pendant notification and Mac planner resume callback; Dashboard view to discard, restart, or inspect a paused task

### "When I say “save this for later” while I’m on a logged-in webpage, preserve only the specific passage or fields I indicate—with its source, date, and why I saved it—so I can ask about it from the pendant weeks later, even when Safari is closed."
- **useful because:** Important information is often visible only inside authenticated sites and disappears into browser history. This gives the owner a durable, searchable memory of selected private facts without archiving whole pages or requiring them to copy and organize anything manually.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Cheap background extraction and metadata model for normalization and deduplication; realtime only when the owner asks for a spoken recall.
- **latency:** Capture in under 3 seconds while the page is open; spoken recall in under 2 seconds when the pendant is connected.
- **cost:** About $0.005–$0.03 per capture and recall, dominated by extraction and embedding; storage is small because only selected snippets and metadata are retained.
- **security:** Raw page content stays on the Mac unless the owner explicitly enables encrypted relay storage. Store only the selected region, origin, timestamp, sensitivity label, retention period, and a keyed hash of the source. Never retain credentials, hidden fields, or unrelated page text. Require explicit owner wording or gesture to capture.
- **missing:** Extension command to capture the owner-selected DOM region and surrounding citation; Local encrypted snippet vault with retention and deletion controls; Relay retrieval API that can return compact, sensitivity-filtered memories to the pendant; Recall UI showing source, age, and exact saved text


## Changes it proposed to its own stack

### `browser-harness` — Add connection-epoch and command-lease reconciliation to the browser bridge. Every queued command gets a device session epoch, expiry, task checkpoint, and idempotency key. On extension disconnect/reconnect, stale commands are moved to a dead-letter state rather than replayed; on reconnect the planner receives a compact report of pending, completed, expired, and ambiguous commands. Before resuming a paused authenticated task, verify the same origin/tab (or an explicit owner-approved replacement), compare a page fingerprint, and skip steps whose receipts already match. Expose cancel/retry/resume controls and retain the current three pending commands as inspectable records instead of silently executing them.
- **owner gets:** When Safari goes offline or the Mac sleeps, the owner gets neither duplicate clicks nor mysterious lost work. A task can safely continue after reconnect, while stale actions cannot unexpectedly send or submit something after the browser context changed.
- effort: Medium: bridge protocol and local persistence, relay job-state reconciliation, planner resume logic, and dashboard states; extension needs a small reconnect/epoch field.  ·  risk: A conservative fingerprint mismatch may pause work that could have continued; recovery is explicit retry from the last verified checkpoint. Network loss during a mutation can still produce an ambiguous outcome, so that step remains marked ambiguous and is never automatically retried.
- cost: Negligible storage and relay traffic; one small background planner call on reconnect or ambiguity, typically under $0.02.  ·  latency: No added latency for ordinary commands; reconnect adds roughly 1–3 seconds for reconciliation and fingerprint validation.
- security: Improves safety by preventing stale command replay and keeping credentials/page bodies local; origin, tab ID, hashes, and status metadata leave the Mac only as needed for coordination.
- depends on: Reliable browser command enqueue/result path; Durable browser job/checkpoint store; Provenance receipts from chg-e14fff33 or equivalent; Authenticated-page watch/session identity from the existing browser session work

### `browser-harness` — Add an explicit browser-to-memory capture protocol. The extension returns only a user-selected DOM range plus URL/title/timestamp and a stable locator; the Mac agent normalizes it locally, strips scripts/hidden fields and nearby unrelated text, assigns sensitivity and retention, and stores an encrypted snippet record. The relay receives only an opaque memory ID and optional encrypted blob when remote recall is enabled. Pendant queries use memory IDs and return source-linked excerpts, with per-record revoke and immediate deletion propagated to every replica.
- **owner gets:** The owner can retain a useful fact from a private webpage without saving an entire page, leaking unrelated account data, or losing the source. Later the pendant can answer “what was that number I saved?” with the exact excerpt and where it came from.
- effort: Medium: extension selection/capture protocol, local encrypted vault and indexing, relay retrieval/deletion endpoints, and a compact pendant recall UI.  ·  risk: A DOM locator may become invalid after a page redesign; the original selected text and source hash remain the authoritative record, and the system should mark it stale rather than silently refresh it. Accidental sensitive capture is mitigated by explicit capture, preview, sensitivity labeling, and deletion.
- cost: Low ongoing API cost; typically one small extraction/normalization call per capture and negligible encrypted storage. Remote mode adds small relay storage and retrieval traffic.  ·  latency: Capture adds under 3 seconds; local recall is near-immediate, remote recall usually under 1 second before speech generation.
- security: Strongly reduces data exfiltration by keeping extraction local and retaining only selected content. Requires encryption at rest, device-bound keys, explicit remote-storage opt-in, and strict redaction of hidden inputs and credentials.
- depends on: A functioning browser command/result transport; Local encrypted storage and searchable memory index; Relay memory retrieval and deletion APIs; Pendant support for source-linked spoken recall


## What it asked for

_Nothing._
