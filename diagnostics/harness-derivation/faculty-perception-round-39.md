# Harness derivation — faculty-perception — round 39

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-perception-and-permissions** — At 2026-08-07T10:59:23.539Z, Mac agent /observe reports Accessibility trusted=false, screenRecording=false, input reachability failed, and uiActionsWillReachScreen=false for AI Pendant Agent. /ops/status at same run reports computerUse.loopEnabled=false, visionModelConfigured=true, visionUploadConsented=false, maxSteps=25. Therefore computer-use loop and trustworthy UI/pixel interaction are not currently available.
  - evidence: GET /observe and GET /ops/status HTTP 200 responses, observedAt 2026-08-07T10:59:23.539Z.
- **machine-timezone** — Mac machine-context currently reports timezone America/New_York. This is a machine-derived candidate, not independently authoritative owner timezone.
  - evidence: GET /machine-context HTTP 200 response observed during round 39 at 2026-08-07T10:59Z.
- **cross-surface-availability** — At 2026-08-07T10:59Z the Mac bridge is online and relay reachable, but browser extension home-chrome is offline; 3 durable browser sessions remain on Mac and 3 browser commands are pending. Browser sessions therefore exist locally but cannot currently be driven through the extension.
  - evidence: GET /ops/status and GET /observe HTTP 200 responses; browser.online=false, home-chrome offline, pendingCommands=3, macBridgeOnline=true.

## Capabilities it proposed

### "Let me say, “Prepare this application but do not submit it until I physically confirm on my pendant,” and have it remain safe and recoverable even if Chrome, the Mac, or the network drops."
- **useful because:** Today a prepared web action is either tied to a live browser or becomes an untracked draft. The owner needs a trustworthy middle state for consequential forms, purchases, messages, and permissions: complete preparation without accidental submission, then confirm from the device they are wearing.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheaper background model for extracting fields, validating constraints, and reconciling checkpoints; use realtime only for the short spoken interaction. The browser extension owns the authenticated page, the Mac bridge supplies accessibility/vision evidence, the relay durably stores an encrypted escrow record, and the pendant supplies an explicit physical confirmation.
- **latency:** Preparation may take seconds and can continue asynchronously. Confirmation feedback should be under 1 second when the pendant and relay are connected; recovery after a dropped surface can take a few seconds.
- **cost:** Usually low: background text/vision validation dominates, roughly cents per complex form; realtime cost is limited to the confirmation exchange. Storage and relay traffic are negligible.
- **security:** Never transmit credentials or raw secrets to the relay; encrypt the escrow payload end-to-end or retain sensitive values only in the browser. Bind the escrow to origin, account/session, form hash, intended recipient/amount, and expiry. A changed page, changed total, expired escrow, lost browser session, or mismatch must invalidate confirmation. Pendant confirmation must be a deliberate button gesture plus spoken summary, not voice alone. Require confirmation again after any material field change; provide cancel and automatic expiry.
- **missing:** A first-class browser transaction-escrow protocol with durable encrypted checkpoints and origin/session binding; A pendant confirmation primitive that survives network loss and cannot be confused with ordinary speech; Mac/browser snapshot hashing and typed field-level diffs so the system can prove what will be submitted; Relay support for encrypted escrow retention, expiry, and replay-safe recovery; Dashboard and receipt UI showing prepared-vs-submitted state and the exact final payload; A cross-surface preflight contract that treats any stale permission, missing browser heartbeat, or changed page as unknown rather than success


## Changes it proposed to its own stack

### `mac-harness` — Add a permission-integrity watchdog that periodically compares the running AI Pendant Agent executable identity (bundle id, bundle path, node exec path) with the macOS TCC grants, runs a zero-delta input probe, and publishes a signed capability state. If trusted=false or screenRecording=false, automatically mark UI/pixel actions as unverifiable and expose a one-click remediation instruction naming the exact binary; never report action success as completion.
- **owner gets:** The owner will stop receiving convincing but false 'done' receipts when macOS granted permissions to the wrong helper or a stale binary. Computer use either becomes trustworthy or clearly unavailable before anything is changed.
- effort: Medium: permission probe integration, identity matching against TCC, status schema, and receipt gating; no new model required.  ·  risk: A transient TCC or probe failure could conservatively disable computer use. Recover by retrying with backoff and allowing explicit re-probe after the owner grants access; retain observation-only routes.
- cost: Negligible API cost; local periodic probes only.  ·  latency: Adds milliseconds to preflight and periodic heartbeat, avoiding costly failed action loops.
- security: Improves security by preventing unverified UI actions and names the exact local binary without exporting secrets or screenshots.
- depends on: A reliable TCC query for the exact running binary; Action receipt/preflight state machine consuming signed perception state


## What it asked for

_Nothing._
## Its own summary

Round 39 established fresh, contradictory reality: the Mac bridge and relay are online, but exact running AI Pendant Agent still lacks effective Accessibility and Screen Recording; input reachability fails, computer-use loop is disabled, vision upload consent is absent, and browser extension is offline. Recorded these facts and machine timezone America/New_York, informed mac-vision and faculty-judgement, and proposed a permission-integrity watchdog that prevents false action receipts.

**Biggest unknown:** Whether the owner has actually granted TCC permissions to the exact running AI Pendant Agent binary and whether vision-upload consent/loop enablement is intentionally withheld; the live probes still say no.

