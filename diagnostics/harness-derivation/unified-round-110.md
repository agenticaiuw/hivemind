# Harness derivation — unified — round 110

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-ui-observability** — The live /observe endpoint confirms Accessibility trusted=false, Screen Recording=false, input reachability failed, and explicitly says ui_click/ui_menu/type_text/press_keys report success while doing nothing; browser sessions exist but home-chrome device is offline.
  - evidence: GET /observe at 2026-08-07T14:42:16.324Z returned accessibility.trusted=false, screenRecording=false, uiActionsWillReachTheScreen=false, and consequence text.

## Capabilities it proposed

### "When I interrupt you while you're speaking, stop cleanly, remember exactly where you were, and continue the task—whether the next step is on the pendant, relay, Mac, or a logged-in browser page."
- **useful because:** Today LTE contention and half-duplex audio can lose speech, while an action may continue on another surface. This gives the wearer natural barge-in and prevents duplicated or conflicting work: the pendant marks the interruption, relay coordinates cancellation/checkpoint, and Mac/browser resume from the last verified step.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Realtime model only for interruption detection and a one-sentence spoken acknowledgement; background/local planner handles checkpoint reconstruction and resume. Browser/Mac extraction stays on cheaper planner tiers.
- **latency:** Local stop of playback under 150 ms; relay interruption receipt under 1 s; spoken acknowledgement under 2 s; resume after reconnect within 10 s.
- **cost:** Usually <$0.01 per interruption; dominant costs are a short realtime turn and any planner/browser calls needed to reconstruct state.
- **security:** Audio around the interruption and authenticated-page state may cross pendant→relay→Mac. Retain only a hashed checkpoint plus minimal transcript; never resume an irreversible browser action without the existing owner confirmation gate.
- **missing:** A typed interruption/checkpoint protocol spanning audio sequence, conversation turn, and Mac/browser job receipt; Pendant local playback-stop and interruption marker (must survive a dropped link); Relay cancellation propagation and resumable job state; Mac/browser handlers that acknowledge cancellation and expose the last verified step

### "When you tell me something you found in my private accounts, let me say “show me why” and hear the exact supporting sentence while my Mac opens the logged-in page at the evidence location—without changing anything."
- **useful because:** Spoken summaries currently force the owner to trust an opaque answer or manually hunt through tabs. This gives an immediate, reversible audit trail that combines the pendant's voice, the relay's cited result, the browser's authenticated session, and the Mac's ability to present the exact source.
- **path:** pendant → relay-realtime → browser-extension → mac-planner → mac-vision → dashboard-ux
- **model tier:** Cheap extraction and citation validation in the background; realtime model only resolves the short “show me why” utterance and speaks the already-validated sentence.
- **latency:** Identify the referenced claim in under 500 ms, speak the evidence in under 2 s, and bring the source tab to the foreground within 3 s.
- **cost:** Usually under $0.005 because it reuses stored extraction and does not reread the page; a planner call is needed only when multiple claims are ambiguous.
- **security:** The source may be a private logged-in page. Send only the selected evidence snippet and locator, not a broad page dump; mask secrets and require the existing browser session binding. Never click submit or mutate the page.
- **missing:** A durable claim-to-evidence record containing URL/tab/session binding, locator, timestamp, and snippet hash; A browser command that focuses or reopens a source at a locator without mutation; A pendant voice intent and relay lookup that resolve “that” to the last spoken claim; A redaction/expiry policy for private evidence snippets


## Changes it proposed to its own stack

