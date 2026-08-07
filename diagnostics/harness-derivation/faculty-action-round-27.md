# Harness derivation — faculty-action — round 27

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **action-execution readiness** — At Round 27, the Mac bridge is online but agent readiness is false because Accessibility and Screen Recording are not trusted; the browser bridge is offline with 3 pending commands. Existing failed browser jobs waited ~45 seconds and produced failed receipts, confirming that receipt existence must not be treated as completion.
  - evidence: GET /ops/status returned ready:false, accessibility.trusted:false, screenRecording.granted:false, browserExtension.online:false, pendingCommands:3. GET /jobs showed browser_navigate failures after 45180 ms with ok:false and irreversibleReason 'The step did not complete, so nothing was changed'.

## Capabilities it proposed

### "When I ask you to do something, check that the right hand is actually available first; if it isn't, tell me exactly what is blocking it, keep the request safely resumable, and finish it automatically when that hand comes back—then tell me only when there is proof it happened."
- **useful because:** Today the system can report a receipt for a failed browser command while the Mac is not ready and the browser is offline. The owner needs one trustworthy contract: no false success, no lost intent, and no need to repeat a request after reopening Safari or granting access.
- **path:** pendant: speaks a concise blocked/queued/completed status and can receive an explicit cancel or retry command → relay: owns the durable intent, idempotency key, retry policy, handoff state, and reconnect-triggered resume → mac-planner: performs a preflight of bridge health, Accessibility/Screen Recording, app authorization, and task-specific reachability → mac-vision: supplies screenshot/DOM evidence only when the task requires UI interaction and only after permissions are confirmed → browser-extension: reports polling, session/tab affinity, page identity, and typed completion evidence; never accepts work while offline → dashboard: shows blocker, queued plan, attempts, evidence, and cancel/approve controls
- **model tier:** Use a cheap background model for routing, retry classification, and evidence reconciliation; reserve gpt-realtime for the spoken status and any owner clarification.
- **latency:** Preflight under 2 seconds when hands are online; queue immediately when offline; resume within 10 seconds of a reconnect event; speak a blocker in under 1 second and completion only after verified evidence.
- **cost:** About $0.002–$0.02 per action lifecycle depending on whether evidence needs vision; most retries and state transitions are deterministic, with occasional cheap text reconciliation. Realtime cost is limited to owner-facing turns.
- **security:** Private URLs, page text, screenshots, and permission state may cross relay boundaries; keep sensitive payloads on Mac/browser where possible and send hashes/typed evidence. Never retry irreversible sends, purchases, deletions, or submissions without a fresh approval lease. Bind retries to the original tab/session and idempotency key; expire queued intents and provide cancel.
- **missing:** A typed cross-surface preflight schema and capability lease (online, permission, session, tab, and evidence requirements); A durable intent state machine separate from action receipts: blocked, queued, running, verified, failed, cancelled, expired; Reconnect events from the Mac bridge and browser extension to wake the relay runner; Evidence requirements per action type and a verifier that distinguishes attempted from completed; A safe retry/approval policy for irreversible actions; Pendant-visible status and cancellation for queued intents

