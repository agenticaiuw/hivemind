# Harness derivation — mac-planner — round 223

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **bridge-audio** — ESP32 HUZZAH32 bridge is prototype, A2DP SOURCE SBC-only at fixed 44.1 kHz stereo, with tight RAM and a known 44 kB buffer starvation failure; pendant I2C/SPI are free, and microSD is failure-buffer only.
  - evidence: get_hardware_spec bridge, io, storage in round 223

## Capabilities it proposed

### ""Check whether my pendant and audio bridge are healthy before I leave, and tell me only if something changed.""
- **useful because:** The hardware is physically connected to this Mac today but LTE is unregistered; a bench check can catch silent codec, serial, or bridge regressions before the owner relies on the wearable. It turns the accepted fixture into a user-visible health signal rather than a developer-only test.
- **path:** pendant → mac → relay → dashboard
- **model tier:** background for scheduled comparison; realtime only when the owner asks for an explanation
- **latency:** 30-90 seconds for a deliberate USB bench run; under 2 seconds to report the last signed result
- **cost:** <$0.01 per scheduled run; mostly local serial/fixture execution, with a small relay comparison call
- **security:** Never captures microphone content: use the accepted synthetic diagnostic fixture only. USB logs stay on the Mac except compact counters and pass/fail hashes; alert payloads should redact paths and serial identifiers.
- **missing:** A mac-terminal bounded serial executor that can arm audio_path_diagnostic_fixture over the existing USB ports and return exit status plus structured counters; A relay health-history route with baseline comparison and change-only alerting; A user-facing routine that runs when the pendant is connected, not on an LTE assumption

### ""Turn this research moment into a packet I can use later: include what I said, the page I was looking at, the source URL, and a ready-to-edit note on my Mac.""
- **useful because:** A short pendant bookmark currently records a moment, but the owner still has to reconstruct context. Combining the worn button event with the authenticated browser tab and an atomic Mac artifact preserves the exact evidence trail while the page and thought are still available.
- **path:** pendant → relay → browser → mac → dashboard
- **model tier:** background synthesis model for transcription and note drafting; realtime only for immediate acknowledgement
- **latency:** Immediate LED/pendant acknowledgement; 5-15 seconds to produce the packet after the link returns
- **cost:** $0.01-$0.05 per packet depending on audio transcription and synthesis; browser and file operations are local
- **security:** The browser URL and page excerpt may contain private data. Require an owner-selected capture mode, redact secrets/form fields, bind the packet to a tab identity, and write via atomic staging. Never upload raw page content beyond the selected excerpt.
- **missing:** A browser command that returns active-tab identity, canonical URL, selected/visible excerpt, and provenance under a lease; A relay join route correlating the queued pendant bookmark ID with the browser observation; A Mac packet writer that uses mac_workbench_transaction and returns a receipt linked to the bookmark

### ""I got interrupted. Reopen exactly the work context I left: the right browser tab, the draft on my Mac, and a one-sentence reminder of what I was trying to do.""
- **useful because:** A durable interruption handoff is more useful than merely reopening an app: it restores the authenticated tab and local draft together, while the pendant supplies the human intent that UI state cannot infer. The owner can resume after a crash, commute, or link drop without searching through tabs and files.
- **path:** pendant → relay → browser → mac
- **model tier:** background model to summarize the handoff; deterministic local actions for reopening and receipt checks
- **latency:** Under 5 seconds to present the capsule; up to 15 seconds if the browser must reacquire a tab lease
- **cost:** <$0.02 per resume; predominantly local browser/Mac work
- **security:** Do not persist page bodies or credentials. Store opaque tab/session IDs, local file paths, hashes, and a short intent summary; require browser identity verification before acting on an authenticated tab.
- **missing:** A cross-surface interruption capsule schema with opaque browser lease, Mac artifact hash, pendant bookmark IDs, and expiry; Browser lease reacquisition that fails closed on tab identity mismatch; A Mac resume executor that verifies hashes before opening and emits one joined receipt

### ""Use my pendant as a local presence key: when I physically press it, carry out the already-prepared high-impact Mac/browser action, but never accept that authorization from the network alone.""
- **useful because:** Today the pendant can converse with the relay and the Mac can act, but there is no cryptographically bound proof that the owner is physically present at the moment a sensitive prepared action runs. This gives the owner a practical way to authorize a purchase, send, or deletion without exposing a broad approval workflow or trusting a stale browser session.
- **path:** pendant → mac → browser → relay → dashboard
- **model tier:** Deterministic nonce verification and action execution; realtime model only explains the pending action in plain language.
- **latency:** Under 2 seconds from button press to authorization result; action completion remains task-dependent.
- **cost:** <$0.01 per authorization; mostly local cryptographic checks and existing action execution.
- **security:** The button press must sign a one-time challenge, be bound to a displayed plan hash and expiry, and be rejected after reconnect or replay. Do not transmit audio or raw credentials. This is opt-in per action class and must coexist with the owner's explicit policy settings.
- **missing:** Firmware challenge-response signing over the connected pendant transport; A relay-issued plan digest and single-use nonce endpoint; Mac/browser executor support for requiring and recording the pendant proof

