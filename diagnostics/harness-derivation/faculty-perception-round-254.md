# Harness derivation — faculty-perception — round 254

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **macOS input and screen observability** — As of 2026-08-09T03:51Z, GET /ops/status reports Accessibility trusted=true, Screen Recording granted=true, all listed Automation permissions granted, requiredMissing=[] and permissions.ready=true. Browser extension is online with Safari tab 85 at https://www.youtube.com, lastSeenAt 2026-08-09T03:51:41Z.
  - evidence: Authenticated GET /ops/status returned HTTP 200 with the complete permissions and browser status payload.
- **pendant registry visibility** — The Mac agent does not expose GET /v1/devices/status (HTTP 404). The current device discovery layer lists nrf9160-pendant as nrf_pendant, offline, last seen 2026-08-09T02:56:31Z, but this cannot establish current physical connectivity or playback.
  - evidence: discover(devices) returned the nrf9160-pendant row; probe_http GET /v1/devices/status on localhost:8000 returned No such route.

## Capabilities it proposed

### "“What am I looking at right now, and can you point to the exact thing I mean?”"
- **useful because:** The owner can ask from the pendant without describing the screen. The Mac vision loop captures the active window and browser tab, the browser extension supplies session-grounded DOM when available, and the relay returns a timestamped answer that clearly distinguishes visible pixels from page text. This turns the system from an executor into an always-available visual witness.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use gpt-4.1-mini for screenshot/region perception, gpt-5.6-luna only to resolve the owner's referring expression; use realtime solely for the short spoken exchange.
- **latency:** 2–4 seconds for a first answer; under 1 second when the active-tab snapshot is fresh (less than 5 seconds old).
- **cost:** About $0.01–$0.04 per query, dominated by one screenshot/vision call; DOM-only answers can be nearly free.
- **security:** Screenshots and page text leave the Mac only if sent to the relay/model; redact passwords, payment fields, and private browser regions locally. Require explicit confirmation before clicking or typing. Record a short-lived hash and source metadata, not raw screenshots, by default.
- **missing:** A mounted active-window capture route that returns screenshot plus window identity and capture timestamp; A relay-to-Mac visual witness contract carrying a stable observation ID and freshness bound; Local redaction of sensitive UI regions before any relay upload; A pendant voice intent that can refer to the observation ID across one turn

### "“Resume the thing I started before I lost connection—tell me exactly what happened and continue only the unfinished step.”"
- **useful because:** Today a Mac job can be marked complete while browser delivery or a later step is still pending. This capability reconstructs one interrupted workflow from the Mac job/receipt ledger, browser command/result state, relay job state, and the pendant's reconnect beacon, then offers a single idempotent continuation instead of making the owner repeat themselves or duplicating an action.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use a cheap background/state-reconciliation model to assemble the checkpoint; use gpt-5.6-luna only when the checkpoint is ambiguous; realtime only to converse and read the concise result.
- **latency:** Under 3 seconds to report the checkpoint; continuation starts only after explicit owner confirmation and should expose each step as it runs.
- **cost:** $0.005–$0.03 per recovery, mostly context assembly; no model call needed for an unambiguous receipt lookup.
- **security:** Never infer that a Mac-side completed job means the owner saw or submitted the browser result. Show the last durable step, its timestamp, and an idempotency key. Require confirmation before any non-reversible continuation; redact receipt payloads containing secrets.
- **missing:** A cross-surface checkpoint schema joining relay job ID, Mac job ID, browser command ID, pipeline ID, and pendant session/connection epoch; A recovery planner that understands resumable versus non-resumable ledger steps and refuses to replay non-idempotent actions; A durable owner-visible continuation record with compare-and-set claim semantics

### "“Keep watching this page and tell me on the pendant only when the important part changes—not every ad or timestamp.”"
- **useful because:** The browser session can observe a logged-in page while the owner is away; the Mac can retain a redacted baseline and classify semantic changes; the relay can queue a concise announcement; and the pendant can speak it when it reconnects. This is a useful delegation no single node can provide: the browser has access, the Mac can compare safely, and the pendant is the notification channel.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic DOM extraction plus hashes/diff first; use a cheap background model only to classify whether a changed region is material. Realtime is unnecessary except to accept the initial voice request and speak the alert.
- **latency:** Poll at a user-selected interval (5–60 minutes); alert within one poll cycle. Initial setup under 5 seconds.
- **cost:** Near-zero for hash/diff; roughly $0.001–$0.01 per meaningful change classification. Browser polling and model calls dominate, not speech.
- **security:** The browser session and page contents are sensitive. Store only a redacted capsule, source URL, selector, content hash, and change summary; never relay raw page text by default. Require explicit opt-in, visible dashboard stop control, expiry, and a confirmation before monitoring pages with financial/health/private content.
- **missing:** A durable watch record joining browser session/tab, selector, baseline evidence capsule, polling schedule, and relay announcement target; A semantic-diff worker that ignores volatile regions and proves the changed region against the baseline hash; A relay announcement path that carries the watch ID and queues exactly-once, reconnect-safe alerts; A mounted browser-provenance route so the owner can inspect or revoke what was watched

