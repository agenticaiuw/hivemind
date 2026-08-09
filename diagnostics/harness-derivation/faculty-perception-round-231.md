# Harness derivation — faculty-perception — round 231

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac permissions and browser continuity** — At 2026-08-09T01:07Z the Mac local agent reports Accessibility and Screen Recording granted, all listed automation grants granted, browser extension online with Safari on doordash.com (5 tabs), relay reachable with D1 store and Mac bridge online. Pipeline shows a held response with 75,350 PCM bytes and heard=unknown because no device_playback event.
  - evidence: GET /ops/status and GET /pipeline returned HTTP 200; /ops/status permissions.ready=true and browser.online=true; /pipeline delivery explicitly says state=held_by_relay, awaitsDevice=true, provesPlayback=false, heard=unknown.

## Capabilities it proposed

### "When you answer something using my Mac or browser, show me exactly what was observed, when, and what is still only an inference."
- **useful because:** The system currently can say a Mac job completed or relay accepted audio while the actual source observation and owner-facing certainty remain scattered. This gives one inspectable chain joining the browser tab, Mac action, relay job, pipeline run, and (when present) device state, so the owner can distinguish observed facts from model claims without trusting a fluent summary.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → dashboard
- **model tier:** Use deterministic joins and hashes on the Mac/relay; use a cheap background model only to compress the already-grounded chain into one sentence. Reserve realtime for the owner's follow-up question.
- **latency:** Record joins inline under 150 ms; dashboard timeline under 500 ms; no extra model call for the raw evidence view.
- **cost:** Usually <$0.001 beyond existing calls; storage and hashing dominate, not inference.
- **security:** Redact secrets before persistence, preserve existing capsule/provenance sensitivity labels, and never expose raw browser text or screenshots by default. Require confirmation before an evidence view reveals a secret or a destructive action's before/after values.
- **missing:** A relay-to-Mac provenance transport that returns a stable read identifier and content hash for relay browser reads; Mount browserProvenance routes and add one durable join record per relay/browser observation; A read-only evidence-timeline endpoint/UI that merges capsule, provenance, action ledger, job receipt, pipeline, and device records

### "Before you use a remembered preference, tell me if a live device or app contradicts it, and stop the stale value from steering your answer."
- **useful because:** A machine-derived America/Chicago preference is currently pinned at confidence 0.99 and injected into every projection even though the Mac's authoritative zone is America/New_York. The same failure can affect browser account state, permissions, and device presence. A contradiction gate prevents a remembered value from silently becoming an action or a wrong time.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → dashboard
- **model tier:** Deterministic field comparison and provenance ranking first; a cheap background model only explains genuinely ambiguous conflicts. No realtime model call for detection.
- **latency:** Under 100 ms for known fields; under 1 s when querying live Mac/browser state.
- **cost:** <$0.001 per check when cached; dominated by optional live browser/Mac probes, not tokens.
- **security:** Do not copy sensitive browser values into memory. Keep conflict records to field names, source origins, hashes, timestamps, and a redacted explanation. Any automatic suppression must be reversible and must not delete owner-authored facts.
- **missing:** A typed contradiction record with source origin, authority scope, freshness, and resolution state; A projection policy that quarantines machine-origin preferences instead of ranking them above live authoritative state; Live adapters for selected browser/account and pendant fields, with explicit unknown rather than guessed values

### "Is the thing I just asked you actually reachable right now, and if not, where will the answer appear instead? Never make me guess whether it is going to my ear, my Mac, or nowhere."
- **useful because:** Today the relay can hold 75,350 bytes while the pipeline truthfully says awaitsDevice=true and heard=unknown; the owner has no concise preflight that distinguishes a live Mac bridge, a live browser, a registered pendant, and relay-held audio. This capability makes absence a first-class result and chooses a visible fallback rather than implying delivery.
- **path:** faculty-perception → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic liveness/freshness classifier using device registry, bridge heartbeat, browser presence, pipeline delivery state, and offline beacon. A cheap model may phrase the result; realtime is not needed.
- **latency:** Preflight under 250 ms from cached state; refresh relay/Mac status within 2 s when stale. Fallback selection must be immediate and non-generative.
- **cost:** <$0.001 per check; no model cost when state is fresh. Dashboard notification/audio fallback costs only existing TTS/action calls.
- **security:** Do not claim a pendant is online from a stale registry row or a relay socket write. Mark every result with source and age; require confirmation before moving a private answer to a browser-visible or Mac-visible surface.
- **missing:** A single presence contract with per-surface freshness and explicit unknown/held/offline states; A Mac fallback renderer that exposes the answer without confusing it with pendant playback; Firmware beacon and relay integration for the accepted offline-reality-beacon frame when a pendant exists; A policy engine that selects or asks for fallback based on answer sensitivity

