# Harness derivation — faculty-perception — round 225

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac reachability** — At 2026-08-09T00:48Z, the live Mac agent reports Accessibility and Screen Recording trusted, all required permissions ready, browser extension online with zero pending commands; relay reachable and Mac bridge online. This is current machine state, not pendant state.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) resolved/invoked GET /ops/snapshot HTTP 200; embedded status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, relay.reachable=true.

## Capabilities it proposed

### "Before you tell me something is done, prove it: what exactly happened, what evidence supports it, and what is still unknown?"
- **useful because:** This would be the system's most valuable trust boundary. It would stop a Mac-side completion, relay socket write, or browser command acceptance from being reported as owner-visible success. Each claim would carry observed timestamps, source, freshness, and an explicit unknown instead of a falsely confident sentence.
- **path:** pendant → relay → mac-planner → browser-extension → unified → faculty-perception
- **model tier:** background for assembling evidence; realtime only to phrase the final one-sentence answer
- **latency:** 2-5 seconds for a normal request; return partial evidence after 1 second rather than waiting on an offline surface
- **cost:** ~$0.01-$0.04 per verdict; dominated by model synthesis, not reads
- **security:** Do not expose page contents, secrets, or full command lines in the evidence graph. Redact sensitive browser claims and require confirmation before treating an action as externally completed. Offline pendant evidence must be labelled device-reported and bounded by its last-seen time.
- **missing:** A claim/evidence graph with stable claim IDs and observed-vs-inferred-vs-unknown status; A device-originated playback event (the accepted audio_delivery_ack_queue is the right firmware direction); One authenticated aggregate reader that can join relay, Mac, browser, pipeline, and permission evidence without truncating away the decisive record

### "Is the time and timezone assumption safe for this reminder, routine, or message?"
- **useful because:** A machine-written America/Chicago preference is currently pinned at 0.99 confidence while the Mac's authoritative zone is America/New_York. This capability would catch that class of silent temporal error before a routine fires, show the provenance and scope (Mac-resolved versus owner's physical location), and refuse to guess for the pendant's zoneless clock.
- **path:** mac-planner → relay → pendant → unified → faculty-perception → faculty-judgement
- **model tier:** background rule engine with a cheap model only for explaining conflicts; no realtime model needed
- **latency:** Under 300 ms for local-zone validation; under 2 seconds when comparing relay schedule and device clock metadata
- **cost:** <$0.005 per check; mostly local reads and deterministic comparison
- **security:** Timezone and location are sensitive. Return only zone IDs and provenance, never location inference. Do not silently rewrite the owner's pinned fact; offer a correction and require owner confirmation. A pendant without NITZ/GNSS must remain null, not inherit the Mac zone.
- **missing:** A typed temporal provenance contract carrying zone, authority, and scope through Mac-to-relay routine creation; Relay scheduler rejection when a routine has unresolved or conflicting zone provenance; Pendant protocol fields for clock provenance and explicit unknown-zone state

### "After you changed something on this website, show me exactly what changed—and tell me if it was only a visual confirmation or a real server-side change."
- **useful because:** Browser success is currently inferred from a click or returned page. This would take a bounded before/after witness around one browser mutation, compare URL, title, relevant text and visible controls, detect login/error interstitials, and classify the result as confirmed change, unchanged, or unobservable. It gives the owner a useful answer without storing the whole page or pretending a button click proves persistence.
- **path:** browser-extension → mac-vision → mac-planner → relay → unified → faculty-perception
- **model tier:** deterministic hashes/diff first; cheap background model only to summarize a small redacted diff
- **latency:** 1-3 seconds after the mutation; never block the click itself longer than 500 ms
- **cost:** <$0.01 per witness; browser snapshots and local hashing dominate, with model use optional
- **security:** Never capture passwords, payment fields, or unrestricted page bodies. Redact secret locators, store only bounded hashes/snippets, and make destructive mutations confirmation-gated. A changed DOM is not proof of server persistence; require a post-navigation or reload witness where safe.
- **missing:** A browser transaction wrapper that atomically records pre-action and post-action observations; A stable redacted content hash and server-ack signal for sites that expose neither URL nor receipt; A mounted browser-provenance route linking commandId, ledger step, capsule, and outcome

