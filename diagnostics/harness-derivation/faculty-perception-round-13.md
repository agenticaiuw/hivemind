# Harness derivation — faculty-perception — round 13

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-agent-status** — Mac local agent v0.5.0 is reachable at /health; bearer token is configured and full-control planner is enabled, but mac-vision loop is disabled because Accessibility trust is false and vision upload consent is false.
  - evidence: GET /health returned 200; GET /ops/status liveResponse agent fields.
- **browser-status** — The home Chrome extension is offline with no active tab metadata and two pending browser commands.
  - evidence: GET /browser/status liveResponse at 2026-08-07T09:21:08.821Z.
- **pendant-audio** — Pendant captures at 15,625 Hz and encodes uplink Opus at 16 kHz/16 kbps; playback decodes 24 kHz 60 ms frames then resamples to 31,250 Hz I2S. Decode is about 25.4 ms per packet; encode about 15 ms per call; simultaneous operation uses roughly 87% of one core.
  - evidence: describe(audio).
- **pendant-offline-alerts** — At 2026-08-07T07:22:00.555Z, a pipeline event reports the pendant surfaced two held alerts from its microSD offline store after reconnect; the event says last_alert_id=a3 and uptime_s=323.
  - evidence: GET /pipeline liveResponse for pipelineId job_27616bb0-ccff-41fb-a752-09d3c6648baa.

## Capabilities it proposed

### "“Did that actually go through?”"
- **useful because:** When LTE-M drops, browser disconnects, or a Mac job is still processing, the owner needs a trustworthy answer without accidentally submitting twice. The system would reconcile the pendant's offline alert/store event, relay job and audio receipt, Mac job/receipt, and browser command result into one evidence-backed status: completed, still running, failed before effect, or unknown—plus the safest next step. It should work from a short spoken query after reconnect and link to the exact evidence on the Mac for review.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for reconciliation and evidence normalization; realtime only for the owner's short spoken question and concise answer
- **latency:** A reconnect-triggered reconciliation should finish within 5 seconds; spoken status should begin within 500 ms using cached state, then correct itself if late receipts arrive.
- **cost:** About $0.005–$0.03 per reconciliation, dominated by background model summarization; deterministic event joins and hashes should handle most cases at negligible model cost.
- **security:** Private browser URLs, command payloads, and audio/job identifiers leave the Mac only as minimized hashes and redacted result fields; full evidence remains local. Never infer success from a request acknowledgment, and require confirmation before offering a retry for any potentially irreversible action.
- **missing:** A shared cross-surface job/effect identity and idempotency key carried from pendant through relay, Mac planner, and browser bridge; A durable receipt schema distinguishing accepted, executed, externally observed, and confirmed effects; Reconnect-triggered reconciliation worker and dashboard timeline; Pendant command/status protocol for asking about the last request offline and surfacing a late correction

### "“Pause this safely when I walk away, and pick it up when I’m back.”"
- **useful because:** Today a browser or Mac task can remain ambiguous when the owner leaves, the pendant loses LTE, or the laptop sleeps. The owner should be able to start a reversible multi-step task, walk away, and return to an exact checkpoint: what was read, what was filled, what was not submitted, and what requires attention. The pendant’s physical presence becomes a practical safety boundary rather than merely an audio endpoint.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background model for checkpoint summarization and resume planning; realtime only for the pendant’s leave/return prompts and concise checkpoint readout
- **latency:** Pause within 2 seconds of a confirmed departure or link-loss policy trigger; on return, speak a checkpoint within 1 second and resume only after explicit confirmation when the next step could have external effect.
- **cost:** Roughly $0.003–$0.02 per pause/resume cycle, mostly for checkpoint compression; presence detection, state persistence, and action gating are deterministic.
- **security:** Presence must not be inferred from audio alone. Require an authenticated pendant-session token plus configurable grace period, and treat loss of presence as a pause—not permission to act. Keep page contents and form data on the Mac/browser; encrypt checkpoint metadata and expire it. Never auto-resume sending, purchasing, deletion, or submission.
- **missing:** Authenticated pendant-presence/session leases shared with relay and Mac; A resumable action graph with durable, per-step checkpoints and compensation/undo metadata; Browser tab/session freeze and reattachment primitives that preserve private-page context without copying content; Owner-configurable departure grace period and explicit resume/approval protocol; Dashboard UI showing the exact paused boundary and evidence


