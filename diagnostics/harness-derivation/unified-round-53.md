# Harness derivation — unified — round 53

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Mark that for later.” During a meeting or while I’m browsing, capture the moment and after I’m done give me a sourced follow-up packet: what I meant, the exact app/page context, suggested next actions, reminders, and drafts ready for approval."
- **useful because:** A wearable can catch an intention at the instant it occurs, while the Mac and authenticated browser can recover the surrounding evidence that the pendant cannot see. This turns fleeting spoken intent into an actionable, reviewable record instead of another forgotten voice note.
- **path:** pendant: button or spoken marker starts a short local/audio event and gives immediate LED/haptic-equivalent acknowledgement; relay: timestamps, transcribes, stores an encrypted event and schedules post-session processing; mac-planner/mac-vision: snapshots foreground app, document title/selection and visible window metadata, then creates a local evidence bundle and reminders; browser-extension: captures the active logged-in tab URL/title/semantic excerpt with provenance, never credentials; dashboard/iOS: presents a chronological review card with source snippets, proposed edits and approve/edit controls
- **model tier:** Realtime only for the acknowledgement and marker transcription; a cheaper background text model performs context reconciliation, action extraction and draft generation. Use no model for deterministic timestamps, tab/app metadata, hashes and receipts.
- **latency:** Acknowledge in under 500 ms; capture context within 2 s. Post-session packet may take 10–30 s and can finish while the owner walks away; deliver a short pendant notification plus a dashboard card.
- **cost:** About $0.01–$0.05 per marker depending on audio duration and background model; dominant costs are speech transcription and optional authenticated-page extraction, not metadata capture.
- **security:** The marker may contain meeting-confidential speech and private-page context. Encrypt in transit and at rest, default to a 24-hour raw-audio TTL and retain only transcript/evidence hashes, show exactly which sources were used, redact passwords/tokens, and require confirmation before sending mail, submitting forms, or creating external commitments. A local privacy latch should suppress capture and a visible LED state should confirm recording.
- **missing:** A first-class cross-surface marker event schema with correlation ID and clock synchronization; Mac APIs to snapshot foreground window/document metadata and selected text with explicit privacy filtering; Browser bridge support for a read-only semantic excerpt plus DOM locator/source hash at marker time; Durable post-session worker and review-card/receipt UI; A pendant-local marker acknowledgement and short capture buffer that survives a dropped link

### "“Is it actually done?” After any important request, verify the real-world result across the Mac, my logged-in browser, and the relay—not just whether an automation step returned success—and tell me what is proven, what is only attempted, and what needs me."
- **useful because:** Today a successful-looking automation can do nothing (the live Mac currently reports that GUI actions may report success while not reaching the screen), and a relay receipt only proves delivery. The owner needs one trustworthy answer about the resulting state, with evidence from the surface that owns that state.
- **path:** pendant: owner asks for verification and receives a short confidence-qualified answer; relay: correlates the original intent, action receipts, retries and verification jobs; Mac agent: checks filesystem, app state, reminder/calendar/mail objects and UI reachability; browser bridge: re-reads the authenticated page and compares the intended field/state against the post-action state; dashboard: shows a claim/evidence matrix and offers one safe recovery or confirmation step
- **model tier:** Use deterministic checks and typed receipts first; use a cheap background model only to reconcile conflicting evidence and phrase the explanation. Reserve realtime for the owner's spoken query and final concise response.
- **latency:** Return a preliminary receipt in under 2 seconds and a verified state in under 15 seconds; if a site or app is slow, keep working durably and notify the pendant when verification completes.
- **cost:** Approximately $0.002–$0.03 per verification; most cases are deterministic local/browser reads, with model cost only for ambiguous evidence reconciliation.
- **security:** Verification may read sensitive pages and mail. Reuse the original session authorization, capture minimum snippets rather than full pages, redact tokens and query parameters, retain evidence briefly, and require confirmation for any recovery action that could duplicate a send, purchase, deletion or submission.
- **missing:** A typed intent-to-outcome contract separating attempted, delivered, observed and verified states; Surface-specific postcondition checkers for Mac objects and authenticated browser fields; A browser read-after-write API with stable locators and before/after evidence; A Mac input-reachability gate that prevents false GUI success receipts; A durable verifier worker and owner-facing confidence/evidence UI


## Changes it proposed to its own stack

