# Harness derivation — faculty-perception — round 83

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live-devices** — At 2026-08-07T13:26Z, relay device registry reports home-macbook-bridge online; home-chrome offline; cloudflare-contract-test mobile offline. No pendant/nRF9160 device is registered or online.
  - evidence: discover(devices) returned exactly three devices, with home-macbook-bridge online and both home-chrome/cloudflare-contract-test offline.
- **mac-permissions** — Mac local agent is reachable and full-control/planner enabled, but Accessibility and Screen Recording are both ungranted; permissions.ready=false. AppleScript automation grant cache is true for listed apps.
  - evidence: GET /ops/status at 2026-08-07T13:26Z: accessibility.trusted=false, screenRecording.granted=false, requiredMissing=[], ready=false.
- **browser-connectivity** — Browser bridge is offline and has 9 pending commands; no browser inspections exist. Browser-dependent logged-in reads cannot currently be verified or completed.
  - evidence: GET /ops/status browserExtension.online=false, pendingCommands=9; GET /browser/inspections returned inspections=[]; discover(devices) lists home-chrome offline.
- **timezone-conflict** — Owner memory says authoritative timezone America/Chicago, while the live Mac machine-context reports timezone America/New_York. Time-sensitive interpretation must use owner timezone until reconciled, not the machine value.
  - evidence: owner.discover remembered timezone America/Chicago; GET /machine-context reports machine.timezone America/New_York.
- **audio-path** — Relay and Mac have a recorded 24 kHz mono PCM TTS path, but this is historical pipeline evidence; with no pendant registered, end-to-end pendant delivery/playback is unverified. A recent run rendered 75,734 PCM bytes and relay accepted it for an nRF9160 that is not live.
  - evidence: GET /pipeline event metadata: sampleRate=24000, format=s16le, channels=1, pcmBytes=75734; discover(devices) shows no pendant.

## Capabilities it proposed

### "“What actually happened while I was offline?” — Give me a causally ordered, evidence-linked timeline for one request, showing when my voice was captured, when the relay received and forwarded it, whether the pendant actually acknowledged playback, and whether the Mac or browser action really completed; clearly separate observed facts from queued or inferred steps."
- **useful because:** Today a relay receipt or rendered PCM can look like success even when no pendant received it, and a planned Mac/browser action can be mistaken for completion. This gives the owner one trustworthy answer after reconnecting, especially for requests made while walking or out of coverage.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** Use deterministic event correlation and a cheap background summarizer for the timeline; reserve realtime only for the owner's spoken question and final concise explanation.
- **latency:** Under 2 seconds when all receipts are stored; if a device is still offline, return the partial timeline immediately and mark the missing acknowledgment rather than waiting on a timeout.
- **cost:** Usually <$0.01 per inquiry; most work is indexed event joins, with a small summarization call only when the timeline needs prose.
- **security:** The timeline may expose private audio metadata, browser URLs, and action contents. Keep raw payloads local/relay-scoped, redact secrets and page text by default, require explicit expansion for sensitive evidence, and never imply playback or execution without a device acknowledgment.
- **missing:** A durable cross-surface event envelope with one request/correlation ID and monotonic plus wall-clock timestamps; Pendant playback-start/playback-complete acknowledgments bound to the response artifact; Relay delivery receipts that distinguish accepted, forwarded, downloaded, and acknowledged; Mac and browser action receipts linked to the originating request, including failure and cancellation states; A read-only owner timeline endpoint/dashboard view with provenance and uncertainty labels; A real registered pendant for validating the end-to-end acknowledgment path

### "“I’m heading out—what will still work if I lose coverage?” Give me a short, live capability forecast for the next few minutes: which spoken requests the pendant can capture offline, which replies are already cached for playback, which Mac/browser actions are impossible until reconnect, and what will be queued versus discarded."
- **useful because:** Today the owner cannot tell whether a spoken request will be answered locally, silently wait in the relay, or fail because the pendant or browser is absent. A pre-departure forecast prevents lost requests and makes offline behavior predictable rather than retrospective.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified → dashboard
- **model tier:** Deterministic availability evaluation from device heartbeats, cached-audio inventory, browser state, and action safety; use a cheap summarizer for one short spoken sentence. Realtime is only the delivery channel.
- **latency:** Under 500 ms when the registry and caches are current; include heartbeat ages and mark the forecast stale rather than blocking.
- **cost:** Near-zero API cost; periodic heartbeats and a compact availability projection are the main resource cost.
- **security:** Do not expose private queued commands or cached message contents in the forecast. Report capability classes and counts, not sensitive URLs, audio text, or action parameters; require confirmation before queuing any side effect for later execution.
- **missing:** A signed, shared capability/availability advertisement from pendant, relay, Mac bridge, and browser bridge; A pendant-local inventory of cached responses with expiry and playback state; A distinction between offline-safe capture, deferred planning, and actions forbidden to queue; A reconnect policy that expires stale queued requests and reports the reason; A compact spoken forecast renderer and dashboard detail view


## Changes it proposed to its own stack

### `context` — Add a live-reality gate to every device, audio, browser, and time-sensitive result: before reporting success, join the artifact with the current device registry and permission state; downgrade historical relay receipts to 'queued/unverified' when no target device is registered, mark browser work blocked when its bridge is offline or commands age past a threshold, and surface timezone conflicts (owner memory versus machine-context) instead of silently choosing one.
- **owner gets:** The owner will stop hearing that a pendant played audio, a browser read a private page, or a reminder used the right local time when those things were only recorded or queued. They get an honest short answer and a concrete reason when the system cannot know.
- effort: Medium: typed truth-status schema, joins in pipeline/browser/routine result composers, and tests for absent device, stale command, missing permissions, and timezone disagreement.  ·  risk: Some previously optimistic completions become 'unverified' or blocked; recover by preserving raw receipts and allowing re-check once a device/bridge returns. Avoid leaking private page contents in status messages.
- cost: Negligible API cost; fewer unnecessary model turns because deterministic gates answer availability first.  ·  latency: Adds one local/relay registry lookup, expected tens of milliseconds; avoids long browser timeouts and misleading waits.
- security: Improves security by preventing claims of actions on absent devices and by keeping sensitive browser content out of generic status projections.
- depends on: Authoritative relay device registry and delivery acknowledgments; Typed context/provenance projection; Owner timezone authority (currently America/Chicago in memory, conflicting with live Mac America/New_York)


## What it asked for

_Nothing._
