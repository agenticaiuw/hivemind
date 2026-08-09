# Harness derivation — faculty-perception — round 251

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac permissions** — The live Mac agent now reports Accessibility and Screen Recording granted for com.aipendant.agent; permissions.ready=true, with requiredMissing and optionalMissing empty.
  - evidence: read_continuity_snapshot include relay, invoked GET /ops/snapshot at 2026-08-09T03:40Z; body status.permissions
- **device registry** — The discovered device view now includes nrf9160-pendant as nrf_pendant, offline, last seen 2026-08-09T02:56:31.366Z; this is materially different from the prior no-registry state.
  - evidence: discover(category=devices) returned nrf9160-pendant · nrf_pendant · offline · last seen 2026-08-09T02:56:31.366Z
- **browser live state** — Safari browser bridge is online with one tab at YouTube (tab 85), zero pending commands and zero spooled commands; extension v1.2.0.
  - evidence: read_continuity_snapshot include relay, GET /ops/snapshot, browser.devices and browser.spool fields

## Capabilities it proposed

### "“Can you reach me right now, and where will your answer come out?”"
- **useful because:** The system currently has contradictory-looking liveness signals: the pendant is present in the registry but offline, while the Mac bridge and Safari bridge are live. This gives the owner a plain-language, timestamped answer based on verified paths instead of pretending relay acceptance means the owner can hear it. It should name the strongest currently working output (pendant, Mac, or browser) and explicitly say when no spoken path is verified.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Background/local deterministic aggregation first; realtime only to phrase the one-sentence answer after the checks.
- **latency:** Under 2 seconds for registry/heartbeat and Mac/browser checks; do not wait for a dead pendant beyond a bounded 500 ms probe.
- **cost:** Near-zero model cost when rendered from structured status; at most one short realtime turn if the owner asks follow-up. Dominant cost is one bounded liveness probe, not tokens.
- **security:** Expose only online/offline, last-seen timestamps, and route availability—never device credentials or browser URL contents. A positive answer must require fresh evidence, not a stale registry row.
- **missing:** A relay-side authenticated, bounded pendant WebSocket reachability probe that distinguishes registered/stale from currently connected.; A common freshness schema joining the relay device row, Mac agent status, browser bridge status, and audio-output readiness.; A user-facing read route that returns the selected output path and evidence timestamps.

### "“Read what is on my screen and tell me the next safe step through the pendant.”"
- **useful because:** With Accessibility and Screen Recording now genuinely granted, the system can finally ground a spoken answer in the actual foreground UI rather than guessing from app names or browser history. The Mac captures a redacted visual/UI observation, judgement selects a reversible next step, and the relay/pendant delivers it; if the pendant is offline, the Mac speaks or displays the answer and records that substitution.
- **path:** mac → browser → pendant → relay → dashboard
- **model tier:** Vision model only for screen interpretation; cheap local planner for UI semantics and reversible-step selection; realtime voice only for the short spoken response.
- **latency:** 3–6 seconds for a fresh screenshot plus interpretation; never execute a click/type from this capability without a separate confirmation.
- **cost:** One vision inference dominates, roughly a few cents depending on image size; local AppleScript/browser inspection is negligible. Keep screenshots ephemeral and send only the cropped/redacted region to the model.
- **security:** Screen data may include secrets. Redact password fields and unrelated windows before model upload; require confirmation before sending, deleting, purchasing, or changing settings. Persist a hash and source app/region, not the raw screenshot, unless the owner asks.
- **missing:** A single cross-surface command that joins the now-ready /observe or computer-use screenshot with browser inspection and a pendant/relay output selection.; A policy gate that labels the result as observed versus inferred and blocks destructive next steps until confirmation.; A delivery fallback that chooses Mac audio when the pendant registry is stale/offline and reports that substitution.

### "“Handle this in the background, but interrupt me only when you need a decision—and prove that I answered the decision.”"
- **useful because:** Long Mac/browser jobs currently can finish, fail, or wait for approval without establishing that the owner was actually reached. This capability turns a workflow into a resilient human-in-the-loop: Mac/browser execute reversible preparation, relay holds the checkpoint, the pendant announces it when genuinely connected, and the owner's spoken response is accepted only after capture-quality and playback/attention evidence. If the pendant is unavailable, it leaves a clearly labeled pending decision rather than silently timing out.
- **path:** mac → browser → relay → pendant → dashboard
- **model tier:** Cheaper background model for monitoring and summarizing state; realtime only for the brief decision prompt and response; deterministic firmware/relay state machine owns retries and deduplication.
- **latency:** Background work may run for minutes or hours. A checkpoint should reach a live surface within 2 seconds; stale or offline pendant paths must fail over to Mac audio/notification without claiming attention.
- **cost:** Low: background polling/event handling dominates; one short realtime exchange per checkpoint. Avoid repeatedly resending full job context by passing an opaque checkpoint ID and a compact diff.
- **security:** Never auto-approve destructive actions from an ambiguous or noisy utterance. Bind each response to a nonce, workflow, and expiry; require confirmation for mail, deletion, purchase, or external publication. The dashboard should show whether the response was heard, merely transcribed, or only queued.
- **missing:** A first-class decision-checkpoint state machine spanning relay jobs, Mac/browser pending commands, and the existing approval route.; Firmware emission and relay consumption of the accepted audio delivery/playback lifecycle so “prompted” and “owner answered” are separate states.; A Mac fallback notifier and dashboard row that expose unanswered checkpoints without inventing pendant delivery.; A compact context-diff payload so background checkpoints do not resend the whole workflow transcript.

