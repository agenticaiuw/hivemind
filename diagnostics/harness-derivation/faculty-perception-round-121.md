# Harness derivation — faculty-perception — round 121

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac perception and browser reachability** — At 2026-08-07T18:04Z the Mac bridge and Safari extension are online. Safari has 3 tabs: Gmail Inbox (logged in), and two example.com tabs titled Failed to open page. /observe reports Accessibility trusted=false, Screen Recording=false, eventsPost=false, and uiActionsWillReachTheScreen=false.
  - evidence: GET /ops/status and GET /observe returned these values.
- **recent browser action truth** — The most recent browser_read_page job failed because the extension could not execute in the Gmail frame ('Extension does not have access to this frame'); a separate browser_list_tabs job succeeded and reported 3 tabs.
  - evidence: GET /jobs returned local_95ac96a9... failed browser_read_page and local_c6268b40... completed browser_list_tabs with receipts.
- **pipeline reality** — The pipeline contains recorded historical nRF9160 and cloud-relay events, including a response waiting for the pendant, while current relay status says mac bridge online and no registered nRF9160 device is exposed by this Mac agent route. Do not treat pipeline history as live pendant presence.
  - evidence: GET /pipeline returned nrf9160/cloud-relay historical runs; GET /ops/status reports relay macBridgeOnline=true and the device route GET /v1/devices/status is absent (404).

## Capabilities it proposed

### "“What’s actually true right now?” Give me one compact, timestamped snapshot of what is on my Mac screen, which private browser tabs are open and readable, what the relay and wearable pipeline are doing, and whether any actions are still pending—separate observed facts from stale history and never claim a UI action succeeded unless its effect is verified."
- **useful because:** This is the single most useful perception capability: it prevents the system from confidently describing a world it has not observed. Today /observe says the Mac agent cannot reach the screen, Safari has three tabs but two are failed pages, Gmail is logged in, and the pipeline contains old simulated pendant events; the owner needs that distinction in one spoken answer.
- **path:** pendant → relay-realtime → relay → mac-planner → mac-vision → browser-extension → unified → faculty-perception
- **model tier:** deterministic for collection and freshness checks; background model only to compress conflicting observations into speech
- **latency:** Under 2 seconds when all surfaces are online; explicitly label any source older than 60 seconds instead of waiting indefinitely.
- **cost:** Usually $0 model cost for typed reads; roughly 1–2k background tokens only when reconciliation or natural-language compression is needed. Browser and relay reads dominate latency.
- **security:** Private tab titles, URLs, and pipeline metadata remain on the owner’s Mac/relay; spoken output must redact tokens and message bodies unless explicitly requested. Read-only by default.
- **missing:** A single typed perception snapshot endpoint joining /observe, /browser/status, /pipeline, /jobs, /ops/status, and relay device state; Freshness/authority rules distinguishing live device telemetry from recorded pipeline history; A wearable delivery path for the snapshot when the pendant is actually registered

### "“Test my pendant without LTE.” With the pendant and ESP32 bridge attached by USB, capture a short end-to-end loop: identify both serial devices, record button/audio/LED packets, send a signed synthetic command from the Mac bridge through the relay simulator, play a known PCM tone or sentence, and return a packet-level receipt showing what was observed locally versus what reached the cloud."
- **useful because:** The hardware can be physically exercised before LTE registration. This turns the currently unverifiable wearable into a testable instrument and catches framing, sample-rate, playback, and reconnect defects without pretending that recorded relay history came from a live pendant.
- **path:** pendant → relay → mac-planner → mac-terminal → unified → faculty-perception → faculty-action
- **model tier:** deterministic harness and background summarizer; no realtime model needed unless the owner asks a spoken follow-up
- **latency:** A smoke test should finish in 10 seconds; a 10–30 second audio loop is acceptable. Fail fast if either serial port is absent or a packet acknowledgement is missing.
- **cost:** No per-run model cost; local USB I/O and optional relay requests dominate. A 1–2 kB receipt per test.
- **security:** Use a development device identity and signed test payloads; never send the owner’s microphone or private audio to the relay. Require explicit confirmation before any test that could move from simulator traffic to production relay/device commands.
- **missing:** Serial protocol adapters for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A relay simulator/test namespace that cannot impersonate a production pendant; Known-good firmware test commands and packet schemas for nRF9160 and ESP32 bridge; A packet-level receipt route exposed to the perception layer

### "“Why didn’t that work?” After any failed or uncertain Mac/browser/relay action, explain the actual blocking condition in plain language, show the evidence that established it, distinguish permission failure from page/frame failure from stale device state, and give me the smallest owner-side fix or safe alternative—without pretending to retry."
- **useful because:** Today the owner can receive a generic failure even though the cause is materially different: UI input is impossible because this binary lacks Accessibility, while Gmail page extraction failed because the extension could not access that frame. A precise explanation saves repeated attempts and tells the owner when a System Settings change—not another prompt—is required.
- **path:** relay-realtime → mac-planner → mac-vision → browser-extension → faculty-perception → faculty-judgement
- **model tier:** deterministic error taxonomy first; background model for a short owner-facing explanation; realtime only when the owner is waiting in voice
- **latency:** Under 1 second for known error classes; under 3 seconds for correlated evidence.
- **cost:** Near-zero for typed error mapping; under 1k background tokens for uncommon explanations. Evidence reads dominate, not inference.
- **security:** Do not expose bearer tokens, page contents, or filesystem paths beyond what is needed. Permission remediation may reveal app identity and should be spoken only to the owner.
- **missing:** A normalized cross-surface failure taxonomy with machine-readable causes; Evidence links from every receipt to the observation that justified its status; A remediation catalog keyed by cause and surface; A final status distinct from failed, blocked, unverified, and stale