### "What did you intend to do for me but never actually did? Show me the missed, skipped, blocked, and expired steps—not just completed jobs."
- **useful because:** A completed relay or Mac job is visible, but an omitted action can disappear between planning, permission, browser delivery, and device output. The owner needs negative-space truth: promises that were never attempted, actions blocked by approval, commands abandoned after a timeout, and steps superseded by a later plan.
- **path:** relay-realtime → mac-planner → browser-extension → faculty-judgement → faculty-action → faculty-perception → dashboard
- **model tier:** Deterministic reconciliation of planned steps, permission decisions, command receipts, browser acknowledgements, and expiry timestamps; use a cheap background model only to summarize clusters of omissions.
- **latency:** Record omission transitions inline under 100 ms; produce an owner-facing audit in under 1 s.
- **cost:** Under $0.001 per audit when records are local; storage and reconciliation dominate.
- **security:** Do not retain sensitive command arguments merely to prove omission. Store step hashes, redacted intent labels, reason codes, and links to existing receipts. Never infer that an unobserved step succeeded.
- **missing:** A durable intent-step identifier carried from relay planning through Mac/browser execution; An explicit terminal omission state machine: not_started, blocked, expired, superseded, abandoned; A reconciliation endpoint that compares intended steps with execution and delivery records; Dashboard and spoken summaries that distinguish omission from failure

### "Before acting, prove that every surface is the account, tab, file, and device I meant—not merely that it is reachable—and stop if the identity changes mid-task."
- **useful because:** A live browser extension, Mac bridge, and relay do not establish that the current Safari tab is the intended account or that a reconnect did not switch tabs, windows, profiles, or devices. This prevents the most dangerous class of “successful” automation: a correct action applied to the wrong identity.
- **path:** browser-extension → mac-vision → mac-planner → relay-realtime → faculty-perception → faculty-judgement → faculty-action
- **model tier:** Deterministic identity attestations and change detection first: browser profile/session pseudonym, tab/window ID, origin, Mac user/workspace, relay job binding, and pendant session ID. Use a background model only to resolve an explicitly ambiguous user reference.
- **latency:** Initial binding under 300 ms; re-check before each irreversible step under 100 ms; abort immediately on identity drift.
- **cost:** Under $0.001 per step; hashes and local metadata dominate, with no model call in the normal path.
- **security:** Use HMAC pseudonyms rather than cookies, account names, or tokens. Never persist credentials or page secrets. Require confirmation when identity cannot be proven, and make the stop safe and visible rather than silently retrying another tab.
- **missing:** A cross-surface identity-attestation schema with freshness and confidence; Browser extension support for profile/container/account pseudonyms and tab binding; Mac-side bindings for workspace, user session, and focused application; Relay and pendant session IDs carried through every job and reconnect; A hard precondition in action execution that rejects identity drift

### "Give me a genuinely private mode: keep my voice, transcript, answer, and playback on my Mac and pendant, with the relay and browser excluded—and prove afterward that nothing crossed that boundary."
- **useful because:** The current voice path can upload audio to the relay and invoke browser/Mac surfaces. For passwords, health, finances, or private conversations, the owner needs a mode whose privacy boundary is enforced technically, not by trusting a prompt or model instruction.
- **path:** pendant → mac-planner → mac-terminal → relay-realtime → browser-extension → dashboard
- **model tier:** Run local speech recognition, local planning, and local TTS where possible; use no realtime relay model in private mode. A small local classifier may detect unsupported requests, but must fail closed rather than route to cloud.
- **latency:** Under 1.5 s to first local response on the Mac; pendant playback may use the existing 24 kHz path. Mode switch must be acknowledged locally before capture begins.
- **cost:** No per-turn cloud inference cost in private mode; local CPU/battery cost and engineering for local STT/planning dominate.
- **security:** Private mode must disable relay upload, browser actions, cloud logs, and cloud announcements at the transport layer. Display a persistent local-mode indicator, encrypt local transcripts, and make unsupported cloud-only tasks return a clear refusal rather than silently downgrade privacy.
- **missing:** A firmware-to-Mac local audio/session transport that works without relay registration; A local STT and planner/TTS stack with capability declarations; A hard egress firewall/policy layer covering audio, prompts, browser payloads, and telemetry; A cryptographic local-mode receipt proving which network transports were disabled and re-enabled


## What it asked for

_Nothing._
