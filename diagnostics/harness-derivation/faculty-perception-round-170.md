# Harness derivation — faculty-perception — round 170

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac/browser permissions and connectivity** — At 2026-08-08T03:11Z, /ops/snapshot reports AI Pendant Agent ready with Accessibility and Screen Recording granted, browser extension online with Safari tab 1163292 on x.com and 9 tabs, no pending commands/spooled items, relay reachable on D1 with macBridgeOnline true. This does not establish a pendant or playback.
  - evidence: Authenticated GET /ops/snapshot returned permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true; browser.online=true; relay.reachable=true and macBridgeOnline=true.

## Capabilities it proposed

### "Before you tell me something happened or act on it, show me the evidence fence: what each surface directly observed, how fresh it is, what is only inferred, and what is unknowable."
- **useful because:** This is the single most useful perception capability: it prevents a completed Mac job, a relay-sent audio frame, or a stale browser session from being reported as owner-heard truth. It gives the owner an honest answer instead of a confident fiction, especially after sleep, disconnection, or an interrupted action.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Cheap background classifier/formatter; escalate to realtime only when the owner asks during a live turn. Deterministic freshness and provenance rules should run without a model.
- **latency:** Under 300 ms from cached snapshots; under 2 s when refreshing Mac, browser, and relay state in parallel.
- **cost:** Usually <$0.001 per request; dominated by no model call or a small summary call. Storage is a bounded ring of evidence references, not page/audio bodies.
- **security:** Never expose bearer tokens, page secrets, or raw screenshots. Every claim needs source, observedAt, freshness deadline, and confidence class (observed/inferred/unknown). Evidence references expire and are redacted before leaving the Mac. Any action gating on this fence must fail closed when required evidence is stale.
- **missing:** A real implementation of the unresolved cross-surface snapshot (the granted read_continuity_snapshot currently fails resolution).; A common evidence envelope with source, observedAt, expiresAt, operationId, stepId, and observed-versus-inferred status.; Pendant-originated playback/health events once a pendant exists; today the registry has no pendant and relay delivery is not playback proof.; Dashboard rendering of unknown and stale states rather than collapsing them into success.

### "When I return, reconstruct one action end to end: what I asked, which plan and browser/Mac steps ran, the exact postcondition observed, where the chain broke, and whether retrying is safe."
- **useful because:** Today a job can be marked complete when the Mac finished even though browser delivery or pendant playback never happened. A causal reconstruction turns scattered logs into a bounded incident report, distinguishes failure from missing observation, and prevents unsafe blind retries or duplicate actions.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Cheap background event joiner and deterministic state machine; use realtime only to explain the already-joined record conversationally.
- **latency:** Build incrementally during execution; answer in under 500 ms from indexed records, with a 2 s fallback for live route reads.
- **cost:** <$0.002 per reconstruction; dominated by one short explanation, with bounded local indexing.
- **security:** Join only by authenticated operation_id/step_id/job_id; redact page content, credentials, and screenshots; retain hashes and small excerpts with TTLs. Never infer success from a missing event. Retry recommendation must be 'unsafe/needs confirmation' when a mutation's postcondition is unknown.
- **missing:** A shared causal ID propagated from relay plan through Mac job, browser command, pipeline event, and any future pendant playback event.; A reader that correlates existing /jobs/:jobId/receipts, /journal/:jobId, /pipeline, and browser result records without treating derived completed status as proof.; A typed terminal state set including succeeded, failed, interrupted, stale, and unobserved-postcondition.

### "Is my wearable usable right now, even if it has no relay connection? Tell me whether the nRF pendant and audio bridge are physically present, which firmware/session they report, whether the Mac can exchange a test frame, and separately whether relay registration and playback are working."
- **useful because:** It separates four states owners currently see as one: no USB device, USB-present but firmware-unresponsive, locally usable but cloud-offline, and cloud-delivered but not physically heard. This is actionable today with the connected Mac/serial hardware and remains useful when LTE is unavailable.
- **path:** pendant → mac-terminal → relay-realtime → dashboard-ux
- **model tier:** Deterministic device probe and small formatter; no realtime model needed unless the owner asks a follow-up.
- **latency:** Initial probe under 2 s; serial identity and loopback under 5 s; relay status refresh under 1 s.
- **cost:** Near-zero API cost; one bounded Mac probe and one relay status read. Persist only the latest frame plus a small failure ring.
- **security:** Do not log serial payloads that may contain audio or bearer credentials. Require explicit consent before transmitting a loopback/test tone. Distinguish observed USB paths from inferred device identity, and never turn local serial presence into an 'online' claim.
- **missing:** A read-only Mac USB/serial health route or tool (the pending read_usb_device_health request was not resolved).; A firmware diagnostic command/response shared by nRF9160 and ESP32 bridge, with build ID, boot/session ID, counters, and monotonic timestamp.; A relay-side correlation field linking local test frame to registered device and (when present) playback acknowledgement.; A dashboard state model with independent local_transport, relay_transport, and playback fields.