### "“Only answer sensitive questions or expose private browser content when my pendant proves it is physically with me; otherwise refuse and tell me why.”"
- **useful because:** A stolen or unattended Mac session should not be enough to reveal private mail, health, financial, or browser-session data. The pendant can provide a short-lived local-presence proof, the relay can enforce it before routing a request, and the Mac/browser can apply a second classification policy. This gives the owner a privacy boundary no single node can provide.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic policy and cryptographic verification; use a cheap classifier only to label content sensitivity. Do not spend the realtime model on authorization decisions.
- **latency:** Under 300 ms for presence verification; under 2 seconds including content classification.
- **cost:** Negligible per request after implementation; cryptographic verification dominates, with occasional low-cost classification.
- **security:** The proof must not reveal location or become a reusable tracker. Use rotating nonces, device-bound keys, replay protection, and fail-closed expiry. Private content must remain on the Mac/browser unless the policy explicitly permits relay processing. The owner needs a visible emergency revoke control.
- **missing:** A pendant-originated rotating presence-attestation protocol with replay protection; Relay middleware that enforces an attestation freshness policy before sensitive tool calls; Mac/browser content sensitivity labels and a local redaction gate; A dashboard showing active attestations, expiry, and revocation state

### "“If I say stop, make every body of this system stop acting immediately—even if the Mac, browser, relay, or pendant is offline—and show me what was prevented.”"
- **useful because:** A single physical emergency gesture should halt queued Mac jobs, browser commands, relay announcements, and future routine execution. The pendant is the only surface that can remain available when the owner cannot reach the Mac or browser; the relay is the always-awake enforcement point; and the Mac/browser must honor the revocation when they reconnect.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** No model should decide whether to honor the stop. Use deterministic firmware and relay revocation; use a cheap background model only to summarize prevented actions afterward.
- **latency:** Pendant-local audio/output and command suppression immediately; relay propagation under 1 second when connected; offline nodes enforce the stop on reconnect before accepting work.
- **cost:** Negligible runtime cost; storage is a bounded revocation epoch and a small prevented-action ledger.
- **security:** The stop gesture must be hard to trigger accidentally but impossible for ordinary model output to override. Persist a monotonic revocation epoch in pendant nonvolatile storage and relay durable storage. Do not silently clear it; require an explicit owner reset with an auditable event.
- **missing:** A firmware-local emergency-stop gesture and nonvolatile revocation epoch; A relay kill-switch endpoint and middleware that rejects stale command epochs; Mac and browser workers that check the epoch before every action and cancel queued work; A bounded cross-surface prevented-action receipt visible in the dashboard

### "“Before you tell me that it worked, prove it from two independent surfaces—or say you do not know.”"
- **useful because:** A Mac receipt can say an action ran while the browser did not commit it, and the relay can say audio was delivered when the owner never heard it. This capability would produce an explicit evidence grade: browser state, Mac execution receipt, relay acknowledgement, and eventually pendant playback are separate witnesses. It prevents confident but false completion claims in the moments that matter.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Use deterministic evidence rules and hashes for the verdict; use a low-cost model only to explain conflicting evidence in plain language. Realtime should speak the verdict, never invent one.
- **latency:** Under 2 seconds after an action for ordinary browser/Mac quorum; asynchronous recheck for relay or pendant evidence with a visible pending state.
- **cost:** Usually negligible; one extra browser read or receipt lookup. Model cost only occurs for conflict explanations.
- **security:** Evidence must be scoped to the action and redact secrets. Do not treat correlated copies of the same Mac report as independent witnesses. Preserve immutable timestamps, source IDs, and conflict records; require confirmation before retrying after disagreement.
- **missing:** A typed evidence-verdict schema with independent witness classes and freshness bounds; Action-specific postconditions for browser, Mac, relay, and pendant outcomes; A verifier that rejects correlated or stale evidence and exposes unknown/conflict instead of guessing; A dashboard and spoken response format that clearly separates attempted, accepted, committed, and physically heard


## What it asked for

### `c14-pjb5` (context) — nrf9160-pendant newly listed offline device
- why: Live discover(devices) now lists nrf9160-pendant with lastSeenAt 2026-08-09T02:56:31Z, contradicting the earlier established claim that it had never registered; I need the authoritative interpretation before making pendant-grounded assertions.
- would change: If this is a real paired/registered pendant, I will propose reconnect/offline workflows and stop saying no pendant has ever registered; if it is a test/stale row, I will keep all pendant runtime claims explicitly unverified.

