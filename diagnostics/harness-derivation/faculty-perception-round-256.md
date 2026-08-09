# Harness derivation — faculty-perception — round 256

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device registry visibility** — The live devices inventory now includes an nrf9160-pendant entry marked offline (alongside online home-macbook-bridge); however, the local Mac agent does not expose GET /v1/devices/status, so I cannot independently retrieve the relay row's timestamps or distinguish a stale registration from current hardware presence this round.
  - evidence: discover(devices) returned nrf9160-pendant · nrf_pendant · offline · last seen 2026-08-09T02:56:31.366Z; probe_http GET /v1/devices/status returned 404 No such route on this agent.

## Capabilities it proposed

### "Before you act, tell me whether the system's important facts agree with reality: timezone, device presence, browser state, and whether the last action actually finished."
- **useful because:** The system currently has a machine-written America/Chicago preference pinned at high confidence while the Mac is America/New_York, and an nrf9160-pendant row can appear offline without proving the pendant is absent. This capability prevents a confident but wrong answer or action by showing conflicts and their evidence sources first.
- **path:** Mac context and OS → relay device registry → browser extension → relay
- **model tier:** background for periodic checks; realtime only to explain a detected conflict during a voice turn
- **latency:** Under 2 seconds for a voice-turn check; under 30 seconds for a full cross-surface audit
- **cost:** Low: one cheap structured audit model call only when facts conflict; most checks are deterministic route reads
- **security:** Read-only by default. Device identifiers and page titles stay local; never send page bodies to the relay merely to compare state. Acting on a conflict still requires the normal confirmation policy.
- **missing:** A signed/provenance-tagged context projection that exposes source.origin and observedAt to the audit; A relay device-status adapter reachable from the Mac agent (the local agent's /v1/devices/status is 404 even though the relay route exists); A browser snapshot freshness/observation timestamp in the shared audit payload

### "Run a one-minute 'can I trust the pendant right now?' check and give me a pass/fail report: relay reachability, USB bench link, browser session, audio path, and the exact last stage that was observed."
- **useful because:** Today the Mac bridge is live, Safari is live, and an nrf9160-pendant registry row exists but is offline; historical pipeline audio is not proof of current hardware. A single bounded report would stop the owner from mistaking recorded telemetry or a stale registry row for a wearable that can hear them now.
- **path:** pendant firmware over USB serial (bench mode) → Mac bridge → relay → browser extension
- **model tier:** Deterministic probes first; a cheap background model summarizes only failures. No realtime model is needed unless the owner asks a follow-up.
- **latency:** 60 seconds maximum, with partial results streamed at 10-second boundaries
- **cost:** Near-zero model cost; bounded serial and HTTP probes dominate. One short summary call only on completion.
- **security:** Read-only diagnostics. USB commands must be allowlisted and capped by bytes/time; never expose relay bearer tokens or raw audio. Clearly label this as bench connectivity, not proof of wearable operation away from the Mac.
- **missing:** A real bounded USB-serial diagnostic action (the granted mac_usb_serial_diagnostics is a proposal, not callable yet); A relay-side device status proxy available to the Mac agent; A standardized audio test pattern and receipt that distinguishes historical /pipeline data from this run

### "Before carrying out an approved action, ask: 'Is the thing I am about to change still the same thing you approved?' Show the page/account/file identity, what changed since approval, and refuse silently drifting targets."
- **useful because:** A browser tab, logged-in account, or Mac file can change between planning and execution. The owner needs protection from acting on a different tab, account, record, or document—not merely a receipt after the fact. This is a perception gate that catches target drift before an action leaves the machine.
- **path:** browser extension holding the authenticated session → Mac agent action ledger and filesystem/app state → relay voice turn that holds the owner's approval → judgement/action faculties
- **model tier:** Cheap deterministic comparison of URL/host/tab/session, content hash, and target locator; use the realtime model only to explain a mismatch in plain language.
- **latency:** 300 ms when a prior evidence capsule exists; up to 2 seconds for a fresh browser snapshot and Mac state read
- **cost:** Minimal: hashes and metadata are local; one short model explanation only for mismatches
- **security:** Never transmit page bodies or secrets to the relay. Treat an account/target mismatch as a hard stop. Evidence must be revocable and content bodies must honor existing capsule expiry.
- **missing:** A shared approval token that binds the planned action to an evidence capsule and target identity; A browser result path that returns a fresh content hash and stable tab/session pseudonym on every inspection; A preflight hook in the action executor that can block execution rather than merely report drift

### "Did anything happen while I was away—and can you prove that it did not happen when you say it did not? Give me a bounded negative-proof report for messages, files, browser mutations, Mac actions, and pendant speech, with the exact sources checked and explicit blind spots."
- **useful because:** Today the system can report many positive receipts, but absence is routinely inferred from count-capped or stale stores. The owner needs to know whether 'nothing happened' means verified absence, expired evidence, an offline surface, or simply an unobserved surface.
- **path:** relay event and job history → Mac action ledger and pipeline → browser extension mutation receipts → pendant delivery ledger → relay voice response
- **model tier:** Deterministic source checks and watermarks first; a cheap model converts the result into a short explanation only after evidence classification.
- **latency:** Under 3 seconds for recent history; up to 15 seconds for a bounded multi-source audit
- **cost:** Low recurring cost; storage and indexed watermarks dominate, with a small summarization call only on request
- **security:** Negative claims must never be presented as global truth when a source was offline or retention expired. Keep sensitive message/file contents local; return event types, hashes, timestamps, and evidence coverage rather than bodies.
- **missing:** A durable per-source observation watermark and explicit 'not observed' state; A unified event identity linking Mac actions, browser mutations, relay jobs, and pendant delivery records; A retention-aware query that returns coverage gaps instead of silently truncating them; A real device-originated playback record for pendant speech

### "Revoke this one permission everywhere now—stop queued Mac work, browser commands, relay jobs, and pending pendant speech—and prove each surface has reached a stopped state."
- **useful because:** Today permission changes and cancellations are fragmented. A browser command, relay job, Mac action, or announcement can remain pending in a different store, and the owner cannot obtain one authoritative proof that a revocation propagated. This gives the owner a real emergency brake for the whole hive without revoking unrelated permissions.
- **path:** relay authorization and job queue → Mac agent sessions, jobs, and action ledger → browser extension command spool and authenticated sessions → pendant announcement/audio queue → voice interface reporting
- **model tier:** Deterministic cancellation fan-out and receipt verification; realtime model only interprets the owner's natural-language scope and explains any surface that could not confirm.
- **latency:** Acknowledge the request in under 300 ms; fan-out and verification within 5 seconds, with an explicit unresolved list if a surface is offline
- **cost:** Near-zero model cost; bounded cancellation calls and a small durable revocation record
- **security:** This is intentionally high-impact and must require explicit confirmation except for a configured emergency phrase. Revocation records need tamper-resistant timestamps, but must not include message/page contents. Offline pendant revocation must remain visibly pending until the device checks in.
- **missing:** A shared revocation identifier and scope model understood by relay, Mac, browser, and pendant; Cancellation endpoints that return durable receipts for every queued artifact; A pendant-held denylist for offline speech and action tokens; A relay coordinator that waits for all surface acknowledgements instead of declaring success after Mac cancellation

### "For any high-stakes claim—'the payment went through', 'the file was deleted', 'the message was sent'—ask an independent surface to challenge it, then tell me whether the evidence is independent or merely the same receipt repeated."
- **useful because:** The hive currently treats multiple projections of one Mac-side completion as corroboration. The owner needs protection against correlated false confidence: a relay receipt and a Mac receipt may both only prove that a request was accepted, not that the external world changed.
- **path:** Mac action execution and ledger → browser authenticated result or iOS mirror → relay job/result records → pendant voice response → judgement faculty
- **model tier:** Deterministic evidence graph first; a background model classifies evidence independence. Realtime is reserved for explaining a failed challenge in conversation.
- **latency:** Under 2 seconds for ordinary claims; high-stakes actions may wait up to 5 seconds for an independent observation
- **cost:** Low: graph joins and hashes are local; occasional small classification call
- **security:** Challenge reads must not mutate the target. Never treat screenshots or model assertions as independent of the action that produced them. Require explicit owner confirmation when no independent observer exists.
- **missing:** Evidence-source lineage that identifies common ancestry between receipts; Read-only verification adapters for external state (browser/iOS/Mac apps); A policy marking which claims require independent confirmation; A result schema distinguishing accepted, observed, and externally verified


## What it asked for

_Nothing._