### `mac-harness` — Add a mandatory preflight capability/readiness contract before any UI action: query Accessibility, Screen Recording, browser-extension connectivity, target-app focus, and screenshot/DOM observability; classify each requested action as executable, AppleScript-safe, browser-bridge-safe, or blocked. Refuse to enqueue UI actions when the required observation/control channel is unavailable, emit a typed blocked receipt with the exact owner remedy, and have relay_job_status surface that instead of reporting success.
- **owner gets:** The Mac currently reports UI actions as successful while Accessibility and Screen Recording are false, so the owner can believe an email, form, or file operation happened when nothing was visible or changed. This makes failures honest and routes safe work through AppleScript or the browser bridge when possible.
- effort: Medium: readiness probe, action capability matrix, queue admission check, receipt schema, and dashboard/voice wording; no TCC grant is needed to implement the guard.  ·  risk: Some existing actions will start returning blocked instead of silently succeeding. Recover by falling back to AppleScript or browser bridge for supported targets, and provide a one-step System Settings instruction only when the owner chooses to enable TCC.
- cost: Negligible API cost; one local probe per job and a small receipt. Saves planner/retry calls.  ·  latency: Adds roughly 100–300 ms to Mac jobs; avoids long false-success workflows.
- security: Improves safety by preventing unverifiable actions; readiness data stays local except for typed status and remedy.
- depends on: A typed local readiness probe (Accessibility, Screen Recording, extension online, screenshot/DOM availability); A shared action capability matrix used by mac_run_actions, mac_delegate, and browser bridge; Extend existing action receipts with blocked reason, fallback, and observability evidence

### `hardware` — Replace the current ESP32 HUZZAH32 SBC-only A2DP source with a production companion that supports Bluetooth LE Audio (LC3) and a hardware-clocked 24 kHz mono I2S path, while retaining a small local relay protocol for the nRF9160. The relay should expose the same audio sequence IDs to the Cloudflare worker and Mac/iOS clients so a spoken session can move from earbuds to the pendant speaker without transcoding or losing position.
- **owner gets:** The owner gets genuinely clear, low-latency speech in ordinary LE Audio earbuds and can switch output to the pendant when earbuds leave range. Today the bridge forces 31.25→44.1 kHz resampling and SBC, while LTE contention already drops speech; this change makes the wearable conversation intelligible and continuous rather than a prototype audio chain.
- effort: High: new companion PCB/radio stack, LE Audio certification and pairing UX, clock-domain and power design, firmware audio framing, and end-to-end acceptance tests across earbuds, pendant, relay, and iOS/Mac clients.  ·  risk: New radio/codec interoperability failures and pairing complexity; preserve the existing ESP32/SBC bridge as a fallback during rollout, and fail over to pendant output with an explicit spoken status rather than silence.
- cost: Roughly $8–20 additional companion BOM at volume plus certification; modest recurring codec CPU cost, but lower relay transcoding and retransmission load. Companion power likely 80–200 mW during playback, requiring a battery and charging design.  ·  latency: Expected 30–80 ms lower output latency and fewer buffering stalls than the current resample/SBC path; pairing adds seconds only at setup.
- security: Bluetooth identity and audio keys must be provisioned per owner; never expose the relay's session audio as an unpaired discoverable stream. LE Audio broadcast mode must be disabled by default.
- depends on: A production pendant/companion audio acceptance specification for 24 kHz capture and playback; Audio sequence IDs shared by pendant firmware, relay, Mac menubar, browser/iOS clients, and receipts; A device-pairing and recovery protocol that survives companion replacement


## What it asked for

_Nothing._
## Its own summary

Discovered live Mac readiness and recorded a verified finding: /observe says Accessibility=false, Screen Recording=false, input reachability failed, and UI actions falsely report success. Recorded two new items: cross-surface interruption/checkpoint/resume for pendant↔relay↔Mac/browser, and a Mac action admission gate that blocks unverifiable UI work and falls back to AppleScript/browser bridge. No new orchestrator grant is required for the design.

**Biggest unknown:** Whether the owner will manually grant Accessibility/Screen Recording to the AI Pendant Agent binary; until then, the readiness gate must prevent UI actions from being represented as successful. Implementation still needs the typed readiness contract, action capability matrix, and interruption checkpoint protocol.

