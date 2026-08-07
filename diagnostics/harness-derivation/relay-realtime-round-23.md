# Harness derivation — relay-realtime — round 23

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When I press the pendant button, capture a short voice note, tag it with time and place if available, and later summarize it into tasks.”"
- **useful because:** The owner can offload thoughts instantly while away from the Mac, and get them turned into actionable reminders without babysitting a workflow.
- **path:** pendant → relay → mac-bridge → mac-planner → dashboard
- **model tier:** Realtime only for the capture conversation; a cheaper planner model on the Mac summarizes and files tasks.
- **latency:** Immediate capture feedback (<300ms perceived) on pendant; summarization can happen seconds to minutes later.
- **cost:** Low per capture; biggest cost is audio transport/storage in R2 and transcription tokens.
- **security:** Audio leaves the device to relay storage; should be retained minimally and deletable. Summaries should avoid exposing sensitive content to broad surfaces.
- **missing:** A durable task ledger with receipts so the owner can see what happened; A scheduler/worker path to run summarization after capture; A consistent way to attach metadata (time, optional location) to notes


## Changes it proposed to its own stack

### `routines` — Introduce a lightweight scheduler using Durable Object alarms or Cloudflare Cron to trigger queued jobs (summarize notes, send digests, retry failed uploads).
- **owner gets:** Things the owner asks for can actually happen later, reliably, without keeping the Mac awake or waiting in a live call.
- effort: Moderate: define job types, persistence, retry policy, and alarm wiring; coordinate with mac-planner for work handoff.  ·  risk: Misfires or duplicate runs could create duplicate reminders; mitigate with idempotent receipts and job state checks.
- cost: Low ongoing cost; alarms are cheap, storage reads/writes dominate.  ·  latency: No impact on live voice; background tasks run when scheduled.
- security: Jobs carry user content; needs strict access control and minimal retention.
- depends on: A durable task ledger and job status API across relay and Mac


## What it asked for

### `s12-jivd` (skill) — offline_voice_note_buffer
- does: Record up to N short audio clips when the network is unavailable, store them encrypted on microSD, and upload when LTE-M is available.
- must be on-device because: If the link drops, the server cannot capture audio; the pendant must hold it until connectivity returns.
- trigger: button
- storage: Encrypted files on microSD; each clip <1 MB, plus a small queue index
- RAM budget: Small ring buffer and encoder state; aim <32 KB additional RAM

## Its own summary

Discovered current surfaces, tools, granted context/permissions, hardware profile, and device status. Proposed a voice-note-to-task capability, a scheduler change for background routines, and requested an offline voice note buffer skill on the pendant.

**Biggest unknown:** No durable task ledger/status API is confirmed available end-to-end, and the system still lacks a scheduler/worker path; without those, anything deferred remains fragile or impossible.

