# Harness derivation — mac-planner — round 252

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-observation-2026-08-09** — AI Pendant Agent has Accessibility and Screen Recording trusted, synthesized input verified, secure input inactive, and the Mac bridge is online. The host is currently at loginwindow; browser sessions are present (YouTube, Google News, and two test forms).
  - evidence: mac_readonly_inspect operation running_apps/foreground_app returned GET /observe at 2026-08-09T00:19:07Z with accessibility.trusted=true, screenRecording=true, inputReachability.status=verified, foregroundApp=loginwindow; discover devices reports home-macbook-bridge online.

## Capabilities it proposed

### "Take this research task from my voice, gather the sources in my authenticated browser, and finish it overnight even if the Mac sleeps or the link drops; in the morning give me the finished files, citations, and a one-sentence report of exactly what succeeded and what was skipped."
- **useful because:** The system can research, browse, and write files, but today a sleep/retry boundary can duplicate work or leave an apparently complete folder with missing pieces. This makes a long-running job trustworthy to the owner: artifacts are atomic, retries are idempotent, and the pendant receives a concise completion or failure notice rather than requiring inspection of logs.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** Use a cheap background model for source extraction, deduplication, and file assembly; reserve the realtime model for accepting the initial voice command and the final short spoken status. Browser actions remain deterministic and authenticated in the browser surface.
- **latency:** Start acknowledgement under 2 seconds. Work may run minutes to hours; the owner gets an alert only on completion, actionable failure, or a requested deadline. A sleeping Mac should pause and resume rather than silently time out.
- **cost:** Roughly $0.02–$0.30 per task depending on source count and synthesis; browser and Mac execution dominate wall time, not token cost. Receipts and manifests are a few KB.
- **security:** Authenticated browser pages and generated files may contain sensitive data. Keep page text on the relay only as long as needed, redact it from spoken alerts, never send or publish externally without confirmation, and scope output to ~/AI-Pendant-Workspace. A retry must prove the same job_id and hashes before replacing anything.
- **missing:** A scheduler/worker that can wake the Mac agent after sleep and distinguish a paused job from a failed job; A browser-side bounded export of citations/content rather than only UI actions; A relay-to-pendant durable job-completion alert carrying receipt id and severity; A single policy declaration for unattended browser reads and file creation

### "Run a wired pendant acceptance check now and tell me, in one spoken sentence, whether capture, Opus uplink, modem transport, and 24 kHz playback all passed; save the raw counters and a human-readable report in my workspace if anything is wrong."
- **useful because:** The pendant is physically attached to this Mac today, yet proving an end-to-end path still requires a specialist to connect logs, fixture output, and firmware counters manually. This gives the owner a trustworthy answer before a call and turns failures into a reproducible report instead of a vague 'audio sounded bad'.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** No realtime generation for the test itself. Use deterministic firmware diagnostic output and a cheap background model only to translate counters into one sentence; use realtime solely if the owner asks follow-up questions by voice.
- **latency:** Arm and start within 2 seconds; complete a bounded 30–60 second test. Speak the result immediately, with a durable report written before announcing PASS.
- **cost:** Near-zero model cost; one small structured report and fixture run. The dominant cost is the test's 30–60 seconds of USB-connected Mac time.
- **security:** The fixture must never open the microphone or persist owner audio; only synthetic frames, counters, and firmware version leave the device. Refuse to call it PASS if logs are truncated or a stage did not run. Store reports under ~/AI-Pendant-Workspace/diagnostics with restrictive file permissions.
- **missing:** A supported Mac-terminal action that performs bounded USB serial reads and invokes the already-accepted audio_path_diagnostic_fixture without arbitrary shell parsing; A parser/validator for sequence continuity, encode/decode timings, mic_drops, tx_starved, and the published alias-rejection/CPU thresholds; A relay event and pendant alert path for the final signed receipt

### "Queue the article currently open in my browser for my next walk: extract the readable page, make a two-minute spoken summary with the source link, and put it on the pendant so I can play it later without reopening the browser."
- **useful because:** This is a real division of labor: the browser has the session and page, the relay can summarize, the Mac can retain a citation, and the pendant is the only surface available while walking. It turns 'I should read this' into a durable, offline-playable item without asking the owner to copy URLs or manage a playlist.
- **path:** browser-extension → relay → mac-planner → pendant → dashboard
- **model tier:** Use a background model for extraction and a low-cost speech synthesis path for the two-minute item; realtime is unnecessary. The voice model only confirms which open tab was selected and reports queue status.
- **latency:** Capture and acknowledge in under 3 seconds; produce the audio within about 60 seconds for a normal article. The owner can walk away immediately; the pendant downloads and retains it for later playback, retrying after link loss.
- **cost:** Approximately $0.01–$0.08 per article including synthesis, dominated by audio generation and page length. A citation/metadata record is under 20 KB; audio size depends on codec but remains bounded by the existing delivery buffer.
- **security:** Only the selected tab's readable content should be sent; exclude passwords, forms, cookies, and unrelated tabs. Preserve the canonical URL for citation but redact query parameters by default. Never auto-submit or share the source. Expire the relay's page text after synthesis while retaining only owner-approved audio and metadata.
- **missing:** A browser action that returns bounded readable text plus canonical URL for the selected authenticated tab; A queue coordinator that binds one source hash to one generated audio item and prevents duplicate synthesis; An explicit owner policy for retaining source audio and metadata on the pendant's microSD; A spoken queue-status event from relay to the existing offline_alert_inbox

### "When I say “stop that job” to the pendant, cancel the running browser/Mac work, prevent any queued retry, and leave the workspace exactly as it was before the job started—with a receipt saying which steps were completed, rolled back, or could not be undone."
- **useful because:** Long-running cross-surface automation is not trustworthy if the owner cannot revoke it from the one device they are carrying. This gives the owner a real emergency brake and a truthful boundary between reversible staging and effects that already escaped. It is more useful than merely reporting job status: the command actively prevents further actions and closes the retry path.
- **path:** pendant → relay → browser-extension → mac-planner → dashboard
- **model tier:** No expensive realtime reasoning is needed after intent recognition. The relay should use a deterministic job controller; a cheap background model may summarize the final receipt. Realtime only confirms ambiguous references such as which of two active jobs “that job” means.
- **latency:** Acknowledge the stop request on the pendant within 1 second, cancel queued work within 2 seconds, and stop new browser/Mac actions at the next action boundary. Reconciliation and the detailed receipt may take longer, but the owner must hear whether the stop was accepted immediately.
- **cost:** Negligible model cost; the main engineering cost is cancellation and rollback bookkeeping. Receipts and staged manifests are a few KB. No additional per-invocation model call is required for an unambiguous command.
- **security:** Cancellation itself must be authenticated to the pendant/session and idempotent. It must never claim rollback for an email sent, purchase made, deletion completed, or other irreversible external effect. Browser credentials and page contents stay in their existing surfaces; the spoken result redacts URLs and private data.
- **missing:** A relay job controller with a cancel state, cancellation token, and retry suppression that propagates to every surface; Action-boundary checks in the Mac and browser executors so cancellation prevents the next action rather than merely marking a record stopped; A true rollback journal for staged files and browser/Mac mutations, with irreversible effects explicitly recorded as unrecoverable; A pendant command/event path for referring to and cancelling the active job, plus a durable completion receipt


## What it asked for

_Nothing._