### "“Keep private things private while you help me.”"
- **useful because:** Today, sensitive text can cross several boundaries independently: a browser page can enter a relay response, a screen can enter a vision request, and spoken output can expose information in the room. The owner should be able to invoke one privacy mode that coordinates all surfaces instead of trusting each tool separately. It would detect or accept a sensitive context, stop cloud transmission, suppress pendant announcements, redact durable traces, and resume only after an explicit local gesture or spoken release.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** Deterministic local policy and redaction first; a small local classifier for sensitivity; no realtime model call while privacy mode is active. Use the realtime tier only to acknowledge the mode after the local device confirms it.
- **latency:** Privacy activation under 300 ms locally; cloud transmission must stop before any new capture or screenshot leaves the Mac. Resume in under 1 second after explicit release.
- **cost:** Minimal model cost if classification runs locally; dominant engineering cost is enforcing the gate at every capture, browser-read, TTS, and telemetry boundary.
- **security:** Fail closed: uncertain classification must suppress upload. Keep only an in-memory mode state and a minimal audit event; never store the sensitive sample used for classification. Require a physical pendant press or local Mac confirmation to resume.
- **missing:** A single privacy-mode policy propagated from Mac to relay, browser extension, and pendant firmware.; Capture/screenshot/browser-read interceptors that enforce the policy rather than merely labeling content untrusted.; A relay-side outbound-audio gate and a firmware mute state that survives a dropped connection.; A dashboard indicator showing which surfaces are currently blocked.

### "“During this meeting, quietly catch factual mistakes and give me a source only when I ask.”"
- **useful because:** The owner cannot currently combine live pendant speech, the Mac's meeting context, browser research, and a low-disruption spoken channel into one reliable assistant. This would transcribe locally, identify candidate claims, research only selected claims through the browser/relay, retain source and timestamp, and whisper a short correction or hold it for an explicit request. It would distinguish a detected disagreement from a verified mistake and never interrupt the meeting by default.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** Local streaming transcription and a cheap claim extractor; background research model for selected claims; realtime tier only for the owner's explicit ask or a very high-confidence urgent alert.
- **latency:** Capture-to-candidate under 2 seconds locally; research can take 5–15 seconds and should queue silently. Spoken intervention must be under 500 ms once explicitly requested.
- **cost:** Streaming transcription and claim extraction dominate; browser research is occasional. Avoid sending the whole meeting to the cloud—send only short, redacted claim windows.
- **security:** Meetings contain other people's private speech. Require a visible/physical recording indication, local retention limits, participant-sensitive redaction, and an explicit policy for whether claims may leave the Mac. Never present search disagreement as fact.
- **missing:** A local meeting-session controller that segments speech, tracks speaker/session boundaries, and supports pause/resume from the pendant.; A claim object linking transcript time, confidence, source query, source capsule, and whether the owner requested an interruption.; A quiet result channel that can queue a correction without speaking until requested.; A consent and retention policy for third-party voices.

### "“Make this change everywhere, but either all copies agree or undo the partial change.”"
- **useful because:** Today a multi-surface task can update a browser site, Mac file, and mirrored iPhone in sequence, leaving a partially completed and difficult-to-reconstruct state if one surface fails. The owner should get a genuine cross-device transaction: preview the intended diff, reserve each surface, commit in a defined order, verify post-state on every surface, and automatically compensate reversible steps when the transaction cannot complete. Irreversible steps remain behind explicit confirmation.
- **path:** mac → browser → ios → relay → dashboard
- **model tier:** Deterministic transaction coordinator and state comparison; cheap planner for mapping the owner's goal to reversible operations; realtime only to explain a conflict or request confirmation.
- **latency:** Preview within 3 seconds; commit may take up to 30 seconds across devices. On timeout, stop further writes immediately and present exact committed/uncommitted surfaces.
- **cost:** Low model cost; engineering and verification dominate. Each surface needs one read-before, write, and read-after rather than repeated conversational planning.
- **security:** Never claim atomicity where an external site or iPhone action is irreversible. Show the complete diff and affected accounts before commit; require confirmation for mail, purchases, deletion, or publication. Store only bounded hashes and rollback recipes, not secrets.
- **missing:** A cross-surface transaction coordinator with leases, idempotency keys, and explicit commit/compensate states.; Standard pre-state/post-state adapters for Mac, browser, and iPhone Mirroring actions.; A capability declaration for which operations are truly reversible and which require a human confirmation.; A dashboard receipt that separates committed, compensated, and unknown outcomes.


## What it asked for

_Nothing._
