# Harness derivation — faculty-perception — round 107

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live reachability round 107** — At probe time, home-macbook-bridge is online and relay reachable; home-chrome/browser extension is offline with 12 pending commands; cloudflare-contract-test mobile is offline; no pendant is registered or exposed by the local agent's /v1/devices/status route (404). Mac /ops/status reports permissions.ready=false because Accessibility and Screen Recording are not granted. The latest stored workday briefing says calendar and mail were not read due to an Automation grant, so cached grant metadata and observed outcome currently conflict.
  - evidence: GET /ops/status 200 at 2026-08-07T14:55Z; GET /browser/status 200; GET /briefing/latest 200; GET /v1/devices/status returned 404.

## Capabilities it proposed

### "“Is my AI connected right now, and what can it actually reach?”"
- **useful because:** Give one honest, current answer across relay, Mac bridge, browser extension, and pendant registration instead of implying that an online Mac means the wearable or private browser is available. It would explain blockers (for example browser offline with queued commands, or Accessibility missing) and distinguish live state from recorded pipeline history, preventing false completion claims.
- **path:** relay-realtime → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** Realtime for the owner's short spoken query; use a cheaper background model to normalize and cache the status snapshot, with no expensive model call when unchanged.
- **latency:** Under 2 seconds for a spoken answer; parallel status reads dominate, not generation.
- **cost:** Typically <$0.01 per query; mostly one short realtime turn, with status reads free of model cost.
- **security:** Expose only reachability, permissions, queue counts, and coarse device identity—not URLs, page contents, tokens, or private account data. Never infer a pendant is present from historical audio telemetry. No confirmation needed because this is read-only.
- **missing:** A single authenticated status aggregator that joins relay device registry, Mac /ops/status, browser /browser/status, and explicit timestamped provenance into a typed snapshot; A registered pendant and its heartbeat protocol (currently no pendant exists, so that branch must honestly report absent); A consistency rule for contradictory cached grant state versus observed task results (for example /ops cache says Calendar granted while the latest briefing says it was not readable)

### "“Show me the final details on my Mac, and let me approve the action with one press on my pendant.”"
- **useful because:** Give the owner a secure approval channel that is physically separate from the Mac and browser. The system can prepare a draft or transaction using private browser sessions, display the exact before/after change on the Mac, and require a short-lived confirmation gesture on the worn device. This makes remote or unattended Mac control safer without forcing the owner to type a password or trust a stale browser tab.
- **path:** relay-realtime → browser-extension → mac-planner → mac-vision → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Use a cheaper background model to assemble and explain the prepared transaction; realtime is used only for the owner's spoken request and concise confirmation status. No model should decide whether a gesture is valid—the relay verifies the cryptographic approval token.
- **latency:** Preparation may take seconds; once the owner presses the pendant, relay-to-Mac authorization should complete within 1 second and expire after 60 seconds.
- **cost:** Usually under $0.03 per transaction, dominated by private-page extraction and any spoken response; the approval verification itself is negligible.
- **security:** The pendant must hold a device key and produce a nonce-bound, one-time approval signed locally; the relay must bind it to the exact transaction hash, browser session, target, and expiry. Never approve a changed draft, replay an old gesture, or expose page contents to the pendant. Require explicit confirmation for sending mail, purchases, deletion, or other irreversible effects; allow a separate lower-risk policy for reversible actions. If the pendant is lost, revoke its key from the relay.
- **missing:** A registered pendant with a secure key, button/gesture firmware, and local signing capability; A relay approval-intent endpoint that issues transaction-bound nonces, verifies signatures, enforces expiry/replay protection, and records an audit receipt; A Mac/browser transaction manifest that canonicalizes the exact proposed mutation and renders before/after evidence on the Mac; An action gate in faculty-action that blocks execution until the matching approval receipt arrives, then hands the same manifest to the existing browser/Mac action runners; A recovery and revocation flow through the Mac agent for lost or replaced pendants


## Changes it proposed to its own stack

### `context` — Add an evidence-reconciliation pass to the perception layer: for each capability claim, compare permission-cache fields from /ops/status with an observed operation result (briefing section, route response, or action receipt), attach observedAt/source/freshness, and mark contradictions as 'unverified' rather than selecting one. In particular, cached Automation grants must not override a fresh Calendar/Mail read failure. Emit a compact machine-readable reachability vector for downstream judgement/action.
- **owner gets:** The owner hears the truth about what worked, not a stale green permission indicator. It prevents the system from saying it read mail or calendar when the latest brief says it could not, and makes recovery actionable (retry, ask for a grant, or wait for the bridge).
- effort: Medium: typed schema plus reconciliation rules and tests across relay, Mac diagnostics, briefing, and receipts.  ·  risk: A transient failure may temporarily downgrade a real capability; recover by expiry (for example 5 minutes), a successful probe, or an explicit owner retry. Never delete the underlying evidence.
- cost: Negligible storage and CPU; avoids unnecessary realtime retries and therefore may reduce API cost.  ·  latency: Adds roughly 50–150 ms for local comparisons; no additional model call.
- security: Stores metadata and error classes only, not page contents or secrets. Keep source paths and URLs redacted in spoken output.
- depends on: A typed cross-surface reachability snapshot; Stable timestamps and provenance on /ops/status, browser status, briefing results, and action receipts

### `integration` — Introduce a transaction-manifest protocol spanning relay, browser, Mac, and a future pendant: canonicalize the exact intended mutation (target account/session, URL or app, fields, before/after hashes, irreversible-risk class, expiry) before execution; display the manifest on Mac; accept only a device-signed nonce bound to that manifest; then require faculty-action to submit the identical hash and attach the signed approval to the receipt. Any DOM change, tab switch, timeout, or retry invalidates the approval and forces a fresh review.
- **owner gets:** A single physical press would approve exactly what the owner saw—not a newer page, a different tab, or an accidentally replayed command. This provides trustworthy one-press control for private browser and Mac actions while the owner is away from the keyboard.
- effort: High: protocol schema, relay persistence and replay protection, Mac/browser rendering, pendant firmware signing, action-gate integration, and end-to-end failure tests.  ·  risk: Lost connectivity or a stale tab can strand a prepared transaction; recover by expiring it visibly and allowing a new manifest. A compromised Mac could misrepresent the display, so the signed manifest must be independently readable in the spoken response and receipt; device revocation must be immediate.
- cost: Small relay storage and cryptographic verification cost; one short model turn for explanation when requested. Hardware key storage/button changes add modest BOM cost.  ·  latency: Adds one preparation round and roughly sub-second verification after the physical gesture; invalidation on any mutation is intentional.
- security: Strongly improves authorization against replay, confused-deputy, and unattended-browser risks. Requires secure key provisioning, encrypted transport, revocation, and careful avoidance of sensitive page content in the pendant payload.
- depends on: A real registered pendant with a hardware-backed or protected private key; A canonical browser/Mac transaction manifest and before/after evidence renderer; A mandatory action gate that faculty-action cannot bypass; Durable relay receipts with nonce replay detection


## What it asked for

_Nothing._
