# Harness derivation — mac-planner — round 202

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac_permissions** — Fresh /ops/snapshot at 2026-08-08T03:00Z reports Accessibility trusted=true and Screen Recording granted=true for AI Pendant Agent; computer-use loop enabled, vision upload consented=false, browser online with 9 Safari tabs.
  - evidence: GET /ops/snapshot HTTP 200 payload: permissions.accessibility.trusted=true, screenRecording.granted=true, computerUse.loopEnabled=true, visionUploadConsented=false; browser tab x.com/home.

## Capabilities it proposed

### "When I press the pendant's bookmark button, package the exact Mac/browser context at that instant—foreground app, visible window, current authenticated tab, and timestamp—then save a redacted incident note and tell me what was captured."
- **useful because:** A bookmark currently records only the pendant-side moment. This would make 'remember this' actually reconstructable later: the screen and logged-in page the owner meant, with provenance and privacy filtering, without requiring them to stop and explain.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** background for packaging and redaction; realtime only for the short acknowledgement
- **latency:** Acknowledge on pendant within 1 s; context capture and durable note within 5 s.
- **cost:** About $0.002–$0.01 per bookmark depending on whether a model is needed; most work is local inspection and hashing.
- **security:** Authenticated page content and window titles leave the Mac only as redacted excerpts; passwords and secrets must be excluded. The owner should explicitly configure which apps/domains may be captured. Never capture microphone audio by default.
- **missing:** A server-triggered correlation endpoint joining pendant bookmark event IDs to a Mac/browser snapshot; A policy-configured redaction pass over UI/browser text; An owner-selected capture allowlist; current FULL_CONTROL_MODE has no effective policy gate

### "Clip the useful part of the authenticated page I am looking at into a dated Markdown file, include the URL and evidence hash, and open the file on my Mac when it is ready."
- **useful because:** It turns a spoken request plus a private browser session into a durable, inspectable artifact instead of a transient answer. The citation/hash lets the owner tell later whether the source changed, while the Mac makes the result immediately usable.
- **path:** pendant → relay → browser-extension → mac-planner
- **model tier:** background model for selecting and cleaning the requested passage; realtime only to confirm completion
- **latency:** 5–10 s for a normal page; return a short spoken status immediately and finish asynchronously.
- **cost:** Roughly $0.01–$0.05 per clip for extraction/summarization; browser read and file staging dominate latency, not tokens.
- **security:** Page text may contain private or financial data. Keep content on the Mac/relay only for the job, redact secrets, preserve source URL and content hash, and require an owner policy entry before writing outside the workbench root.
- **missing:** A route that combines browser evidence capsule retrieval with atomic Markdown staging; A typed selector for current tab versus a named tab and a maximum excerpt size; Owner policy specifying permitted output directories and domains

### "Run a complete pendant-over-USB health check: inject a synthetic uplink, exercise 24 kHz playback, verify the relay and Mac pipeline receipts, and give me one spoken pass/fail with the failing layer named."
- **useful because:** The chips are physically connected now even though LTE registration is not. This would turn a difficult audio/network diagnosis into a one-button test that distinguishes pendant codec faults, USB/bridge faults, relay faults, and Mac handoff faults before a real conversation fails.
- **path:** pendant → relay → mac-planner → dashboard
- **model tier:** background/cheap deterministic evaluator; realtime only for the spoken result
- **latency:** Under 30 s for the full fixture; stream progress to the dashboard and keep the pendant acknowledgement immediate.
- **cost:** Under $0.01 per run if fixture frames are local; storage is a small receipt and counters.
- **security:** Use synthetic audio only—never microphone content. Device identifiers and telemetry should be scoped to the owner's account. A failed run must not alter durable audio or silently change the active profile.
- **missing:** A live USB serial exchange capability for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay endpoint to launch and correlate the firmware diagnostic fixture with Mac pipeline IDs; A deterministic verdict schema and dashboard timeline joining device counters to execution receipts

### "When a logged-in website reaches a human-verification, approval, or two-factor checkpoint while carrying out my request, pause safely, tell me on the pendant exactly what decision is needed, let me answer by voice or button, and resume the same browser job without exposing the secret to the model."
- **useful because:** Today browser automation either stalls at the hardest point or forces the owner to take over an entire workflow. This would make authenticated tasks finishable while keeping passwords and one-time codes outside model context.
- **path:** browser-extension → relay → pendant → mac-planner
- **model tier:** Realtime only for the short challenge explanation and answer capture; background model for classifying the checkpoint and resuming the plan.
- **latency:** Detect within 2 seconds, notify the pendant within 1 second, and resume within 3 seconds after the owner's response.
- **cost:** About $0.005–$0.03 per checkpoint; browser polling and session retention dominate, with little model usage.
- **security:** Never OCR or transmit passwords, TOTP seeds, security answers, or payment data. The browser must expose only a challenge type and safe choices; the owner response should be a scoped capability, expiring after one step. Record that a checkpoint occurred without recording the secret.
- **missing:** Browser-side challenge taxonomy and a pause/resume lease for a specific job; A pendant response event that carries only an enumerated decision, not free-form credentials; Relay correlation between the paused browser job and the owner's response

### "After an important action, let me say 'give me proof' and receive a selectively redacted evidence packet containing what the browser showed, what the Mac changed, when the relay instructed it, and a verification hash I can save or share."
- **useful because:** A success message is not enough for a purchase, filing, booking, or work submission. The owner needs an auditable answer that joins the private browser state, desktop receipt, and server instruction without exposing unrelated tabs or conversation history.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Cheap deterministic assembly and hashing; background model only to write a plain-language summary.
- **latency:** Generate the packet in under 5 seconds after the request; spoken explanation under 2 seconds.
- **cost:** Under $0.01 per packet; storage and hashing dominate, not inference.
- **security:** Selective disclosure is essential: default to destination, timestamp, action, and hashes—not raw page text or screenshots. Packets need expiration/revocation metadata, encrypted local storage, and an explicit share/export action.
- **missing:** A cross-surface evidence-bundle schema joining browser evidence capsules, Mac receipts, and relay pipeline/job IDs; A redaction and selective-disclosure policy chosen by the owner; An export route that writes a signed or content-addressed bundle without copying the whole activity log

