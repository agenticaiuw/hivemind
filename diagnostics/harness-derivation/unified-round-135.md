# Harness derivation — unified — round 135

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “what am I looking at?”, use the Mac’s active window and my currently open Safari page to answer aloud, with the exact page title, relevant quoted evidence, and links; if the page is private, keep its contents on my Mac."
- **useful because:** This is the shortest path from wearable voice to the owner’s actual screen. Today the pendant, Mac agent, and authenticated browser each know only fragments; joining them makes the system useful in the moment rather than requiring the owner to explain a URL or copy text.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Realtime for the spoken question and concise answer; use a cheaper background model only if the page requires long extraction or comparison.
- **latency:** Answer in 3–6 seconds for an ordinary page; stream a one-sentence acknowledgment from the relay while the Mac/browser gather evidence.
- **cost:** Roughly one realtime turn plus a small extraction call; typically $0.01–$0.05, dominated by speech and vision/context tokens. Private page text should not leave the Mac unless the owner explicitly permits it.
- **security:** Only inspect the active tab/window, never all tabs by default. Return URL/title and source snippets, redact passwords and form fields, and require confirmation before any page mutation. If the browser heartbeat or Mac observation is stale, say so instead of guessing.
- **missing:** A typed active-window snapshot route that includes the selected tab and a redacted screenshot or DOM excerpt; A policy-enforced private-page extraction path that can answer locally without uploading page text; Pendant-to-Mac correlation IDs so the spoken request is tied to the exact observation

### "At the end of the day, tell me which commitments I actually made today, where each came from, and what is still unresolved; let me correct any item by voice and create only the reminders I approve."
- **useful because:** A wearable hears promises made away from the keyboard, while the Mac and browser hold the written follow-through. A provenance-backed evening reconciliation would prevent the most expensive personal failure—forgetting an obligation—without silently creating noisy tasks.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → relay-realtime
- **model tier:** Background/slow model for the daily extraction and clustering; realtime only for the owner’s corrections and approval conversation.
- **latency:** Prepare asynchronously before the chosen evening time; spoken summary under 45 seconds, with drill-down on request.
- **cost:** About $0.02–$0.10 per daily run depending on transcript and page volume; most cost is summarizing evidence, not the final voice turn.
- **security:** Treat transcripts, mail, calendar, and private pages as sensitive. Show source and timestamp for every inferred commitment, distinguish explicit promises from guesses, never send messages, and require a separate confirmation per reminder batch. Delete raw audio after extraction according to the owner’s retention setting.
- **missing:** A commitment extractor that consumes the day’s audio/transcript and Mac/browser journals with confidence and source spans; An approval-aware reminder batch endpoint with idempotency and undo; A privacy projection that excludes unrelated conversations and credentials

### "Read the one-time code from the page I’m on and speak it once into my ear, then erase it; never put the code in the transcript, Mac logs, relay logs, or screen."
- **useful because:** The browser can reach authenticated pages and the pendant can deliver privately, but today the owner must expose a code on-screen or dictate it. A deliberate, ephemeral browser-to-ear path is a genuinely new joint surface and is useful for sign-ins while keeping credentials out of normal conversation history.
- **path:** browser-extension → mac-planner → relay-realtime → pendant
- **model tier:** Use deterministic local extraction/validation first; realtime is unnecessary except for a short confirmation. A cheap background model may classify the page region only when selectors fail.
- **latency:** Under 2 seconds after approval, with one spoken confirmation and a single playback; no retries that could repeat the secret.
- **cost:** Near-zero when the page has a known OTP pattern; at most $0.005–$0.02 for fallback extraction. The dominant cost is implementation and security testing, not inference.
- **security:** This must be opt-in per utterance with an unmistakable confirmation gesture. Restrict extraction to a six/eight-digit code in the active tab, validate expiry/length, encrypt end-to-end, mark audio non-recordable, suppress transcription, avoid relay persistence and Mac job receipts, and zero buffers after playback. Never infer passwords, recovery keys, or full card numbers; refuse those categories.
- **missing:** A secret-handling browser command that returns a typed OTP token rather than page text; A no-transcript/no-persistence audio envelope from browser through relay to pendant; An ephemeral playback acknowledgment and zeroization receipt without revealing the secret in logs