### ""If a browser task gets stopped by an expired login, tell me on the pendant exactly what needs re-authentication, wait without losing the work, and continue automatically when I finish signing in.""
- **useful because:** Authenticated browser work currently fails as a brittle one-shot interaction: a session expiry can leave a partially completed task with no safe continuation. The owner should not have to repeat the task or explain where it stopped, and the system must never ask the relay to handle the password.
- **path:** browser → relay → pendant → mac
- **model tier:** Deterministic browser state machine and receipt matching; a small background model may summarize the blocked step, but must not see credentials.
- **latency:** Immediate pendant alert when auth is blocked; continuation within 3 seconds after the extension reports a new authenticated session.
- **cost:** <$0.02 per interrupted task; local polling dominates, with occasional short summarization.
- **security:** Pause before any submit or payment step; credentials remain in the browser. Bind continuation to the same origin, tab lease, and pre-auth plan hash. Expire the parked state quickly and redact page contents from relay logs.
- **missing:** Browser harness auth-block detection with origin and step metadata but no secrets; A durable parked-step state machine that can resume idempotently after re-authentication; Pendant alert payload that names the site and safe next step without exposing account data

### ""Before you touch an authenticated site or my files, show me one compact privacy card: what data will leave the Mac, which tab and files will be touched, and what will remain local.""
- **useful because:** The owner has deliberately chosen broad automation, but today the surfaces expose separate plans and receipts rather than one understandable data-boundary view. A single card lets him use powerful automation without guessing whether page text, filenames, audio, or credentials are crossing the relay.
- **path:** relay → browser → mac → pendant → dashboard
- **model tier:** Deterministic inventory and redaction classification; a cheap model can turn the result into a spoken summary.
- **latency:** Under 1 second for a prepared action plan; under 5 seconds when browser and Mac state must be inspected.
- **cost:** <$0.01 per preview; almost entirely local metadata processing.
- **security:** The card itself must contain metadata and redacted categories, never passwords or raw page bodies. It must identify stale observations and refuse to claim a current tab/file state when the lease has changed.
- **missing:** A cross-surface privacy manifest schema covering browser origins, selected fields, Mac paths, and audio/text egress; A relay aggregator that joins mac_action_preflight with browser provenance and current pendant mode; A pendant-sized spoken/card renderer for the manifest


## Changes it proposed to its own stack

### `integration` — Extend the existing workbench transaction receipt into a cross-surface continuity receipt: accept opaque pendant bookmark IDs and browser lease IDs alongside staged Mac files, record pre/post hashes and lease validity, and expose one idempotent resume token. On retry, it must reopen only resources whose hashes and tab identity still match, while marking the rest as stale rather than guessing.
- **owner gets:** After an interruption, the owner gets one trustworthy "resume" action instead of a half-restored draft, wrong authenticated tab, or duplicated file. It makes the wearable's moment and the computer's work refer to the same recoverable event.
- effort: Medium: receipt schema, relay join logic, browser lease verification, and a Mac resume adapter.  ·  risk: A stale or expired browser lease could prevent reopening; recover by presenting the token with a clear stale-resource list and leaving staged files untouched. Never overwrite a changed draft.
- cost: Negligible API cost; a few hundred bytes of receipt metadata and one verification request.  ·  latency: Adds roughly 1-3 seconds for hash and lease checks on resume.
- security: Improves security by using opaque IDs and hashes, but must never serialize cookies, page bodies, or raw audio into the receipt.
- depends on: A browser tab lease/identity primitive from the browser harness; A relay correlation route for pendant bookmark IDs; mac_workbench_transaction receipt schema

### `hardware` — Replace the HUZZAH32 A2DP prototype in the eventual wearable dock with an ESP32-S3-class bridge (at least 512 kB SRAM plus PSRAM) and add a small hardware watchdog/reset supervisor. Keep the pendant's existing full-duplex I2S contract, but move the 44.1 kHz polyphase buffering and Bluetooth stack into the larger memory budget; expose the bridge's reset reason and underrun counters over the existing USB bench link.
- **owner gets:** Bluetooth headphones stop going silent during long replies or reconnections. The owner gets a dependable audio accessory instead of a prototype whose 44 kB buffer can starve the Bluetooth stack and require unplugging it.
- effort: High: new board/layout, A2DP port and timing validation, enclosure/power redesign, and a regression run against the accepted 24 kHz pendant path.  ·  risk: A new Bluetooth stack or clocking path could introduce latency or resampling artifacts. Recover with an A/B dock firmware mode and retain the current bridge as a bench reference until packet-loss, underrun, and end-to-end latency tests pass.
- cost: Roughly +$10-$25 per prototype dock, plus engineering; power likely +50-150 mW under active Bluetooth depending on module.  ·  latency: Potentially reduces underrun-induced stalls; nominal codec latency should remain within the current A2DP buffering envelope.
- security: No new cloud data. A watchdog reset counter may reveal only local reliability metadata; do not expose Bluetooth identifiers in relay reports.
- depends on: A reproducible bridge audio regression fixture; A defined pendant-to-bridge I2S clock and buffer contract; A2DP reconnection test harness


## What it asked for

_Nothing._
## Its own summary

Round 223 produced three cross-node capabilities and two changes. Recorded: (1) owner-facing, change-only pendant/bridge health checks built on the accepted synthetic diagnostic fixture; (2) a research evidence packet joining the pendant bookmark, authenticated browser tab provenance, and an atomic Mac note; (3) interruption recovery that reopens the matching browser tab and Mac draft with an intent sentence; (4) a cross-surface continuity receipt extending workbench transactions; and (5) a hardware proposal replacing the RAM-starved HUZZAH32 bridge with an ESP32-S3-class dock plus watchdog. I also established that the current bridge is SBC-only 44.1 kHz stereo and can starve around a 44 kB buffer.

**Biggest unknown:** The live inventory still lacks proof of a browser tab lease/identity API, a relay join route for pendant bookmark IDs, and a bounded USB serial fixture runner with structured exit status. Those are the concrete blockers I still need; the existing Mac workbench transaction is useful for atomic files but does not itself pause/resume browser work.

