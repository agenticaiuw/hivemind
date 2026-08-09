# Harness derivation — mac-terminal — round 246

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Let me have a normal conversation through the pendant and hear your reply in my headphones, with the Mac bench path working now and LTE taking over later without changing the experience."
- **useful because:** This is the system's core promise: hands-free speech that does not silently degrade into stale audio or a dead speaker. It would exercise the two chips that are physically attached today, while making the wearable transport honest when the relay is unavailable.
- **path:** pendant → relay-realtime → mac-planner → mac-terminal
- **model tier:** Realtime for turn-taking and codec/transport control; background tier for bench reports and codec quality summaries.
- **latency:** Under 250 ms from end of utterance to first audible reply packet; 60 ms packet cadence; a USB bench smoke test should report pass/fail in under 30 seconds.
- **cost:** Realtime inference and audio transcription dominate, roughly $0.01–$0.05 per short turn depending on model/audio duration; codec work is local. A scheduled quality report is pennies or less.
- **security:** Audio leaves the pendant to the relay and may traverse the Mac USB bench path; never log raw PCM by default. Persist only turn IDs, packet loss, codec mode, and bounded error samples. Require explicit owner choice before any diagnostic capture is uploaded.
- **missing:** A real end-to-end 24 kHz/superwideband negotiation and packet-format contract shared by nRF9160, relay, and ESP32; A Mac bench runner that can open both currently connected serial devices and validate sequence numbers, latency, underruns, and replay after disconnect; Relay transport support that can switch USB/LTE-M routes while preserving turn ID and replay cursor; A playback acceptance test against the ESP32's fixed 44.1 kHz SBC A2DP path without overflowing its tight buffer

### "What are the four latest items on my Safari reading list? Read them to me in one short spoken summary, and let me ask for any one item to be opened."
- **useful because:** The owner has asked this repeatedly, and the browser is online with five Safari tabs but there is no dependable voice path from Safari's private reading-list state to the pendant. This turns a recurring question into a useful cross-surface handoff: browser session access, concise judgement, and spoken delivery.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Background model to extract title, URL, age, and one-sentence gist from four items; realtime only when the owner asks a follow-up or says open item two.
- **latency:** Return the four titles in 3 seconds; spoken summary within 8 seconds; opening a selected item within 2 seconds after the follow-up.
- **cost:** Usually under $0.01 for four titles and short extracts; reading full pages is the dominant cost and should happen only after selection.
- **security:** Safari Reading List may contain private URLs and authenticated pages. Keep extraction on the Mac/browser session, send only title/domain/short summary to relay, and do not expose page text or cookies in logs. Opening an item is reversible navigation and should be scoped to the selected tab.
- **missing:** A Safari-specific reader that can enumerate Reading List entries (not merely the active tab) through the browser extension; A stable browser result schema with item index, title, URL, added/updated time, and bounded text excerpt; A relay-side spoken-summary intent that can stream four items and retain the item index for the next turn

### "Is my pendant bench healthy right now? Check both connected chips, tell me exactly which link, clock, audio, and firmware checks passed, and give me the next repair command if one failed."
- **useful because:** The owner currently has live nRF9160 and ESP32 hardware on USB but no trustworthy single health answer. This would replace guesswork and make the 24 kHz audio work shippable: it distinguishes a missing device, stale UART, codec underrun, bad clock, and relay absence instead of reporting only that the Mac is online.
- **path:** pendant → mac-terminal → mac-planner → relay-realtime
- **model tier:** Cheap background model parses bounded diagnostic frames and compares them to fixed thresholds; realtime only speaks the concise result when the owner asks.
- **latency:** A bounded read-only check in 5 seconds; spoken verdict in 7 seconds; never leave a serial process running after the check.
- **cost:** Near-zero model cost if the parser is deterministic; occasional repair explanation is under $0.01. The expensive part is implementation and maintaining firmware/host protocol compatibility.
- **security:** Read-only UART health frames may include identifiers and crash snippets. Keep raw logs on the Mac workspace, redact tokens/keys, and send relay only pass/fail plus a short error code. Repair commands must be presented as a plan, not silently flashed or reset.
- **missing:** A real serial-device health action (the current granted schema still cannot resolve because serial is absent from the live inventory) or a narrowly bounded shell wrapper around diagnostics/dual_chip_autocapture.sh; A versioned diagnostic frame emitted by both firmwares with monotonic sequence, sample rate, codec mode, underrun count, and build ID; A parser and threshold table that correlates nRF9160 frames, ESP32 frames, and relay status without treating USB attachment as LTE registration; A safe repair-plan output that maps each failure code to an existing firmware/build command and records the result

