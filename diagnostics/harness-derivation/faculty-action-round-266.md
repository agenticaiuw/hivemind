# Harness derivation — faculty-action — round 266

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **device reachability** — The live device inventory currently shows home-macbook-bridge online, Safari online, and nrf9160-pendant offline (last seen 2026-08-09T02:56:31.366Z). Bench USB presence cannot be inferred from relay registration.
  - evidence: discover(devices) live result in round 266

## Capabilities it proposed

### "“Save what I’m looking at for later, and remind me what it was when I’m back at my desk.”"
- **useful because:** Turns a fleeting browser moment into a durable, searchable handoff without requiring the owner to dictate a URL or interrupt their work. The browser contributes the authenticated page context, the relay preserves it while the Mac or browser is unavailable, and the pendant later gives a short spoken reminder.
- **path:** browser → relay → pendant → mac-planner
- **model tier:** background for page extraction and concise summary; realtime only for the spoken capture/recall turn
- **latency:** Capture acknowledgement under 2 seconds; background note creation and summary within 30 seconds; recall should be under 3 seconds when the Mac is online.
- **cost:** Usually one small background model call per saved page; roughly $0.002–$0.02 depending on page text. Browser extraction and note creation dominate latency, not inference.
- **security:** Never send page text to the pendant or model when a URL/title is enough. Treat logged-in pages and selected text as private; redact passwords, payment fields, and secrets. Saving a note is reversible and can be proactive, but transmitting page content or creating an external share must require confirmation.
- **missing:** A typed cross-surface bookmark envelope carrying URL, title, capture time, optional selection, sensitivity, and source tab/session; A durable relay inbox item that can be addressed by the pendant later and acknowledged after the Mac writes the note; A recall intent that searches these captured handoffs without exposing the full browser session

### "“Bookmark this meeting moment.”"
- **useful because:** A moment bookmark should become a useful artifact rather than an unlabeled timestamp: the pendant captures the instant, the browser supplies the active meeting/page identity, and the Mac attaches the calendar event and writes a timestamped private note. The owner can later ask for “the moment I bookmarked in yesterday’s meeting” and get the exact context.
- **path:** pendant → browser → relay → mac-planner
- **model tier:** realtime for the immediate acknowledgement only; background model for event matching and a one-sentence note
- **latency:** Haptic/spoken acknowledgement under 1 second; context enrichment within 15 seconds; if offline, queue the bookmark and enrich it when the relay and Mac return.
- **cost:** Near-zero for the raw bookmark; one small background call, typically $0.001–$0.01, for matching calendar context and summarizing nearby page text.
- **security:** Meeting titles, URLs, and page text are private by default. Do not record microphone audio merely because a bookmark was pressed. Only use the active browser tab and calendar metadata; never transmit credentials or meeting participant lists unless explicitly requested. Calendar/note writes are reversible but should show a clear local receipt.
- **missing:** A typed bookmark event linking monotonic pendant time, relay receipt time, active browser session/tab, and optional calendar correlation window; A Mac-side resolver that can match the bookmark to the current Calendar event without opening a microphone; A later query that searches bookmark metadata and returns provenance instead of pretending the bookmark contains a transcript

### "“Run a real end-to-end pendant bench check and tell me exactly what passed before you say the hardware is healthy.”"
- **useful because:** The owner gets an honest hardware verdict instead of a configuration label: audio quality, packet-loss behavior, and the connected bridge/pendant state are measured together, with a receipt that can be inspected later. This is especially valuable because the pendant is currently offline from the relay but physically testable on the bench.
- **path:** pendant → relay → mac-planner → mac-terminal
- **model tier:** background/cheap model for interpreting bounded numeric results; no realtime model needed
- **latency:** A standard 10–30 second fixture run is acceptable; return a pass/fail matrix within 45 seconds and preserve raw measurements for audit.
- **cost:** Under $0.01 in model cost per run; most time is hardware fixture playback, serial capture, and metric computation.
- **security:** Use synthetic speech/sweep fixtures by default and never open the microphone. Do not flash, build, or modify hardware automatically. A run may write only a bounded diagnostic receipt; firmware changes require separate approval. Clearly distinguish “not connected,” “not measured,” and “failed.”
- **missing:** A resolved read-only Mac bench diagnostic operation with enum selectors for serial ports, J-Link probes, build status, and test results; A fixture runner that can correlate pendant UART, ESP32 bridge, and audio_path_probe measurements by run ID; A signed acceptance receipt that records firmware identity, sample rate, frame duration, loss injection, mic drops, tx starvation, alias rejection, and peak-before-speech