## Changes it proposed to its own stack

### `context` — Add a signed, timestamped cross-surface capability snapshot (“truth card”) compiled by perception. It polls/receives Mac agent health, browser heartbeat, relay reachability, pendant link/SD queue state, and audio pipeline headroom; each capability is marked available, degraded, queued, or unavailable with freshness and the concrete evidence. Judgement and action consume this card rather than stale hand-written fleet context. On reconnect, late events update the same snapshot and invalidate decisions that depended on stale state.
- **owner gets:** The pendant would stop promising actions that cannot currently work and would explain short, actionable blockers (“browser is offline; I queued nothing” or “your request is still processing”) before the owner repeats a command. It also prevents a silent audio overload or stale browser tab from being mistaken for a successful interaction.
- effort: Medium: define schema/signing, adapters for relay and Mac routes, pendant status event ingestion, freshness rules, and a compact spoken projection plus dashboard detail.  ·  risk: A transient probe failure could incorrectly block a useful action. Recover with per-source grace periods, explicit “unknown” instead of false failure, and a manual retry/status query; never treat health alone as effect confirmation.
- cost: Negligible for deterministic probes; roughly $0.001–$0.01 only when a cheap background model compresses many findings into a human explanation.  ·  latency: Adds parallel health probes, targeted under 300 ms when services respond; cached card supports immediate speech while refresh continues.
- security: Transmit only health metadata, IDs, timestamps, and redacted error codes; do not copy page content, audio, or secrets into the card. Sign snapshots to prevent a stale or spoofed surface from claiming readiness.
- depends on: Cross-surface correlation/idempotency identity from the proposed ‘Did that actually go through?’ capability; A pendant/relay status event and offline-queue observation path; Browser heartbeat and Mac diagnostic routes remaining authenticated

### `hardware` — Add a low-power authenticated proximity channel to the pendant: use the existing ESP32 bridge’s BLE capability, or add a small BLE beacon if the bridge is not continuously powered, with rotating challenge-response tokens tied to the active relay session. The pendant should emit only presence lease/expiry and link-quality events; the Mac agent verifies the lease before allowing a paused workflow to resume.
- **owner gets:** Walking away from the Mac would reliably stop a private or potentially consequential workflow, and returning would restore the exact checkpoint without requiring the owner to remember what was left open. It gives the owner a physical, privacy-preserving safety boundary even when LTE or audio is intermittent.
- effort: Medium hardware/firmware and integration work: BLE power policy, rotating-token pairing, lease protocol, sleep/wake handling, Mac verification, and failure-mode testing around laptop sleep and pendant battery loss.  ·  risk: False departures could pause work or frequent BLE scanning could reduce battery life. Recover with a configurable grace period, hysteresis, explicit paused state, and fallback to conservative pause on uncertainty. Do not use proximity as authorization for irreversible actions.
- cost: Potentially $0 using the existing ESP32 bridge if its BLE radio and power budget are available; otherwise approximately $3–$8 for a beacon/module. BLE advertising/scanning would add a small intermittent current draw, likely tens to a few hundred mW only during scans, requiring measurement against the current LTE/battery budget.  ·  latency: Presence changes can be detected in roughly 1–3 seconds, with no added latency to normal voice traffic. Resume still waits for checkpoint validation and confirmation where required.
- security: Use rotating, per-session challenge-response tokens rather than a stable identifier that enables tracking. Store pairing keys in protected storage where available, expose no page content over BLE, and invalidate leases on relay-session termination.
- depends on: The resumable action/checkpoint protocol in the proposed pause-and-return capability; A Mac-side authenticated lease verifier; Confirmed ESP32 bridge BLE availability and measured sleep current


## What it asked for

_Nothing._
