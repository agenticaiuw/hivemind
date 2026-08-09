# Harness derivation — faculty-perception — round 175

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live continuity infrastructure** — At 2026-08-08T04:38Z, Mac local agent v0.5.0 is healthy with Accessibility and Screen Recording granted and no required permissions missing; browser extension is online with one Safari tab and zero pending commands; relay is reachable, D1-backed, and Mac bridge online.
  - evidence: GET /ops/snapshot returned status.ok=true, permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser online=true pendingCommands=0, relay.reachable=true store=d1 macBridgeOnline=true.

## Capabilities it proposed

### "Tell me exactly what I missed while I was away, and separate 'the system did it' from 'I could have heard it'."
- **useful because:** The current catch-up digest can enumerate bounded records, but completion is routinely inferred from Mac execution and the pendant-held sources are empty. This would give the owner a short causal timeline with explicit evidence grades, retention gaps, and unknown playback instead of a falsely reassuring completed label.
- **path:** relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner
- **model tier:** background for reconstruction; realtime only to answer the spoken question
- **latency:** Under 3 seconds for a recent bounded window; under 10 seconds for a full-day reconstruction.
- **cost:** Usually one cheap structured synthesis call; dominated by no model cost if the evidence is normalized first.
- **security:** Must not expose secret browser claims or infer absence from count-capped stores. Every item needs source, observed-at, and confidence; say 'unknown' when no device playback event exists. Confirmation is required before any proposed retry or action.
- **missing:** A resolved, authenticated continuity snapshot surface (the granted tool currently fails resolution); An evidence-grade timeline schema that distinguishes relay acceptance, Mac completion, socket bytes, and device playback; A gap/retention annotation from each source

### "Before I trust the wearable, run a bench session that proves my spoken request reached the pendant firmware, came back as audio, and records the exact first failing layer if it did not."
- **useful because:** There is no registered pendant today, yet the firmware and audio bridge are the only physical path the owner will eventually rely on. A deterministic Mac-attached bench mode would turn 'the relay says completed' into a reproducible transport/audio test and catch regressions before the device is worn.
- **path:** mac-terminal → mac-planner → relay-realtime → faculty-perception → faculty-action
- **model tier:** background model to orchestrate the test and summarize measurements; no realtime model needed except an optional spoken trigger
- **latency:** A smoke test in 30 seconds; full codec and loss characterization in 2 minutes.
- **cost:** Negligible API cost; dominated by local serial capture and firmware test runtime.
- **security:** Serial logs may contain speech or tokens; redact payloads and retain only hashes, counters, firmware build ID, and failure excerpts. Never send raw UART to the relay without confirmation.
- **missing:** A Mac serial harness for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A loopback/test command in both firmware images with deterministic sequence numbers; A signed bench receipt joining relay job ID, firmware build, serial session, and audio metrics; A safe way to run it while the owner is not in a live conversation

### "When you answer from a web page, let me ask 'where did that come from?' and hear the exact page, capture time, and whether the page was read through my logged-in browser or the public relay."
- **useful because:** Relay browser reads currently return untrusted text with no ID, hash, or persistence, while the Mac already has a strong evidence-capsule schema and grounded-claim model. Bridging them would make spoken answers auditable without leaking page bodies or pretending public and authenticated reads are equivalent.
- **path:** browser-extension → relay-realtime → mac-planner → faculty-perception → unified
- **model tier:** Cheap background extraction and hashing; realtime only formats the owner's follow-up answer.
- **latency:** Add less than 300 ms to a browser-backed answer when the capsule transport is warm; provenance lookup under 1 second.
- **cost:** One small hashing/redaction operation and a bounded local write; negligible model cost. Browser rendering remains the dominant external cost.
- **security:** Never copy authenticated page bodies to the relay. The Mac should redact and mint the existing content-addressed capsule locally; relay returns only correlation ID, URL origin, title, capture time, and content hash. Secret locators remain withheld. Opening or acting on a cited page still requires the normal browser permission/confirmation rules.
- **missing:** Relay read_web_page must return a stable read ID and content hash; A Mac callback that mints the existing evidence capsule and browserProvenance extraction record; Mount browserProvenance routes so the owner can retrieve/revoke the claim; A spoken citation formatter that distinguishes public relay text from authenticated extension evidence