### "When you tell me something important or claim you completed an action, let me ask “prove it” and hear a compact evidence chain: what you observed, when, which device or page it came from, what you inferred, and what—if anything—you actually changed."
- **useful because:** The owner currently has to trust a seamless voice assistant across a wearable, Mac, browser, and relay. A spoken, tamper-evident explanation for both answers and actions would make errors discoverable and let the owner safely rely on the system for consequential work. This is not merely an action history: it covers claims, uncertainty, stale observations, and the boundary between observation and inference.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use deterministic event assembly and hashes for the evidence chain; a cheap background model can compress it. Reserve realtime for the owner’s “prove it?” follow-up and spoken rendering.
- **latency:** Normal work is unaffected; a proof response should begin within 2 seconds and expand only when requested.
- **cost:** Usually under $0.01 per proof because it reuses stored events; occasional source retrieval may cost $0.01–$0.05. Storage and signing dominate, not model inference.
- **security:** Evidence must redact secrets, page contents, and unrelated microphone audio. Bind every item to a source, timestamp, freshness/expiry, request ID, and model version; distinguish raw evidence from inference; make deletion propagate to derived proofs. Never claim cryptographic certainty when only a model summary exists.
- **missing:** A cross-surface event ledger that records observations, inferences, decisions, and mutations under one request ID; Signed, typed evidence references from browser and Mac actions, including before/after state and staleness; A proof renderer that can answer aloud without replaying sensitive source data; Retention and redaction rules for evidence chains


## Changes it proposed to its own stack

### `hardware` — Replace the single-button prototype interaction with a wearable input module containing a low-power 6-axis IMU plus a capacitive wear/contact sensor, while retaining the button. Firmware should expose explicit gestures (double-tap to interrupt, long hold to mute locally, remove-from-body to stop capture) with local LED confirmation and signed event timestamps.
- **owner gets:** The current one button means starting, stopping, interrupting, and privacy all compete for one ambiguous gesture. Reliable physical interruption and automatic capture stop are what make an always-worn assistant safe to use in public, especially when the Mac or relay is unreachable.
- effort: Medium hardware spin and firmware work: sensor selection, enclosure redesign, low-power driver, gesture calibration, and event protocol. Prototype first with an I2C IMU and capacitive pad on the currently free I2C bus.  ·  risk: False gestures could cut off speech or leave the owner muted; mitigate with conservative thresholds, LED patterns, a physical button override, and a watchdog default that never transmits after uncertain contact. Validate across clothing and motion.
- cost: Approximately $3–$10 in prototype parts and <$1–3 mA average for IMU/contact sensing depending on duty cycle; negligible API cost.  ·  latency: Local gestures can interrupt/mute in under 100 ms, faster than a relay round trip; sensor polling adds minimal audio scheduling load.
- security: Improves privacy because removal can stop capture locally. Do not upload raw motion/contact data; send only signed state transitions and monotonic timestamps.
- depends on: Define the one-button gesture compatibility contract; Add a local output-mute latch and privacy policy; Test the full-duplex I2S path so gesture handling cannot starve Opus encode/decode

