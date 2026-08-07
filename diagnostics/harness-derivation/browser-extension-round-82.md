# Harness derivation — browser-extension — round 82

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Read my Gmail, GitHub, or calendar in Safari, even if the browser bridge is asleep, and tell me what needs attention."
- **useful because:** The owner has repeatedly asked for private Gmail/GitHub/calendar reads and currently gets failures when Safari has no live extension heartbeat. This uses the Mac to wake the real Safari extension, the browser to retain authenticated sessions, the relay to keep the request alive, and the pendant to deliver a concise result—something no single surface can do.
- **path:** relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Use the cheap planner for target classification and bridge-health recovery; use realtime only to acknowledge and speak the final short digest. Escalate to a stronger model only when cross-site reconciliation or urgency ranking is ambiguous.
- **latency:** Acknowledge immediately; allow up to 15 seconds to open/wake Safari and obtain a heartbeat, then 30–45 seconds for authenticated reads. If the Mac is unavailable, report a clear offline result rather than looping.
- **cost:** Usually one low-cost planner invocation plus one browser read; roughly <$0.01 excluding any premium model escalation. Browser extraction and Mac wake dominate latency, not tokens.
- **security:** Read-only by default; use the existing Safari profile and never transmit cookies or passwords to the relay. Restrict navigation to the requested origins, redact tokens/query strings in spoken/logged output, and stop before sending mail, changing calendar events, or mutating GitHub. Ask for confirmation only for those irreversible mutations, consistent with owner policy.
- **missing:** A cross-surface browser bootstrap action: Mac opens/activates Safari and waits for the extension heartbeat, then the browser bridge retries the queued read against Safari—not the never-seen home-chrome device.; An origin-aware read recipe for Gmail/GitHub/calendar plus concise urgency and provenance merging (the current origin fan-out still requires caller-supplied origins and has no web-content urgency scorer).; A durable result handoff from the browser job to relay audio when the original voice turn has ended.


## Changes it proposed to its own stack

### `browser-harness` — Add device-liveness leases and a dead-letter/recovery queue to the browser bridge. A command must target a registered extension with a fresh heartbeat (for example, heartbeat age < 2 lease intervals) and matching browser/device affinity before it can be claimed; an offline or never-seen device may not claim work. Requeue commands whose lease expires, cap attempts with exponential backoff, and quarantine stale commands with a typed reason (offline_device, expired_lease, tab_missing, or result_timeout). Expose queue health (pending/leased/expired/dead-letter, target device, age, attempts) and provide an explicit retry/rebind operation for the planner. Preserve authenticated work on Safari rather than silently routing it to the unused home-chrome stub.
- **owner gets:** The owner's private browser tasks will either run on the real logged-in Safari or clearly explain why they cannot. They will not sit for hours as 'processing', get claimed repeatedly by an offline fake device, or risk a future command being sent to the wrong browser. Recovery after reopening Safari becomes automatic and observable.
- effort: Moderate: extend browserBridge queue records and heartbeat registry, add lease sweeper/backoff/dead-letter persistence, status fields, and tests for offline/never-seen devices and restart recovery.  ·  risk: A heartbeat outage could temporarily defer legitimate work; recover by explicit retry/rebind after Safari heartbeats. Never drop commands silently: retain full payload and reason in dead-letter storage, with bounded retention. Avoid exposing page contents in queue-health responses.
- cost: No meaningful model/API cost; small local JSON/D1 storage and a low-frequency sweeper.  ·  latency: Adds only a heartbeat/lease check before execution; retries back off instead of burning 45-second waits. Successful commands remain unchanged.
- security: Improves isolation: device-target and session affinity are enforced, and authenticated commands cannot fall through to an unrelated device. Queue diagnostics must redact URLs/query strings and action text unless requested by the owner.
- depends on: A durable browser command/job record (the existing browser queue and session store are sufficient initially; full durable job runner remains useful but is not required).; Heartbeat endpoint must record last-seen extension/device identity and capabilities.

