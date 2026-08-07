# Harness derivation — faculty-action — round 62

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "Run a 24 kHz audio path check and tell me exactly where quality or timing breaks."
- **useful because:** The owner can currently decide to ship the audio path but cannot obtain one trustworthy, end-to-end proof across the worn pendant, relay, Mac, and Bluetooth bridge. A tagged test run would distinguish codec, transport, I2S, resampling, and A2DP failures instead of reporting that a command merely queued.
- **path:** pendant → relay-realtime → mac-terminal → mac-planner → dashboard
- **model tier:** background/scheduled work on a cheaper model; use realtime only to explain the short spoken result
- **latency:** Start within 2 seconds; a 10–20 second test is acceptable. Spoken result under 3 seconds after the run ends.
- **cost:** About $0.01–$0.05 per run, dominated by a small diagnostic transcript; most work is local counters and timestamps.
- **security:** Test audio should be generated locally and contain no microphone content. Do not upload owner speech. Bluetooth device names and packet diagnostics may leave the Mac only if explicitly enabled. Require confirmation before any firmware flash, pairing change, or sustained speaker output.
- **missing:** A pendant-side diagnostic command that emits packet/frame timestamps and counters without flashing; A relay test-session mode that tags and correlates frames end to end; Mac/bridge capture of A2DP underruns and a deterministic return/telemetry channel; A signed, durable audio acceptance receipt with per-hop evidence; An owner-approved audio-path acceptance spec (the 24 kHz criteria request is still pending)

### "From whatever private page I’m looking at, turn the relevant deadline or follow-up into a Mac reminder and tell me what you used."
- **useful because:** Today the mind can read a logged-in page and it can create a reminder, but it cannot safely join those two acts into one provenance-preserving handoff. The owner must manually copy the date, title, URL, and context, which is exactly where deadlines get lost. This would make the browser, Mac, relay, and pendant function as one hand rather than separate tools.
- **path:** browser-extension → mac-planner → relay-realtime → pendant → dashboard
- **model tier:** Use a cheaper background model for extracting and normalizing the deadline; use realtime only for the short spoken confirmation.
- **latency:** Extract and prepare in under 5 seconds; create the reminder in under 2 seconds after preparation; one short spoken receipt immediately afterward.
- **cost:** Roughly $0.01–$0.04 per invocation; model extraction dominates, while browser and reminder operations are local.
- **security:** The source may contain private account data. Keep page text and URL on the Mac/relay job record with least-privilege retention, redact unrelated text, and include a source link and exact quoted evidence in the receipt. Creating reminders is allowed without confirmation under the owner’s policy; never send messages or submit forms as a side effect.
- **missing:** A typed cross-surface handoff contract carrying source tab/session, quoted evidence, timezone, confidence, and reminder fields; A browser extraction action that returns a stable citation for the selected deadline rather than an unverified summary; A Mac reminder action that accepts the contract and returns the created reminder identifier; A compact pendant receipt that can read back title, due time, and source without replaying private page contents


## Changes it proposed to its own stack

### `integration` — Build an end-to-end audio acceptance transaction that creates a local tagged test stream, correlates relay pipeline events with pendant decode/I2S counters and ESP32/A2DP telemetry, computes per-hop latency/jitter/loss/underruns, stores a signed receipt, and automatically tears down the test. It must fail closed when telemetry is missing rather than infer success from HTTP 200.
- **owner gets:** When the owner asks whether the 24 kHz path works, they get a defensible answer naming the failing hop—or a verified pass—instead of a vague queued-job success. It prevents shipping a path that sounds acceptable in one segment but drops frames at the bridge.
- effort: Medium-high: a relay correlation schema, a Mac diagnostic runner, firmware/bridge counters, and a receipt renderer. No Accessibility grant is needed; shell/AppleScript and existing pipeline routes suffice for orchestration.  ·  risk: Diagnostics could generate audible output, consume radio/battery, or mis-correlate reused packet IDs. Use a unique run nonce, bounded duration, local-only synthetic audio, explicit teardown, and mark incomplete on any missing counter. Recovery is deleting the run receipt and stopping the pipeline; never flash automatically.
- cost: Negligible API cost for local tests; roughly $0.01–$0.05 if a model summarizes the receipt. Firmware flash/storage impact is small if counters are compact, but must be budgeted against 211,608 B application RAM and 1 MB flash.  ·  latency: Adds no production voice latency. Test startup under 2 s and test duration 10–20 s; receipt available within 3 s of teardown.
- security: Synthetic audio avoids microphone leakage. Receipts may reveal Bluetooth device identity and network timing; keep local by default and redact identifiers before relay upload. Require confirmation before pairing changes, firmware writes, or prolonged playback.
- depends on: An authoritative 24 kHz acceptance spec; A diagnostic counter/event schema on pendant, relay, and ESP32 bridge; A local Mac runner using existing run_shell/run_applescript and pipeline routes; Durable receipt storage and a dashboard/voice summary path

