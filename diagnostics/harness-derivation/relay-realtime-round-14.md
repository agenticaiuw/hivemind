# Harness derivation — relay-realtime — round 14

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Summarize this webpage" or "Check the price on this product""
- **useful because:** Fast, hands-free answers without needing the owner’s Mac to be online, especially when they’re out wearing the pendant.
- **path:** relay → server-side browser (Cloudflare Browser Run) → dashboard
- **model tier:** Cheaper background model for browsing/extraction; relay only handles the voice handoff and a short summary.
- **latency:** Relay response should be near-immediate (“I’m checking”). Page processing can take several seconds; that’s fine as long as it returns a concise summary.
- **cost:** Dominated by browser runtime and extraction tokens; relay cost stays low because it doesn’t parse the full page.
- **security:** Web content can include tracking and authenticated pages. Only fetch public URLs by default; require explicit confirmation before using stored credentials or accessing private sites. Return minimal extracted data.
- **missing:** Server-side browser capability wired into the relay’s tool registry and routing; Job status/notification path so results can arrive later as audio or dashboard update

### ""Remind me to do X at 6 pm" or "Every weekday at 9, remind me to stand up""
- **useful because:** Routines are a classic wearable job: set it once, then get gentle prompts without having to open a laptop.
- **path:** relay → scheduler (Worker Cron/Durable Object alarms) → mac-bridge or iOS notification → dashboard
- **model tier:** Relay for quick intent capture; a cheaper scheduled worker for recurring delivery; optional mac_delegate for creating system reminders if the Mac is available.
- **latency:** Setting a reminder should feel instant. Delivery can be a push/notification; if offline, it can queue until reachable.
- **cost:** Low per reminder; cost comes from scheduled checks and notification delivery rather than conversation tokens.
- **security:** A malicious reminder could spam or leak private text. Require explicit confirmation for recurring reminders and for reminders that send content to external services. Provide clear list and one-shot cancellation.
- **missing:** Scheduler/recurring job system (Cron or Durable Object alarms); Notification channel to pendant or phone, or a fallback to macOS Reminders


## Changes it proposed to its own stack

### `model-routing` — Add explicit, cheap tiers: relay captures intent and hands off to mac_delegate or server_browser_actions. Introduce job creation, status, cancellation, and completion notifications (audio and dashboard) so the relay doesn’t stay in the loop.
- **owner gets:** They can ask for something and get on with their day; results arrive later without tying up a live conversation.
- effort: Medium: add job APIs, status polling/DO, and notification plumbing; update dashboard UI.  ·  risk: Jobs could run with stale context or the wrong scope. Use scoped confirmation tokens, show what will run, and allow cancellation.
- cost: Lower relay token/audio cost; background work uses cheaper models.  ·  latency: Better perceived latency; relay returns quickly while work continues elsewhere.
- security: Centralizes execution control. Require explicit confirmation for high-risk actions (spending money, sending email, accessing private data).
- depends on: Job status endpoint/tool and notification mechanism; Server-side browser for web tasks or Mac availability for desktop tasks

### `firmware` — Implement adaptive duplex behavior: when downlink audio is playing, reduce or pause uplink capture/encoding to avoid LTE contention; resume capture after playback. Add LED state to indicate “receiving” vs “recording.”
- **owner gets:** Fewer dropped speech packets and clearer conversations when they and the agent talk at the same time.
- effort: Medium: audio pipeline changes and state management; careful testing with half-duplex LTE behavior.  ·  risk: Could miss user speech while the agent is speaking. Mitigate with a short buffer and a quick “hold on” prompt; allow a button press to force recording.
- cost: No new cloud cost; firmware development time only.  ·  latency: Improves reliability; may add slight delay when switching modes.
- security: Low; local behavior only.


## What it asked for

_Nothing._
