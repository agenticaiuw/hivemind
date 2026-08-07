# Harness derivation — faculty-perception — round 20

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-accessibility** — Mac local agent is not operationally ready for UI control: Accessibility trusted=false, synthesized input not accepted, input reachability failed, Screen Recording missing; ui_click/type_text/press_keys can report success while doing nothing.
  - evidence: GET /observe at 2026-08-07T09:52:32.557Z and GET /ops/status: accessibility.trusted=false; eventsPost=false; inputReachability.status=failed; screenRecording.granted=false; consequence explicitly says receipts cannot be trusted.
- **browser-connectivity** — Home Chrome browser extension is offline, with 2 pending browser commands and no live tab/session control; last seen 2026-08-07T09:21:08.821Z.
  - evidence: GET /browser/status and GET /ops/status at 2026-08-07T09:52Z: online=false, home-chrome offline, pendingCommands=2.
- **pipeline-audio** — The Mac pipeline has successfully rendered 24 kHz mono PCM speech (164,650 bytes, 3,430 ms) and relay accepted it for pendant download; a recent pendant offline-store alert was surfaced with microSD origin.
  - evidence: GET /pipeline response: pipeline job_165a9c... event tts done format s16le sampleRate 24000 pcmBytes 164650; relay_result done; separate nrf9160 alert_delivered event storage=microSD.

## Capabilities it proposed

### "“I was away or offline—what happened while I was gone, and what still needs my attention?”"
- **useful because:** Today events are split across pendant offline storage, cloud relay, Mac pipeline/jobs, and browser commands. A single continuity answer would distinguish delivered speech, held pendant alerts/bookmarks, completed/failed Mac work, and browser commands that are still pending—without pretending a UI action succeeded when Accessibility was unavailable.
- **path:** pendant: button/voice request and local offline event sequence → relay: durable event/job store and reconnection window → mac-planner/mac-terminal: read-only pipeline, job, receipt, and permission state → browser-extension: pending command/session state when it reconnects → faculty-perception: normalize IDs/timestamps and attach evidence → faculty-judgement: rank unresolved items and decide what to tell/ask → relay-realtime: speak a short owner-facing digest back to the pendant
- **model tier:** background text model (gpt-4.1-mini or equivalent) for event normalization and summarization; deterministic code performs deduplication, ordering, and status classification. Realtime is only used for the spoken request/response.
- **latency:** Under 2 seconds when all stores are local/available; under 5 seconds if relay reconciliation is needed. If a node is offline, answer immediately with an explicit partial view and update on reconnect rather than blocking.
- **cost:** About one background call per request, roughly 2–4k prompt tokens and <300 completion tokens (approximately <$0.01 at mini pricing); deterministic reconciliation dominates reliability, not API cost. Realtime speech remains the existing low-latency cost.
- **security:** Do not export page contents, message bodies, audio, or secrets—only event metadata, user-approved labels, timestamps, and receipt hashes. Browser sessions and relay records require existing authentication. Mark UI actions as unverified whenever Accessibility/screen recording is missing. Require confirmation before retrying, cancelling, undoing, or sending any unresolved action.
- **missing:** A shared continuity-event schema with globally unique event IDs, source, captured/received/delivered timestamps, retention, and evidence links; Relay read endpoint that can return pendant-held events and reconnection intervals without exposing payload secrets; Mac read-only reconciliation endpoint joining pipeline events, job receipts, permission/observability state, and browser pending commands; Reconnect handshake that acknowledges exactly which event IDs the owner has heard, preventing repeated alerts; A compact spoken digest formatter and dashboard timeline with partial/offline confidence labels