### "Challenge this claim before I rely on it: independently re-check it through a second path, try to falsify it, and tell me whether the witnesses agree or merely repeat the same stale source."
- **useful because:** A system that only gathers more telemetry can still confidently repeat one bad observation. An adversarial claim challenge would catch cached browser state, relay mirror errors, stale Mac receipts, and duplicated derived statuses before they become advice or an action.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → dashboard-ux
- **model tier:** Deterministic witness selection and freshness checks first; a cheap background model summarizes disagreements, with realtime reserved for an interactive challenge.
- **latency:** 2–5 seconds for two independent reads and a concise verdict; longer challenges may run in background and notify only on material disagreement.
- **cost:** About $0.002–$0.01 per challenged claim, dominated by optional summarization; most checks are local deterministic reads.
- **security:** Independent must mean independent provenance, not two routes over the same cache. Do not replay private browser content into the relay; send hashes, classifications, and minimal redacted excerpts. A failed challenge must produce unknown, never a guessed answer.
- **missing:** A provenance graph that records shared upstream dependencies so apparent witness agreement is not mistaken for independence.; A read-only challenge orchestrator that can request fresh browser reload/DOM observation, Mac-side state, and relay state without mutating the owner's world.; A claim record with falsifier, witness set, freshness windows, and disagreement severity.

### "Keep an identity boundary for every fact: is this about me, my Mac account, a browser session, a relay device, or an unknown person/device? Warn me when those identities are being conflated before you personalize an answer or act."
- **useful because:** The owner can be logged into several accounts and browsers while the relay sees only device IDs and the Mac sees only local principals. Identity confusion can leak another account's page, send an action to the wrong device, or turn a machine's timezone and preferences into a claim about the person.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic identity and scope lattice; use a cheap model only to phrase a warning. Never infer owner identity from a tab title, device name, or bearer token alone.
- **latency:** Under 100 ms for every read/action preflight from cached scope; under 2 seconds when rechecking account/session ownership.
- **cost:** Negligible API cost; bounded metadata only, with occasional small model summaries.
- **security:** Identity labels must be pseudonymous and local where possible. Keep account names and browser secrets on-device. Require explicit confirmation before crossing from machine/account identity to owner identity or from one device to another.
- **missing:** A signed identity-and-scope envelope attached to browser observations, Mac jobs, relay device records, and future pendant telemetry.; A user-maintained mapping for which accounts/devices are the owner's, shared, delegated, or unknown; do not infer it from presence.; Cross-surface policy checks that block personalization and action when the target identity is unknown or scope has expired.

### "Tell me whether two events can honestly be ordered: reconcile the Mac, relay, browser, and pendant clocks, show the uncertainty interval, and say when the timestamp is too ambiguous to support 'before', 'after', or 'while'."
- **useful because:** Temporal mistakes are perception failures with real consequences: a stale browser result can look newer than a relay event, a zoneless pendant clock can be assigned the Mac timezone incorrectly, and a 'this morning' answer can silently use the wrong clock. Honest partial ordering is more useful than fabricated precision.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard-ux
- **model tier:** Deterministic clock-offset estimation and interval algebra; a cheap model converts the result into natural language only after the intervals are computed.
- **latency:** Under 300 ms from stored heartbeats; under 3 seconds when fresh probes and a round-trip offset measurement are needed.
- **cost:** Near-zero API cost; occasional relay/Mac round trips and a few hundred bytes of clock metadata per session.
- **security:** Use monotonic counters and signed timestamps where available; never expose raw device identifiers unnecessarily. Do not silently assign the owner's timezone to a pendant with no location/timezone evidence. Mark wall-clock conversions as uncertain.
- **missing:** A cross-surface clock-sync protocol carrying monotonic boot/session counters, send/receive times, and measured uncertainty rather than bare ISO timestamps.; Pendant NITZ/GNSS or an explicit owner timezone setting; currently the pendant clock is zoneless and the Mac's America/New_York zone is not proof of the owner's location.; Event queries that return source clock, offset estimate, and uncertainty interval alongside each record.


