# Harness derivation — faculty-perception — round 114

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **computer-use-consent** — Live Mac agent has visionModelConfigured=true but visionUploadConsented=false; computer-use loop disabled; Accessibility and Screen Recording are both ungranted, so screenshot/mouse computer-use is not currently trustworthy.
  - evidence: GET /ops/status at 2026-08-07T17:40Z returned computerUse.loopEnabled=false, visionUploadConsented=false, accessibility.trusted=false, screenRecording.granted=false, permissions.ready=false.
- **surface-reachability** — Safari browser bridge is online with 3 tabs and zero pending commands; Mac bridge is online. No pendant is registered in the discovered device table, so pipeline audio records cannot be treated as live pendant reachability.
  - evidence: discover(devices) returned Safari on MacIntel online, home-macbook-bridge online, cloudflare-contract-test offline; GET /ops/status returned browser online, tabCount=3, pendingCommands=0, macBridgeOnline=true.
- **timezone-conflict** — Owner profile says America/Chicago while live machine-context reports America/New_York. This is an unresolved one-hour scheduling and spoken-time discrepancy.
  - evidence: discover(owner) remembered.timezone=America/Chicago; GET /machine-context returned machine.timezone=America/New_York.

## Capabilities it proposed

### "“What time is it for me, and are my scheduled briefs going to run at the right local time?”"
- **useful because:** The live Mac reports America/New_York while the owner's remembered timezone is America/Chicago. A perception layer should detect this contradiction instead of silently giving times and running routines an hour off; it can state both observed values and ask once which is authoritative.
- **path:** relay-realtime → mac-planner → relay → dashboard
- **model tier:** background for drift detection; realtime only for the spoken answer
- **latency:** under 1 second when asked; nightly background check
- **cost:** <$0.01 per check; mostly local route reads, with no model call unless explaining a conflict
- **security:** Timezone is low sensitivity, but routine names and next-run times should stay local; require confirmation before changing timezone or rescheduling routines
- **missing:** authoritative timezone reconciliation state; a scheduled drift check comparing owner profile, Mac machine-context, and relay schedule interpretation

### "“Is the pendant/audio hardware actually reachable right now, and if not, what exact link is missing?”"
- **useful because:** The Mac bridge and browser are online, but no pendant is registered and historical pipeline telemetry can be mistaken for live hardware. A USB-aware reality report would distinguish physical serial attachment, firmware handshake, relay registration, and audio playback acknowledgment, so the owner gets an honest answer before attempting a voice interaction.
- **path:** mac-terminal → mac-planner → relay → relay-realtime → dashboard
- **model tier:** background/local rules for probes; realtime only to summarize
- **latency:** 2 seconds for an on-demand answer; 30-second polling while chips are attached
- **cost:** <$0.01 per probe; local serial reads and relay status dominate, no vision or cloud model needed
- **security:** Do not upload raw UART audio or secrets; expose only device id, firmware version, link state, and timestamps; require confirmation before flashing firmware
- **missing:** a Mac serial-port observer for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; a typed contract joining USB handshake, relay registration, and live-vs-historical pipeline timestamps; device-side registration acknowledgment

### "“Do the thing I just asked, and don't tell me it worked until every handoff is proven.”"
- **useful because:** The system currently has independently online Mac and browser surfaces, while computer-use permissions are not ready and the pendant is absent. An end-to-end handoff witness would correlate the spoken request, planner decision, Mac/browser receipt, and returned audio/device delivery, then report the first broken edge in one short sentence. This is the most useful trust feature: it prevents confident false completion across a hive of partially disconnected surfaces.
- **path:** relay-realtime → relay → mac-planner → mac-action → browser-extension → mac-vision → dashboard
- **model tier:** realtime for low-latency acknowledgment; background rules for correlation and timeout analysis
- **latency:** immediate acceptance under 300 ms; completion or precise failure within 5 seconds, with asynchronous update for long jobs
- **cost:** <$0.02 per request; event correlation is local/D1, model cost only for ambiguous failure wording
- **security:** Persist opaque request ids and minimal status, not page contents or microphone audio; destructive actions retain existing confirmation gates; never claim delivery from a queued event
- **missing:** a shared request-id envelope across relay, planner, action, browser, and audio events; delivery acknowledgments with monotonic timestamps and explicit historical/live flag; a small state machine that expires incomplete handoffs and emits a causal failure