### "When I’m physically with my Mac, let me approve a prepared action from the pendant with one button or a spoken phrase, and make sure the approval is bound to this device, this computer, and this exact preview—so the action cannot run later from an old request or on the wrong machine."
- **useful because:** The owner gets a practical, trustworthy bridge between their physical presence and high-impact digital actions. A prepared browser submission, local file change, or message can be approved while wearing the pendant, but a stale queued request, replayed voice command, or action on another Mac cannot silently execute.
- **path:** pendant: captures the short approval phrase or button gesture, displays a preview hash/status, and emits a device-bound approval token → relay: issues short-lived approval challenges, binds them to the pendant identity, Mac identity, exact action hash, and expiry, and records an auditable decision → mac-planner: assembles the exact action preview and refuses execution unless the challenge matches the current machine and unchanged plan → mac-vision: supplies visual confirmation of the final target when a GUI action is involved → browser-extension: confirms the exact tab/session/page identity and verifies that the submitted fields still match the approved preview → dashboard: displays pending approval challenges, target machine, preview digest, expiry, and revocation history
- **model tier:** Use deterministic cryptographic checks and a cheap background model for preview summarization; use realtime only to conduct the short spoken approval interaction.
- **latency:** Preview preparation can take seconds; approval acknowledgement should be under 1 second, with execution beginning within 3 seconds after a valid token. Expire challenges after 60 seconds by default.
- **cost:** Negligible model cost for most actions, approximately $0.0005–$0.005 for a generated preview summary; cryptographic checks and audit records dominate neither latency nor cost.
- **security:** The pendant becomes an approval credential, so loss or theft requires revocation and re-pairing. Never include secrets in spoken previews. Bind approvals to a nonce, action digest, tab/session identity, Mac host fingerprint, and narrow expiry; require a stronger confirmation for financial, deletion, publication, or message-send actions. Store audit metadata, not full private page contents, in the relay.
- **missing:** Secure pendant identity and challenge-response signing or equivalent paired-device attestation; A canonical action-preview digest shared by judgement, relay, Mac, and browser; A Mac host fingerprint and browser tab/session identity in the approval verifier; Pendant-side approval interaction and revocation flow; A final pre-execution comparison that rejects any plan changed after approval


## Changes it proposed to its own stack

### `relay` — Implement an Action Handoff Contract shared by judgement, relay, Mac, and browser: every intent carries intentId, idempotencyKey, requiredHands, preflight predicates, approval lease, retry budget, and evidence schema. The relay persists an append-only lifecycle (planned→preflight_blocked/queued→running→verified or failed/cancelled/expired), consumes bridge/browser reconnect events, and only emits completed after typed evidence verification. Existing receipts link to lifecycle events but cannot imply success alone.
- **owner gets:** The owner can say a goal once and trust that it will either happen or clearly explain the exact missing access/device. Requests survive closing Safari or temporarily losing the Mac, without duplicate sends or the dangerous illusion that an attempted action succeeded.
- effort: Medium-high: shared TypeScript contract, D1/local persistence migration, reconnect hooks, preflight adapters for Mac and browser, verifier library, dashboard and pendant status plumbing, and failure-injection tests for disconnects between side effect and receipt.  ·  risk: A bad verifier could delay a genuinely completed action or a retry could duplicate an external side effect. Recover with idempotency keys, per-action irreversible gates, explicit unknown outcome state, conservative expiry, and a manual reconciliation view. Roll out read-only/preflight mode first.
- cost: Low ongoing API cost: deterministic state transitions and hashes; roughly $0.001–$0.01 per lifecycle for occasional cheap reconciliation, excluding vision. Storage is small append-only records plus bounded evidence metadata.  ·  latency: Adds about 0.5–2 seconds for preflight and evidence checks; avoids 20–45 second doomed browser waits observed in failed jobs. Reconnect resume is event-driven rather than polling.
- security: Improves security by scoping retries to a session/tab and approval lease, minimizing private page contents in relay logs, and making cancellation/expiry auditable. Requires careful encryption/access control for evidence metadata.
- depends on: Browser bridge reconnect and typed completion events; Mac bridge readiness endpoint that reports permissions without exposing unrelated screen content; Durable relay job runner; Per-action evidence schemas and irreversible-action approval policy; Pendant status/cancel protocol


## What it asked for

_Nothing._
## Its own summary

Recorded a new capability: presence-bound, device-bound approval for exact prepared actions. The pendant approves a cryptographically bound preview tied to the specific Mac, browser tab/session, action digest, and short expiry; stale, replayed, changed, or wrong-machine actions are rejected.

**Biggest unknown:** Whether the pendant hardware/firmware currently supports a secure paired identity and challenge-response signing primitive; that determines whether approval can be cryptographically device-bound or needs a server-mediated fallback.

