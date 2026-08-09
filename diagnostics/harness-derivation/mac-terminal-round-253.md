# Harness derivation — mac-terminal — round 253

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### ""Are the pendant and audio bridge actually alive right now?" Give me one truthful answer from the worn device, including which chip is silent, the last heartbeat age, firmware counters, and the exact next bench action if either is unhealthy."
- **useful because:** Both chips are physically on the Mac today, but USB is currently only a pile of capture scripts with no structured health result. This would turn bench bring-up from guessing at two UART logs into a single answer the owner can ask while wearing the pendant, and it would never confuse USB bench health with LTE product connectivity.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** A deterministic Mac-side parser should read the existing dual-chip capture/health frames; use a cheap model only to summarize anomalies. Realtime is unnecessary except for speaking the short result through the pendant.
- **latency:** Initial answer within 3 seconds of the request; poll both serial streams for at most 1 second and return per-chip age/counter evidence. Do not wait indefinitely for LTE registration.
- **cost:** Near-zero model cost when frames parse; a small background call only for an unfamiliar diagnostic code. Engineering cost is a bounded serial reader and framing parser, not repeated LLM vision.
- **security:** Read-only serial access, no firmware flashing or arbitrary writes. USB identifiers and raw logs should stay local; return hashes/counters and short error codes to relay. Explicitly label this as bench USB status, never as wearable LTE status.
- **missing:** A real bounded serial-reader implementation (the granted schema is not live); A common framed health message emitted by nRF9160 and ESP32 with firmware version, monotonic counter, uptime, CRC and reset reason; Mac machine-context fields for per-chip last-seen and parser confidence; A relay/pendant spoken status route that carries age and uncertainty

### ""What exactly changed when you did that?" Return a concise, causally ordered explanation of the Mac shell, browser, and wearable effects, what is reversible, what is unknown, and offer the correct undo or recovery action."
- **useful because:** The current system records fragments in jobs, receipts, ledgers, activity logs, and browser provenance, but the owner cannot ask one question and get a trustworthy causal account. This is more valuable than raw observability: it lets the owner catch a wrong command, understand a failed browser fill, or know whether a pendant request reached the Mac.
- **path:** relay → mac-planner → browser-harness → dashboard → pendant
- **model tier:** Use deterministic joins and redaction first; use a cheap summarizer for wording. Realtime only speaks the final 2–4 sentence answer. Never send raw shell environments or page bodies to the model.
- **latency:** Under 2 seconds for a completed job using stored receipts; under 5 seconds if browser provenance and Mac journal must be joined. For a running job, say still running and return the latest settled step.
- **cost:** One low-cost summarization call at most; most work is local JSON joins over existing records. Token savings come from passing receipt IDs and state deltas rather than full stdout or browser snapshots.
- **security:** Redact tokens, environment variables, cookie-bearing URLs, and page text; preserve command identity, cwd, exit code, timestamps, touched paths, source URL, and reversibility. Treat exit-unknown as unknown, never failure or success. Undo should link to the existing undo route and state when no undo exists.
- **missing:** Exit code, pid, argv and bounded stdout/stderr summaries in shell receipts; A durable job-to-ledger join and guaranteed ledger close; A normalized effect schema shared by shell, browser provenance, pendant delivery, and Mac actions; A read-only explanation endpoint that can correlate /jobs, /journal, /receipts, and /browser/provenance without exposing secrets

