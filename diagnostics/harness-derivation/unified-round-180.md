# Harness derivation — unified — round 180

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say 'what did I just authorize?', tell me exactly which action was approved, where it ran, whether it completed, and what evidence proves it—without replaying secrets or claiming success from a mere dispatch."
- **useful because:** The owner gets a trustworthy answer after voice commands, browser forms, or delayed Mac jobs. It closes the dangerous gap between spoken intention, physical approval, execution, and actual effect.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic receipt join and evidence classifier first; realtime model only turns the verified result into a short spoken answer. Background model may summarize a long history.
- **latency:** For a recent action, answer within 1 s from cached receipts; historical evidence lookup under 3 s. Never wait on a browser action while speaking an unverified success claim.
- **cost:** Near-zero for deterministic joins; $0.002–$0.01 for a spoken explanation. Storage/indexing and browser evidence collection dominate.
- **security:** Require the current session or physical approval nonce to query sensitive receipts; redact secrets and page contents; distinguish planned, dispatched, accepted, completed, and owner-observed states. Refuse when evidence is stale, ambiguous, or bound to another tab.
- **missing:** A durable cross-surface receipt index joining ledger step, relay job, browser command, audio delivery, and physical approval nonce; A strict evidence-state vocabulary and retention/deletion policy; A pendant query gesture or next-turn intent that cannot accidentally execute anything

### "If the Mac, browser, or relay is unhealthy, say what is broken, what I can still safely do over USB, and offer one reversible repair; after I approve, verify the same job and tell me what changed."
- **useful because:** Today a timeout or offline browser can look like a successful command or lead to repeated retries. This gives the owner a short, actionable diagnosis and a recovery path that respects the live USB-connected pendant even when LTE is unregistered.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic health correlation and repair-plan generation; realtime model only presents the diagnosis conversationally. No expensive reasoning for routine health checks.
- **latency:** Initial health answer under 2 s; safe repair under 10 s; revalidation immediately after repair and before claiming recovery.
- **cost:** Usually no model cost beyond a brief spoken response, approximately $0.001–$0.01; the cost is local probes and any browser/Mac restart.
- **security:** Read-only diagnosis by default. Repairs must be allowlisted, idempotent, scoped to named surfaces, logged with before/after receipts, and require confirmation when they could interrupt an active conversation or close a session. Never infer pendant LTE registration from Mac USB presence.
- **missing:** A real mutating implementation behind the currently unresolved fleet_health_and_repair repair branches; A lease-aware relay job requeue policy and orchestrator ledger closure before automatic retry; A USB-aware health adapter that reports the pendant and ESP32 bridge independently

### "When LTE is unavailable but my pendant is plugged into this Mac, let me issue a command by voice over the USB session; show that the command stayed local, preserve turn order across the transport handoff, and refuse any action that would need relay or browser credentials I did not explicitly bind."
- **useful because:** The owner can use the wearable today while it is physically attached, instead of losing the entire assistant whenever LTE is unregistered. It turns the real USB-connected hardware into a safe local mode rather than pretending it is an LTE device.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay-realtime
- **model tier:** Local deterministic transport/session policy plus the Mac planner; use realtime only for the spoken command and response. Do not send command content to the relay when local-only mode is selected.
- **latency:** Button-to-ack under 300 ms over serial; command planning under 2 s; handoff only at a turn boundary with monotonically increasing turn and frame sequence numbers.
- **cost:** No relay inference in local-only mode; roughly $0–$0.01 for local model/planner work. USB serial and Mac execution dominate latency.
- **security:** Pair the pendant serial identity to this Mac session, display a local-mode LED/state, and keep a tamper-evident local receipt. Browser actions must name an already-bound session; no ambient credential discovery. Physical approval remains required for irreversible/off-machine work. On disconnect, fail closed rather than replaying queued commands.
- **missing:** A command/control framing layer alongside the accepted usb_fallback_audio_session; Explicit local-only routing and receipt fields distinguishing USB from LTE/relay; A serial identity/pairing record and disconnect-safe command lease

### "Treat my physically connected pendant as a presence key: for a sensitive browser or Mac action, require the pendant to be USB-attached, display the exact short action summary, and accept one physical approval; if the cable or link disappears before completion, cancel rather than retry."
- **useful because:** It gives the owner a simple, observable boundary for high-consequence actions: possession of the pendant plus a deliberate press, not merely a bearer token or a spoken phrase. It is especially useful today because the pendant and bridge are physically attached even though LTE is not registered.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic presence/nonce/lease checks and action policy; realtime model only explains the staged action in plain language.
- **latency:** Stage and show the summary within 1 s; approval receipt within 2 s over USB; abort immediately on link loss and reconcile before any retry.
- **cost:** Negligible model cost, approximately $0–$0.005 per action; serial heartbeats and receipt persistence dominate.
- **security:** USB attachment is presence, not identity: bind it to a paired device key and monotonic counter. Never treat cable presence alone as approval. Scope the approval to one plan digest, expiry, target tab/app, and world fingerprint; fail closed on disconnect or changed page.
- **missing:** A cryptographic pendant-to-Mac identity handshake over the existing serial link; A presence lease consumed by /execute and browser commands; A disconnect abort/reconciliation hook that marks the staged transaction rather than silently retrying

