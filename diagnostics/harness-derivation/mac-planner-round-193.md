# Harness derivation — mac-planner — round 193

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I leave a meeting, turn what happened into a ready-to-send follow-up: decisions, owners, deadlines, and the exact draft, using the meeting on my calendar, the document or browser tab I was looking at, and the bookmarks I made on the pendant."
- **useful because:** This closes the loop from a wearable moment marker to an actionable artifact instead of a transcript nobody revisits. It works only by joining pendant timing, Mac Calendar/Mail, the authenticated browser tab, and relay-side reasoning; the Mac alone cannot know the spoken/bookmarked moments or safely retain the browser session context.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the realtime tier only to acknowledge a bookmark or a spoken 'wrap this meeting'; use a cheaper background model to reconcile calendar, browser and Mac sources, extract decisions, and draft. Escalate to realtime only when the owner asks for interactive edits.
- **latency:** A spoken acknowledgement under 1 s; first follow-up draft within 30 s of the wrap command; source collection is bounded to the active meeting window and one explicitly selected browser session.
- **cost:** Roughly $0.01-$0.06 per meeting depending on audio/bookmark volume; background model tokens dominate, not the short acknowledgement.
- **security:** Calendar titles, mail snippets, local documents and authenticated browser content leave the Mac only as redacted, source-scoped extracts. Never send the draft automatically; require an explicit owner command before any mail send. Expire raw excerpts after the draft and retain only cited source IDs and the owner's accepted edits.
- **missing:** A serial/event bridge that exposes offline_moment_bookmark records to the relay while USB-attached; A meeting-window correlation service joining bookmark timestamps to Calendar events; A browser command to return the active tab's selected document context with explicit session scope; POST /meeting-followup implementation and a send-after-confirmation path

### "Tell me when the thing I am about to do conflicts with my actual commitments—for example, when a browser deadline, an email promise, a local file, and my calendar disagree—and show me the smallest correction before I act."
- **useful because:** People lose trust when separate surfaces disagree. A cross-node consistency check catches stale dates, wrong time zones, duplicate commitments, and an outdated document while there is still time to fix them. The pendant gives a low-friction 'check this' trigger; the Mac and browser provide evidence that the relay cannot reach by itself.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Background model performs structured extraction and contradiction ranking; realtime model only answers the owner's short query and reads the top conflict. Deterministic date/time and duplicate checks should run without an LLM.
- **latency:** Return a preliminary conflict scan in 3 s from bounded sources; stream deeper document/browser comparison within 15 s. Never block unrelated Mac use.
- **cost:** $0.005-$0.03 per scan; most cost is document/browser text normalization and comparison, so cap each source and hash unchanged content.
- **security:** Default to metadata, snippets, dates and hashes; do not upload whole documents or mail bodies unless the owner names the source. Authenticated browser pages must be session-scoped and never rendered into dashboard logs. A warning is read-only; changing a calendar event, file, or draft always becomes a separate explicit action.
- **missing:** A typed cross-source evidence schema with provenance, timestamps, timezone and confidence; A browser read endpoint that returns bounded visible text/structured dates rather than screenshots alone; A relay trigger for a pendant bookmark plus current Mac foreground context; A conflict-ranking routine and a dashboard card with dismiss/snooze/correct actions

### "I plugged the pendant into my Mac—run a complete audio and link check, tell me exactly what failed, and leave a one-page repair report I can send to you."
- **useful because:** The pendant is physically testable over USB today even though LTE registration is not. One command should exercise capture, Opus encode, serial transport, relay ingestion, decode and playback, then turn counters into an understandable pass/fail report instead of requiring firmware logs and expert interpretation.
- **path:** pendant → mac-planner → relay-realtime → dashboard
- **model tier:** Use deterministic firmware thresholds and a cheap background model to explain the report; realtime is unnecessary except for a spoken result if the owner asks while wearing the pendant.
- **latency:** Start immediately and finish a normal fixture in 20 s; if a serial or relay stage stalls, stop after 5 s and report the exact stage rather than hanging.
- **cost:** Under $0.01 per run; the fixture and local parsing dominate, with almost no model tokens needed.
- **security:** The fixture must use synthetic audio only and never open the microphone beyond the deliberate diagnostic mode. Serial output may contain identifiers, so redact device IDs in the dashboard and report. No network upload of raw PCM; send counters, sequence numbers, and hashes only.
- **missing:** A resolved mac_serial_exchange tool for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; A USB session protocol that arms audio_path_diagnostic_fixture and correlates pendant, ESP32 bridge, Mac and relay clocks; A deterministic report generator with the shipped thresholds (alias rejection, codec CPU, mic drops, tx starvation, clipping and underruns); A dashboard/download route for the signed repair report