### ""Stop what you are doing now." Make the pendant's second button an immediate, truthful panic stop for the currently active Mac/browser job: terminate the actual process group, cancel queued browser commands, leave a durable partial-state receipt, and tell me what may already have happened."
- **useful because:** The existing cancel endpoint only sets a cooperative signal; a 120-second shell keeps running because execAsync receives no abort signal, and browser/computer-use work is not reliably cancellable. A worn physical stop is the one control the owner needs when an action is visibly going wrong, and it must work without finding a phone or opening the dashboard.
- **path:** pendant → relay → mac-planner → browser-harness → dashboard
- **model tier:** No expensive model is needed to stop. Relay performs a deterministic job lookup and sends an authenticated cancel/kill command; a cheap summarizer converts the resulting receipt into a short spoken report. Realtime only speaks the acknowledgement if the owner is already in conversation.
- **latency:** Local pendant acknowledgement under 150 ms; relay dispatch under 500 ms; Mac process-group termination target under 1 second. Report separately when browser cancellation is only queued and cannot retract a click already sent.
- **cost:** Near-zero inference cost. Engineering work is process-group supervision, a relay command, and durable receipt handling; no continuous model loop.
- **security:** The stop command must be authenticated, bound to the owner's current active job, idempotent, and never claim rollback. It should record whether termination was confirmed, whether a step was in-flight, and which external effects are irreversible. Offline, the pendant should cache a stop intent with an expiry and refuse to apply it to a later unrelated job.
- **missing:** A dedicated pendant stop-intent item using the existing crash-safe outbox, with active-job binding and short expiry; run_shell execution via spawn/execFile with a process-group ID and abort signal, rather than uninterruptible execAsync; A relay route that maps the pendant request to the active job and acknowledges kill confirmation; Browser command cancellation that can retract queued commands and mark already-delivered commands as unknown; A durable partial-state receipt containing termination time, signal, step key, and post-stop inspection request

### ""Make sure that actually took effect." After an action completes, verify its promised postcondition across the Mac and authenticated browser, then notify the pendant if it is missing, reverted, or only uncertain."
- **useful because:** A completed receipt currently means a command returned, not that the owner's goal happened. A shell can exit 0 while a file is unchanged, a browser click can be delivered while a save fails, and a remote page can revert later. This gives the owner outcome truth instead of transport truth.
- **path:** pendant → relay → mac-planner → browser-harness → dashboard
- **model tier:** Use deterministic checks for files, app state, browser URL/DOM assertions, and job receipts; use a cheap model only to translate a natural-language goal into a bounded postcondition before execution. Realtime is only for the brief spoken failure notice.
- **latency:** Run immediate checks within 2 seconds after completion; schedule delayed checks at 30 seconds and 5 minutes when the task is eventually consistent. Pendant notification should say verified, failed, or unknown with age.
- **cost:** Usually zero model calls after planning; one small planner call to compile the postcondition. Dominant cost is browser round trips and any delayed Mac wake, not inference.
- **security:** Postconditions must be explicit and scoped to the action, never broad surveillance. Do not capture page bodies or secrets; store only assertion outcome, locator, timestamp, and evidence hash. If verification would mutate state (retrying a save), ask rather than silently repair.
- **missing:** A typed postcondition schema shared by Mac actions and browser commands (path/content hash, app state, URL/field/value, expected time window); Mac and browser observation endpoints that return bounded evidence hashes, not raw secrets; A durable verification watcher tied to a job ID and pendant notification state; A distinction in receipts between command success, effect verified, and effect unknown

### ""Carry my work to the other computer." Package the exact project, browser-session, application-layout, and pending-action context from this Mac into a device-bound continuity capsule, then restore it on another authorized Mac without exposing credentials or making me explain everything again."
- **useful because:** Today the hive's useful context is tied to one local agent, its filesystem, and browser sessions that another node cannot reach. A lost, replaced, or temporarily unavailable Mac strands the owner's active work. A signed capsule would make the pendant the portable identity and continuity anchor rather than merely a remote microphone.
- **path:** pendant → relay → mac-planner → browser-harness → dashboard
- **model tier:** Use deterministic state collection and redaction; use a cheap background model only to summarize unresolved conflicts between the source and destination Mac. Realtime is unnecessary except to confirm the handoff aloud.
- **latency:** Create a capsule in under 10 seconds for normal project/browser state; restore in under 30 seconds plus application launch time. Report every item that could not be transferred rather than silently approximating it.
- **cost:** Low model cost; the dominant cost is local file hashing, application startup, and browser-session reauthentication. Do not upload project contents by default—transfer only metadata and explicitly selected files.
- **security:** Capsules must be encrypted to the destination device, signed by the pendant, expire, and omit cookies, tokens, passwords, and page bodies. Browser sessions should transfer as session references requiring the destination extension to re-establish access, never as copied credentials.
- **missing:** A device-bound capsule format with encrypted metadata, file manifests, project/session handles, and conflict markers; Relay storage and transfer for encrypted capsules, with expiration and revocation; A destination-Mac importer that can recreate projects, app layout, and browser session references; Pendant authentication and secure-element signing so a stolen relay token cannot authorize a handoff

