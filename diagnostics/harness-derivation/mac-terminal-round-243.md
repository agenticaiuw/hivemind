# Harness derivation — mac-terminal — round 243

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **USB bench visibility** — The newly granted mac_usb_serial_diagnostics schema still has no live implementation: invocation was unresolved, with nearest action:get_mac_status. The two chips are physically connected, but no production capability can read their UARTs except arbitrary run_shell/bench scripts.
  - evidence: mac_usb_serial_diagnostics call returned unresolved; live inventory reported no serial/USB/tty capability.

## Capabilities it proposed

### ""If my Mac went to sleep or restarted, continue the thing I asked for instead of making me start over—and tell me exactly what remains.""
- **useful because:** A long browser or shell task should survive the laptop disappearing. The pendant is the only surface that can tell the owner the task is still alive while away; the relay can retain the handoff; the Mac can reconcile its durable action ledger and resume only unfinished steps. Today interrupted jobs remain stuck forever and resuming requires manually reconstructing POST /execute.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background for reconciliation and cheap summarization; realtime only for the owner's spoken status question
- **latency:** On Mac reconnect, reconcile within 5 seconds; speak a concise status within 2 seconds of a button/voice query.
- **cost:** Usually <$0.01 per recovery; filesystem/relay work dominates, with a small model call only to summarize unfinished steps.
- **security:** Resume must preserve the owner's existing maximum-access policy, but must not silently repeat non-idempotent mutations. Store a step-level replay classification and pre/post state; send only step labels, statuses, and bounded output to relay, not shell environment or secrets. Ask for confirmation only where the existing action itself would have required it (do not add a new blanket gate).
- **missing:** Boot-time reconciliation that marks processing jobs interrupted rather than forever-running; Call closeLedger on every orchestrator execution and persist planMeta.jobId so ledger and job are joinable; A resume worker that uses the existing executionContext idempotency engine and replays only incomplete/replay-safe steps; A pendant-facing status payload that distinguishes resumed, blocked, and irrecoverable steps

### ""Run a five-minute health check on the pendant and audio bridge, then tell me whether the microphone, radio, and speaker are actually usable.""
- **useful because:** The chips are physically attached to this Mac today, but there is no trustworthy owner-facing diagnostic. A bounded dual-UART capture can detect boot loops, codec underruns, framing errors, USB enumeration, and the nRF9160/ESP32 handshake before the owner wears a silent device. The result should be spoken through the pendant or shown in the Mac dashboard, not left as raw logs.
- **path:** pendant → mac-planner → relay → dashboard
- **model tier:** background deterministic parser first; cheap model only to turn measured faults into a short explanation
- **latency:** Connect and collect within 10 seconds, analyze within 3 seconds, report under 15 seconds total.
- **cost:** Near-zero model cost for healthy runs; <$0.01 only when a log needs explanation. USB capture and parsing dominate.
- **security:** Read-only serial access, bounded to the two known device paths, maximum capture duration/bytes, and no network. Redact any identifiers before relay upload. Never claim LTE readiness from USB-only evidence; report bench transport separately from wearable transport.
- **missing:** A real bounded USB serial reader with port autodiscovery and framing-aware nRF9160/ESP32 parsers; A structured health schema with per-component state, evidence offsets, firmware versions, and timestamps; A route/action that runs the existing diagnostics/dual_chip_autocapture.sh or equivalent without arbitrary shell output; A relay/pendant result packet that speaks actionable failures and preserves raw logs locally

### ""When I close the lid, keep the safe parts working, pause anything that needs my screen, and tell me on the pendant what is waiting for me when I come back.""
- **useful because:** Today a Mac sleep, browser disconnect, or locked display looks like an opaque failure. The relay can keep the intent and job state alive, the Mac can classify the next step's actual dependency (network, browser session, Accessibility/UI, or pure local work), and the pendant can report a compact waiting-for-owner reason when offline or on reconnect. This turns leaving the desk into a safe handoff rather than a dead task.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** deterministic state machine for sleep/lock/session events; cheap model only for grouping several waiting jobs into one sentence
- **latency:** Detect sleep/lock within 2 seconds of the Mac event; queue or pause before the next step; pendant status on reconnect under 1 second.
- **cost:** Near-zero inference; local event handling and one small summary call when multiple jobs are waiting.
- **security:** The relay stores only job IDs, step classes, and owner-facing reasons, never browser cookies or shell environment. Browser work must never be falsely marked complete while the extension is disconnected. Resume should use existing replay-safety metadata and keep the owner's no-gate maximum-access policy.
- **missing:** Mac sleep/wake/lock/unlock event feed into the local agent; Per-step dependency declaration and a scheduler that can pause UI-bound work while continuing independent work; Browser extension presence/session-lock signal tied to the same job ID; Pendant status packet for waiting reasons, not merely running/failed