### "“For anything consequential, only tell me it happened when the Mac receipt, the browser’s independent state check, and my pendant confirmation all agree; otherwise stop and explain the disagreement.”"
- **useful because:** Today the system can execute, approve, and verify pieces independently, but the owner cannot demand a single atomic truth boundary across them. This capability prevents the dangerous half-success where a message was sent but the browser stayed stale, an action receipt exists but the intended postcondition did not occur, or a physical approval was recorded for the wrong attempt.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime only for the short spoken status; a cheaper background model can classify disagreement and produce the human explanation.
- **latency:** Stage immediately; complete within 5 seconds for ordinary Mac/browser actions, or return ‘unknown’ within 2 seconds when evidence cannot be joined. Never silently retry a consequential action.
- **cost:** Usually one small background classification call, about $0.002–$0.02; the dominant cost is the extra read-only verifier and receipt correlation, not tokens.
- **security:** The pendant receives only an opaque transaction summary, digest, deadline, and outcome—not page contents or secrets. Approval must bind to one operation and attempt, expire, and be single-use. A disagreement must fail closed; retries require a new approval for potentially duplicated external effects. Dashboard evidence should be hash/minimal-snippet by sensitivity.
- **missing:** A commit coordinator that joins operation ID, attempt ID, executor receipt, independent verify_operation_step provenance, and the pendant’s physical approval nonce; An explicit evidence policy saying which postconditions are mandatory for each risk class and how to represent unknown versus failed versus verified; An idempotency/retry fence for browser and Mac actions so evidence disagreement cannot cause a duplicate send or purchase; A user-visible disagreement record that remains queryable after the live conversation ends

### "“For the next hour, you may handle only low-risk tasks in this category; show me every item you skipped and let me revoke the delegation from the pendant.”"
- **useful because:** The owner cannot currently grant a narrowly bounded, temporary delegation that spans relay, Mac, and logged-in browser state. This would turn repeated approvals into a transparent lease: useful for routine triage while preventing an old permission from silently becoming permanent.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Realtime for issuing/revoking the lease; background model for classifying candidate tasks and producing the skipped-item summary.
- **latency:** Grant/revoke acknowledgement under 2 seconds; each low-risk item under 10 seconds; revocation must prevent new work within 1 second and mark in-flight work as stopped or unknown.
- **cost:** A few cents per hour for classification and summaries, dominated by the number of candidate items; no model call is needed for lease validation or revocation.
- **security:** Lease must be scoped by action class, destination, data sensitivity, app/site, maximum count, expiry, and transaction budget. Never include secrets or page contents in the pendant payload. High-risk, external-send, purchase, deletion, and ambiguous actions are excluded regardless of lease. Revocation and expiry fail closed, and every skipped item is logged without exposing private content.
- **missing:** A signed, monotonic delegation lease understood by relay, Mac, browser, and pendant; A policy evaluator that applies lease scope before planning and re-checks it immediately before execution; A revocation fan-out and durable audit record that covers queued, in-flight, completed, skipped, and unknown work; A dashboard view showing remaining time, spend/count budget, and exact reason each item was excluded