### `integration` — Add a Secret Delivery Envelope spanning browser bridge, relay, and pendant: typed secret kinds (OTP only), active-tab origin binding, one-use nonce, 30-second expiry, encrypted payload, and a non-persistent playback route. The browser must return only the typed secret token to the relay; ordinary page extraction, transcript, journal, job receipts, and /capture must reject and redact this envelope. Pendant playback emits only a success/failure receipt and zeroizes its buffer.
- **owner gets:** It lets the owner complete sign-ins privately from the wearable without codes leaking into conversation transcripts, Mac logs, browser history, or cloud storage. This is a user-visible safety boundary, not a refactor.
- effort: High security-sensitive integration across browser extension, relay, and firmware; implement typed schemas, key exchange, red-team tests, and failure/expiry handling before enabling it.  ·  risk: A bug could leak or replay a login code, or strand the owner mid-login. Default-deny unknown secret types, refuse if tab identity or clock/nonce checks fail, show a clear LED error, and keep ordinary code-copy fallback available.
- cost: Negligible API cost; small firmware RAM buffers (under 2 kB) and implementation/security-review cost.  ·  latency: Adds one local validation and encryption hop; target under 500 ms before playback, with no model call in the normal path.
- security: Strongly positive if implemented as a separate non-persistent data plane. Requires key rotation, origin binding, replay protection, and explicit owner approval for every delivery.
- depends on: Browser bridge typed secret extraction; Relay non-persistent audio envelope; Pendant local mute/privacy latch and zeroization primitive; A separate redacted receipt schema

### `integration` — Create a cross-surface Evidence Ledger with append-only, signed envelopes for observation, inference, decision, mutation, and owner approval. Every envelope carries requestId, surface, source locator, monotonic and wall-clock time, freshness/expiry, sensitivity class, model/version, and parent hash. Browser and Mac agents emit typed before/after facts; relay assembles a Merkle-linked chain and exposes a redacted spoken proof view. Deleting a source tombstones all derived evidence.
- **owner gets:** When the assistant is wrong, the owner can identify exactly whether the page was stale, the Mac misreported an action, or the model over-inferred—rather than receiving an unrepairable confident apology. It also makes long-running delegated work auditable across devices.
- effort: Large protocol and storage change across relay, Mac, browser extension, and pendant-facing voice responses; requires schema migration, signing-key management, redaction tests, and fault-injection for dropped or reordered events.  ·  risk: Ledger gaps or clock errors could create false confidence; mitigate with explicit incomplete-chain status, monotonic sequence numbers per surface, and a rule that missing evidence yields “unknown,” never success. Compromised logs must not expose private page data.
- cost: Low inference/API cost; modest durable storage and cryptographic CPU cost on Mac/relay. Pendant receives only a short proof summary, not the ledger.  ·  latency: No added latency on the normal action path if events are buffered locally; proof requests add retrieval/signature verification, target under 2 seconds.
- security: Improves accountability but creates a sensitive metadata store. Encrypt at rest, minimize source snippets, rotate signing keys, enforce per-surface retention, and make proof access require the same owner authorization as the underlying data.
- depends on: Typed browser and Mac observation/action result schemas; A durable request ID propagated through relay, job runner, browser, and pendant audio; Redaction-aware retention and deletion propagation; Owner-visible incomplete-proof and correction semantics


## What it asked for

_Nothing._
## Its own summary

This round produced four recorded proposals: active-screen spoken answers with private-page locality; an evidence-backed daily commitment reconciliation; a production wearable input module for local interruption/privacy; and a one-use browser-to-pendant OTP delivery path, plus its Secret Delivery Envelope integration. The strongest new safety/usefulness seam is the last one: authenticated browser reach plus private wearable output without putting secrets in transcripts or logs. Discovery confirms the pendant is one-button/one-LED with full-duplex I2S, while the ESP32 bridge is SBC/A2DP constrained; the hardware is physically USB-connected today but not LTE-registered.

**Biggest unknown:** The pending grants/requests still leave the exact USB fallback audio-session protocol, local privacy-latch semantics, queue-resume policy, and end-to-end audio acceptance criteria unspecified. I did not re-request them because they are already queued. macOS Accessibility/Screen Recording also remains owner-granted and cannot be obtained from this harness; current designs should stay on the already-granted AppleScript/browser surfaces until that changes.

