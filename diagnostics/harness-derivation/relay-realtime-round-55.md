# Harness derivation — relay-realtime — round 55

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Hold this for when I’m back at my Mac: reopen the exact research context I’m talking about, restore the relevant browser tabs and draft state, then tell me on the pendant what’s ready.”"
- **useful because:** Today a spoken request made while away can be routed or queued, but the owner cannot leave behind a durable, resumable workspace capsule. This would preserve intent plus the browser/Mac context needed to continue, rather than making them reconstruct tabs, drafts, and constraints later. It only works as a hive feature: the pendant captures intent, the always-on relay stores and wakes the task, the browser extension restores authenticated tabs, and the Mac planner reconstructs local application state and returns a receipt to the pendant.
- **path:** pendant → relay → browser-extension → mac-planner → mac-vision → dashboard
- **model tier:** Realtime relay performs only short utterance normalization and acknowledgment; a cheaper background model builds and validates the task capsule, while mac-planner handles execution and mac-vision is used only when visual restoration is required.
- **latency:** Acknowledge the spoken capture in under 1 second. Restoration may take minutes after the Mac/browser becomes available; the owner should receive a brief pendant notification and be able to ask for status without waiting synchronously.
- **cost:** Approximately $0.01–$0.08 per task depending on whether visual restoration is needed; most cost is background planning and any mac-vision retries, not the realtime acknowledgment.
- **security:** The capsule may contain private URLs, draft text, and references to authenticated sessions. Encrypt it at rest and bind it to the owner/device; never copy cookies or passwords into the relay. Restoration must be limited to the owner’s paired Mac/browser and produce a receipt showing what was reopened or changed. The owner’s stated maximum-access policy means no confirmation gate is required for reversible reopening, but sending or destructive edits must remain explicitly represented in the capsule and receipt.
- **missing:** A durable encrypted task-capsule store with lifecycle/expiry and idempotency keys; A Mac/browser availability trigger and worker that resumes capsules when either surface reconnects; Browser-extension support for snapshotting and restoring a named tab group plus scroll/form/draft metadata without exporting credentials; Mac-planner/mac-vision restore primitives for application/window state and a structured partial-success receipt; Relay-to-pendant notification and “what is waiting for me?” status query; Dashboard UI to inspect, cancel, expire, or retry capsules

### "“If you get stuck or find two plausible things on my Mac, ask me on the pendant with the smallest useful choice, then continue the same job when I answer.”"
- **useful because:** A long-running Mac/browser task currently has to fail, guess, or leave the owner to inspect logs when the planner encounters ambiguity. This creates a true spoken exception channel: the machine supplies concise evidence and choices, the owner answers hands-free, and the exact job resumes with its prior context and idempotency rather than restarting or silently guessing. It is only possible through the pendant, always-awake relay, Mac planner/vision, and browser session together.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Mac-planner or mac-vision detects an ambiguity and generates a structured question using a cheaper background model. Realtime relay only speaks the short question and normalizes the owner’s answer; the planner applies it and continues.
- **latency:** Surface an exception within 2 seconds of detection, keep the question under 15 seconds of speech, and resume within 3 seconds after the answer reaches the Mac. If the owner does not answer, suspend safely rather than guessing.
- **cost:** About $0.005–$0.04 per exception, dominated by a screenshot/context interpretation call; ordinary successful tasks incur no additional realtime model call.
- **security:** Questions may quote private page text or expose a screenshot. Send the minimum redacted evidence, retain it only for the job TTL, and bind replies to a signed job/step nonce so a late answer cannot affect a different task. This is clarification, not a confirmation gate: reversible actions continue after the owner selects an option, consistent with the owner’s maximum-access policy.
- **missing:** A first-class suspended-job state with step nonce, serialized planner context, TTL, and idempotent resume; An exception schema supporting choice, free-form answer, timeout, and cancellation; Relay push of a concise question to the pendant and correlation of spoken replies to the waiting job; Mac planner/vision hooks that pause before an ambiguous step and resume without replaying completed actions; Browser-extension support for returning the selected tab/session context; Dashboard view of waiting questions and an audit trail of the answer and resumed receipt


