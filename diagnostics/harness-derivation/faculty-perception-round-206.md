# Harness derivation — faculty-perception — round 206

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-permissions** — Live Mac agent reports Accessibility and Screen Recording trusted, automation grants present, requiredMissing empty, permissions.ready true; browser extension online with 2 tabs and zero pending commands.
  - evidence: GET /ops/status HTTP 200 at 2026-08-08T23:49Z; fields permissions.accessibility.trusted=true, screenRecording.granted=true, ready=true, browser.online=true.
- **relay-liveness** — Relay is configured and reachable; D1-backed cloud relay reports Mac bridge online and pendant pipeline telemetry, speech, persistent state, durable audio capabilities. No pendant presence established by this response.
  - evidence: GET /ops/status HTTP 200: relay.reachable=true, payload.store=d1, macBridgeOnline=true, capabilities listed.
- **browser-liveness** — Safari browser bridge is currently online, exposing a YouTube tab titled 'Max Hodak: Average Is Not Good Enough - YouTube', tabCount 2, pendingCommands 0, staleForMs under 1 second at observation.
  - evidence: GET /ops/status HTTP 200 browser.devices[0] with online=true, tabCount=2, pendingCommands=0, lastSeenAt 2026-08-08T23:49:01.455Z.

## Capabilities it proposed

### "“Mark this moment so I can come back to it later.”"
- **useful because:** The owner can capture an actionable thought without stopping to organize it: the pendant records the utterance, the Mac records the exact visible app/browser state, and the relay preserves a resumable checkpoint. Later “take me back to that moment” opens the same page/app and reads the owner's note, instead of relying on an ungrounded memory.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Realtime only for the short spoken intent and confirmation; a cheaper background model extracts a title and next action from the note and context.
- **latency:** Acknowledge within 1 s; capture Mac/browser state within 3 s; resume within 5 s when the browser bridge and Mac are online.
- **cost:** About $0.01–$0.04 per checkpoint, dominated by one short realtime turn; background extraction can use a low-cost text model.
- **security:** The checkpoint may contain screen text, logged-in URL, and a voice transcript. Store a redacted evidence capsule and URL host by default, require explicit confirmation before capturing sensitive page bodies, and never send browser cookies or credentials to the relay.
- **missing:** A single checkpoint record joining pendant capture ID, Mac session, browser command/result, evidence capsule ID, and relay job ID; A user-facing resume route that reopens the recorded app/tab and reports which parts are unavailable; A pendant-connected capture event; today the relay has no registered pendant

### "“Watch this page and tell me only if something important changes.”"
- **useful because:** The owner gets a hands-free alert for a price, appointment, ticket, shipment, or research page without repeatedly checking it. The browser extension observes the authenticated page, the Mac creates a redacted content hash and decides whether the change is meaningful, the relay schedules checks while the Mac sleeps, and the pendant speaks only a confirmed delta.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → unified
- **model tier:** Cheap background model for periodic diff classification; realtime is used only to phrase the final spoken alert.
- **latency:** Check on the requested interval; after a detected change, deliver a concise alert within 10 s when the pendant link is available, otherwise queue it.
- **cost:** Roughly $0.002–$0.01 per check using hashing and a small classifier; realtime speech is the dominant cost only when an alert fires.
- **security:** Authenticated page contents must stay on the Mac; send only a redacted diff, source host, and content hash to the relay. Require confirmation for sensitive domains, provide an immediate stop command, and expire watchers by default.
- **missing:** A durable watcher scheduler joining browser session affinity, evidence capsule revisions, and relay announcements; A meaningful-change policy that distinguishes page chrome/ads from the watched region; A browser-originated authenticated change event; current relay read_web_page has no ID, hash, or persistence; A pendant playback acknowledgement before marking an alert heard

### "“What actually happened, and what should I do next?”"
- **useful because:** After any spoken request, the system would give one honest account across the whole chain instead of saying “done” when only the Mac ran. It correlates the pendant's capture-quality verdict, relay job and socket state, Mac action receipts, browser command/result, screenshots, and (when available) playback confirmation, then tells the owner exactly where the chain stopped and offers the next reversible recovery.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** A cheap deterministic correlator produces the evidence graph and confidence labels; use realtime only to explain the short result conversationally, escalating to a stronger model for ambiguous screenshots or competing receipts.
- **latency:** For completed work, answer within 2 s from existing receipts; if a fresh screenshot or browser poll is needed, under 8 s. Never block the owner on a missing pendant acknowledgement.
- **cost:** Usually under $0.01 because it is structured joins; screenshot interpretation is the variable cost, roughly $0.02–$0.10 only when needed.
- **security:** Screenshots and browser results can contain private content. Keep raw evidence on the Mac, expose redacted snippets and hashes to the relay, require confirmation before proposing a retry with side effects, and clearly distinguish observed, inferred, and unknown states.
- **missing:** A stable cross-surface correlation key propagated from voice turn through relay job, Mac job, browser command, and pipeline run; A perception reducer that treats Mac completion as distinct from pendant playback and labels unknown rather than guessing; A screenshot/evidence attachment on job receipts, with redaction and bounded retention; A pendant-originated playback event; the existing device_playback reader has zero emitters

