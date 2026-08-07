# Harness derivation — faculty-action — round 115

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **current execution prerequisites** — Mac bridge is online and automation grants are present, but Accessibility and Screen Recording are still false; browser bridge is offline with 12 pending commands; no pendant is registered. The relay and 24 kHz TTS path are operational, but there is no end-to-end device playback verification.
  - evidence: GET /ops/status returned permissions.accessibility.trusted=false, screenRecording.granted=false, browserExtension.online=false with pendingCommands=12, relay.macBridgeOnline=true; devices discovery showed no pendant.

## Capabilities it proposed

### "When I say “send it” on the pendant, prepare the message on my Mac or logged-in browser, show me the exact recipient and content, wait for a deliberate physical button confirmation, execute once, then verify and report what actually happened."
- **useful because:** It turns a spoken intention into a safe, auditable real-world action across the wearable, relay, Mac, and private browser. The owner gets convenience without the system ever silently sending a message or submitting a form.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use realtime only to capture the short spoken intent and confirmation; use the cheaper background/local planner to gather data and prepare the draft; deterministic code performs the final commit and verification.
- **latency:** Draft in 3–8 seconds; confirmation response under 500 ms; commit and receipt within 5 seconds, with background polling for slow sites.
- **cost:** About $0.01–$0.05 per invocation depending on draft complexity; most cost is one planner call, while confirmation, commit, and verification are deterministic.
- **security:** Private page content remains on the Mac/browser unless explicitly sent to the relay. Never commit without a fresh confirmation bound to a draft hash, recipient, tab/session, and short expiry. Require an extra confirmation for destructive, financial, or external-send actions; redact secrets from receipts.
- **missing:** A durable cross-surface action state machine (draft → presented → physically confirmed → committed → verified); A pendant-local confirmation skill and confirmation event API; Proof-producing postcondition checks for Mac and browser actions; Browser bridge online and Mac Accessibility/Screen Recording grants for GUI-only steps

### "If an online action is interrupted halfway—such as a booking, purchase, form submission, or account change—tell me whether it actually happened, reconcile the browser, Mac, relay, and pendant state, and give me one safe recovery action instead of making me start over or risk a duplicate."
- **useful because:** Today a dropped bridge, timeout, or reconnect can leave the owner unsure whether an external side effect occurred. This would turn ambiguous failures into a trustworthy answer and a safe continuation, which no single node can establish alone.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic state reconciliation and cheap background polling first; invoke the realtime model only to explain the result or ask a concise clarification when evidence conflicts.
- **latency:** Initial determination in 2–5 seconds from existing receipts and browser state; allow up to 60 seconds of background reconciliation for a slow site, with the pendant announcing interim status.
- **cost:** Roughly $0.005–$0.03 per incident; storage and polling dominate, with model use only for conflict explanation.
- **security:** Private browser evidence stays on the Mac unless the owner permits relay sharing. Never retry an uncertain external mutation automatically. Match account, tab, target, and idempotency key; redact payment and secret fields. Require confirmation before any compensating or duplicate-risk action.
- **missing:** A cross-surface transaction ledger that records intent, observed side effects, and evidence independently of a single job; Site-specific postcondition and duplicate-detection adapters for browser and AppleScript actions; A reconciliation worker that survives Mac/browser disconnects and reports confidence plus next safe step; A pendant notification channel for pending, resolved, and owner-confirmation-needed states


## Changes it proposed to its own stack

### `integration` — Add a cross-surface commit protocol shared by relay, Mac agent, browser bridge, and pendant: every externally visible action receives a canonical intentId, draftHash, target fingerprint, expiry, and risk class; the relay exposes a pending-commit record, the pendant displays a distinct LED/button confirmation state, the Mac/browser executor refuses stale or mismatched commits, and completion requires a typed postcondition proof (or an explicit unverifiable result) before a receipt is spoken. Keep preparation and commit separate so reconnects cannot replay a send.
- **owner gets:** The owner can confidently say “send it” without guessing whether the right tab, recipient, or draft was used, and gets an honest answer when a site or disconnected bridge prevents verification.
- effort: Medium-high: shared schema and idempotency logic in relay/local-agent, pendant event firmware, browser and Mac adapters, dashboard review state, and integration tests for reconnect/replay.  ·  risk: A lost confirmation or site race may leave an action pending rather than completed; recover with expiry, explicit retry from the unchanged draft, and receipt/undo where supported. Never infer success from an HTTP 200 alone.
- cost: Negligible per-action API/storage cost (small D1 receipt); one extra local verification step. No new hardware required for the prototype.  ·  latency: Adds roughly 0.2–2 seconds for confirmation and postcondition verification; avoids expensive realtime calls for execution.
- security: Improves security by binding approval to exact content and target, preventing replay and confused-deputy actions; receipts must hash rather than store sensitive content.
- depends on: owner grants Accessibility and Screen Recording for GUI-only Mac steps; browser bridge reconnect/heartbeat; pendant hardware registration and a local confirmation event; a typed verify_operation_step/verify_action_proof implementation

### `integration` — Add a pendant-minted, one-shot delegation token for high-consequence actions. The pendant signs a compact scope (operation class, exact target or draft hash, expiry, and maximum amount/recipient), the relay validates it and attaches it to the job, and the Mac/browser executor must present the same token at commit. Consume it atomically and publish a tamper-evident receipt; reconnects may resume preparation but can never mint or replay the commit token.
- **owner gets:** The owner could safely authorize one precise real-world action from the device they are wearing, without granting the whole Mac agent standing authority or trusting a stale dashboard approval. A lost or compromised session would not be enough to send, buy, or submit outside that narrow scope.
- effort: High: pendant signing and secure key provisioning, relay token validation and atomic consumption, Mac/browser enforcement, key rotation/recovery UX, and tests across offline/reconnect races.  ·  risk: Lost pendant keys could strand approvals; recover through explicit re-pairing and revocation, never silent fallback. Clock skew and interrupted commits require server-issued expiry windows and an idempotent consume endpoint.
- cost: Negligible API cost and a few hundred bytes per approval; modest firmware flash/RAM and secure-element or protected-key provisioning cost if the current board lacks suitable key storage.  ·  latency: Under 300 ms for validation/consumption once connected; no extra model call.
- security: Substantially reduces confused-deputy, replay, and stale-approval risk. The signed scope must avoid embedding sensitive content; use hashes and opaque target identifiers in relay logs.
- depends on: registered pendant with protected per-device signing key; relay-side atomic token consume/revoke endpoints; Mac and browser adapters that refuse unscoped commits; owner recovery flow for key rotation and lost-device revocation


## What it asked for

_Nothing._
## Its own summary

Discovered live execution state and recorded a new cross-surface commit protocol proposal. The Mac bridge and relay are online; automation grants work, but Accessibility and Screen Recording are still missing, the browser bridge is offline with 12 queued commands, and no pendant is registered. Proposed a capability and integration change that binds a physical pendant confirmation to an exact draft hash/recipient, prevents replay, and requires typed postcondition proof before reporting success.

**Biggest unknown:** Whether the owner will manually enable the two macOS TCC permissions, reconnect the browser bridge, and register a pendant; without those, GUI/browser execution and end-to-end 24 kHz playback cannot be verified.

