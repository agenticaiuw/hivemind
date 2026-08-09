# Harness derivation — faculty-perception — round 237

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live macOS input authority** — At 2026-08-09T01:51:49Z, /observe reports Accessibility trusted, Screen Recording granted, inputReachability.status=verified, eventsPost=true, secureInputActive=false, and uiActionsWillReachTheScreen=true for com.aipendant.agent. The route does not expose lock/wake state.
  - evidence: Authenticated GET /observe HTTP 200; response accessibility and inputReachability objects.
- **iPhone Mirroring observability** — At 2026-08-09T01:51:49Z, /observe confirms iPhone Mirroring.app is running (pid 68343), but its schema contains no phone-connected, mirrored-session, device, or target-screen field. This proves app presence only, not an active iPhone link.
  - evidence: Authenticated GET /observe HTTP 200; runningApps includes iPhone Mirroring and no iPhone session object.

## Capabilities it proposed

### "“Set up and verify my pendant from this Mac, then tell me exactly what is working.”"
- **useful because:** Today the system can have firmware source and a Mac bridge yet no registered pendant; the owner should get a one-command bench-to-relay proof instead of guessing whether USB, audio, pairing, and cloud delivery each work. It would explicitly stop at the first failed layer and preserve evidence.
- **path:** mac-terminal → pendant → relay → dashboard
- **model tier:** background for firmware/serial inspection and pairing validation; realtime only for narrating the result over voice
- **latency:** 2–5 minutes for a full bench validation; under 10 seconds for a cached health summary
- **cost:** Low API cost: mostly local serial reads and relay HTTP; one background model call only to summarize measurements. Hardware bench time dominates.
- **security:** Pairing credentials and relay keys must never be echoed or stored in logs. Require explicit confirmation before flashing firmware or pairing; read-only serial identity/audio tests can run automatically. USB is a bench transport, not an assumed wearable transport.
- **missing:** A bounded serial protocol adapter that can identify the nRF9160 and ESP32 ports, read the offline-reality-beacon, and run the existing audio probe; A guided firmware flash step with explicit confirmation; A relay-side pairing/register call that links the verified device identity to the Mac test report

### "“Before you do anything in my browser, prove you are looking at the same page I am, and stop if it changed.”"
- **useful because:** A logged-in browser session can drift while a relay job is queued: tabs change, sessions expire, and a Mac action can target a different window than the extension snapshot. A cross-surface preflight would make destructive or consequential browser actions conditional on current, corroborated UI identity rather than a stale plan.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background/state comparison for URL/title/tab/session hashes; realtime only to explain a mismatch to the owner
- **latency:** Under 1 second for the preflight; fail closed if either browser or Mac observation is stale
- **cost:** Negligible model cost if implemented as deterministic comparisons; one small realtime turn only when reporting the refusal
- **security:** Never transmit page bodies or cookies to the relay for this check. Compare origin, URL/path policy, title digest, tab/window identity, and observation timestamps; require confirmation for a navigation or mutation after a mismatch.
- **missing:** A shared signed observation envelope joining browser_snapshot, /observe foreground state, and the queued Mac action; A Mac-side action gate that rechecks the envelope immediately before click/type/submit; A relay job state that records preflight passed/failed and the reason without storing secrets

### "“Before touching my iPhone, verify that a real phone is mirrored—not merely that the iPhone Mirroring app is open—and show me the exact app and screen you will affect.”"
- **useful because:** The Mac currently proves only that iPhone Mirroring.app is running; that is not proof of a connected phone, active mirror, or correct target. A witness spanning the Mac process/UI, the iOS action surface, and the relay voice request would prevent confident actions against an absent or wrong mirrored session.
- **path:** pendant → relay → mac-planner → ios-control → dashboard
- **model tier:** Deterministic Mac/UI and iOS status checks; realtime only to report the verified target or refusal
- **latency:** 1–2 seconds before any iOS action; never proceed on stale status
- **cost:** Low: local status and one screenshot/UI query; no model call unless the UI needs visual interpretation
- **security:** Do not expose message contents in relay telemetry. Record only device/session identifiers, app bundle, target title, and freshness. Mutating iOS actions still require the existing approval policy.
- **missing:** A read-only iPhone Mirroring session/status probe that distinguishes app-running from phone-connected and exposes the mirrored target; A signed freshness token consumed by ios_* actions so a status check cannot be replayed after the screen changes; A dashboard/voice result that names the target without leaking its contents