### `integration` — Add a unified Context Event Envelope and clock-synchronization path shared by pendant, relay, Mac agent and browser bridge. Each event gets a UUID, monotonic device tick, relay and Mac wall-clock observations, source surface, sensitivity class, retention deadline, and provenance references (active app/window, tab/session, transcript segment). On reconnect, compute bounded clock offset/drift and preserve the original device ordering; expose an append-only event timeline and deterministic receipt IDs to jobs, memory and the dashboard.
- **owner gets:** When the owner says “mark that,” the resulting note will point to the right second, app and private browser page even if the network drops or the Mac clock differs. It also lets follow-up packets explain exactly where each recommendation came from instead of producing an untrustworthy generic summary.
- effort: Medium: define the schema and D1/R2 indexes, add a lightweight NTP-like handshake and reconnect merge, instrument Mac/browser metadata capture, and add timeline rendering and retention tests.  ·  risk: Clock bugs could attach evidence to the wrong moment; mitigate with uncertainty intervals, explicit “time alignment unavailable” labels, monotonic ordering, and never silently merging events outside a confidence bound. If relay storage is unavailable, keep a bounded local queue and deliver a receipt when reconnected.
- cost: Negligible per-event storage and network overhead (roughly 0.5–2 KB metadata); no additional model calls. Raw audio remains governed by the existing short-retention policy.  ·  latency: One small handshake at connection/reconnect and <10 ms metadata overhead per event; no effect on normal audio streaming.
- security: Event envelopes must carry sensitivity and retention policy end-to-end; redact window text and URL query strings by default, encrypt stored payloads, and make evidence access auditable. Never place secrets in correlation IDs or logs.
- depends on: A pendant-local marker/capture buffer; Mac foreground-context snapshot API; Browser semantic excerpt API; Durable event timeline storage and review UI

### `integration` — Introduce an outcome-verification protocol for every cross-surface job. Before execution, compile a typed postcondition (for example, reminder exists with title/time, browser field equals value, file hash changed, or message remains draft). After execution, independently query the owning surface, attach before/after evidence and freshness, and classify the result as planned, attempted, delivered, observed, verified, contradicted, or unknown. Do not allow a transport/action receipt to be presented as completion.
- **owner gets:** The pendant can finally say “it is done” only when the thing itself confirms it, rather than making the owner inspect apps or trust a misleading success sound. Failures such as missing Accessibility become honest unknowns instead of silent false positives.
- effort: Medium-high: define postcondition schemas and adapters for Mac/browser/relay, add independent readback workers, migrate existing job receipts, and expose evidence and confidence in the shared dashboard.  ·  risk: A stale or partial readback could misclassify state; mitigate with freshness limits, idempotent checks, contradiction states, retries, and explicit unknown rather than guessing. Never auto-retry an irreversible action solely because verification is unknown.
- cost: Small metadata and readback traffic increase; most checks require no model call. Ambiguous reconciliation may add a low-cost text-model invocation.  ·  latency: Adds one readback round trip (typically 1–15 seconds), while allowing an immediate provisional acknowledgement.
- security: Readbacks inherit the originating session's authorization and must log only redacted evidence hashes/snippets. Verification artifacts need short retention and audit access controls.
- depends on: Typed intent/postcondition compiler; Mac and browser read-after-write adapters; Durable verifier worker; Reliable input-reachability reporting


## What it asked for

### `s9-pxr6` (skill) — moment_marker_buffer
- does: On a deliberate double-press (or a spoken marker command already detected by the active session), latch a marker event, record a bounded 2-second pre-roll and 4-second post-roll from the microphone when privacy mode permits, flash a distinct acknowledgement pattern, and queue the event with a monotonic tick, sequence number and link status. If the link is down, retain the compact event/audio fragment until delivery or expiry.
- must be on-device because: The pendant is the only surface present at the instant the owner notices something, and only it can capture pre-roll audio and acknowledge success without a round trip. It must also work during a dropped cellular link.
- trigger: Button double-press, with spoken marker as a secondary trigger from the active conversation; cancel by holding the button for 1 second before upload.
- storage: Ring buffer in RAM for up to 6 seconds of PCM; persist at most 2–3 compressed short clips plus metadata in a small flash spool, deleting after delivery receipt or 24 hours. Never persist while the local privacy latch is active.
- RAM budget: Use the existing audio ring buffer with a bounded extra 12–24 kB; metadata under 1 kB. Avoid a second Opus encoder and reuse the current audio task; target <30 kB peak additional RAM and no additional long-lived thread.

## Its own summary

Discovered the live stack: Mac bridge is online but Accessibility and Screen Recording are still unavailable, so GUI receipts are currently untrustworthy; browser extension is offline with three pending commands; pendant audio is still the prototype 15.625 kHz capture / 24 kHz playback path and Opus consumes about 87% of one core when duplex. I proposed a new cross-surface capability, “Mark that for later,” plus the Context Event Envelope/clock-sync integration and queued a pendant-local moment_marker_buffer skill. The capability captures a fleeting marker on the wearable, aligns it to Mac/app and authenticated-browser evidence, then produces a sourced review packet and drafts without sending anything.

**Biggest unknown:** Whether the product should permit any meeting audio pre-roll at all, and the exact raw-audio retention/privacy policy. Implementation also needs the missing cross-surface event API, read-only Mac/browser context snapshots, durable worker/review UI, and a real pendant-local queue; current live permissions/browser status must be rechecked after those grants are applied.