### "Let me designate a task as a private delegation, then have the relay and Mac continue it across sleep, browser disconnects, and dropped pendant links; when it reaches a real-world decision or expires, wake me with the exact pending choice and a compact state summary rather than starting over."
- **useful because:** Today long-running work is fragmented across jobs, browser sessions, and relay state. The owner should be able to delegate something once and trust that a temporary outage will not lose the plan or cause a duplicate action.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Background model for checkpoint summaries and recovery classification; realtime only for escalation to the owner.
- **latency:** Checkpoint every meaningful state transition; recovery notification within 10 seconds of a blocked condition; no requirement for continuous connectivity.
- **cost:** About $0.01–$0.10 per delegated task depending on duration; durable state and browser polling dominate.
- **security:** Delegations need a narrow scope, expiration, destination allowlist, and idempotency key. Never retry an irreversible browser submission without a recorded proof of whether it succeeded. The pendant should reveal only the minimum needed to decide.
- **missing:** A durable cross-node delegation state machine with leases, checkpoints, and idempotency keys; Browser and Mac workers that can resume from a named checkpoint rather than replaying all actions; A pendant escalation payload limited to safe, enumerated decisions


## Changes it proposed to its own stack

### `integration` — Add a USB-tether transport mode: the Mac agent speaks the existing pendant serial protocol, forwards synthetic/live control and audio frames to the relay websocket, and exposes the connection as a device session with sequence, loss, and receipt correlation. It must be explicit that LTE is bypassed, and fall back cleanly when either serial node disappears.
- **owner gets:** The pendant can be a real daily wearable today while attached to the Mac, instead of waiting for LTE registration. Conversations, bookmarks, and diagnostics would work at the desk with the same relay semantics used remotely.
- effort: Medium-high: implement framed serial I/O for both connected chips, a reconnecting transport adapter, and relay session binding; test against the shipped 24 kHz/60 ms path.  ·  risk: Serial framing or reconnect bugs could duplicate audio or leave a stale session. Use sequence numbers, idempotent session IDs, bounded buffers, and a visible offline/tethered status; never silently switch transports mid-call.
- cost: Negligible API cost; one persistent local process and small buffers, typically under 20 MB RAM. No hardware purchase.  ·  latency: USB forwarding should add roughly 5–30 ms one way; substantially better than cellular for desk use.
- security: Serial data remains on the Mac until forwarded. Bind only the two explicitly identified device paths, require a local pairing record, and do not expose the serial ports to arbitrary routes.
- depends on: mac_serial_exchange capability (currently queued/unavailable); relay device-session endpoint accepting a Mac transport; A typed framing specification for nRF9160 and ESP32 serial links

### `model-routing` — Use a consent-aware two-tier visual context path now that Accessibility and Screen Recording are actually granted: keep screenshots local to the Mac vision loop by default, send only structured UI facts (app, role, label, selected text after redaction) to the relay, and require a separately stored owner switch before any image upload. Add a per-job receipt stating whether pixels left the Mac.
- **owner gets:** The agent can finally understand what is on screen without turning every computer-use task into a privacy leak. The owner gets visual automation and an honest, inspectable answer about whether an image was sent off-device.
- effort: Medium: wire permission state from /ops/snapshot into planner routing, add local-only vision mode, structured extraction/redaction, and receipts.  ·  risk: Local extraction can misread UI and structured labels can still contain secrets. Show uncertainty, redact password/credit-card fields, and fail closed to a text-only route when the local vision model is unavailable.
- cost: Lower cloud vision-token cost in local-only mode; local CPU/GPU use rises during snapshots.  ·  latency: Local snapshots should save network round trips; structured extraction adds 0.5–2 s per step.
- security: Strongly reduces data egress. Image upload remains disabled until explicit owner configuration; every run records the mode.
- depends on: A local structured UI extraction result from the computer-use loop; An owner-configurable visionUploadConsented policy value; Receipt fields for pixel egress and redaction outcome

### `context` — Add a cross-surface 'context stitch' record keyed by a monotonic event ID and timestamp: merge pendant bookmark/mic session events, Mac foreground/UI observations, browser evidence capsules, and relay pipeline IDs into one timeline, with explicit missing-surface markers rather than guessed alignment.
- **owner gets:** When something goes wrong—or when the owner says 'what was I doing then?'—the system can show one trustworthy timeline instead of four unrelated logs and false certainty about which tab or conversation matched the button press.
- effort: Medium: define the event envelope, clock-offset estimation, append-only local journal entry, and a read API that returns aligned events plus confidence and gaps.  ·  risk: Clock skew can create misleading ordering; solve with monotonic local sequence numbers, server receipt times, and confidence intervals. Keep raw audio out of the stitch record unless separately retained.
- cost: Tiny storage growth (metadata only); negligible model cost for alignment, with background summarization optional.  ·  latency: Event append is sub-100 ms; cross-surface reconstruction can be asynchronous in 1–3 s.
- security: This becomes a sensitive activity timeline. Encrypt at rest, apply per-source retention, redact browser text by default, and let the owner delete a stitch without deleting unrelated source logs.
- depends on: Pendant events carrying stable event IDs; Browser evidence capsule IDs and Mac execution receipt IDs; A relay/Mac endpoint to read the stitched timeline


## What it asked for

_Nothing._
