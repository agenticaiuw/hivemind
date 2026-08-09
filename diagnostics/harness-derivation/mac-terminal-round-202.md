# Harness derivation — mac-terminal — round 202

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When something I asked the pendant to do on my Mac fails, tell me exactly what failed, what it changed before failing, and offer a one-press retry that will not repeat completed steps."
- **useful because:** Today a failed multi-step job collapses into a short error, while the owner cannot know whether a file moved, an app opened, or a browser step already succeeded. This turns the wearable into a trustworthy recovery console: the Mac supplies per-step receipts and the pendant supplies the immediate, physical retry decision.
- **path:** pendant → mac-planner → relay-realtime → browser → dashboard
- **model tier:** Use a cheap background classifier on the Mac to summarize receipts and determine which remaining steps are idempotent; use realtime only to speak the concise result and accept the button choice.
- **latency:** Under 2 seconds after job failure for the first spoken diagnosis; retry dispatch under 500 ms after the button press.
- **cost:** Usually <$0.01 per failure; most work is deterministic receipt formatting, with a small model call only when classifying recovery.
- **security:** The Mac must send only action labels, touched paths/domains, exit status, and bounded stderr—not inherited environment or secrets. A retry must be generated from the durable ledger and use the existing action idempotency key, never replay the entire original command. Require an explicit button press for retry, but not for ordinary trusted execution.
- **missing:** Per-step shell exit code, signal, pid and resource outcome in the receipt; A durable job-to-ledger join and closed ledger on every execute; A resume endpoint that returns only unfinished, replay-safe steps; A relay event carrying a compact failure capsule and retry token to the pendant

### "Run a two-minute pendant health check: exercise the nRF9160 and ESP32 audio bridge over USB, measure microphone-to-speaker latency and dropped frames, and tell me whether the wearable is ready before I leave."
- **useful because:** The owner should not discover a dead microphone or one-way audio after leaving Wi-Fi. The physical chips are connected now, but there is no user-level verdict that covers both firmware endpoints and the Mac audio path in one test.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic shell/serial test and thresholding first; use a cheap model only to turn the measurements into a short spoken explanation. Realtime is unnecessary unless the owner is actively talking through the test.
- **latency:** A bounded 120-second test, with progress on the pendant every 10 seconds and a final result within 3 seconds of the last frame.
- **cost:** <$0.005 per run; CPU and USB serial capture dominate, not model inference.
- **security:** Read-only diagnostics except for a generated local test tone and loopback frames. Never upload raw microphone audio; retain only counters, latency percentiles, firmware versions, and a short failure code. Require explicit invocation because the test briefly drives the speaker.
- **missing:** A host-side framed reader for the two currently enumerated USB serial devices; A shared diagnostic protocol with firmware version, frame counters, timestamps, and CRC; A bounded loopback/test-tone mode in the ESP32 and nRF firmware; A dashboard and pendant result event that distinguish cable/firmware/audio failures

### "Before you submit or edit anything in my browser, save a private recovery snapshot; if I later say 'undo that browser change' into the pendant, restore the exact form state and show me the page and fields that changed."
- **useful because:** Browser automation is the one surface holding sessions and unsaved work that the Mac and relay cannot recreate. A mistaken submit or navigation currently leaves the owner guessing. A short-lived, encrypted draft snapshot gives the wearable a practical undo path without exporting passwords or page contents to the cloud.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic extension snapshot/diff and browser undo first; use a cheap model only to explain the changed fields in plain language. Realtime handles the owner's brief undo command.
- **latency:** Snapshot before an action in under 150 ms; diff and pendant acknowledgement in under 1 second; restore in under 2 seconds.
- **cost:** Near zero model cost for ordinary changes; storage is bounded per tab/session (for example, five snapshots capped at 256 KB each).
- **security:** Keep snapshots local to the browser profile, encrypted at rest, TTL them aggressively, and redact password fields, tokens, payment numbers, and hidden inputs. Never send DOM or values to the relay; send only field labels, hashes, URL origin, and a reversible snapshot handle. Restoration must target the same tab/session and refuse if the origin or DOM signature changed.
- **missing:** An extension-side snapshot store and DOM-aware diff/restore protocol; A browser action transaction hook that takes the snapshot before navigation/click/submit; A pendant command and relay route carrying a scoped undo handle; Dashboard UI showing the proposed diff and expiry