## Changes it proposed to its own stack

### `hardware` — Add a low-power coin vibration motor and a dedicated haptic driver to the nRF9160 pendant, with firmware patterns for capture accepted, task completed, attention needed, and link lost. Keep the existing single button and LED as controls/visual fallback; expose a small relay API that maps job receipts and urgency to patterns.
- **owner gets:** The owner can reliably notice a queued Mac/browser task finishing or needing attention while walking, in a meeting, or somewhere audio would be inappropriate. A discreet vibration pattern gives the hive a real asynchronous return channel instead of forcing the owner to keep checking the pendant or miss spoken output.
- effort: Mechanical enclosure and PCB revision, driver integration, battery characterization, firmware pattern table, and relay receipt-to-notification mapping. Prototype effort is moderate; production validation must include ingress protection and wear testing.  ·  risk: Added vibration can annoy the owner, consume battery, or be mistaken for an urgent alert. Keep patterns short, rate-limit repeats, provide a physical long-press mute, and fall back to LED/audio. If the motor or driver fails, existing operation remains intact.
- cost: Roughly $1–$4 in prototype components/assembly and approximately 5–30 mW only while vibrating; negligible API cost. Battery impact should be low with short, rate-limited patterns.  ·  latency: Notification begins as soon as the relay receives a receipt, typically no meaningful added network latency; local pattern start should be under 100 ms.
- security: Haptic patterns intentionally reveal only coarse urgency, not content. Do not encode sensitive information in pattern length or count; require an authenticated paired relay for notification commands.
- depends on: A durable receipt/notification event schema shared by relay, Mac planner, and browser extension; Pendant firmware support for haptic output and a user-configurable mute/rate limit

### `hardware` — Add a simple capacitive/proximity wear sensor and a hardware microphone-mute indicator path to the pendant, with firmware publishing worn/removed transitions to the relay. On removal, stop voice capture immediately and mark any in-flight audio segment as ended; on re-wear, require the existing button gesture before resuming capture.
- **owner gets:** The owner can wear the pendant all day without worrying that setting it on a desk or handing it to someone leaves the microphone live. The relay, Mac, and browser can also avoid sending private spoken results when the device is not being worn, while still preserving non-audio task completion receipts.
- effort: PCB/enclosure revision, sensor calibration across clothing and skin conditions, firmware state machine, and relay handling for wear transitions. Add a local visible mute indication and a short test mode during setup.  ·  risk: False removal/wear detections could clip a sentence or prevent capture. Debounce transitions, announce state locally, allow a deliberate button override, and preserve a clearly visible hardware mute state. Sensor drift and sweat require calibration and environmental testing.
- cost: Approximately $0.50–$2.50 in components/assembly and a few hundred microwatts to a few milliwatts depending on sensor duty cycle; negligible API cost.  ·  latency: Local mute should take effect within tens of milliseconds; relay state propagation is useful within roughly one second but is not on the critical mute path.
- security: This adds a privacy boundary rather than collecting new content. Wear-state events should be minimized and authenticated; do not infer location or identity from them, and expire them from relay logs quickly.
- depends on: Pendant firmware event and local mute support; Relay session state that can invalidate audio capture on a wear transition; Mac/browser notification policy that distinguishes task receipts from private spoken content


## What it asked for

_Nothing._
## Its own summary

Recorded four new proposals: durable cross-device task capsules that restore Mac/browser context when the owner returns; a spoken exception-resolution channel for suspended jobs; a low-power haptic notification channel on the pendant; and a wear/proximity sensor with hardware microphone mute. These address capabilities the owner cannot have today and explicitly identify the relay, pendant, Mac, browser, and persistence work required.

**Biggest unknown:** Whether any existing backlog item already covers suspended-job conversational exception handling or wear-aware capture closely enough to merge these proposals rather than implement them separately; no further discovery is possible this round.