### "Keep this private: understand what I say, but do not send my words or the resulting note to the relay, browser, or cloud."
- **useful because:** Today the pendant, Mac agent, browser session, and relay have no owner-controlled, end-to-end local-only mode. This would let the owner use the system for sensitive health, legal, financial, or relationship notes without guessing which surface retained the audio or transcript. The final local result could still be filed into an explicitly chosen Mac app, while the cloud receives only an opaque success/failure signal—or nothing at all.
- **path:** pendant → mac-planner → mac-terminal → browser-extension → relay → unified
- **model tier:** On-device keyword/gesture gate first; local Mac model for transcription and classification; no realtime cloud model on private turns
- **latency:** Button/phrase privacy mode acknowledgement under 150 ms; local transcript within 3 seconds for a short utterance
- **cost:** Near-zero API cost in private mode; local CPU and encrypted local storage dominate
- **security:** The privacy state must be visible and fail-closed: if the Mac is unavailable, do not upload or silently fall back to relay. Encrypt local audio/transcript, exclude it from logs, receipts, memory projections, browser provenance, and crash reports, and require confirmation before filing into a cloud-synced app.
- **missing:** A signed privacy-mode state shared by pendant, Mac, and relay with fail-closed expiry; A local-only transcription and filing path that does not invoke cloud tools or memory projection; Redaction/enforcement middleware covering audio, pipeline events, job receipts, browser claims, and relay logs

### "Fill out this website for me, but never show the model or relay my passwords, one-time codes, payment numbers, or private messages."
- **useful because:** A logged-in browser is the one surface with reach the Mac and relay do not have, yet current browser automation treats page text and fields as broadly observable. This capability would let the model reason about a form using opaque field handles and redacted values while the extension performs sensitive insertion locally, then reports only constrained validation (for example, 'format accepted') and a redacted outcome.
- **path:** browser-extension → mac-vision → mac-planner → relay → pendant → faculty-perception
- **model tier:** Deterministic local field classifier and policy engine; background model may plan around opaque handles; never send secret field values to realtime or relay
- **latency:** Under 300 ms to classify fields; under 2 seconds for a form step and local validation
- **cost:** <$0.005 per form step; local DOM inspection and policy checks dominate
- **security:** Treat autofill, OTP, password, payment, and private-message fields as secret by default. Block screenshots/OCR and browser snapshot serialization over those regions. Require owner confirmation for sends, purchases, or account changes, and maintain a local audit of field classes without values.
- **missing:** Extension-side sensitive-field isolation for snapshots, screenshots, OCR, and action receipts; Opaque secret handles with one-use, origin-bound insertion and expiry; A relay policy that rejects secret values even if a compromised client attempts to send them

### "When other people are speaking, protect them: do not upload or retain a conversation unless I explicitly mark that everyone consented."
- **useful because:** The pendant is physically present in conversations where the owner may forget that an always-on microphone is connected. Today there is no reliable boundary between the owner's command and a third party's speech, no consent state, and no cross-surface guarantee that discarded audio cannot become a transcript, browser claim, relay job, or memory fact. This would make the device usable in workplaces, clinics, and homes without turning bystanders into unknowing data sources.
- **path:** pendant → mac-planner → relay → browser-extension → unified → faculty-perception
- **model tier:** On-device VAD and short-lived speaker-change detector; local Mac classifier for consent phrase/gesture; cloud model unavailable until an explicit consent lease exists
- **latency:** Mute or quarantine within one audio frame; consent-state propagation under 500 ms; no cloud upload before the lease is confirmed
- **cost:** <$0.01 per session; local audio buffering and optional speaker-change inference dominate
- **security:** Fail closed on uncertainty, never claim to identify people by voice, and keep quarantined PCM in volatile memory only. Consent must be time-bounded, visible on the pendant, revocable, and scoped to the current conversation; scrub relay buffers, Mac logs, browser evidence, and crash dumps on revocation.
- **missing:** Firmware-side consent lease and hard mute/quarantine path before uplink encoding; A local, auditable consent state propagated to relay and browser with monotonic sequence numbers; Deletion guarantees for in-flight audio and derived transcripts across relay D1/R2, Mac stores, and browser provenance


## What it asked for

_Nothing._
## Its own summary

Fresh discovery established a materially changed live state: the Mac agent now reports Accessibility and Screen Recording granted, all required permissions ready, Safari/browser bridge online with zero pending commands, and the relay/Mac bridge reachable. There is still no registered nRF9160 pendant, so pipeline/audio history cannot be treated as current wearable health. I recorded this fact and proposed three owner-facing capabilities: (1) prove-before-claim verdicts with observed/inferred/unknown evidence, (2) timezone and temporal-provenance safety checks that catch the pinned machine-written America/Chicago fact and preserve the pendant's unknown zone, and (3) browser before/after witnesses that distinguish a real server-side change from a click or visual confirmation. I also told faculty-judgement and unified about the live state.

**Biggest unknown:** The decisive missing reality remains pendant-side: whether any physical nRF9160 can currently connect, report its health, and emit playback/clock evidence. Until it registers, I need a real device heartbeat and device-originated playback/clock events; relay acceptance, Mac completion, and recorded pipeline traces cannot establish that the owner heard anything.

