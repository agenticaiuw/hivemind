# Harness derivation — mac-terminal — round 142

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Start this job on my Mac and keep me informed through the pendant—even if I walk away or the internet drops.”"
- **useful because:** This turns the worn device into a real local control plane rather than a remote microphone: the owner can launch a long browser/file task, hear concise milestones, interrupt it, and later get a truthful completed/failed/recovered result. USB-attached operation works today even though LTE registration does not.
- **path:** pendant → mac-planner → relay-realtime → relay → browser-extension
- **model tier:** Use the realtime tier only for the initial command and short spoken milestone summaries; run the actual workflow on the Mac/browser job runner and use a cheaper background model to summarize logs.
- **latency:** Acknowledge within 1 second over USB; milestones within 3 seconds of job events; reconnect reconciliation within 10 seconds.
- **cost:** Low API cost: one planning call plus occasional cheap summaries; dominant cost is browser/computer execution, not tokens. USB serial daemon and durable event storage are the engineering cost.
- **security:** Job metadata and milestone text can leave the Mac through the relay; redact page contents by default and send only summaries. The owner has explicitly chosen maximum Mac access, so this is status/interrupt behavior, not a new approval gate.
- **missing:** A USB serial control protocol and Mac daemon binding the nRF9160 at /dev/cu.usbmodem00096003658*; Pendant firmware events for job-start, milestone, cancel, and reconnect (one button can cancel/ack while speech remains the normal input); Durable event cursor and reconciliation between /jobs, /pipeline/events, and serial transport; A browser job runner that emits typed progress, rather than one opaque completion

### "“Before I submit this form or send this message, tell me exactly what information is about to leave my Mac, where it is going, and what I copied from my private tabs.”"
- **useful because:** The browser can hold authenticated context and the Mac can hold local files, but today the owner cannot get a compact, trustworthy egress report. A spoken, field-level diff catches accidental personal or work-confidential data without blocking the owner's maximum-access workflow.
- **path:** browser-extension → mac-planner → mac-vision → relay-realtime → pendant → relay
- **model tier:** Use a cheaper background model for DOM/file classification and redaction; use realtime only to answer the owner's short spoken question and read the final concise report.
- **latency:** Preview in 2–5 seconds for a normal form; under 10 seconds for a multi-tab draft. Never delay ordinary browsing unless explicitly requested.
- **cost:** Moderate per preview, dominated by DOM/screenshot extraction and local file hashing; keep model input to changed fields and nearby labels, not whole pages.
- **security:** The inspector itself sees highly sensitive authenticated content. Keep raw values local, send only typed labels, destination, sensitivity class, and salted hashes to relay; never persist secrets or full form values. This is advisory and does not introduce a confirmation gate.
- **missing:** A browser pre-submit interception hook that can capture the final field set and destination before send; A Mac-local egress classifier covering clipboard, file attachments, browser fields, and network destination; A common provenance schema linking each outgoing field to tab URL/DOM locator or local file path; A pendant-friendly spoken diff renderer with truncation and a local redaction cache

### "“Only interrupt me when something is genuinely urgent: combine my Mac notifications, calendar context, and logged-in browser changes, then explain why you interrupted me on the pendant.”"
- **useful because:** The owner gets fewer distracting alerts and does not have to poll several surfaces. Corroborating a change with current meeting/focus state and the source page makes the interruption useful rather than another notification stream; USB-tethered pendant operation is testable now.
- **path:** mac-planner → browser-extension → relay → relay-realtime → pendant → mac-vision
- **model tier:** Use a background classifier/ranker for event correlation and quiet-hour batching; reserve realtime for the one-sentence spoken interrupt and follow-up question.
- **latency:** Urgent events surfaced within 15 seconds; non-urgent changes batched into the next spoken digest. The local Mac path should continue when relay is unavailable and sync later.
- **cost:** Low-to-moderate: event normalization and ranking dominate, with one cheap classification pass per burst rather than one model call per notification.
- **security:** Notification text and private-page snippets are sensitive. Keep full payloads local, transmit only a minimal explanation and source label, and allow per-app/site exclusions. It must never infer urgency from message content without showing its evidence.
- **missing:** A Mac notification/workspace/focus event feed with stable event IDs; Browser watch events normalized to the same event envelope as Mac events; A user-tunable urgency policy with corroboration, quiet hours, and deduplication; Pendant serial/audio delivery and acknowledgment state that survives a dropped relay link; A spoken evidence phrase (source, timestamp, reason) attached to every interrupt