### `integration` — Add a private-browser self-healing handshake across Mac and Safari: when a browser read is requested and no valid Safari heartbeat exists, the local Mac agent may activate Safari and the AI Pendant Browser Bridge, issue a harmless Start Page/no-op ping, and wait for a fresh heartbeat before dispatching the original read. Bind the request to Safari's extensionId and abort if only the never-seen home-chrome stub responds. Return a typed unavailable reason instead of leaving the voice job pending.
- **owner gets:** Asking to read Gmail, GitHub, or calendar works after Safari has been idle or closed, without the owner manually opening a tab or retrying. It preserves the owner's existing login and avoids silently using the wrong browser.
- effort: Moderate: add a Mac action/health handshake, extension capability response, bounded wait, and integration tests for Safari closed, bridge asleep, and wrong-device heartbeat.  ·  risk: Safari may be unavailable, locked, or require a user gesture; recover by reporting unavailable and leaving the original read untouched. A no-op tab activation must never navigate to an unrequested origin or alter page state.
- cost: No external API cost; a few local Mac actions and one heartbeat round trip per recovery.  ·  latency: Only offline recovery adds up to 10–15 seconds; healthy browser reads are unchanged.
- security: Improves security by refusing fallback to an unrelated device. The handshake carries only extension identity/capabilities, not cookies or page text; origin allowlisting remains enforced for the actual read.
- depends on: A working browser device heartbeat/lease registry and device-aware queue fencing.; A Mac action that can activate Safari and the installed AI Pendant Browser Bridge without granting broad unrelated desktop control.

### `interaction` — Add an owner-triggered browser privacy kill switch spanning pendant, relay, Mac, and Safari: a dedicated pendant long-press or spoken emergency phrase immediately cancels queued and leased browser commands, revokes active browser evidence/session capabilities, asks the Mac bridge to close authenticated tabs, and returns a signed completion receipt. It must be distinct from ordinary action approval: it is always available, does not block normal work, and is safe to repeat while offline (the pendant stores the revocation epoch and the relay/Mac enforce it when they reconnect).
- **owner gets:** If the owner lends the Mac, loses the pendant, notices a sensitive page was opened, or simply wants private browsing stopped now, they can shut down every AI-held browser action from the device they are wearing. Today there is no single gesture that reaches the browser queue, Mac bridge, relay, and authenticated Safari session together.
- effort: High cross-surface integration: firmware gesture/state, signed revocation epoch, relay fan-out, Mac bridge cancellation and Safari tab closure, plus restart/offline reconciliation and an auditable receipt.  ·  risk: Closing tabs can discard unsaved human work, so the default should cancel AI commands and revoke access immediately, then close only AI-owned tabs; the owner may explicitly choose all authenticated tabs. If a node is offline, persist the revocation and show pending surfaces rather than claiming completion. Avoid logging URLs, page text, or credentials.
- cost: Negligible inference/API cost; small durable revocation record and one low-rate control message per surface. Hardware can use an existing button/gesture if available.  ·  latency: Pendant-side revocation is immediate locally; relay/Mac/Safari convergence target under 2 seconds when online, with explicit per-surface status if not.
- security: Strongly improves containment: monotonic signed epochs prevent replay of old browser commands, and every command checks the current epoch before claim and before execution. The receipt proves cancellation/revocation state without including private page content.
- depends on: A durable browser command identity and lease model.; Bridge support for command cancellation and AI-owned tab tracking.; A pendant firmware event or spoken control path that works while the network is unavailable.


## What it asked for

_Nothing._
## Its own summary

Live discovery found a concrete browser failure: Safari is offline, the never-seen home-chrome stub is also offline, yet /browser/poll is still serving a 3-hour-old navigate command marked processing and claimed by home-chrome after 9 attempts. I proposed (1) device-liveness leases with stale-command quarantine/dead-letter recovery, (2) a cross-surface Safari wake/heartbeat handshake for private reads, and (3) a capability to read authenticated Gmail/GitHub/calendar with relay-to-pendant delivery. The current browser queue and session records are present, but they are not reliably connected to a live extension.

**Biggest unknown:** I still need a functioning Safari extension heartbeat/command path (or an orchestrator-provided way to wake it). The granted browser enqueue tools remain schemas/stubs, and no authenticated browser workflow can be verified while Safari reports offline. I also still lack the owner's preferred Gmail/GitHub/calendar origin list and urgency sensitivity, though the existing request history confirms those three are high-value.