### "“What changed while I was away, and show me only changes that are backed by a fresh Mac, browser, or pendant observation.”"
- **useful because:** The owner currently receives summaries and job statuses, but cannot get a single cross-surface change feed that distinguishes a fresh observation from a stale memory, an attempted action, or an unverified claim. This would make the system useful after sleep, travel, or a dropped link without pretending that old state is current.
- **path:** pendant → relay → mac-planner → browser → dashboard
- **model tier:** Background model for clustering and one-sentence narration; realtime only when the owner asks from the pendant.
- **latency:** Return a cached delta summary under 2 seconds; refresh eligible sources and return a provenance-qualified update within 10 seconds. If a source is stale, say so rather than blocking.
- **cost:** Typically $0.002–$0.02 per refresh, mostly metadata clustering; raw observation retrieval should not require a model.
- **security:** Default to metadata, application names, URLs, and action outcomes; do not include page text, message bodies, audio, or secrets unless explicitly requested. Per-source freshness and sensitivity labels must travel with every item. Never infer a change solely from a failed action or missing heartbeat.
- **missing:** A durable per-surface observation cursor with source timestamps and monotonic sequence IDs; A change-set joiner that deduplicates the same event seen by relay, Mac, and browser while preserving provenance; A freshness policy with explicit stale/unknown semantics and owner-configurable retention; A compact pendant presentation that can say ‘three verified changes, two stale, one unknown’ without reading private content aloud


## Changes it proposed to its own stack

### `hardware` — Add a low-profile detented rotary encoder with an integrated push switch as the pendant’s selection axis, wire its quadrature and switch lines to interrupt-capable GPIOs, and reserve a distinct hardware identity for the existing sw0/sw1 inputs. Define a small input protocol: rotate selects or scrubs, click acknowledges, and the existing deliberate approval gesture remains on the dedicated approval input rather than being overloaded.
- **owner gets:** The pendant stops forcing twenty meanings onto one press. The owner can select a pending action, browse saved moments, or scrub a response without looking at a screen, while the jewellery-shaped enclosure gains the control axis the owner explicitly wants.
- effort: Medium hardware/firmware effort: choose an encoder that fits the gold pendant enclosure, route two GPIOs plus switch, add debounce and wake handling, then expose events to the relay and Mac. Prototype wiring can be done on the DK before enclosure work.  ·  risk: Quadrature bounce or accidental rotation could create spurious actions; rate-limit and require a click/approval for any consequential operation. A failed encoder must degrade to the existing buttons. Validate EMI, battery draw, and mechanical wear before committing the enclosure.
- cost: Roughly $3–$15 for a quality low-profile encoder and prototype PCB/wiring; negligible steady-state power, with only interrupt pull-ups and brief scan activity.  ·  latency: Selection feedback should be under 100 ms locally; no network round trip should be needed for navigation. Consequential actions still wait for relay verification and the existing physical approval latch.
- security: Rotation and click may navigate or stage only; they must never authorize an irreversible action. Preserve the invariant that the pendant receives opaque transaction metadata, not page contents or secrets.
- depends on: Owner selecting the mechanical encoder footprint and enclosure constraints; A typed pendant input-event envelope understood by relay and Mac surfaces; Existing physical_transaction_approval_latch semantics for deliberate approval


## What it asked for

_Nothing._
## Its own summary

Round 266 produced three new cross-surface proposals: browser-to-pendant saved handoffs, meeting moment bookmarks enriched by browser and Calendar context without opening the microphone, and a bounded synthetic-fixture bench acceptance run with truthful numeric receipts. I also proposed the owner-requested rotary encoder as a hardware change, and recorded that the relay currently sees the nRF9160 pendant offline while the Mac bridge and Safari are online.

**Biggest unknown:** I still need owner decisions rather than more infrastructure: the rotary encoder footprint/enclosure choice, which bookmark captures are allowed proactively versus staged, and the acceptance-test policy for an offline/unmeasured component. The resolved read-only Mac bench diagnostic capability and a typed cross-surface bookmark envelope remain missing; I did not re-request the already-queued tool.