### ""Make the whole system quiet until it matters." Let me set an attention policy from the pendant—focus, meeting, sleep, or emergency—then have the relay, Mac, browser, and wearable jointly suppress, defer, and summarize interruptions while allowing only explicitly urgent events through."
- **useful because:** The owner currently has separate jobs, browser watches, routines, and pendant alerts with no shared notion of attention. The result is either missed important events or a wearable that interrupts at the wrong moment. A single policy should follow the owner across devices and explain what was deferred.
- **path:** pendant → relay → mac-planner → browser-harness → dashboard
- **model tier:** Use deterministic policy evaluation for routing and suppression. A cheap background model can cluster deferred notifications into a digest; realtime should only deliver an urgent alert or accept a short mode change.
- **latency:** Mode changes should take effect locally within 250 ms and at the relay within 1 second. Urgent events should break through within 2 seconds; deferred summaries can wait for the next deliberate interaction.
- **cost:** Negligible inference for routing; one inexpensive summarization call per digest. Storage and event filtering dominate, not model tokens.
- **security:** The policy must not hide safety-critical or owner-whitelisted events. Keep a durable audit of what was suppressed, why, and when it will reappear. Browser page content should be classified locally where possible, with only event metadata leaving the Mac.
- **missing:** A shared attention-policy state replicated between pendant, relay, Mac, and browser extension; A priority/urgency contract for jobs, page watches, routines, and audio alerts; Mac notification and browser-watch interception hooks that can defer without losing events; A compact pendant control that changes modes without using a button gesture that delays conversation start


## Changes it proposed to its own stack

### `hardware` — Add a latching, normally-closed physical privacy switch and a small secure element to the pendant. The switch should cut microphone bias and audio transmit power in hardware, while the secure element signs a monotonic privacy-state transition and device identity for the relay. Expose the state to the Mac only as signed attestation; never rely on an LED or software flag to claim the microphone is off.
- **owner gets:** The owner gets a privacy control that remains trustworthy during firmware crashes, relay outages, or a compromised Mac. They can physically know that no audio is being captured or transmitted, and the hive can refuse to tell them an untrusted device is private.
- effort: Board spin, enclosure change, low-power switch path, secure-element provisioning, firmware state reporting, relay verification, and Mac/browser behavior that stops capture when the attestation is absent. This is a substantial hardware and firmware project, not a software refactor.  ·  risk: A failed switch or brownout could leave audio unavailable; recover by making the switch fail-closed, exposing a local diagnostic blink, and allowing replacement hardware to be reprovisioned. Do not infer privacy from a lost link.
- cost: Roughly $2–8 in components plus PCB/enclosure work; secure-element and switch power draw should be under 1 mA in steady state, with essentially no additional draw while open.  ·  latency: Hardware mute is effectively immediate; relay attestation updates within one heartbeat. The Mac may take up to one heartbeat to stop a queued capture unless it also subscribes to the local USB state.
- security: Strongly improves microphone privacy and device identity. Provisioning and recovery keys become critical; never export the private key, and bind relay commands to the attested device state.
- depends on: A signed pendant-state protocol shared by firmware, relay, and Mac; Mac and browser capture paths that react to a verified privacy-off state; A provisioning and replacement procedure for the secure element


## What it asked for

_Nothing._