### "Look at the tracking page I already have open, tell me whether the package is delayed and when it should arrive, and remind me tomorrow only if it still has not arrived."
- **useful because:** The browser is already on a USPS tracking page, so the owner should not have to dictate a tracking number or navigate while wearing the pendant. The browser reads the authenticated/current tab, judgement turns carrier language into a clear status, and the Mac creates a conditional follow-up rather than a noisy reminder.
- **path:** pendant → relay-realtime → browser-extension → mac-planner
- **model tier:** Background model extracts tracking events and normalizes dates; realtime handles the spoken question and answer. A scheduled cheap check runs only while the conditional reminder is active.
- **latency:** Answer from the open tab in 5 seconds; create the conditional reminder in another 2 seconds; scheduled check should not wake the realtime tier.
- **cost:** A few cents at most when page text changes; near-zero on days with no change if the browser performs a bounded structured check. Reading the full page is the dominant cost.
- **security:** The current page can expose a tracking number and delivery address. Keep those on the Mac, pass only carrier/status/date to the relay, and do not put the number in spoken logs or reminder titles. Creating the reminder is allowed by owner policy; sending anything externally is not.
- **missing:** A browser intent that targets the currently active tab and returns structured carrier events rather than generic page text; A conditional-reminder primitive (recheck predicate, deadline, and cancellation on delivered) rather than a fixed reminder; A browser-to-routine handoff that can re-read the same session without losing tab affinity

### "What changed across my digital life since I last asked? Give me only new or newly-important things from my Mac project, authenticated Safari sessions, and pendant interactions, with one next action for each."
- **useful because:** The current briefings summarize fixed sources, but they do not establish a durable cross-surface baseline. This would answer the question the owner actually has after being away: what is different now, without rereading pages, reopening sessions, or remembering which pendant request was unfinished.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Background model maintains compact per-surface change summaries and computes deltas; realtime only delivers the short spoken answer and handles a follow-up such as 'open the second one'.
- **latency:** Under 5 seconds for a spoken delta when the baseline is warm; under 30 seconds after a first baseline capture. No continuous audio recording.
- **cost:** Low: incremental metadata and short excerpts dominate, typically below $0.02 per refresh; full-page rereads happen only when a changed URL needs verification.
- **security:** Authenticated browser URLs, project names, and pendant transcripts are sensitive. Store hashes, timestamps, titles, and short evidence capsules by default, never cookies or raw audio; keep per-surface access controls and let the owner say 'forget that source'. Do not infer importance from private content without showing its source.
- **missing:** A durable cross-surface baseline with versioned snapshots and a field-level diff, rather than separate latest-briefing stores; A common event schema linking a browser page change, Mac project change, and pendant turn without copying their private payloads into the relay; A judgement pass that ranks novelty and urgency while retaining evidence links for each spoken claim; A pendant follow-up token that maps 'the second one' back to the exact source and opens or resumes it on the Mac/browser

### "Do not interrupt me while I am speaking or driving; collect only genuinely urgent results from my Mac and authenticated browser, then tell me the three most important ones the next time I press the pendant."
- **useful because:** Today each surface can produce work, but there is no shared attention policy: a browser result, scheduled brief, or Mac failure can arrive at the wrong moment or be lost. This makes the pendant an intentional inbox rather than another stream of notifications, while preserving urgency and age.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Cheap background classifier scores urgency and deduplicates events; realtime speaks only on the owner's next available interaction or for an explicitly configured emergency class.
- **latency:** Capture events immediately, decide in under 2 seconds, and deliver a three-item digest within 10 seconds of the next button press. Zero unsolicited audio during an active turn.
- **cost:** Usually pennies per day; event scoring and deduplication are small, with realtime used only for the final spoken digest.
- **security:** Urgency classification must not leak private browser content into notifications. Store only encrypted event envelopes and source handles; speak sensitive titles only after the owner initiates retrieval. Emergency exceptions must be explicit, narrow, and cancellable.
- **missing:** A shared attention-state protocol (speaking, unavailable, available, driving/quiet) emitted by the pendant and respected by relay, Mac, and browser; A durable cross-surface inbox with expiry, deduplication, urgency rationale, and source handles rather than independent notification queues; A single-button retrieval contract that can enumerate the digest and resolve 'tell me more about item three' back to its originating session; A policy editor for the owner to define what qualifies as urgent without adding confirmation gates to ordinary Mac actions

