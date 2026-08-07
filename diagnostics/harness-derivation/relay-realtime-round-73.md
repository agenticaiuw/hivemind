# Harness derivation — relay-realtime — round 73

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When the connection gets choppy, switch to a super-compact voice mode and keep the conversation intelligible, then restore quality when the link improves."
- **useful because:** The pendant’s LTE-M link can saturate when both sides talk, causing dropped packets and a frustrating experience. A degraded-but-clear mode keeps the conversation usable instead of failing outright.
- **path:** pendant → relay → model-routing → audio pipeline
- **model tier:** Realtime relay remains for conversation; the change is in audio encoding and turn-taking strategy rather than heavier modeling.
- **latency:** Mode switch decision must be fast (<200ms) based on observed packet loss/latency; audio stays real-time.
- **cost:** Mostly engineering cost. Runtime cost is neutral or slightly lower because lower bitrate means fewer bytes over the modem.
- **security:** No new data types; but changing buffering strategies must not accidentally retain audio longer than intended. Any retention must follow existing policy and be observable.
- **missing:** Network health signals surfaced to the relay in real time; A negotiated codec/bitrate ladder between pendant and relay; A firmware skill to change capture bitrate/packetization and LED state for degraded mode; An explicit audio buffering policy with retention limits

### "“I’m unavailable for the next 45 minutes. Quiet my Mac and authenticated browser sessions, but tell me on the pendant if something genuinely urgent arrives; restore everything exactly afterward.”"
- **useful because:** The owner can currently ask a Mac agent to change one setting, but cannot establish a temporary, cross-surface attention policy while away and have it safely unwind. This capability turns the worn pendant into an availability control: it coordinates local notifications, browser-session monitoring, relay escalation, and exact restoration without requiring the owner to be at the Mac.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Realtime handles the short spoken policy and any urgent interruption. A cheaper background model classifies incoming items against the owner’s stated urgency rule and produces a one-line reason; Mac-planner performs settings changes, while browser-extension/mac-vision observe the relevant authenticated surfaces.
- **latency:** Acknowledge and apply the temporary policy in under 3 seconds when the Mac is online; if it is offline, queue it and clearly say so. Urgent detection should reach the pendant within 10 seconds. Restoration should occur at the declared end time or immediately on “I’m available,” with a receipt in under 5 seconds.
- **cost:** About $0.005–$0.03 per availability window, dominated by low-frequency notification/browser checks; use event-driven browser heartbeats where possible and avoid realtime inference except for the initial command and interruption.
- **security:** Notification text and authenticated pages may contain private content; relay should retain only urgency decision, source, timestamp, and a short redacted excerpt. Capture a before-state snapshot per affected Mac/browser setting and restore only that snapshot, never a guessed default. Do not silently suppress safety-critical OS alerts. “Stop quiet mode” must always work from the pendant, and every suppression/restoration needs an auditable receipt.
- **missing:** A cross-surface notification-policy adapter that snapshots and restores Mac notification state and browser notification/session behavior; A temporary lease/alarm primitive on the relay with expiry guarantees and crash recovery; An urgency rule interface that can be spoken naturally and compiled into deterministic sender/topic/time conditions before model ranking; A pendant push channel with a distinctive urgent LED/audio pattern while no voice session is active; Browser event/watch hooks that can inspect new authenticated items without polling full page contents


## Changes it proposed to its own stack

### `relay` — Add an expiring Attention Lease subsystem: compile a spoken availability window into a versioned policy, snapshot every Mac/browser notification setting it touches, deliver policy changes to whichever surfaces are online, classify incoming events, push only qualifying interruptions to the pendant, and restore the exact snapshots on expiry or explicit cancellation. Persist lease state and restoration journal in a Durable Object so Worker eviction, Mac sleep, and browser reconnect cannot leave the owner muted.
- **owner gets:** The owner can leave the Mac without losing control of their attention. They get quiet when they asked for it, urgent matters on the device they are wearing, and their prior notification setup back exactly—rather than a forgotten mute or a flood of stale alerts later.
- effort: Medium-high: policy compiler and lease state machine, Mac notification adapter, browser watch/event adapter, crash-safe restore journal, pendant push/LED mapping, and dashboard controls. Requires integration tests for disconnects, expiry races, and partially applied snapshots.  ·  risk: A bad classifier could suppress something important; default to pass-through on classifier uncertainty and preserve OS safety alerts. If restoration fails, retry from the journal and surface a clear pendant alert. If a surface reports an unknown before-state, do not alter it. Explicit cancellation must be idempotent.
- cost: Small Durable Object storage and alarm cost per active lease; inference cost roughly cents per hour only when events arrive. No hardware purchase required if existing audio/LED uplink supports push; otherwise a firmware push/status packet is needed.  ·  latency: Policy application typically 1–3 seconds; urgent event delivery target under 10 seconds. Durable persistence adds negligible foreground latency but retries may take longer when a surface is offline.
- security: Store setting snapshots and event metadata encrypted with redaction; never copy full authenticated page contents into the relay. Scope browser observation to declared sessions and delete lease data after restoration plus a short audit retention period.
- depends on: A relay-to-pendant push path independent of an active voice turn; A durable alarm/lease primitive (Cloudflare Durable Object alarm or equivalent); Mac and browser adapters that report and restore versioned notification state; An event-level browser watch API rather than only page snapshots


## What it asked for

_Nothing._
