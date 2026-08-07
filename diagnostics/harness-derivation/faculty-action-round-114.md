# Harness derivation — faculty-action — round 114

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser bridge availability** — home-chrome is offline with 12 pending browser commands; no tab/session is attached. Browser-only actions cannot currently be verified or safely drained.
  - evidence: GET /browser/status returned online:false, tabId:null, pendingCommands:12.
- **Mac action surface** — Mac bridge is online and AppleScript automation grants are present, but Accessibility and Screen Recording are still ungranted; computer-use GUI actions are therefore unavailable/unverified.
  - evidence: GET /ops/status returned macBridgeOnline:true, accessibility.trusted:false, screenRecording.granted:false, automation grants true, computerUse.loopEnabled:false.
- **pendant reachability** — No physical pendant is reachable; only Mac bridge is online and mobile device is offline/stale.
  - evidence: discover(devices) returned home-macbook-bridge online, cloudflare-contract-test offline, no pendant entry.

## Capabilities it proposed

### "“Prepare this action on my Mac, but don’t release it until I give the pendant a deliberate physical confirmation—even if the voice link is gone; then tell me exactly what was released.”"
- **useful because:** The owner can safely authorize a consequential action while mobile, without relying on a fragile spoken yes/no or trusting that a stale browser/Mac job is still the one they intended. The pendant becomes a local second factor and a clear boundary between preparation and release.
- **path:** faculty-judgement → relay-realtime → relay → pendant → mac-planner → mac-terminal → browser-extension → faculty-action
- **model tier:** Use the realtime tier only to explain the pending action and collect conversational edits; compile the action packet and proof requirements with a cheaper planner/background tier. The pendant confirmation and release decision should be deterministic, not model-generated.
- **latency:** Preparation may take seconds in the background; confirmation should release in under 2 seconds when the pendant is connected. If disconnected, retain a short-lived pending packet and never auto-release on reconnect.
- **cost:** Usually one planner/background compilation plus ordinary Mac/browser execution; roughly $0.01–$0.08 depending on context size. Pendant button confirmation and relay routing add negligible API cost.
- **security:** The packet must be content-bound (target, exact fields/recipients, proof obligation, expiry, idempotency key), signed or MAC-authenticated between relay and pendant, and invalidated on any edit or timeout. Never expose secrets in spoken prompts or LED patterns. Sending mail, purchasing, deleting, or submitting still requires this explicit confirmation; reconnect must not count as consent.
- **missing:** A pendant-local confirmation protocol and signed pending-action display/LED state that works offline; A relay-held two-phase action packet with expiry, hash, and one-shot release endpoint; Mac/browser adapters that can prepare without committing and then release the exact prepared transaction; A durable proof receipt joining pendant confirmation, prepared state, release, and post-action observation


## Changes it proposed to its own stack

### `integration` — Add a cross-surface execution contract between faculty-judgement and faculty-action. Every dispatched plan carries typed steps {target surface, preconditions, intended effect, proof obligation, confirmation class, idempotency key, expiry}. faculty-action may execute reversible steps autonomously, but must return a structured receipt only after satisfying the proof obligation (for example: reminder ID exists, file hash matches, browser field value is observed after reload); otherwise it reports blocked/unknown rather than success. The relay persists the contract and checkpoints, routes each step to Mac AppleScript, browser bridge, or relay, and resumes only uncompleted idempotency keys after disconnect/restart. Irreversible steps stop at the existing confirmation boundary. This is intentionally narrower than a generic durable runner: it prevents the mind from saying 'done' when an action merely dispatched.
- **owner gets:** When the owner says 'handle it,' they get a trustworthy answer: completed with evidence, waiting for their decision, or genuinely unable—not a confident success message after a dropped browser or half-finished Mac action.
- effort: Medium-high: shared contract schema, relay persistence/checkpointing, adapters for existing Mac and browser receipts, and planner/action tests for duplicate delivery and missing proof.  ·  risk: A strict proof obligation may mark useful work unknown when an app has weak observability; recover by exposing the evidence and allowing a retry or explicit owner override. Never silently retry sends, purchases, deletes, or other irreversible effects.
- cost: Negligible storage; one small model/router pass to compile proof obligations, with cheaper background execution for retries. No new per-action model call required.  ·  latency: Adds one observation/verification round after writes (typically 1–5 s); avoids long delays from duplicate or misrouted work.
- security: Contracts and receipts must redact secrets and keep private browser evidence on the Mac; confirmation class and expiry prevent stale authorization from being reused.
- depends on: Durable browser job runner (chg-16bc5dee) or equivalent persistence; Mac action receipts/undo (chg-5fc73ce3 is implemented but lacks gates); A shared typed context/permission projection so the contract knows current authorization

### `firmware` — Add an offline, one-shot action-release latch to the pendant/relay protocol. The relay sends a signed pending-action digest (human-readable short label, target, exact effect class, expiry, and packet hash); the pendant stores only that bounded packet, shows a distinct pending state, and requires a long-press plus a second deliberate press to emit a signed approval nonce. The relay accepts that nonce only for the matching hash and then releases the already-prepared Mac/browser transaction exactly once. Reconnect, button bounce, duplicate packets, or an expired lease must not release anything. Emit a receipt chain linking packet hash, local confirmation timestamp, release, and post-action proof.
- **owner gets:** They could approve a prepared consequential action with a deliberate physical gesture even when the voice session has dropped, while being protected from stale queued browser commands or accidental reconnect execution.
- effort: High: pendant firmware state machine and flash persistence, authenticated relay endpoints, packet signing/key provisioning, and Mac/browser prepare-vs-release adapters; requires a real pendant for integration testing.  ·  risk: A lost pendant or compromised relay key could block approvals or authorize the wrong packet. Mitigate with short expiry, visible digest spoken/displayed before arming, monotonic nonce tracking, server-side one-shot consumption, and a revoke-all endpoint. Recovery is to discard the packet and prepare again; never auto-release.
- cost: Small firmware/storage footprint and negligible relay compute; one background/planner compilation per prepared action, no extra model call at button time. Hardware cost is zero if the existing button/LED are sufficient.  ·  latency: Local confirmation is sub-second; release waits for relay round trip and then a deterministic post-action proof, typically 1–5 seconds.
- security: Meaningfully improves authorization by binding consent to the exact action hash and a physical gesture; requires key rotation, anti-replay counters, and no secret payload in the pendant.
- depends on: A connected pendant with usable button and LED; Relay endpoints for prepare/arm/release/revoke and durable packet storage; Mac/browser transaction adapters that can hold a prepared action without committing it; Post-action proof receipts shared across relay, Mac, and browser


## What it asked for

_Nothing._
## Its own summary

Discovered the live action boundary and recorded three findings: Mac bridge is online with AppleScript automation available, but Accessibility/Screen Recording are still unavailable; browser bridge is offline with 12 pending commands and no tab; no pendant is connected. I proposed a proof-carrying cross-surface execution contract so faculty-action reports completed only after observing the required effect, with idempotent checkpoints and safe interruption. I did not execute or replay anything.

**Biggest unknown:** Whether the owner will manually bring the browser bridge and pendant online, and which proof obligations faculty-judgement should attach to its highest-priority actions.