### "“Freeze this moment, and tell me what changed when I come back.” Capture a signed, read-only reality freeze of the Mac foreground app, browser tab identities and titles, relay/device connectivity, active pipeline/jobs, and permission reachability; later compare a fresh freeze and narrate only meaningful changes, including which changes are observations versus events recovered from history."
- **useful because:** The owner needs a dependable boundary around interruptions and handoffs. A live system currently mixes current Mac state with historical pendant pipeline records; an immutable freeze would let them return from sleep or travel and know what actually changed rather than trusting an unbounded stream of stale events.
- **path:** pendant → relay → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** deterministic snapshot and semantic diff; background model only to produce the short spoken narrative
- **latency:** Freeze under 2 seconds; comparison under 3 seconds, with no waiting on an offline pendant.
- **cost:** No model cost for hashes/diffs; roughly 2–5kB per freeze plus optional under 1k summarization tokens.
- **security:** Snapshots contain private tab metadata and app state. Encrypt at rest, give each freeze an explicit name/expiry, redact URLs/query strings by default, and require confirmation before sharing a freeze with the relay.
- **missing:** An append-only, signed reality-freeze store with retention controls; Stable typed schemas for foreground app, browser tabs, relay/device state, jobs, pipeline events, and permissions; Semantic diff rules that exclude volatile timestamps and browser counters; A spoken retrieval/comparison command available from the relay or wearable

### "“Before you use the cloud, show me exactly what would leave my Mac.” For a task involving a logged-in page, microphone, screenshot, or local document, produce a field-level transfer manifest naming each datum, its source surface, destination/model, retention, and purpose; let me approve only selected fields or keep the whole task local."
- **useful because:** The collective spans a private browser, Mac, relay, and wearable, but the owner cannot currently see the boundary between local observations and cloud model input. This makes sensitive tasks understandable and lets them use the system without surrendering an entire page, recording, or URL when only one field is needed.
- **path:** browser-extension → mac-planner → relay-realtime → relay → pendant → faculty-perception → faculty-judgement → faculty-action
- **model tier:** deterministic data-flow manifest; no model needed to enumerate fields; background model may explain tradeoffs after the owner selects a policy
- **latency:** Manifest under 500ms for known action types; under 2 seconds when extracting fields from a private page.
- **cost:** No inference cost for manifests; small metadata storage. Optional explanation under 500 background tokens.
- **security:** The manifest itself must not contain the sensitive payload it describes. It needs local enforcement, not merely a UI promise: unapproved fields must be removed before relay upload, audio streaming, screenshot capture, or planner context assembly.
- **missing:** A data-classification and provenance label on browser, audio, filesystem, and context fields; A preflight interception point before relay/model upload; Per-field redaction and approval tokens enforceable by all surfaces; An audit log the owner can inspect and revoke


## Changes it proposed to its own stack

### `integration` — Add an effect-verification gate to every Mac/browser action receipt. Before execution, record the relevant reachability precondition (Accessibility for UI input, Screen Recording for visual verification, extension frame access for browser reads). After execution, require typed evidence: changed app state, returned DOM/text, or an explicit device acknowledgement. If the precondition is false, mark the action blocked/unverified rather than successful; retain the attempted receipt and a recovery instruction. For the current machine this would have prevented false confidence from UI actions while /observe reports eventsPost=false, and would have classified the Gmail browser_read_page failure as an access/frame failure rather than a generic failed job.
- **owner gets:** The owner gets honest answers and safe recovery instead of receipts that say an action worked when it did nothing. It also tells them exactly why a private page or UI action could not be completed.
- effort: Medium: typed precondition/evidence schema, adapters for AppleScript/browser extension/vision, and receipt status migration.  ·  risk: Some actions that really worked but lack a verifier will become unverified; recover by allowing a clearly labeled owner confirmation or a surface-specific verifier. Never silently retry irreversible actions.
- cost: Negligible storage; 0–500 deterministic tokens per action. Verification may add one browser or AppleScript round trip.  ·  latency: Adds roughly 0.2–1.5 seconds for evidence collection; skips pointless retries when reachability is known false.
- security: Improves safety by preventing fabricated success. Evidence capsules must redact page content and avoid uploading screenshots unless consented.
- depends on: The existing action receipt/undo records from chg-5fc73ce3; GET /observe reachability fields; Typed browser results and tab affinity from chg-14accc01; A small per-action verifier registry


## What it asked for

_Nothing._
## Its own summary

Round 121 established three live facts: the Mac bridge and Safari extension are online; the agent cannot inject or verify UI input because Accessibility and Screen Recording are false; and a recent Gmail read failed at the extension frame boundary while tab listing succeeded. I recorded these facts, informed judgement/action/unified, and proposed (1) a single timestamped cross-surface truth snapshot, (2) typed effect verification that blocks false-success receipts, and (3) a USB serial pendant/ESP32 smoke-test loop that works before LTE registration.

**Biggest unknown:** The remaining decisive unknown is the physical USB protocol and identity state: which serial ports are currently open, what packet/ack schemas the nRF9160 and ESP32 firmware implement, and whether a safe relay-simulator namespace exists. I also still need a typed authority/freshness contract for reconciling live observations with historical /pipeline events; without it, the system can collect facts but cannot safely say which world is current.