### "Make this change everywhere I named—update the browser form, save the resulting file, and put the appointment on my calendar—but if any step fails, undo the parts that already happened and tell me exactly what was restored."
- **useful because:** Today a plan spanning the authenticated browser, local files, and Calendar can leave a half-completed mess: a submitted form with no file, or a file and calendar event after the browser failed. The owner should get one atomic, explainable operation rather than manually repairing partial side effects. The pendant is the natural place to receive a concise success/failure result without staring at the Mac.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background planner to compile a typed saga and deterministic compensations; use realtime only for the owner's initial command and final spoken receipt. Never let an LLM decide whether an irreversible external submission is compensatable; mark it as a commit boundary and require an explicit confirmation before crossing it.
- **latency:** Preview the ordered steps and compensation plan within 5 s; execute reversible steps within 30 s; retain a heartbeat and recover/reconcile after a dropped Mac or browser link for up to 10 minutes.
- **cost:** About $0.01-$0.05 per workflow; API/browser calls and reconciliation retries dominate, while model use is limited to plan compilation and a short receipt.
- **security:** The relay must hold only opaque operation IDs and redacted receipts, not browser credentials. Browser actions remain session-scoped. Every mutation records before/after hashes or object IDs, compensation status, and an idempotency key. A true external submission (send/submit/purchase) is a non-compensatable commit boundary and must be clearly announced before execution.
- **missing:** A cross-surface saga coordinator with durable idempotency keys, leases, dependency ordering, and compensation handlers for browser, file, and Calendar mutations; Browser and Calendar adapters that expose pre-state, post-state, and an honest compensation result—not just success/failure; A server-to-Mac/browser two-phase receipt protocol that survives retries and a sleeping Mac; A pendant result envelope for 'completed', 'rolled back', 'partially committed', and 'needs attention' with a durable dashboard timeline


## Changes it proposed to its own stack

### `hardware` — Revise the next pendant revision to include a physical microphone power-cut switch with an independent sense line, plus a small LRA haptic driver. Keep the existing two-button/one-LED protocol as fallback, but make the cutoff electrically local so firmware, relay, Mac, and LTE cannot override it; expose switch state in the USB and relay status frames.
- **owner gets:** The owner gets a privacy control they can verify by touch and a silent, unambiguous acknowledgement while moving. Today the pendant has no mic-disable switch, no vibration motor, and one LED overloaded with recording, inbox, and staged-reply meanings; software privacy alone cannot provide that confidence.
- effort: Moderate hardware respin: switch, load switch or analog cutoff, sense GPIO, LRA and driver, enclosure change, firmware state/event integration, and privacy/audio acceptance tests.  ·  risk: A bad cutoff implementation could leave the mic biased or create audio pops; default hardware state must be mic-off until firmware explicitly enables capture, and every transition needs a fixture test. If the haptic driver fails, LED/button behavior remains functional.
- cost: Approximately $3-$8 BOM increase in small volume, negligible average power when idle; brief haptic peaks require a regulated current path and may affect battery sizing on a future board.  ·  latency: Local cutoff is instantaneous; relay notification is best-effort and must not gate the local state.
- security: Strongly positive: an independent electrical path prevents compromised firmware, relay commands, or Mac automation from recording while the switch is off. Switch state should be reported as coarse state only, not tied to location or audio.
- depends on: A pendant board revision with one spare GPIO/ADC sense path and a power domain that can actually disconnect the microphone; Firmware integration with local_privacy_latch and existing audio-path diagnostics; Updated enclosure and a defined owner-visible haptic/LED state table


## What it asked for

_Nothing._
## Its own summary

Fresh work this round: (1) a cross-node meeting-to-follow-up flow that joins pendant bookmarks, Calendar/Mail, the active authenticated browser session, and a confirmed draft; (2) a commitment-conflict detector that compares bounded browser/Mac sources and warns before action; (3) a USB-connected pendant clinic that runs the synthetic audio fixture and produces a repair report; plus a hardware proposal for an independent physical mic cutoff and LRA haptic feedback. I also discovered live Mac state: Accessibility and Screen Recording are now trusted for AI Pendant Agent, input posting is verified, 18 apps are running, and three browser sessions exist. I told mac-terminal which accepted/duplicate ideas to avoid.

**Biggest unknown:** The missing resolved mac_serial_exchange capability remains the blocker for the USB clinic. I still cannot directly arm/read /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA from this agent; the orchestrator's queued request has not resolved. Browser inspection is also currently ambiguous between action:browser_inspect and POST /browser/inspect, so I cannot reliably read the active authenticated tab until that resolver tie is fixed.