### `hardware` — Replace the provisional ESP32 classic-A2DP bridge with a BLE Audio-capable bridge (or a production codec module) whose transport and sink can preserve a 24 kHz mono path, while retaining a compatibility SBC output mode. Keep the pendant's 24 kHz decode as the canonical sample rate and move any unavoidable conversion to one explicitly measured boundary.
- **owner gets:** The current bridge hard-locks classic A2DP to 44.1 kHz stereo, forcing an extra 31,250→44,100 resample after the pendant's 24 kHz decode. A 24 kHz-capable sink would reduce avoidable conversion artifacts and make the owner's request for a true 24 kHz path physically achievable, not just true inside the codec.
- effort: High: select a supported BLE Audio/LC3 chipset and headphones, redesign the bridge firmware and power/audio board, then validate coexistence with the nRF9160 link. Keep the existing ESP32 as a fallback during migration.  ·  risk: BLE Audio interoperability, pairing UX, and battery draw may regress; some headphones will only support SBC. Mitigate with dual-mode fallback, an A/B hardware harness, and the proposed tagged acceptance transaction before changing the daily path.
- cost: Prototype bridge roughly $20–$60 in parts plus new headphones if needed; modest additional power versus the current ESP32 bridge, exact draw requires measurement. No per-run API cost.  ·  latency: Potentially lower buffering than the current SBC/A2DP path, but BLE Audio scheduling may add 10–30 ms; require measured p50/p95 latency in acceptance receipts.
- security: New pairing keys and Bluetooth identifiers must remain local and be resettable. Do not auto-pair or replace the current sink without confirmation.
- depends on: The end-to-end acceptance transaction and per-hop telemetry; A written 24 kHz acceptance criterion; Hardware/audio compatibility study for the chosen BLE Audio sink

### `integration` — Add a provenance-preserving browser-to-reminder handoff transaction: browser extraction must return a cited source (tab/session, URL, timestamp, quote, normalized date and timezone, confidence); the Mac reminder creator must accept that typed payload and return the reminder ID; the relay stores one receipt linking source evidence to the created reminder; the pendant speaks only the minimal result. Reject the handoff when the date is ambiguous or the source tab changed between extraction and creation.
- **owner gets:** The owner gets a reliable reminder from a private page without copying details by hand, while being able to answer “which page and text caused this reminder?” later. Ambiguous dates become a clear stop instead of a silently wrong calendar entry.
- effort: Medium integration work across the existing browser result, reminder, job receipt, and spoken-summary paths; no new model or Accessibility grant is required for the basic version.  ·  risk: A stale page or timezone conversion could create a wrong reminder. Use source hashes, explicit timezone normalization, confidence thresholds, and automatic undo of the just-created reminder if post-verification fails. Do not retain unrelated page content.
- cost: Low API cost, approximately $0.01–$0.04 per handoff for extraction and summary; local browser/Mac operations dominate latency.  ·  latency: One extra verification round adds about 1–3 seconds, keeping total completion under 7 seconds in normal conditions.
- security: Private page evidence stays scoped to the job and expires quickly; receipts retain only the minimal quote, URL, and source hash. No message sending or form submission is permitted by this transaction.
- depends on: A typed browser extraction result with stable citation and source hash; A reminder endpoint accepting normalized timezone and provenance metadata; A receipt schema that links browser evidence to the created Mac object; A spoken-summary renderer that redacts private page text


## What it asked for

_Nothing._
## Its own summary

I found and recorded a genuinely action-specific gap: the system can route audio and report HTTP/job state, but cannot yet execute a bounded synthetic 24 kHz test across pendant → relay → Mac/bridge → sink, correlate per-hop evidence, and fail closed when telemetry is missing. I proposed that acceptance transaction plus a hardware follow-on replacing the ESP32 classic-A2DP 44.1 kHz bottleneck with a 24 kHz-capable BLE Audio bridge. I also told faculty-judgement that this is evidence/verification work, not another generic audio-player proposal.

**Biggest unknown:** The authoritative 24 kHz acceptance criteria and the still-unavailable pendant/bridge diagnostic access remain unresolved. Specifically, I still need the previously requested firmware/build-and-device permission, audio-path probe and operation-proof tools, and owner-approved acceptance policy before this can safely become an executable action rather than a recorded proposal.