### "When I finish a fiddly task, let me say 'make this reproducible' into the pendant and receive a private replay recipe containing the exact Mac commands, browser steps, project revision, and required session assumptions."
- **useful because:** The owner repeatedly performs workflows that are difficult to explain or repeat. A normal transcript loses hidden browser state, working directory, versions, and the order of UI actions. A replay recipe would turn a successful one-off into a durable personal procedure that another day—or another hive node—can execute and verify.
- **path:** pendant → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Capture deterministic events and machine facts without a model; use a cheap background model only to turn the event trace into a readable recipe and flag steps that cannot be replayed. Realtime is only for the short spoken trigger and confirmation.
- **latency:** Capture is continuous with no perceptible delay; recipe generation under 10 seconds after the trigger; replay preflight under 3 seconds.
- **cost:** Usually <$0.02 per recipe, dominated by one summarization call; raw trace storage is bounded and local.
- **security:** Do not record keystrokes, passwords, tokens, page contents, or inherited shell environment. Replace secrets with typed placeholders, retain origins and selectors rather than DOM dumps, encrypt the local trace, and show a redaction report before sharing or replaying. Browser-session-dependent steps must be marked non-portable instead of silently exporting cookies.
- **missing:** A cross-surface event trace with monotonic ordering and causality IDs; Mac shell and UI action instrumentation that records typed intent, cwd, revision, and outcome without secrets; Browser-extension instrumentation for navigation, clicks, downloads, and form-field labels; A recipe format with placeholders, preflight checks, replay-safety annotations, and versioned export; A pendant command to mark the beginning/end of capture and retrieve the recipe status

### "Let me ask the pendant 'is that still true?' about any remembered fact, and have the hive check the Mac files, authenticated browser pages, and relay memory for contradictory or newer evidence before answering with a confidence and an expiry date."
- **useful because:** A remembered fact is dangerous when it silently becomes stale—an address, project branch, deadline, or configuration can change. No single node can validate all of those sources: the browser has authenticated truth, the Mac has local artifacts, and the relay has history. The owner gets a freshness judgment instead of a confident but obsolete answer.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use deterministic source fetches, timestamps, hashes, and contradiction detection first; use a background model to normalize claims and explain disagreements. Realtime only speaks the final short answer.
- **latency:** Answer in under 5 seconds for cached sources; under 15 seconds when a live browser check is required.
- **cost:** <$0.03 for a multi-source check; browser/network retrieval and evidence normalization dominate.
- **security:** Query only sources authorized for the owner and preserve source boundaries. Do not copy private page bodies into relay memory; store claim snippets, hashes, URL/origin, timestamps, and sensitivity labels. Require confirmation before treating a newly observed value as the canonical memory when sources conflict.
- **missing:** A cross-node claim-validation coordinator with source freshness policies; A claim schema carrying value, observedAt, expiresAt, authority, and evidence references; Live browser checks that can be explicitly scoped to an existing authenticated session; Conflict-aware memory updates rather than unconditional fact replacement; A compact spoken response format that names the winning source and disagreement

### "Let me demonstrate a task once while I work—using my browser and Mac normally—and then say 'do this every Friday'; have the hive turn the demonstration into a parameterized routine, ask only about the parts that vary, and run it with a spoken result on the pendant."
- **useful because:** The owner can perform a task but may not know how to describe selectors, file paths, or ordering. Demonstration captures the real workflow across the browser session and Mac, while the pendant supplies the natural-language schedule and exception handling. This is more useful than a fixed macro because it learns which values are inputs and which are stable steps.
- **path:** pendant → browser-extension → mac-planner → relay-realtime → dashboard
- **model tier:** Deterministic event capture and replay validation first; a background model infers parameters and asks a small number of clarification questions. Scheduled executions use a cheaper model; realtime is reserved for the spoken setup and exceptions.
- **latency:** No added latency during demonstration; initial routine proposal within 30 seconds; scheduled run starts within one minute of its trigger and reports completion promptly.
- **cost:** <$0.05 to infer and validate a routine; later runs are mostly deterministic and <$0.01 unless an exception needs reasoning.
- **security:** Never record secrets or raw keystrokes. Treat authenticated browser steps as session-bound, redact form values, list every inferred parameter and side effect, and keep the owner’s demonstrated trace local until explicitly saved. A routine must stop and report when its page, project, or assumptions differ rather than improvising silently.
- **missing:** A demonstration recorder spanning Mac actions and browser events; Parameter-inference and human review for converting a trace into a routine; Replay validation against a disposable or preview mode where possible; A routine schema for assumptions, variables, side effects, and stop conditions; A pendant conversational setup flow for schedule, exceptions, and result reporting


## What it asked for

_Nothing._