### "Give me temporary, scoped abilities: 'for the next hour, let this pendant approve calendar edits but not messages or purchases.' Enforce that policy across the relay, Mac, and browser, and revoke it automatically when the time or task ends."
- **useful because:** The owner gets a practical middle ground between an all-powerful bearer token and approving every harmless action individually. A stolen session, misheard phrase, or wrong tab cannot silently expand beyond the capability he granted.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic policy compiler and enforcement; realtime model only parses the spoken scope and asks for confirmation. No background model is needed.
- **latency:** Compile and display the scope within 1 s; enforce every action before dispatch; revocation should propagate within one lease interval.
- **cost:** Usually under $0.01 per grant; storage, policy checks, and receipt signing dominate rather than inference.
- **security:** Scopes must be deny-by-default and bind to action types, app/site, target accounts, expiry, and a device/session identity. Never let a model widen a scope. Physical approval is still required for irreversible or off-machine actions. Log grants and revocations without storing page secrets.
- **missing:** A common capability-token format understood by relay, Mac executor, and browser bridge; Policy enforcement before /execute and browser command dispatch, not only after planning; A dashboard and spoken readback showing the exact active scope and expiry

### "Let me submit a form without exposing my passwords or private fields to the assistant: use the Mac's credential store to fill only the named fields in the already-bound browser tab, show me the non-secret fields and destination, then ask for physical approval before submission."
- **useful because:** The owner could safely automate authenticated web work while keeping credentials outside model context, relay logs, browser receipts, and spoken audio. It turns the browser from a screen to copy into a controlled instrument.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic field allowlisting and Keychain/browser automation; realtime model handles only the user's intent and non-secret confirmation summary.
- **latency:** Preview under 2 s; credential fill and submission within normal browser latency; never speak or persist secret values.
- **cost:** Approximately $0.002–$0.01 for intent interpretation; Mac Keychain and browser operations dominate.
- **security:** Credentials must be fetched only by a local privileged helper and written directly to the bound field. The model receives field labels and redacted hashes, never values. Bind origin, tab, DOM fingerprint, destination, and plan digest; abort if any changes. Require physical_transaction_approval_latch before submit.
- **missing:** A least-privilege Mac credential broker with field/origin allowlists; Browser commands for secret fill that return no secret echo, screenshot, clipboard, or DOM value; A submission preview and post-submit evidence contract that proves effect without retaining credentials


## Changes it proposed to its own stack

### `integration` — Make the accepted USB fallback session a first-class local command transport, not audio-only: add authenticated serial session establishment, turn/frame sequence binding, local-only routing, action leases, and disconnect-fail-closed reconciliation. Route only explicitly local commands to the Mac; do not mirror them to the relay.
- **owner gets:** The owner can wear and use the pendant against the Mac today even while LTE is unregistered, without commands being duplicated or secretly leaving the machine.
- effort: Medium: serial framing and Mac route integration, then hardware-in-the-loop tests for cable removal at each command phase.  ·  risk: A framing or lease bug could drop a command or execute twice. Recover with monotonic IDs, idempotency keys, explicit aborted receipts, and no automatic replay after disconnect.
- cost: No meaningful API cost in local mode; modest persistent receipt storage and serial heartbeat traffic.  ·  latency: Improves local acknowledgement to sub-second; adds a small handshake at session start and turn-boundary handoff.
- security: Improves security only if the serial identity is cryptographically paired; cable presence alone must never authorize sensitive work.
- depends on: usb_fallback_audio_session firmware work; a pendant-to-Mac identity handshake; local-only routing fields in /plan and /execute; disconnect-safe command lease and receipt states

### `hardware` — Add a small secure element or equivalent hardware-backed key store to the next pendant revision, with an immutable device identity, monotonic anti-replay counter, and signing of USB/LTE session attestations and physical approval decisions.
- **owner gets:** The owner can trust that a physical approval came from his actual worn device, rather than from a copied serial stream, replayed packet, or software process pretending to be the pendant.
- effort: High: select and integrate a secure element, provision keys during manufacturing, add firmware signing APIs, update Mac/relay verification, and test recovery across reboot, link loss, and counter exhaustion.  ·  risk: Provisioning mistakes could permanently orphan a device; counter corruption could reject valid approvals. Provide factory recovery with a new device identity, explicit owner re-pairing, and monotonic journal checkpoints.
- cost: Roughly a few dollars per unit plus board/layout and provisioning cost; negligible runtime power compared with the modem and audio path.  ·  latency: Adds milliseconds to approval/session handshakes, not to the audio stream.
- security: Substantially strengthens identity and anti-replay. It does not make a stolen already-authorized Mac safe by itself; capability leases and physical approval remain necessary.
- depends on: A defined pendant–Mac pairing ceremony; Signed approval/session envelope shared by firmware, Mac, and relay; Receipt verification and device replacement policy


## What it asked for

_Nothing._