### "Why did you tell me that, and what exactly did you use? Give me a short spoken chain of evidence and let me reopen the source or undo the action."
- **useful because:** A cross-surface hive can otherwise sound confident while hiding whether a claim came from a stale browser page, a Mac command, or a remembered pendant turn. The owner should be able to challenge any answer in plain speech and get the exact source, age, action receipt, and available undo path.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → unified
- **model tier:** Background model assembles a compact evidence graph and detects stale or conflicting sources; realtime translates it into one short spoken explanation and handles 'open source' or 'undo' follow-ups.
- **latency:** Evidence summary in under 4 seconds from durable records; opening a source or presenting an undo action in under 3 seconds.
- **cost:** Low, mostly metadata retrieval and graph ranking; under $0.01 for ordinary queries, with full page rereads only when the source has changed.
- **security:** Evidence can expose private URLs, command arguments, and file paths. Redact secrets and parameter values by sensitivity, speak only the minimum necessary, and require the existing owner confirmation policy for irreversible undo or external effects.
- **missing:** A common evidence-record schema linking spoken claims to browser provenance, Mac receipts/journals, routine runs, and pendant turn IDs; A freshness/conflict evaluator that refuses to present a stale source as current; A source resolver that can reopen a browser page or Mac artifact without exposing credentials to relay; A durable claim-to-action relationship so undo is offered only when the exact action is reversible


## Changes it proposed to its own stack

### `integration` — Ship a first-class, read-only dual-UART bench health action implemented in the Mac agent, backed by the existing diagnostics scripts but returning structured per-port frames, exit status, timestamps, and bounded log excerpts; correlate the nRF9160 and ESP32 result with relay /health and explicitly label USB-bench versus LTE state.
- **owner gets:** Today the chips are physically connected but the system cannot answer whether either is alive; the owner has to guess from raw logs. This would make the next 24 kHz audio iteration actionable in one spoken answer and prevent claiming wearable/LTE health from a USB-only test.
- effort: Medium: host action and parser, versioned firmware diagnostic frame, tests for absent/stale/noisy ports, and dashboard/voice formatting.  ·  risk: A malformed or stale frame could produce false green. Require monotonic sequence and freshness thresholds, show UNKNOWN rather than pass, and retain the raw bounded excerpt for debugging. Never flash or reset as part of health.
- cost: Negligible runtime/API cost; roughly 1–2 engineer-weeks. No hardware cost.  ·  latency: 5 seconds or less for a bounded read; no impact on normal voice turns.
- security: UART logs stay local by default; redact tokens and identifiers before any relay upload. Read-only action has no device mutation.
- depends on: A real implementation of the unresolved serial diagnostic tool or a narrowly scoped run_shell wrapper; A versioned diagnostic frame in both firmware images; The existing GET /health and GET /ops/status correlation


## What it asked for

_Nothing._
## Its own summary

This round produced four owner-facing capabilities: (1) the highest-value one, a real end-to-end 24 kHz spoken conversation over the currently attached USB bench path with LTE handoff later; (2) spoken Safari Reading List retrieval with indexed follow-up opening; (3) a truthful dual-chip pendant-bench health verdict; and (4) spoken USPS tracking status with a conditional tomorrow reminder. I also recorded the integration change needed to make the bench verdict real. Live discovery confirms Safari is online (five tabs, currently USPS tracking) and the Mac bridge is online. The granted serial diagnostic call still cannot resolve: serial/USB is absent from the action inventory, so I could not inspect either chip this round. The granted broad Mac diagnostics call also remains unresolved against the live inventory.

**Biggest unknown:** Whether /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA actually emit valid, fresh diagnostic frames right now. The next useful work is not another proposal or resolver rename: implement the bounded dual-UART health action (or invoke the existing autocapture scripts through the already-authorized shell), add versioned frame parsing, and then validate the 24 kHz path against the ESP32's 44.1 kHz SBC/A2DP buffer constraints.