### "Before a routine fires, tell me if its time is being interpreted in the Mac's timezone or mine, and warn me when those differ instead of silently running it four hours off."
- **useful because:** The system has an authoritative Mac timezone of America/New_York while the owner's remembered timezone is America/Chicago, and pendant time is explicitly zoneless. A perception fence would prevent a daily brief, quiet hour, or reminder from being confidently reported at the wrong local time.
- **path:** faculty-perception → mac-planner → relay-realtime → faculty-judgement → faculty-action
- **model tier:** No model for normal checks; background model only to explain a detected conflict in one short sentence.
- **latency:** At routine creation and before firing, under 100 ms; warning delivery can be asynchronous.
- **cost:** Negligible; timezone resolution and a small state record dominate, not inference.
- **security:** Do not claim the owner's physical location from the Mac zone. Keep the two identities explicit: machine-resolved and owner-declared. Require confirmation before changing existing schedules or firing a location-sensitive action.
- **missing:** A persisted owner timezone preference distinct from machine timezone; A routine preflight that records the resolved zone and UTC instant in the run receipt; A visible conflict state consumed by spoken briefings; A pendant rule that refuses to interpret zoneless device timestamps as instants

### "When two parts of you disagree, tell me what conflicts, which observation is newer or more authoritative, and let me choose which fact becomes the one you act on."
- **useful because:** Today browser state, Mac state, relay state, routine receipts, and memory can each be individually plausible while disagreeing about the same object. The owner has no conflict view and may hear a confident answer assembled from incompatible snapshots. A cross-surface claim dispute system would expose the disagreement before judgement or action silently chooses one.
- **path:** faculty-perception → unified → browser-extension → mac-planner → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Cheap structured comparison first; use the realtime tier only to explain a material conflict conversationally.
- **latency:** Under 1 second for known records; under 5 seconds when a fresh browser or Mac observation is needed.
- **cost:** Low: hashes, timestamps, and deterministic precedence dominate. Model cost only occurs when translating a conflict into speech.
- **security:** Do not reveal secret values merely because they conflict. Compare classifications, hashes, owners, timestamps, and redacted summaries. Choosing a winning claim must be recorded and require confirmation if it would drive an external action.
- **missing:** A cross-surface claim envelope with source, observation time, freshness, authority, sensitivity, and supersession links; A conflict index spanning browser provenance, Mac ledgers, relay jobs, routines, and memory; A judgement gate that refuses to act on unresolved conflicts; An owner-visible resolution record with expiry

### "Show me exactly what I allowed, to which surface, for how long, and what data may leave my devices—and automatically stop using an old permission when its scope or time expires."
- **useful because:** Permissions are currently scattered across Mac TCC grants, browser sessions, relay credentials, and per-action confirmations. The owner cannot answer the practical question 'what did I authorize this system to do?' or revoke one capability without guessing which credential or surface it affects.
- **path:** faculty-perception → unified → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** Deterministic ledger and policy evaluation; cheap background model only summarizes a requested audit.
- **latency:** Permission check under 100 ms; spoken audit under 2 seconds.
- **cost:** Negligible local storage and hashing; no model call for enforcement.
- **security:** The ledger itself is sensitive. Store capability names and scope, not secrets; hash credential identifiers; never claim OS-level revocation if only application-level blocking occurred. Destructive or external actions remain confirmation-gated.
- **missing:** A single append-only consent ledger with grant, scope, surface, purpose, expiry, revocation, and enforcement result; Adapters for macOS TCC, browser-extension grants, relay device credentials, and action confirmations; A preflight hook that denies stale or over-broad grants before execution; A revocation propagation path to browser, Mac, relay, and eventually pendant

### "Before you do anything consequential, let me hear a reversible simulation of the whole cross-device chain: what each surface would read, what it would send, what would change, and where it could fail."
- **useful because:** Existing previews are feature-specific, while a request can cross relay, Mac, browser, and a future pendant. The owner cannot inspect the complete blast radius or data path before approving an action. A universal dry-run would make the system understandable without pretending that a plan was executed.
- **path:** relay-realtime → unified → faculty-perception → faculty-judgement → faculty-action → mac-planner → browser-extension
- **model tier:** Background model builds the plan and explanation; deterministic adapters perform dry-run reads and capability checks; realtime only narrates a short approval summary.
- **latency:** Simple actions under 2 seconds; multi-surface simulations under 8 seconds.
- **cost:** One planning call plus local dry-run work; browser rendering or external API reads dominate variable cost.
- **security:** Dry-run adapters must be side-effect-free by construction, with an allowlist preventing sends, deletes, purchases, navigation submissions, or device writes. Clearly label simulated values and stale observations. Approval must bind to a hash of the exact plan, inputs, destinations, and data egress.
- **missing:** A common dry-run contract for Mac, browser, relay, and pendant operations; Side-effect classifications and simulation handlers for every action type; A plan hash and approval token consumed exactly once by faculty-action; A structured data-egress report including sensitive-field transformations


## What it asked for

_Nothing._