### "“If I lose my phone or laptop, make sure I can still recover the important things.”"
- **useful because:** The owner would have a cross-surface emergency recovery mode: the pendant can locally seal a tiny manifest of critical contacts, active tasks, and recovery instructions; the Mac can periodically encrypt and attest the corresponding evidence; the relay can hold the encrypted escrow while offline. A replacement device could authenticate and reconstruct only the owner's explicitly marked essentials, rather than losing the continuity graph with one machine.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → unified
- **model tier:** Cheap background summarization and deterministic encryption/manifest generation; realtime is used only for spoken enrollment, confirmation, or recovery guidance.
- **latency:** Enrollment under 30 s; periodic Mac-side refresh under 2 s; emergency recovery begins within 10 s of authentication.
- **cost:** Low ongoing model cost, typically under $0.01 per refresh; storage and key-management dominate rather than inference.
- **security:** This is exceptionally sensitive. Use owner-held recovery keys, threshold approval or a second factor, client-side encryption so the relay cannot read contents, per-item expiry/revocation, and never include browser cookies, passwords, raw audio, or unrestricted screen captures.
- **missing:** An owner-controlled encrypted escrow format and key rotation protocol; A recovery ceremony spanning a replacement browser/Mac and a locally authenticated pendant; A device-independent export of selected evidence, tasks, and context-graph entities rather than raw workspace files; A durable relay route for encrypted recovery bundles with auditable access receipts

### "“Never let any of you send, buy, publish, or delete anything unless I physically confirm it.”"
- **useful because:** The owner would get a real cross-device safety boundary rather than trusting a model prompt. The relay classifies the requested side effect, the Mac/browser prepares but does not commit it, and the pendant's physical button plus a spoken transaction summary authorizes exactly one bounded action. A stale page, changed amount, or changed recipient invalidates the approval.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Deterministic policy engine for action classification, target/amount hashing, and expiry; use a small model only to summarize the pending transaction; realtime handles the short confirmation exchange.
- **latency:** Preparation can take seconds; after a physical confirmation, commit within 3 s and return a receipt. No irreversible action may proceed without the bounded approval.
- **cost:** Usually below $0.01 per transaction; browser/Mac inspection and cryptographic receipt handling dominate, not model tokens.
- **security:** The authorization must be device-bound, single-use, short-lived, and include a hash of the exact final action. Protect against clickjacking, confused-deputy browser sessions, replay, and an attacker who can speak near the pendant. Require a physical button gesture for high-risk classes and expose a local cancel gesture.
- **missing:** A policy-enforcement gate below every irreversible Mac and browser action, not merely a planner instruction; A pendant-signed nonce/approval protocol with monotonic expiry and replay protection; A final-state re-read immediately before commit, with target and content hash comparison; Receipts that prove which physical approval authorized which exact side effect

### "“That was wrong—freeze everything needed to understand it and prevent a repeat.”"
- **useful because:** The owner would be able to turn a frustrating failure into a reproducible incident without manually gathering logs. The pendant preserves the utterance and capture-quality frame, the relay freezes its job/session trace, the Mac captures pre/post UI state and receipts, and the browser records the exact tab/result. A later run can compare against the incident and warn before repeating the same failure.
- **path:** pendant → relay-realtime → mac-planner → mac-vision → browser-extension → unified
- **model tier:** Deterministic snapshot assembly and hashing first; a cheaper background model writes the incident summary and extracts a regression condition; realtime only acknowledges and explains the immediate finding.
- **latency:** Freeze the evidence within 2 s of the owner's phrase; produce a short explanation within 10 s; background analysis may take minutes.
- **cost:** Usually $0.01–$0.05 per incident, dominated by optional screenshot/audio analysis; hashes and structured receipts are nearly free.
- **security:** Incident bundles can contain private screens, URLs, transcripts, and action parameters. Redact locally before relay upload, classify sensitivity, allow the owner to inspect/delete, and keep raw audio/screenshots on the Mac unless explicitly exported.
- **missing:** A cross-surface incident transaction that atomically snapshots relay, Mac, browser, and pendant evidence; A bounded pre-trigger ring buffer for Mac/browser observations and pendant quality metrics; A redaction-and-diff pipeline that can compare incidents without exposing secrets; A regression guard that can consume an incident's condition before permitting a future action


## Changes it proposed to its own stack

### `integration` — Add a postcondition evidence bundle to every Mac/browser action: after execution, use the now-live Accessibility/Screen Recording permissions to capture a bounded redacted UI observation, attach its content hash and capsuleId to the existing job receipt, and classify the outcome as observed-success, observed-failure, or unknown. Propagate the same correlation ID to relay jobs and browser commands.
- **owner gets:** The owner will stop hearing “done” when a button did nothing or a page stayed unchanged; the system can show what was visibly true after it acted and recover from the actual failure.
- effort: Medium: instrument the existing action/receipt finalization and browser result paths, call the already-mounted evidence capsule machinery, and add a reducer over existing job/pipeline records.  ·  risk: Screenshots may capture secrets or transient UI; redact before persistence, cap size, and fall back to unknown if capture fails. Never retry side effects automatically based only on a screenshot.
- cost: Small storage increase within existing evidence caps; one screenshot-vision classification only when DOM/result data is insufficient.  ·  latency: Adds about 0.5–3 s to actions requiring a screenshot; structured browser results can avoid the screenshot.
- security: Improves auditability but increases local sensitive-data exposure; keep raw pixels local, store hashes/redacted regions, and require explicit domain exclusions.
- depends on: Accessibility and Screen Recording are now live (verified via GET /ops/status).; Mount and invoke the existing evidenceCapsules/browserProvenance modules on the action completion path.; Define a shared correlation ID across relay, Mac, browser, and pipeline records.


## What it asked for

_Nothing._
## Its own summary

Recorded three non-trivial owner capabilities: encrypted cross-device recovery escrow, physical-confirmation side-effect firewall, and cross-surface incident freeze/replay. Each requires new connective protocols despite existing Mac/browser/relay primitives.

**Biggest unknown:** Whether the backlog already contains an equivalent proposal for any of these; the recorder accepted all three but flagged that their named routes are existing connective pieces.