## Changes it proposed to its own stack

### `integration` — Make operation_id and step_id mandatory, stable join keys across relay plans, Mac jobs, browser commands/results, pipeline events, action-ledger receipts, and future pendant events. Add an evidence envelope to each step with observedAt, source, postcondition type, redacted evidence reference or content hash, expiresAt, and observed/inferred/unknown status. Require every completion reader to reject a success claim when required postcondition evidence is absent or expired.
- **owner gets:** After asking the system to do something, the owner can see exactly which step produced proof and which did not, instead of being told 'done' because a machine merely ran. It makes retries safer and exposes stale or unverifiable results.
- effort: Medium: adapters at existing writers/readers plus a migration for old records; no new large data store.  ·  risk: Older jobs lack IDs and evidence; label them legacy/unknown rather than fabricating joins. Redaction bugs could leak sensitive page data; hash-first references, short TTLs, and tests around secrets mitigate this.
- cost: Negligible API cost; bounded metadata adds roughly hundreds of bytes per step.  ·  latency: <10 ms local bookkeeping; no extra model turn.
- security: Improves least-privilege auditing, but evidence references must be capability-scoped and expire. Never put raw screenshots, audio, or bearer tokens in relay receipts.
- depends on: Mount the existing Mac browser provenance routes and connect them to browser result handling.; Define a pendant-originated device_playback event on POST /v1/pendant/jobs/:jobId/events when hardware is available.; Add a relay-to-Mac correlation field to relay browser reads; current cloud relay read_web_page emits no ID/hash/provenance.

### `firmware` — Add a time-provenance frame to the pendant protocol: capture modem NITZ when available (and GNSS fix only when explicitly enabled), retain source, acquisition age, UTC offset, monotonic boot/session counter, and uncertainty; if unavailable, emit an explicit zoneless/unknown marker. Have the relay and Mac preserve this metadata rather than coercing pendant digits into the Mac timezone.
- **owner gets:** Voice notes, reminders, and 'what happened when' answers will stop silently landing on the wrong date or timezone. When the pendant has no network, the owner sees honest monotonic ordering instead of a fabricated wall-clock time.
- effort: Medium firmware and protocol work plus small relay/Mac schema adapters; GNSS policy and battery impact need owner choice.  ·  risk: GNSS can expose location and consume power; NITZ can be stale or carrier-dependent. Keep GNSS off by default, require explicit opt-in, age out stale fixes, and preserve unknown rather than guessing.
- cost: Firmware work only if using the existing modem GNSS/NITZ path; optional GNSS adds measurable radio power and possibly 1–3 seconds per fix, no new recurring API cost.  ·  latency: No effect on live audio; a NITZ frame is available on registration, while GNSS acquisition is asynchronous and must never block conversation.
- security: Location and timezone metadata are sensitive. Store coarse/short-lived provenance, encrypt in transit, and never include coordinates in spoken output without confirmation.
- depends on: Cross-surface clock interval capability and event metadata carrying uncertainty.; A scoped pendant telemetry endpoint; the current pendant is not registered and real firmware heartbeat is absent.; Owner opt-in policy for GNSS/location use.


## What it asked for

_Nothing._
## Its own summary

I verified a meaningful state change: the Mac agent is now fully ready (Accessibility and Screen Recording granted), Safari bridge is online with 9 tabs and no pending/spooled commands, and the D1 relay is reachable with the Mac bridge online. I recorded this as a fresh fact and proposed three distinct owner-facing capabilities: an evidence trust fence, causal end-to-end action reconstruction, and a USB/local-versus-relay wearable usability probe. I also proposed the concrete operation_id/step_id evidence-envelope integration requested by faculty-action. What I still need is not another permission grant: the unresolved read_continuity_snapshot implementation, a read-only USB/serial health probe for the physically connected chips, and a pendant-originated playback event once a pendant actually registers.

**Biggest unknown:** Whether any pendant/audio hardware is physically present and responsive right now; the live relay registry has no pendant, and no available probe can inspect the USB serial devices. Even with the Mac and relay healthy, playback remains unknown.