### "“Use the account I’m already signed into, do exactly this one thing, and prove which page/account it happened in—without giving the other machines permanent access.”"
- **useful because:** Today the pendant, relay, Mac, and browser can each know different pieces of an authenticated session, but there is no owner-visible, narrowly scoped delegation tying the spoken request to the exact browser identity, page, action, and result. This would let the owner safely use browser sessions they cannot otherwise expose to the cloud or Mac planner, while making confused-account and stale-tab mistakes detectable.
- **path:** pendant: capture the spoken instruction and display/announce a short delegation challenge → relay: mint a single-use, expiry-bound capability containing intent hash, allowed operation class, target session alias, and owner confirmation nonce → mac-planner: translate only the permitted operation into a typed action plan; never receive browser cookies or page secrets → browser-extension: resolve the named authenticated session locally, show the exact target and operation, enforce the capability, and return a signed redacted receipt plus page/account fingerprint → faculty-perception: compare intent hash, session identity, target fingerprint, and receipt evidence; report mismatches as unknown rather than success → faculty-judgement: decide when the operation is sufficiently scoped and when explicit confirmation is required → faculty-action: execute only after the capability and browser receipt checks pass → relay-realtime: provide concise spoken confirmation or explain the mismatch
- **model tier:** Deterministic protocol and policy checks first; background text model only to extract a structured intent from ambiguous speech. Realtime is reserved for the live conversational turn and never authorizes an action by itself.
- **latency:** 2–4 seconds for a connected browser; up to 10 seconds if the extension must wake or the owner must confirm a challenge. Expired or disconnected capabilities fail closed without retrying silently.
- **cost:** Usually one small background extraction call (<1k input tokens, <150 output tokens; under about $0.005 at a mini model), with deterministic signing/verification and browser execution dominating latency rather than API cost.
- **security:** Cookies, passwords, page bodies, screenshots, and account identifiers stay in the browser unless the owner explicitly asks to disclose them. Capabilities are single-use, audience-bound, operation- and origin-scoped, short-lived, and auditable. Never accept a receipt lacking session/origin fingerprint or one whose intent hash differs. Destructive, financial, messaging, and publication actions require a fresh spoken confirmation. Revocation and replay protection are mandatory.
- **missing:** A cross-node capability-token protocol with nonce, audience, expiry, intent hash, operation class, and replay-resistant storage; Browser-extension enforcement that can identify the active authenticated account/session locally and produce a signed, redacted result receipt; A Mac planner/action adapter that passes opaque browser capabilities without inspecting or storing secrets; A pendant confirmation/challenge UX and durable audit trail understandable in speech; A policy engine mapping operation classes to confirmation requirements and safe failure states


## Changes it proposed to its own stack

### `integration` — Add a read-only `/continuity/snapshot` contract at the relay/Mac boundary. It returns a bounded, redacted snapshot of node liveness (pendant, relay, Mac bridge, browser), permission trust, offline-event high-water marks, pipeline/job terminal states, and browser pending-command counts. Every field carries source, observedAt, freshness, and confidence; payload bodies and secrets are excluded. The endpoint must never trigger work or mutate acknowledgements.
- **owner gets:** The owner can ask one question and receive an honest answer about what the system knows right now, instead of hearing a success receipt from an untrusted Mac UI path or missing events held on the pendant. It also makes “partially offline” understandable.
- effort: Medium: define schema and redaction rules, implement relay aggregation plus Mac adapter, add stale/offline tests and fixture replay from existing pipeline/observe records.  ·  risk: A stale snapshot could be mistaken for current state; mandatory observedAt/freshness/confidence and a visible “partial” label mitigate this. Aggregation must fail closed to partial data, never infer success. Recovery is to disable the endpoint and continue existing per-node status paths.
- cost: Negligible API cost for deterministic aggregation; small relay storage/read overhead. No hardware cost.  ·  latency: ~50–200 ms for cached data; up to ~1 s for bounded parallel reads, with a timeout per node.
- security: Improves security by making permission failures explicit and preventing secret-bearing payloads from crossing nodes; endpoint still needs bearer/pairing authentication and audit logging.
- depends on: A redacted continuity-event schema and globally unique event IDs; A relay read API for pendant-held event metadata; Mac read-only adapters for pipeline/jobs/observe/browser status


## What it asked for

### `c4-1hkd` (context) — continuity-event retention and acknowledgement semantics
- why: The live pipeline already contains pendant-held alerts/bookmarks and relay-delivered audio, but I cannot tell how long each source retains events or whether owner-heard acknowledgements are durable and deduplicated.
- would change: I would either record a verified retention/acknowledgement fact and tighten the continuity proposal, or explicitly label the proposed digest as best-effort rather than implying complete history.

### `t3-s77a` (tool) — read_continuity_snapshot
- why: Perception needs one authenticated, read-only view of liveness, freshness, offline high-water marks, pipeline/job states, browser pending commands, and permission trust to answer the owner's 'what happened while I was away?' without scraping multiple endpoints or inferring success.

```json
{
  "type": "object",
  "properties": {
    "since": {
      "type": "string",
      "format": "date-time",
      "description": "Optional lower bound for event metadata; default bounded recent window"
    },
    "include": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "pendant",
          "relay",
          "mac",
          "browser",
          "pipeline",
          "permissions"
        ]
      },
      "description": "Optional source filters"
    },
    "maxItems": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Maximum event metadata records"
    }
  },
  "additionalProperties": false
}
```

## Its own summary

Established fresh truth: Mac UI control is untrusted (Accessibility false, input probe failed, Screen Recording missing), Chrome extension is offline with 2 pending commands, while the pipeline has demonstrably produced and relayed 24 kHz PCM and surfaced pendant microSD-held alerts. Recorded all three findings. Proposed a cross-device “what happened while I was away?” continuity digest and the read-only `/continuity/snapshot` integration needed to make it honest, plus requested a precise `read_continuity_snapshot` tool. I still need durable retention/acknowledgement semantics, a relay metadata read path, and browser reconnection before claiming complete history.

**Biggest unknown:** Whether pendant-held alerts/bookmarks and relay/job events have durable, globally unique acknowledgements and defined retention; without that, continuity answers must remain explicitly partial.

