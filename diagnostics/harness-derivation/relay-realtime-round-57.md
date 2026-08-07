# Harness derivation — relay-realtime — round 57

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "What can you do for me right now?"
- **useful because:** When the owner is wearing the pendant, they need a quick, honest summary of what’s reachable (Mac UI, browser, server-only reads) and the safest next action. It prevents false confidence and wasted attempts.
- **path:** pendant → relay → mac-bridge → browser
- **model tier:** Realtime only summarizes; any deeper probing or execution is delegated to cheaper tiers or existing status endpoints.
- **latency:** Under a second for the spoken summary; longer only if the owner asks to proceed with a specific task.
- **cost:** Low. Dominated by a small number of status reads; execution is separate and only happens when requested.
- **security:** Must not leak sensitive session details. Only report reachability and high-level capability, not contents of tabs, emails, or files.
- **missing:** A unified reachability snapshot API across relay, mac-bridge, browser, and pendant; A standard merge rule and TTL for status fields so stale data doesn’t get reported as live

### "“Mark this as my work checkpoint. When I’m back at my Mac, restore the exact context and tell me what changed since I left.”"
- **useful because:** The pendant is often used away from the Mac, so the owner currently cannot preserve a reliable, cross-device stopping point and resume without reconstructing it manually. A checkpoint would capture the spoken intent, relevant Mac project/app state, and authenticated browser tabs at departure, then later rehydrate that context and produce a concise delta before acting. This is a new continuity primitive, not merely a reminder or a job receipt.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime only for the brief checkpoint/resume conversation and spoken summary; a cheaper background model should normalize the checkpoint and compute the later change summary, while mac-planner and browser-extension perform the state capture/restoration.
- **latency:** Acknowledge the checkpoint in under 2 seconds; capture may finish asynchronously within 30 seconds. On resume, speak an initial status within 5 seconds and let restoration continue with progress updates.
- **cost:** Roughly $0.01–$0.05 per checkpoint/resume, dominated by background summarization and any browser/Mac vision calls; realtime tokens stay limited to confirmation and the spoken delta.
- **security:** The capsule may contain private browser URLs/titles, app names, file paths, and transcript text. Encrypt it end-to-end, retain only an owner-selected TTL, redact secrets/form fields, bind restoration to the paired device, and clearly report which surfaces were unavailable. Restoration of app/tab state is reversible but must never silently submit forms, send messages, or mutate files.
- **missing:** A durable cross-node context-capsule store with versioned schema and expiry; Mac capture and restore adapters for project/app/window state that do not rely on the disabled computer-use loop; Browser-extension capture/restore of already-open tabs with authenticated content metadata but no secret extraction; A change-diff worker that compares the departure snapshot with the resume snapshot; Pendant command and status protocol for naming, pausing, expiring, and resuming capsules; A unified receipt showing captured fields, omitted fields, restoration results, and per-surface freshness

### "“Privacy mode now. Don’t record or read anything sensitive until I say resume, and show me what you paused.”"
- **useful because:** Today there is no single owner-controlled privacy boundary spanning the worn microphone, relay memory, Mac activity, and authenticated browser. The owner should be able to establish a spoken privacy perimeter while walking into a meeting or sensitive environment, then receive a verifiable resume receipt rather than trusting that one component stopped while another continued.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime handles the short mode command and status acknowledgment; deterministic firmware/relay controls enforce capture behavior, while a cheap background model is used only to summarize paused events after resume.
- **latency:** The pendant must acknowledge and enforce the mode locally in under 500 ms, even if LTE or the Mac is unavailable. Cross-node pause propagation should complete within 3 seconds, with explicit degraded status for nodes that did not confirm.
- **cost:** Near-zero model cost for entering/exiting mode; about $0.005–$0.02 for an optional post-resume digest. Engineering and device firmware dominate rather than API spend.
- **security:** Privacy mode must fail closed for recording and content ingestion, use a local button/LED indication, and persist an auditable monotonic mode interval. The relay must discard audio rather than merely mark it private; queued transcripts and browser extracts must be encrypted and excluded from downstream agents. The owner must be able to inspect and delete the interval, and a node that cannot confirm must be reported—not implied paused.
- **missing:** An offline pendant privacy-mode state machine and local LED/button indication that survives a dropped uplink; A relay ingestion gate that drops audio/transcripts during the interval and propagates signed mode epochs to downstream nodes; Mac and browser adapters that stop capture, queued commands, page reads, and telemetry, then return explicit acknowledgments; A tamper-evident privacy receipt and dashboard view of each node’s pause/resume state; A safe reconciliation protocol for events generated during a partition, with no retroactive ingestion unless the owner explicitly requests it


## Changes it proposed to its own stack