### "“Pause this task and let me resume it tomorrow from exactly the same browser tab, Mac app, iPhone screen, approvals, and pending step.”"
- **useful because:** Today the system records fragments—jobs, browser sessions, pipeline traces, and receipts—but cannot create one owner-visible, resumable checkpoint of a multi-surface task. After sleep, a tab change, or a relay restart, the owner must reconstruct where the work stopped and risks repeating or skipping a consequential step.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control → dashboard
- **model tier:** Cheap deterministic checkpoint serialization and freshness validation; use the expensive realtime model only to explain conflicts or reconstruct an ambiguous next step
- **latency:** Capture in under 500 ms; resume preflight in 1–2 seconds, failing closed when any target is stale or unavailable
- **cost:** Low API cost and bounded local storage per checkpoint; the dominant cost is optional model reasoning only when the saved plan is ambiguous
- **security:** Checkpoint metadata must omit page bodies, message contents, cookies, and secrets. Mutations must never replay automatically: resume restores context, revalidates every target, and asks for confirmation before the next irreversible action. Encrypt or access-control iPhone/browser identifiers.
- **missing:** A durable cross-surface checkpoint schema linking relay job, Mac ledger step, browser tab/session, iPhone Mirroring target, and pending approval; A restore validator that compares saved identities and freshness before handing control to action; A user-facing resume/abandon/inspect flow on the dashboard and pendant

### "“For anything irreversible, ask me for a physical button confirmation on the pendant, and do not act unless that exact approval is tied to the current screen and action.”"
- **useful because:** Dashboard approval is easy to miss or can become stale while a browser, Mac, or mirrored iPhone target changes. A tactile confirmation from the worn device would give the owner a fast, unambiguous consent channel and bind consent to one displayed action instead of trusting a delayed UI click.
- **path:** pendant → relay → mac-planner → browser-extension → ios-control → dashboard
- **model tier:** Deterministic policy and token verification; realtime only to speak the concise approval request and result
- **latency:** Approval request under 300 ms; expire tokens after 30 seconds or any target/context change
- **cost:** Very low API cost; a small bounded pending-approval record and one relay round trip dominate
- **security:** Use single-use, nonce-bound approval tokens containing action digest, target identity, expiry, and origin. Never treat a button press as blanket consent. Do not include secrets in the spoken prompt or token; require a second confirmation for destructive bulk actions.
- **missing:** Firmware support for a distinct confirm/reject gesture and monotonic sequence number; Relay endpoint to mint and consume single-use approval challenges with replay protection; Mac/browser/iOS action gates that verify the challenge against the exact current action and target

### "“Keep this task entirely on my Mac and browser; prove before and after that no page text, audio, or secrets crossed to the relay.”"
- **useful because:** The owner currently cannot tell, per task, whether a relay voice turn, browser read, TTS job, or Mac delegate transmitted content off-device. A locality contract would let them use the system with confidential work by making data residency an enforceable, inspectable property rather than a hope based on tool choice.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic routing and byte/classification accounting; use a cheaper background model only to classify ambiguous content, never as the enforcement point
- **latency:** Policy check under 100 ms before each tool call; end-of-task receipt within 1 second
- **cost:** Low runtime API cost; storage for redacted transfer manifests is bounded. Classification of sensitive text is the main variable cost and should default to local rules.
- **security:** The relay must not receive raw content merely to prove it did not receive raw content. Enforce deny-by-default routes, emit signed byte-count/type manifests, redact URLs and metadata, and require explicit confirmation to leave local-only mode. A compromised local process remains outside this guarantee.
- **missing:** A task-scoped locality policy propagated from voice to Mac, browser, and iOS actions; Relay and Mac egress middleware that denies non-approved uploads and records tamper-evident transfer manifests; A dashboard receipt showing destinations, content classes, byte counts, and policy decisions


## What it asked for

_Nothing._
## Its own summary

Fresh discovery changed an important constraint: Accessibility and Screen Recording are now granted for com.aipendant.agent; /observe reports inputReachability.status=verified, eventsPost=true, secureInput=false, and UI actions will reach the screen. The Mac bridge and Safari extension are online; relay is reachable on D1. /observe still has no lock/wake state, and iPhone Mirroring being running is not evidence that a phone is connected. I recorded three new capabilities: a USB-to-relay pendant setup proof, a cross-surface browser identity preflight, and an iPhone Mirroring session witness. The first is the most immediately testable with the bench hardware; the latter two require new signed freshness/status joins.

**Biggest unknown:** The pendant's actual USB serial identity and whether either chip is physically available to this running Mac agent remain unverified: the system can observe the relay registry but has no callable bounded serial reader. I still need that adapter, a lock/wake observation source, and a real iPhone Mirroring session/status probe. The browser preflight also needs a shared signed observation envelope rather than independent stale snapshots.

