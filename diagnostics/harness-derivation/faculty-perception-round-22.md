# Harness derivation — faculty-perception — round 22

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-input** — As of 2026-08-07T09:57Z, Mac local agent is not ready for reliable UI control: Accessibility trusted=false, Screen Recording=false, synthesized events rejected because permission belongs to a different binary. UI actions may report success while doing nothing; receipts for ui_click/ui_menu/type_text/press_keys are untrustworthy.
  - evidence: GET /observe returned accessibility.trusted=false, eventsPost=false, inputReachability.status=failed and explicit consequence; GET /ops/status returned ready=false.
- **browser-reachability** — Chrome extension is offline (home-chrome, 0 tabs), but Mac local agent retains 3 durable browser sessions/tabs, including time.is/UTC and two test forms. Browser commands requiring live extension cannot currently reach Chrome.
  - evidence: GET /ops/status and GET /browser/status show browser online=false, pendingCommands=2; GET /observe shows sessions=3 with durable tabs.
- **pendant-pipeline** — Relay pipeline telemetry is live and exposes pendant-origin offline events: held alerts surfaced from microSD and a moment bookmark held offline with link_at_capture=down. A later cloud-relay reply was rendered as 24 kHz mono PCM (164650 bytes, 3430 ms), uploaded and waiting for pendant; pipeline record status may remain processing even after terminal events.
  - evidence: GET /pipeline returned nrf9160 alert_delivered/bookmark events and cloud-relay run with tts done, relay_result done, but status processing.

## Capabilities it proposed

### "When you do something on my Mac, don't tell me it worked until you can prove the visible result actually changed; if the Mac can't safely control its screen, tell me and switch to a reliable route or ask me to fix it."
- **useful because:** The current Mac agent reports UI steps as successful even though Accessibility is untrusted and synthesized events are rejected; this would stop false completion claims. It uses the pendant for immediate truthful status, the relay for durable state, and the Mac/browser for independent evidence rather than trusting action receipts.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Deterministic permission/readiness classifier and postcondition checks on Mac/relay; cheap background model for comparing before/after screenshots or extracted page state. Realtime only speaks the short status or asks for confirmation.
- **latency:** 2–5 s for local postcondition verification; up to 10 s when a screenshot or browser extraction is needed. If Accessibility or Screen Recording is missing, announce immediately rather than spending model time.
- **cost:** Usually <$0.01 per invocation; dominated by an occasional small vision comparison, not the realtime turn. No extra cost for deterministic permission and receipt checks.
- **security:** Screenshots, URLs, and extracted private-page state may leave the Mac only if the owner has already enabled that route; redact secrets before relay storage and retain only hashes/evidence snippets. Never claim success from a receipt alone; irreversible actions still require the existing approval checkpoint.
- **missing:** A shared typed action-outcome contract distinguishing attempted, permission-blocked, observed-success, observed-failure, and unverifiable; Mac postcondition probes that can verify app state without Accessibility (for example filesystem, process, AppleScript, or API evidence where available); A startup/continuous permission repair flow for the actual AI Pendant Agent binary, plus relay and dashboard surfacing of unverifiable actions; Browser extension reconnection/handshake so authenticated tab verification is available when Chrome is offline

### "When I press the pendant twice, save a private 'what was happening' snapshot I can ask for later: what the pendant heard and whether it was offline, what the Mac was showing or running, which browser sessions were reachable, and what jobs or alerts were pending at that exact moment."
- **useful because:** Today the system records disconnected pieces, but the owner cannot reconstruct the context of a moment across the wearable, relay, Mac, and private browser. This would make a missed command, interruption, or offline period understandable without pretending that an action occurred.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Device and Mac collect structured telemetry deterministically; a cheap background model renders a concise timeline only when requested. Realtime is used solely to answer a spoken lookup or acknowledge capture.
- **latency:** Capture must complete locally in under 500 ms and queue through the relay when disconnected. A later spoken summary can take 2–4 s; dashboard rendering can be asynchronous.
- **cost:** Near-zero at capture; <$0.01 per requested summary, dominated by optional multimodal summarization. Store compact metadata by default, not raw audio or screenshots.
- **security:** Snapshots can expose private tab titles, foreground apps, and audio metadata. Encrypt on the SD card and relay, use a short configurable retention, redact URL paths and secrets, require pendant button plus spoken confirmation to include screenshots/audio, and provide deletion by snapshot ID.
- **missing:** A cross-surface snapshot schema with one monotonic capture ID and synchronized timestamps; Pendant firmware event marker and encrypted local queue for snapshot metadata; Mac read-only snapshot endpoint for foreground/window/process state and browser-session reachability; Relay API for delayed upload, deduplication, retention, and spoken/dashboard lookup; A user-facing redaction and deletion control


## Changes it proposed to its own stack

### `mac-harness` — Make the signed AI Pendant Agent app bundle the sole event-posting identity: detect the currently running executable versus the TCC-granted binary at startup, show a repair dialog/deep link when they differ, and mark all UI actions as unverifiable until a zero-delta input probe and a readback postcondition both pass. Propagate this readiness state to relay, pendant speech, jobs, and dashboard.
- **owner gets:** The owner will stop hearing confident false confirmations when a Mac action silently did nothing. They get a clear fix request once, and thereafter only verified screen changes are reported as completed.
- effort: Medium: TCC identity/startup diagnostics, signed bundle deployment correction, readiness state in job receipts, and postcondition hooks for common actions.  ·  risk: TCC repair may require owner interaction and existing permissions can be reset during app updates. Recover by retaining the current read-only/terminal/API routes and explicitly saying unverifiable instead of attempting GUI actions.
- cost: Negligible API cost; engineering-only. No hardware cost or added power draw.  ·  latency: Adds roughly 0.1–1 s for readiness probe and up to a few seconds for readback verification.
- security: Improves safety by refusing to trust unverified GUI receipts. TCC prompts remain local; do not send screen contents to relay unless the existing vision consent is enabled.
- depends on: A single canonical signed app bundle identity for AI Pendant Agent; Typed action outcome states shared by Mac agent and relay; Per-action postcondition/readback implementations


## What it asked for

_Nothing._
## Its own summary

Fresh live checks found a critical truthfulness gap: the Mac agent is online but not ready for UI control. Accessibility and Screen Recording are absent, synthesized events are rejected because TCC permission belongs to a different binary, and the agent explicitly warns that UI actions can report success while doing nothing. Chrome extension is offline, although three durable browser sessions remain. Relay/pipeline telemetry is live and confirms offline-held pendant alerts/bookmarks plus a successfully rendered 24 kHz response waiting for the pendant. I recorded these findings, notified all agents, and proposed a new permission-aware, postcondition-verified action outcome contract and a concrete Mac harness repair.

**Biggest unknown:** Whether the owner can grant Accessibility/Screen Recording to the actual signed AI Pendant Agent binary, and whether the browser extension can reconnect; without those, GUI/browser completion cannot honestly be asserted. I still need the shared typed outcome contract, postcondition probes, and a TCC identity-repair flow to make the proposed capability real.