### "“Continue this conversation on my Mac exactly where I left off, without making me repeat myself or exposing the transcript to another account.”"
- **useful because:** Today the wearable, relay, Mac agent, and browser are separate reachability domains. The owner should be able to move an active task between body and machine as a single authenticated session, preserving intent, pending confirmations, and the exact browser tab without copying a transcript through the model.
- **path:** relay-realtime → relay → mac-planner → browser-extension → mac-terminal
- **model tier:** realtime only for the handoff phrase; a cheaper background model can summarize older context after transfer
- **latency:** under 2 seconds for a handoff acknowledgment; continuation available within 5 seconds
- **cost:** <$0.03 per handoff; dominated by one compact context projection, with token savings from transferring a signed state reference instead of full history
- **security:** Requires device-bound keys, explicit owner gesture/phrase, expiry, and audience-scoped context. Browser cookies and secrets remain on the browser surface; the relay transports only an opaque session reference and redacted task state.
- **missing:** device-bound session migration protocol between pendant, relay, Mac bridge, and browser extension; authenticated context projection with confirmation-state continuity; physical or spoken handoff trigger and revocation UI

### "“Tell me before anything I say or receive leaves the room, and give me a physical signal for the privacy level.”"
- **useful because:** The owner cannot currently tell from the pendant whether a request is being handled locally, sent to the relay model, or used against a logged-in browser. A privacy-state channel spanning pendant feedback, relay routing, Mac execution, and browser access would make cloud use and privileged page access legible at the moment it matters.
- **path:** relay-realtime → relay → mac-planner → browser-extension → dashboard
- **model tier:** local deterministic policy for the signal; realtime model only interprets ambiguous spoken consent
- **latency:** privacy signal before capture/upload, under 100 ms locally; spoken explanation under 1 second
- **cost:** Near-zero per interaction after firmware work; optional policy explanation costs <$0.01
- **security:** The signal must fail closed when state is unknown, never encode sensitive content in LEDs/haptics, and require explicit consent for a cloud or browser escalation. Policy state should be signed and auditable.
- **missing:** pendant-visible local/cloud/browser privacy indicator; relay policy decision event emitted before audio or page data crosses a boundary; Mac/browser hooks that acknowledge the policy state before privileged reads

### "“When I am in a meeting, quietly keep track of what I ask you to do and only interrupt me when it truly cannot wait.”"
- **useful because:** The owner should not have to choose between losing tasks and having an AI speak aloud at the wrong moment. Calendar state on the Mac, pendant interaction state, relay scheduling, and action urgency can cooperate to defer nonurgent responses while immediately surfacing safety-critical or expiring work.
- **path:** relay-realtime → mac-planner → mac-terminal → relay → dashboard
- **model tier:** cheap background classifier for urgency and batching; realtime reserved for explicit interruptions
- **latency:** capture acknowledgment under 300 ms; quiet queue updates within 1 minute; urgent interruption under 2 seconds
- **cost:** <$0.02 per deferred task; background classification dominates, with batching reducing repeated model calls
- **security:** Calendar titles and captured requests are sensitive; retain only event timing and an urgency label by default. Never infer recording consent from calendar presence; require explicit owner policy for meeting capture.
- **missing:** calendar-aware interruptibility state shared with relay and pendant; urgency taxonomy with owner-configurable exceptions; quiet delivery channel and deferred spoken/audio digest


## Changes it proposed to its own stack

### `browser-harness` — Add a navigation truth guard to the Safari bridge: every open/read/click transaction records the tab's pre-state, command id, post-state URL/title, and a compact DOM/page-result hash. Mark completion as failed (not successful) when the tab remains on an error title such as “Failed to open page,” the URL did not change when navigation was requested, or the post-state heartbeat is older than the command. Return the exact failing edge and preserve the receipt for retry.
- **owner gets:** The owner will stop hearing “done” when Safari is actually sitting on a failed page. Browser actions become verifiably complete or plainly retryable, without needing screenshots or Accessibility permission.
- effort: Medium: browser extension transaction wrapper plus relay/agent typed receipt schema and tests for stale tabs, failed navigation, and duplicate commands.  ·  risk: Some sites legitimately keep the same URL or title; use action-specific expectations and allow an explicit same-document mode. If the extension crashes, the receipt remains pending rather than falsely succeeding; retry must use the existing command id.
- cost: Negligible API cost; a few hundred bytes of receipt metadata per browser action.  ·  latency: Adds one post-action heartbeat/read, typically 100–500 ms.
- security: Store hashes and URLs, not page bodies, in the receipt; existing browser session access controls remain unchanged.
- depends on: browser command/result routes must expose command id and tab identity; existing browser heartbeat/status must include a fresh timestamp; typed action receipts need a success-state enum beyond generic completed


## What it asked for

_Nothing._