### "“When I have a thought while I’m away from my Mac, let me capture it immediately on the pendant, keep it safe offline, and turn it into the right reminder, project note, or follow-up when I’m next connected.”"
- **useful because:** The owner’s most valuable thoughts happen while walking, commuting, or disconnected—exactly when the current cloud conversation cannot hear them. This gives the pendant an offline-first capture path and lets the Mac/relay later classify, deduplicate, attach context, and present the result without requiring the owner to reconstruct it.
- **path:** pendant → mac-planner → relay → relay-realtime → unified
- **model tier:** No expensive realtime model while offline: store a short encrypted audio clip and lightweight local metadata. On reconnection, use a cheap background transcription/classification model; use realtime only if the owner asks to clarify or correct the resulting item.
- **latency:** Capture begins in under 300 ms and must never wait for network. Sync starts within 5 seconds of USB/relay reconnection; a categorized draft should be ready within 30 seconds per minute of audio.
- **cost:** Low-to-moderate per capture, dominated by transcription; cap clips at 60 seconds and batch them. Hardware/firmware work is larger than API cost.
- **security:** Offline clips may contain sensitive speech. Encrypt at rest with a device key, use a bounded ring buffer with explicit expiry, authenticate sync, and avoid sending audio to the relay until connectivity and ownership are established. Classification creates drafts only; it must not silently send messages or create high-impact commitments.
- **missing:** Pendant firmware offline recorder using available flash, with encrypted ring-buffer storage, low-battery handling, and a clear LED/audio cue for saved/full/error states; A USB serial sync protocol for /dev/cu.usbmodem00096003658* plus a relay fallback when LTE eventually registers; A durable ingest endpoint and idempotency scheme so reconnects cannot duplicate notes; Background transcription, intent classification, and routing into existing reminders/projects/capture records with a review queue; A spoken or LED confirmation that tells the owner whether the clip is safely stored, synced, or awaiting review

### "“When I say ‘save that’ or ‘send that to my Mac,’ use what I was just hearing plus the page or selection currently in front of me, and put the right excerpt in the right note—without making me repeat it.”"
- **useful because:** The pendant hears the owner’s deictic references, while Safari and the Mac know what ‘that’ visually means. Joining the most recent spoken turn, active tab/selection, and local destination removes the exhausting re-copying and re-explaining that no single surface can solve.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → mac-vision → unified
- **model tier:** Realtime resolves the short reference only when invoked; a cheaper background model extracts and formats the excerpt. Keep raw audio and page text local to the relevant surface whenever possible.
- **latency:** Acknowledge intent in 1 second; show or speak the proposed excerpt in under 4 seconds; write only after the owner’s ordinary explicit command is complete.
- **cost:** Low per invocation, with vision/DOM extraction dominating. Use DOM selection first and screenshot vision only when no selection or semantic target exists.
- **security:** The system may combine private audio and authenticated page content. Require same-session/tab binding, keep provenance, redact unrelated page regions, and expose a concise source citation before writing. Do not infer a target when ambiguity is high.
- **missing:** A cross-surface reference token linking the last spoken utterance to a timestamped active-tab/selection snapshot; Browser selection and accessibility-tree capture exposed to the Mac planner; A destination resolver for Notes, project records, reminders, and clipboard with provenance; A pendant response that reads back the selected excerpt and source before committing