### `integration` — Add a unified reachability snapshot endpoint (or tool) that merges relay, mac-bridge, browser-extension, and pendant telemetry into a single typed status object with TTLs and confidence levels. Provide a small, stable schema and a merge rule that treats expired data as unknown and transport-online-but-action-unreachable as degraded.
- **owner gets:** They get a truthful “what’s possible right now” answer and avoid asking for actions that will fail. It also reduces chatter and retries when a surface is offline or degraded.
- effort: Medium. Needs coordination across relay, mac harness, browser harness, and pendant telemetry. Mostly glue and schema discipline, plus tests for staleness/merge behavior.  ·  risk: If merge logic is wrong, we could misreport availability. Mitigate with conservative defaults (unknown beats guessed), explicit TTLs, and logging.
- cost: Low ongoing cost. One small status call per request; minimal bandwidth.  ·  latency: Improves perceived latency by preventing doomed attempts and reducing back-and-forth.
- security: Low, as long as payload contains only reachability metadata and not user content.
- depends on: Pendant telemetry availability and a stable status feed from each surface

### `context` — Make tool discovery authoritative. Ensure anything callable by the relay appears in the discover('tools') list, and anything listed can be described via describe(name). If tools are injected via system prompt, register stubs so discovery stays consistent.
- **owner gets:** Reduces failures and weirdness in the voice experience. If I can’t reliably discover tools, I either underuse capabilities or call the wrong thing.
- effort: Low to medium. Requires aligning the tool registry and the discovery/describe endpoints, plus tests.  ·  risk: Minor. The risk is breaking existing discovery; mitigate with backward-compatible registration and fallbacks.
- cost: Minimal.  ·  latency: Neutral; fewer failed discovery attempts.
- security: Neutral; this is metadata hygiene.

### `routines` — Build a real scheduler using Worker Cron triggers and/or Durable Object alarms. Support delayed execution and periodic checks, with clear ownership of what runs where and how results are reported back to the relay.
- **owner gets:** Enables “later” tasks (follow-ups, recurring checks) without leaving the relay guessing or relying on the Mac being online.
- effort: High. Needs persistence, idempotency, and a reporting path back to the relay and voice UI.  ·  risk: Scheduling bugs can spam or miss tasks. Mitigate with receipts, undo, and idempotent job keys.
- cost: Moderate; background work has ongoing compute/storage costs.  ·  latency: Improves responsiveness by moving non-urgent work off the live voice path.
- security: Requires careful auth and scoping for any background access.

### `hardware` — Add a low-power 3-axis accelerometer/proximity-orientation sensor and a small haptic actuator to the nRF9160 pendant, with firmware exposing signed worn/removed transitions and private vibration patterns. On removal, firmware immediately enters a local capture-suspend state; on re-wear it requires a deliberate button gesture to resume. The relay, Mac, and browser consume the signed epoch to pause or restore their own capture and return node-by-node receipts.
- **owner gets:** The owner gets a physical, private safety boundary that works when they forget to speak or cannot look at the LED: taking the pendant off stops its microphone path and tells the rest of the hive not to continue collecting sensitive context. A vibration confirms state silently in a meeting, and re-wearing does not unexpectedly resume recording.
- effort: Moderate hardware respin and enclosure work, low-to-moderate firmware work, then relay/Mac/browser protocol integration and field testing for false removal detection.  ·  risk: False removal or re-wear events could interrupt a conversation or leave capture paused. Debounce transitions, require stable orientation for several seconds, expose a clear LED/haptic code, and let the owner override with the button. If the sensor fails, default to privacy-paused rather than recording. Recovery is a deliberate resume gesture and an auditable receipt.
- cost: Approximately $3–$8 incremental components and PCB/enclosure changes at low volume, with roughly 1–3 mA average sensor draw and brief haptic peaks; battery life may fall modestly. No meaningful per-request API cost.  ·  latency: Local suspend indication under 100 ms; LTE propagation to relay and other nodes remains bounded by network latency, with the relay treating the local epoch as authoritative immediately.
- security: Improves privacy by making capture suspension local and fail-closed. Signed monotonic epochs prevent stale Mac/browser acknowledgments from re-enabling capture; wear telemetry itself should be minimized and retained only as mode transitions.
- depends on: An explicit signed privacy-mode epoch protocol across pendant, relay, Mac, and browser; Firmware flash/RAM budget validation and a hardware revision; Downstream adapters that honor pause epochs and produce truthful acknowledgments


## What it asked for

_Nothing._
## Its own summary

Discovery shows the production tool list is present, and relay_job_status is describable and usable for checking prior Mac work without touching the Mac. However, two tools named in the ‘granted’ list (relay_route_intent and server_browser_actions) are not discoverable/describable via the standard discovery path, which means capability discovery is inconsistent. Proposed a unified reachability snapshot capability and the integration change it needs, plus a discovery/registry fix and a real scheduler for delayed/recurring tasks.

**Biggest unknown:** Actual live reachability right now (pendant, mac action readiness, browser online state) via a single authoritative status feed. Today it must be inferred from multiple sources and may be stale.

