# Harness derivation — browser-extension — round 68

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser queue health** — GET /browser/status reports Safari offline, only home-chrome registered with no tab, and 5 pending commands; GET /browser/poll nevertheless claims an old navigate command for home-chrome at attempts=4, indicating stale retry/affinity failure rather than merely no tab.
  - evidence: GET /browser/status 200 and GET /browser/poll 200 responses in round 68

## Capabilities it proposed

### "When I ask “is my browser there, and what happened to my last browser task?”, give me one truthful spoken answer: which browser device is reachable, whether it has a usable tab, what the last command did or failed to do, and the safest next step; if it is safe, resume only the read-only part after I say “resume.”"
- **useful because:** Today the owner can receive contradictory device states and has no dependable way to distinguish an unexecuted private-page action from a command repeatedly claimed by a dead or wrong browser device. This turns a silent failure into an immediate, evidence-backed answer from the pendant, while preserving the owner’s authenticated browser access and preventing accidental replay of typing or clicks.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use deterministic heartbeat/queue reconciliation and receipt lookup first; use the realtime model only to turn the typed evidence into a short spoken explanation and interpret “resume.” No background model call is needed.
- **latency:** Status and last-result evidence should be under 1 second from cached fleet state; spoken explanation under 2 seconds. A read-only resume may take one browser poll/result cycle. Never wait silently for an offline extension.
- **cost:** Usually near-zero model cost when templated; at most one short realtime turn (roughly <$0.01 depending on provider). Dominant cost is extension/server engineering and bounded queue history, not inference.
- **security:** The response must not expose page URLs, titles, or private content beyond what the owner asked for; return redacted command labels and scoped evidence. Bind every resume to the original extensionId/tab/session and require an explicit spoken resume. Never replay click/type/select/submit actions automatically; preserve receipts proving whether an action ran.
- **missing:** A single heartbeat-derived device-health record shared by browser status, generic device registry, and mac-planner; Queue leases, typed terminal states, and command receipts that distinguish never-run, processing, succeeded, failed, and expired commands; A relay/mac-planner intent that compiles browser health plus last-command evidence into a compact spoken status card; A read-only resume operation that can rebind only navigation/read/extract work after the owner explicitly says resume


## Changes it proposed to its own stack

### `browser-harness` — Add a lease-aware browser command quarantine and recovery protocol. Each queued command gets target extensionId, tab/session requirement, idempotency key, lease expiry, attempt history, and last error. The poller must not claim commands for an offline/non-reporting device (or keep retrying a command whose target has never produced a tab); after lease expiry it moves the command to a typed dead-letter state with reason (offline_device, missing_tab, expired_result, or extension_error). A recovery endpoint/job should emit one compact evidence card to mac-planner/relay containing queue age, command labels, attempts, and a safe recommendation: reopen Safari and retry only idempotent navigations/reads, or discard stale commands. Successful heartbeat should rebind only explicitly unbound commands; never silently replay clicks/types. Add an operator action to drain/quarantine/reset selected command IDs, with receipts and no automatic mutation replay.
- **owner gets:** When Safari disappears, the pendant currently has no trustworthy answer and old commands can be claimed repeatedly by the wrong stub device. The owner would hear exactly what is stuck, why, and the one safe way to recover—without duplicate navigation, typing, or accidental form actions when Safari reconnects.
- effort: Medium: queue schema/state machine and lease handling in browserBridge/browserSessions, heartbeat-aware poll filtering, typed status/recovery route, and a small mac-planner/relay evidence formatter; extension update only needs to report stable device identity and explicit result/error codes.  ·  risk: A command could be quarantined even though the extension is briefly slow; use a generous lease, preserve raw receipts, and allow explicit retry. Recovery must default to no replay for click/type/select/submit-like actions; idempotent reads/navigation can be retried only when their target is confirmed. Existing pending commands need a one-time migration to unknown-target/quarantined, not execution.
- cost: Negligible API cost (state transitions and short JSON evidence); modest local storage/D1 growth from bounded attempt history, with retention cleanup.  ·  latency: Adds no latency to healthy browser actions; recovery status is available immediately from queue state, while reconnect reconciliation may take one heartbeat/poll interval.
- security: Improves safety and privacy by preventing commands from leaking to the wrong registered browser and by keeping URLs/page errors in scoped, redacted evidence. Requires authenticated operator access for drain/retry and strict extensionId/session binding.
- depends on: Current GET /browser/status and GET /browser/poll plus POST /browser/result/:commandId flow; Durable browser job runner and request-id/tab-affinity work (chg-16bc5dee and chg-14accc01); Cross-node failure recovery card proposed by mac-planner, extended with browser queue evidence

### `integration` — Unify browser device health with the fleet device registry instead of exposing two contradictory truths. The browser heartbeat should publish a signed presence record (extensionId, browser/version, tabCount, active tab hash, lastSeenAt, monotonic sequence); /browser/status and the generic device list should derive the same state using one freshness window and explicit states online, stale, offline, or registered-never-seen. Include a discrepancy diagnostic when registries disagree, and pass that typed health fact into mac-planner/relay recovery cards. A stale device must not be eligible as a command target even if the generic registry says online.
- **owner gets:** The pendant can currently be told the wrong story: the device list says home-chrome is online while browser status says it is offline with no tab. One consistent status means the owner knows whether opening Safari will help, rather than losing commands into a dead browser.
- effort: Small-to-medium: define the heartbeat schema and freshness calculation, update registry/status adapters and command-target selection, add tests for stale heartbeats, clock skew, duplicate extension IDs, and never-seen devices.  ·  risk: A missed heartbeat may briefly label a healthy browser stale; use server receipt time plus sequence numbers and show the timestamp, never delete registrations. If extension versions cannot emit all fields, mark them unknown rather than infer health.
- cost: No model/API cost; a few bytes per heartbeat and a small registry record.  ·  latency: No added action latency; status reads may perform one shared registry lookup.
- security: Avoids sending private-page commands to an unintended/stale device. Do not store raw URLs in the global registry—retain only a hash or scoped tab metadata, and authenticate heartbeat identity.
- depends on: GET /browser/status and GET /browser/poll; POST /browser/heartbeat; GET /devices/device registry surface; The browser queue lease/quarantine change proposed this round


## What it asked for

_Nothing._
## Its own summary

Discovered and recorded two new browser/integration gaps. Live evidence: /browser/status says Safari offline, only never-seen home-chrome with no tab, 5 pending commands; /browser/poll is nevertheless repeatedly claiming an old navigate for home-chrome (attempts=4). Proposed (1) lease-aware command quarantine/dead-letter and explicit safe recovery with no click/type replay, and (2) one unified heartbeat-derived device-health registry so /devices and /browser/status cannot disagree. Sent the concrete incident evidence to mac-planner.

**Biggest unknown:** The browser command enqueue wrappers remain implementation stubs, so I cannot perform a real navigate/read test or verify recovery end-to-end. I also still lack the owner's first authenticated workflow and sensitivity preferences; those were already requested and should not be re-requested this round.

