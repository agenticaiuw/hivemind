# Harness derivation — mac-planner — round 148

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac stack state round 148** — Mac agent and relay are reachable; Safari bridge is online with 3 tabs and zero pending commands, but current tab is https://example.com titled 'Failed to open page'. Accessibility and Screen Recording are both ungranted. Pipeline has completed 24 kHz mono PCM rendering/upload and also shows an offline nRF9160 held-alert event, so cross-surface health needs to distinguish browser-page failure from bridge connectivity.
  - evidence: GET /ops/status HTTP 200; GET /browser/status HTTP 200; GET /pipeline HTTP 200

## Capabilities it proposed

### "“Save this for me” (press the pendant button): capture the text or item I’m looking at on my Mac, its browser URL or app, the active project, and a one-sentence spoken label; later let me ask “what did I save about this?” and reopen the exact source."
- **useful because:** It turns fleeting discoveries into reliably attributable notes without interrupting work. The pendant supplies a zero-friction trigger, the Mac/browser supply the actual selection and provenance, and the relay makes the capture searchable and confirms it aloud.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** Realtime model only for the short spoken label/confirmation; a cheaper background model normalizes, tags, and deduplicates captures.
- **latency:** Confirmation under 2 seconds; source extraction under 5 seconds; search/reopen under 3 seconds.
- **cost:** About $0.002–$0.01 per capture, dominated by transcription/labeling; URL, selected text, and metadata should avoid a model call when already structured.
- **security:** Selected text and private URLs leave the Mac only to the authenticated relay; redact secrets and never capture passwords or hidden page fields. Reopening is read-only; sharing or sending requires confirmation.
- **missing:** A Mac read API for current selection and foreground document metadata that does not depend on Accessibility; A browser command to return selected text plus stable tab URL/title and DOM locator; A capture schema joining pendant event, source provenance, project, and searchable embedding; A pendant button/event bridge while attached over USB serial and eventually LTE

### "“Put a resume point here.” When I stop or the Mac restarts, preserve my active project, open browser tabs, foreground app/document, pending Mac job receipts, and the next concrete step; when I say “resume,” restore only the relevant tabs/files and read me the checkpoint."
- **useful because:** The owner loses less work between interruptions and can resume across the physical pendant, authenticated browser, and Mac rather than reconstructing context from memory. It is more useful than a generic task list because it records what was actually open and what was already done.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** Cheap background model extracts a short next-step/checkpoint from receipts and project state; realtime is used only to answer the resume command and read the summary.
- **latency:** Checkpoint write within 3 seconds; resume briefing within 5 seconds; restoration can proceed asynchronously with progress receipts.
- **cost:** Roughly $0.001–$0.005 per checkpoint, mostly storage and optional summarization; no model call for raw tab/job state.
- **security:** Checkpoint contents can contain private URLs, filenames, and snippets. Encrypt at rest, bind browser sessions to the owner, expire stale checkpoints, and require an explicit spoken confirmation before destructive restoration (closing/replacing tabs or files).
- **missing:** A versioned resume-capsule store with provenance and expiry; Read-only Mac state for foreground document, project, and open windows without Screen Recording; Browser tab/session serialization and safe restore with tab affinity; An action-plan executor that reports per-step success and leaves existing work untouched by default

### "“Run a desk check.” From the pendant, verify that the Mac, browser bridge, pendant serial link, and audio bridge are healthy, then give me one concise diagnosis and the exact next action; if everything is healthy, save a timestamped proof-of-health receipt."
- **useful because:** Today the owner repeatedly asks to launch the bridge and check status, but a single node cannot prove the whole chain. This turns a vague “it’s broken” moment into a useful cross-device diagnostic, especially while the pendant is physically attached over USB but not LTE-registered.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** Deterministic health checks and a small background classifier should do the work; realtime only speaks the final one-sentence diagnosis.
- **latency:** Initial verdict under 5 seconds; serial/audio probes may take up to 15 seconds with a live progress update.
- **cost:** Under $0.001 per check when deterministic; occasional $0.002 diagnostic summary for ambiguous logs.
- **security:** Health data should include versions, link states, and error codes, not message contents or browser page data. Serial probes must be bounded and read-only; never replay queued browser commands during a check.
- **missing:** A privileged-but-read-only serial probe for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A loopback audio fixture and codec/radio health endpoint; A browser heartbeat freshness check that explicitly separates online status from pending-command execution; A signed, correlated health receipt spanning all four surfaces

### "“Prove it’s done.” After I ask the system to change something, independently verify the real-world result across the relevant surfaces—for example, confirm the calendar event exists, the browser confirmation is present, the file checksum changed, or the service returned the expected state—and tell me what was actually observed, not merely that a click ran."
- **useful because:** Today an action receipt can say an operation completed while the intended outcome failed, landed in the wrong account, or was overwritten. The owner gets a trustworthy result, with evidence, across the browser, Mac, relay, and pendant.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** Deterministic postconditions and hashes first; a cheap background model maps natural-language intent to observable assertions. Realtime only speaks the concise proof or failure.
- **latency:** Simple verification under 3 seconds; multi-surface verification under 15 seconds with progress events.
- **cost:** $0.001–$0.01 per invocation; most checks are local/API reads, with model cost only for ambiguous intent-to-postcondition mapping.
- **security:** Verification must not expose full private page or mail contents; retain only evidence snippets/hashes and account identity. Never retry a mutation automatically when proof fails; report uncertainty and ask before any repair.
- **missing:** A declarative postcondition format tied to each action type; Read-only browser/Mac/calendar/mail adapters that can observe resulting state; Evidence snapshots with timestamps, account scope, and before/after hashes; A relay-to-pendant result protocol that distinguishes verified, disproven, and unknown