### "“Know when I’ve left my Mac and stop reading private things aloud; queue the useful result, then resume it safely when I’m wearing the pendant nearby again.”"
- **useful because:** The owner should not have a private browser page or notification spoken into an empty room, nor lose the result because they walked away. USB attachment and pendant presence can provide a concrete local signal today, while a future wearable link can extend it beyond the desk.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → relay
- **model tier:** Use local deterministic presence and routing for mute/queue decisions; use a cheap background model to compress queued results. Realtime is only for playback once presence is confirmed.
- **latency:** Mute or queue within 2 seconds of disconnect; resume handshake within 5 seconds of reconnect; queued digest within 15 seconds.
- **cost:** Minimal API cost; the main work is presence-state firmware, Mac serial monitoring, encrypted queueing, and correct audio routing.
- **security:** Presence is a privacy signal, not proof of user identity. Never treat it as authorization for irreversible actions. Encrypt queued text/audio, expire it, and default to withholding sensitive page content until a fresh local presence handshake succeeds.
- **missing:** A truthful USB attach/detach beacon and reconnect state machine for the pendant serial device; A Mac audio/privacy router that can suppress spoken output while preserving job execution; Sensitivity labels on browser, notification, and job outputs; Encrypted local pending-audio queue with resume cursor and expiry; A future BLE/LTE presence protocol if this must work away from the Mac


## Changes it proposed to its own stack

### `mac-harness` — Keep FULL_CONTROL_MODE and arbitrary run_shell, but wrap every invocation in a durable execution envelope: argv/command fingerprint, resolved cwd, start/end monotonic timestamps, exit code, signal, bounded stdout/stderr tail, network/process side-effect hints, and a resumable checkpoint for multi-command plans. Persist the envelope in the existing job journal and expose a machine-readable retrieval route; on failure, automatically run a cheap diagnosis pass and offer a corrected retry without rerunning successful steps.
- **owner gets:** When the owner says “what happened?” the agent can answer precisely instead of guessing, and a failed long task can recover from the failed step rather than starting over. This adds capability and truthfulness without restricting the owner’s trusted shell access.
- effort: Medium: executor wrapper, journal schema, shell stream capture, step IDs, and retry planner; high-value tests around timeouts, SIGTERM, and partial output.  ·  risk: Command output may contain secrets and giant logs; redact known token patterns, cap stored tails, and keep raw output local. A bad retry could duplicate side effects, so retry only steps explicitly marked idempotent or after the model diagnoses them; never pretend an unverified command succeeded.
- cost: Negligible API cost for envelopes; modest local disk usage with retention limits. A cheap diagnosis call only occurs after failure.  ·  latency: Near-zero start overhead; streaming output improves perceived latency. Failure diagnosis adds roughly 1–3 seconds.
- security: No new gate and no reduction of shell authority. Improve auditability by recording hashes and outcomes, while redacting secrets before relay exposure.
- depends on: Existing POST /execute and GET /jobs/:jobId/receipts; Existing GET /journal/:jobId and job records; A durable local output-retention policy; A typed step/idempotency annotation in plans


## What it asked for

_Nothing._
## Its own summary

Produced three distinct owner-facing capabilities. The strongest is a USB-tethered wearable control plane: start a long Mac/browser job, hear truthful milestones, cancel it from the pendant, and reconcile completion after walking away or losing the relay. Also proposed a non-blocking egress preview that explains exactly what a private-tab form/message will send, and corroborated urgency alerts that combine Mac focus/notifications with authenticated browser changes and explain every interruption. I additionally proposed stronger shell failure recovery/observability, while preserving the owner's explicit FULL_CONTROL_MODE and no-gates policy.

**Biggest unknown:** The essential missing seam is not another model: it is the live USB serial protocol/daemon and pendant firmware event contract. I still need that, plus a Mac notification/focus event feed, browser pre-submit hook, and a durable cross-surface event cursor. Existing routes cover planning, jobs, browser results, pipeline audio/events, watches, and journals, but none alone proves a physical pendant is attached or carries resumable job state.

