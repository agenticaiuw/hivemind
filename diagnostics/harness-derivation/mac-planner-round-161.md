# Harness derivation — mac-planner — round 161

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Use my pendant as a physical handoff key: when I say “approve this” and hold its button, authorize exactly the prepared browser or Mac transaction that is shown in the receipt, then tell me what changed."
- **useful because:** It turns the wearable into a trustworthy, eyes-free confirmation device for work prepared across private browser tabs and Mac apps. The relay can keep working while the owner is away; only the pendant's deliberate gesture releases the one exact mutation, with no broad approval prompt or accidental replay.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → dashboard
- **model tier:** Realtime for parsing the spoken approval and matching it to the pending transaction; background model for preparing and validating the transaction and generating the receipt.
- **latency:** Preparation may take seconds in the background; approval-to-action should be under 2 seconds and the pendant should speak a one-sentence receipt.
- **cost:** Low per approval: one short realtime turn plus browser/Mac execution; browser and Mac calls dominate latency, not tokens.
- **security:** The relay must bind a nonce to exact action list, tab/session, before-state hashes, expiry, and device identity; never accept a generic “approve.” Do not transmit page secrets to the pendant; require a fresh physical gesture and report before/after evidence. Sending mail, deletion, and purchases remain explicitly confirmable transactions.
- **missing:** USB-serial pendant challenge/response and button gesture firmware; short-lived transaction approval endpoint in relay; browser/Mac executor support for nonce-bound prepared transactions; receipt UI/audio that shows the exact pending mutation

### "Keep me in the right attention mode automatically: when Calendar says I’m in a meeting or my Mac is presenting, silence routine pendant replies and queue them; break through only for a genuinely urgent item, then give me the queued one-sentence digest when I’m free."
- **useful because:** The system can finally be present without being disruptive. It combines calendar truth, live Mac foreground/presentation state, browser urgency, and the pendant's output path—something none of those surfaces can determine alone.
- **path:** mac-planner → relay-realtime → pendant → browser-extension → dashboard
- **model tier:** Cheap background classifier for urgency and queue compression; realtime only for the eventual spoken digest or an owner interruption request.
- **latency:** State changes should propagate within 5 seconds; routine items wait silently, urgent escalation should speak within 2 seconds once classified.
- **cost:** Very low: event-driven state checks and one batched summary; no model call for ordinary suppressed events, cheap model only when ranking a batch.
- **security:** Calendar titles, browser snippets, and foreground-app names are sensitive; keep raw data on the Mac/relay, send only urgency labels and short redacted summaries to the pendant. Never infer emergency from arbitrary page text without a clear policy and audit trail.
- **missing:** Mac presentation/meeting-state detector without relying on Screen Recording permission; relay-side per-owner attention state and suppression queue; pendant command/event for quiet-mode status and digest playback; browser watch events mapped to urgency rather than daily polling

### "Even without LTE, let my pendant work through the Mac it is plugged into: press the button, speak a short command, have the Mac/relay perform local actions or read my calendar and browser, and play the result back; sync the transcript and receipts when the pendant reconnects."
- **useful because:** This is usable today while the nRF9160 is USB-attached but unregistered: the wearable remains an interface instead of becoming dead hardware whenever cellular is unavailable. It combines the pendant's physical button/audio, the ESP32 bridge, Mac serial, local agent, and later relay reconciliation.
- **path:** pendant → mac-planner → relay-realtime → browser-extension → mac-vision → dashboard
- **model tier:** Local/cheap model for short offline commands and deterministic local intents; realtime model only after connectivity returns for complex interpretation or reconciliation.
- **latency:** Button-to-local acknowledgement under 500 ms; simple Mac result under 5 seconds. Unsynced events persist until connectivity returns, then reconcile in the background.
- **cost:** Near-zero while offline for deterministic commands; later sync costs a small batch request. USB serial and audio bridge dominate engineering, not API spend.
- **security:** Treat USB as an explicitly paired local link, not an open serial console. Encrypt or authenticate queued transcripts and receipts, cap offline command scope, and prevent replay with monotonic counters. Never queue destructive actions for later execution; queue only drafts and read results.
- **missing:** nRF9160 USB-serial command/audio framing and offline event journal; ESP32 audio bridge transport between pendant and Mac; Mac serial daemon that maps authenticated events to /plan and local reads; relay sync endpoint with deduplication and conflict receipts; offline playback queue and reconnect state shown on pendant

### "When I plug my pendant into another trusted Mac, restore my work exactly where I left off: reopen the right apps and files, reattach my browser workspaces without exposing passwords, and show pending jobs and drafts so I can continue immediately."
- **useful because:** The pendant becomes a portable continuity anchor rather than a single-computer accessory. A lost, replaced, or borrowed Mac would not strand the owner's active work, while browser secrets remain in the browser's own authenticated profile instead of being copied into the cloud or pendant.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background/cheap model to summarize and rank resumable work; deterministic state capture and restoration should not spend realtime-model tokens. Realtime is only needed if the owner asks for a spoken explanation of conflicts.
- **latency:** Capture on detach or explicit command within 10 seconds; restoration should show a usable workspace within 30 seconds, with browser tabs reattached opportunistically.
- **cost:** Low API cost; storage and local state transfer dominate. A compact manifest is cheap, while optional summaries are a small background-model call.
- **security:** The pendant must hold only a hardware-backed device key, never passwords or raw session cookies. Relay stores encrypted, per-device workspace manifests with expiry and revocation. A new Mac must be explicitly paired; browser extension proves tab ownership locally. Do not restore destructive queued actions automatically—restore them as drafts with receipts.
- **missing:** Portable workspace manifest schema covering apps, files, browser tab/session identifiers, drafts, and pending jobs; Hardware-backed pendant identity and pairing/revocation protocol over the live USB serial link; Mac capture/restore adapters for apps and files; Browser extension reattachment protocol that preserves authenticated sessions without exporting credentials; Encrypted relay storage and conflict resolution when two Macs diverge


## What it asked for

_Nothing._
## Its own summary

Round 161 produced three new cross-surface capabilities: (1) nonce-bound pendant physical approval for an exact prepared Mac/browser transaction, (2) an attention firewall that combines Calendar, presentation/foreground state, browser urgency, relay queueing, and pendant output, and (3) a USB-local offline mode so the currently attached but LTE-unregistered pendant remains useful through the Mac and later syncs receipts. The third is the highest immediate-value opportunity because the hardware is physically testable now.

**Biggest unknown:** The missing implementation boundary is still the live USB serial/audio path: whether the nRF9160 and ESP32 firmware expose a usable authenticated framing protocol and whether the Mac agent has a serial daemon. The orchestrator should grant or build that path before assuming the pending offline skills can run.