### "“Warn me when my plans contradict each other.” Continuously reconcile my calendar, mail commitments, authenticated browser reservations, and local project deadlines; alert only on actionable conflicts such as impossible travel, double-booking, expired dependencies, or a deadline that no longer matches the latest confirmation."
- **useful because:** No single surface knows the owner’s actual commitments. The wearable can interrupt at the right moment while the Mac and authenticated browser provide private evidence, turning silent inconsistencies into early, specific warnings instead of another generic daily brief.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** Background model extracts normalized dates, locations, dependencies, and confidence from source deltas; realtime is reserved for urgent spoken alerts. Deterministic interval and dependency checks handle most cases.
- **latency:** Routine reconciliation within 10 minutes of a source change; urgent contradiction alert within 60 seconds.
- **cost:** $0.01–$0.05 per changed source batch; extraction dominates, and unchanged sources should cost nothing through hashes/fingerprints.
- **security:** Cross-source joining is sensitive: store normalized commitments with provenance and TTL, not whole messages/pages. Quiet hours, severity thresholds, and per-source opt-out are required; alerts must avoid speaking private details aloud in public.
- **missing:** A normalized commitment/dependency graph with source provenance and confidence; Change subscriptions or efficient deltas for Calendar/Mail/browser watches; Travel-time and timezone reasoning, including uncertainty; A severity/quiet-hours policy and pendant alert acknowledgement path

### "“Keep a private decision ledger.” When I state a decision, preference, or promise on the pendant, link it to the relevant email, browser page, calendar event, project, and later outcome; when circumstances change, tell me which decisions are affected and show the original evidence before suggesting an update."
- **useful because:** The owner can make a decision in one place and lose it in another. This creates durable continuity across the worn device, authenticated browser, Mac workspace, and always-awake relay without pretending that an inferred preference is a fact.
- **path:** pendant → mac-bridge → browser → relay-realtime → dashboard
- **model tier:** Realtime captures the short spoken statement; a cheaper background model extracts entities and links evidence, with human review for low-confidence links.
- **latency:** Capture acknowledgement under 2 seconds; linking within 30 seconds; impact analysis asynchronously with a notification when ready.
- **cost:** $0.005–$0.03 per decision, dominated by linking and later impact analysis; raw audio can be discarded after transcription under the owner’s retention policy.
- **security:** Decisions may include sensitive personal or work data. Encrypt records, attach sensitivity and expiry, keep verbatim evidence opt-in, and never silently rewrite a decision—only propose a revision with old/new provenance.
- **missing:** A durable typed decision entity and relation model distinct from generic notes; Cross-surface evidence linking with confidence and contradiction tracking; A pendant capture event that works offline and reconciles after reconnect; A review UI/audio protocol for accepting, correcting, or expiring decisions


## Changes it proposed to its own stack

### `integration` — Ship a local USB hardware companion service that continuously correlates nRF9160 UART events, ESP32 audio-bridge events, Mac agent jobs, browser heartbeats, and pipeline audio into one bounded event timeline. Expose read-only status plus downloadable failure bundles; emit a pendant-visible diagnostic event but never execute queued browser or Mac commands as part of probing.
- **owner gets:** When the owner says “it’s not working,” they get a precise answer—radio registration, serial link, audio path, browser bridge, or Mac job—with the relevant evidence, instead of repeatedly relaunching apps and guessing. It works today while both chips are physically connected even though LTE registration is absent.
- effort: Medium: launchd service, two serial readers, event schema/correlation IDs, bounded ring buffer, and adapters for existing /pipeline, /browser, and /jobs receipts.  ·  risk: Serial framing bugs or a stuck reader could consume the port; recover by reopening with backoff and never writing to either device. Event logs may grow or expose private URLs; use a small encrypted ring buffer with redaction and explicit export.
- cost: No per-check model cost; approximately 1–3% CPU and under 20 MB RAM on the Mac, plus negligible flash writes if the pendant only receives a compact status code.  ·  latency: Health verdicts become sub-second after initial probes; serial reconnect may take up to 10 seconds.
- security: Read-only serial access and local authenticated API; do not include message/page bodies in bundles. Export requires an explicit owner action.
- depends on: A stable serial framing contract for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A correlated receipt/event ID shared by /jobs, /browser, and /pipeline; A bounded redaction and retention policy


## What it asked for

_Nothing._
## Its own summary

Round 148 produced four recorded items. Three owner-facing capabilities: (1) pendant-triggered “Save this” capture that joins Mac selection, browser URL/DOM provenance, active project, and later exact reopen; (2) a cross-device resumable work capsule that restores relevant browser/Mac state and reads the next step; (3) a spoken “Run a desk check” proving Mac, browser, serial pendant, audio bridge, relay, and pipeline health without replaying commands. I also proposed a concrete integration: a read-only USB companion service correlating nRF9160 UART, ESP32 audio, browser heartbeats, Mac receipts, and pipeline events into bounded diagnostic receipts. Live checks show Mac/relay/browser online, 3 Safari tabs, zero pending browser commands, but the active tab is a failed example.com page; Accessibility and Screen Recording remain ungranted. Pipeline confirms 24 kHz PCM rendering/upload and an offline-held-alert event.

**Biggest unknown:** The missing serial framing/probe contract for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, plus a safe Mac API for current text/document selection. Those are the key blockers to making the capture and desk-check capabilities real today; resume capsules additionally need versioned state serialization and restore semantics.