### ""Before you submit anything in a logged-in website, read me the exact fields and attachments that will be sent, let me correct them from the pendant, and then submit the same verified version—even if the browser or relay reconnects in between.""
- **useful because:** The owner can ask the system to act in authenticated browser sessions, but cannot safely verify a dynamic form at arm's length. This gives them a compact, durable commit contract: the browser produces a canonical field/attachment digest, the Mac renders the exact diff, the pendant speaks it, and the relay preserves the verified version across disconnects. It is useful for applications, messages, purchases, and work portals without exposing page contents to the relay.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic extraction, canonicalization, hashing, and replay; realtime model only for the pendant's spoken summary and correction parsing.
- **latency:** Prepare a review under 5 seconds; correction acknowledgement under 2 seconds; after reconnect, either submit the exact digest or refuse within 1 second.
- **cost:** Usually under $0.01, dominated by one short speech-summary call; browser extraction and hashing are local.
- **security:** Raw authenticated page data and attachments remain on the Mac/browser. Relay stores only a redacted review, field names, content digests, target origin, expiry, and commit nonce. Any DOM or attachment change invalidates the nonce. Never submit a version whose digest differs from what the owner reviewed; never treat a browser reconnect as approval.
- **missing:** A browser action that extracts a canonical, user-readable submission manifest including attachment hashes; A durable two-phase commit object shared by browser, Mac, relay, and pendant; Pendant correction protocol for field-level edits and explicit commit/cancel; Browser-side submit guard that accepts only the verified manifest nonce; A local encrypted review cache so the Mac can survive browser or relay reconnection without sending secrets

### ""After you send or change something on a website, prove that the server accepted it—not just that the button clicked—and tell me if the result is still uncertain.""
- **useful because:** A browser click is not a successful outcome: sessions expire, network retries duplicate submissions, and sites show optimistic UI. The owner currently cannot distinguish submitted, accepted, rejected, and unknown from the pendant. The browser can collect a postcondition (confirmation ID, changed record, or stable page evidence), the Mac can independently re-read it, and the relay can retain the evidence until the owner hears the truth.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Deterministic postcondition checks and retry classification; cheap model only to summarize contradictory evidence.
- **latency:** Verify within 5 seconds after a response; if the site is asynchronous, poll with an explicit deadline and report unknown rather than claiming success.
- **cost:** Near-zero for structured checks; under $0.01 when an ambiguous page needs semantic interpretation.
- **security:** Evidence stays local to the Mac/browser except a redacted result, origin, timestamp, and confirmation reference. Never retry a non-idempotent action without a server-side idempotency key or an owner-approved recovery policy. The pendant must say “uncertain,” not infer completion from a click.
- **missing:** A browser postcondition DSL supporting URL, DOM, confirmation-ID, and record-value assertions; Idempotency-key and duplicate-detection support for submissions; A durable evidence capsule linked to the originating browser command and Mac job; Relay/pendant states for accepted, rejected, pending, and unknown with expiry; A verifier that can safely re-read a page without repeating its mutation

### ""For anything important you find in my logged-in sites, check it against a second independent source before you tell me it is true, and tell me when the sources disagree.""
- **useful because:** The owner currently receives a page-derived answer, but has no way to know whether it is stale, mis-rendered, or contradicted elsewhere. The browser extension can inspect the authenticated source, the Mac can use a separate public or local source, and the relay can compare timestamped claims before speaking a conclusion through the pendant. This is especially valuable for deadlines, account balances, delivery status, and security alerts.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Cheap background extraction and deterministic claim comparison; realtime only when the owner asks a follow-up about a disagreement.
- **latency:** Return a verified answer in 10 seconds for two reachable sources; otherwise report provisional/unknown rather than waiting indefinitely.
- **cost:** Usually <$0.02 for two short extraction calls; network and browser navigation dominate.
- **security:** Keep authenticated page text and cookies on the Mac. Relay receives claim hashes, source host/URL, timestamps, and bounded evidence excerpts only when necessary. Never silently substitute a public source for an authenticated one; label freshness and source authority explicitly.
- **missing:** A claim-level browser extraction API with timestamps and quoted evidence; A second-source resolver that can select an independent host or local record without reusing the same session; A deterministic contradiction/freshness evaluator and provenance graph linking both claims; Pendant speech states for verified, conflicting, stale, and single-source answers


## What it asked for

_Nothing._
