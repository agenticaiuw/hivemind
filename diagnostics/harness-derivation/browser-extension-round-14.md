# Harness derivation — browser-extension — round 14

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Watch my logged-in websites (bank, bills, delivery, work portals) and tell me only when something important changes; read the details to me, but never submit, send, purchase, or transfer without showing me the exact action first."
- **useful because:** This turns the browser's unique access to authenticated pages into an always-on assistant: it catches due dates, fraud alerts, delivery changes, and work updates without making the owner repeatedly open sites. It also avoids unsafe autonomous side effects.
- **path:** dashboard → mac-bridge → browser → relay → pendant
- **model tier:** Scheduled polling and page extraction use a cheap background model (or deterministic DOM selectors first); a small diff/classifier summarizes changes. Use realtime only when the owner asks a follow-up by voice. Use the Mac/browser bridge because it owns the existing Safari login session; public pages should use web search instead.
- **latency:** A scheduled check can take 10–60 seconds and should run without holding a conversation open. An owner-requested read-aloud should begin within ~2 seconds after the cached result is available. Initial site setup needs a one-time interactive browser session.
- **cost:** Roughly low cents per monitored site per daily check when selectors and hashes suppress unchanged pages; model tokens dominate only changed-page summaries. Audio costs occur only when the owner asks to hear a digest. Browser CPU/network cost is on the Mac.
- **security:** Authenticated page contents and extracted diffs leave Safari via the local agent and Worker unless configured for local-only processing; redact account numbers, health data, and message bodies before persistence. Store only hashes plus short summaries by default, encrypt credentials by relying on Safari's session rather than copying them, and provide per-site pause/delete controls. Require explicit confirmation and a preview for any click that submits a form, sends a message, changes account settings, spends money, or transfers funds. Detect login expiry and never attempt to bypass MFA or CAPTCHA.
- **missing:** Reliable idempotent browser command enqueue/result delivery (the current enqueue wrappers are implementation stubs); Per-site monitor definitions with selectors, schedule, sensitivity, and retention policy; A background scheduler and cheap change-diff worker; Dashboard UI for monitor setup, pause, redaction, and pending-action previews; A local-only mode or documented redaction boundary for sensitive authenticated content


## Changes it proposed to its own stack

### `browser-harness` — Replace the current fire-and-forget browser enqueue path with a durable command queue: persist commandId, target tab/device, requested action, idempotency key, expiry, and risk class; expose list-tabs/bootstrap-navigation; let the extension acknowledge receipt separately from result; retry only unacknowledged commands and reconcile late results. Add a deterministic browser_read_page/snapshot fallback and a visible pending-command state in the dashboard.
- **owner gets:** The owner gets dependable authenticated browser help instead of silent timeouts or duplicate clicks. A dead Safari tab can be reopened safely, and the assistant can explain whether it is waiting for login, MFA, a page, or the owner's confirmation.
- effort: Medium: local-agent bridge, extension protocol, Worker queue schema, and dashboard status UI; add integration tests for tabCount=0, Safari restart, network loss, and late results.  ·  risk: Retries could duplicate a click or navigation. Use idempotency keys, classify navigation/read as retryable, classify click/type as non-retryable unless the extension confirms no execution, and stop on ambiguous outcomes. Recovery is a visible paused command requiring owner review.
- cost: Negligible model/API cost; a few D1 rows and small heartbeat/result payloads per command. Local CPU and network use remain low.  ·  latency: Adds at most one quick acknowledgement round-trip; avoids the current 45-second timeout and makes normal reads faster and predictable.
- security: Persisted commands may contain page text or form input; encrypt sensitive payloads, redact logs, set short TTLs, and require confirmation for risk classes that can submit, send, purchase, or alter settings.
- depends on: A working extension enqueue endpoint/bridge implementation; Per-action risk classification shared with the Mac harness


## What it asked for

### `s13-369p` (skill) — offline_alert_inbox
- does: Receives short, prioritized alerts from the relay (for example, a changed authenticated bill or fraud warning), queues them locally, and lets the owner long-press the single button to play the next alert over the existing speaker. The LED indicates unread count and an error/expired state; alerts remain available across a dropped phone/Mac link.
- must be on-device because: The owner may be away from the phone and the browser/Mac link may disappear after the alert is generated. Playback and queue access must work locally, and server-side delivery alone cannot guarantee the owner hears an urgent alert.
- trigger: Server push over the existing pendant connection; long-press of the existing button plays/acknowledges the next item. Do not change the current short press start/second press end conversation behavior.
- storage: A fixed ring in application flash, e.g. 8 alerts with 20–30 seconds of compressed audio each (roughly 80–240 kB depending on bitrate), plus a few hundred bytes of metadata; retain no sensitive page text beyond what is spoken. RAM: one decode/playback buffer and metadata only.
- RAM budget: Target 12–20 kB peak additional RAM: 8–12 kB Opus decode state/buffer plus 4–8 kB I2S ring buffer and <1 kB metadata. This must be measured against the 211,608 B application RAM, with queue metadata bounded and conversation buffers taking precedence; if RAM is tight, stream from flash in small chunks and cap to 4 alerts rather than evicting conversation audio.

