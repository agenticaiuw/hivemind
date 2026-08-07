# Harness derivation — faculty-perception — round 131

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac accessibility state** — At 2026-08-07T18:37Z AI Pendant Agent is running but Accessibility and Screen Recording are not granted; inputReachability is failed, eventsPost=false, and UI actions report success while doing nothing.
  - evidence: GET /observe response observedAt 2026-08-07T18:37:25.520Z
- **browser live state** — Safari browser bridge is online with 3 durable sessions/tabs; the default session is authenticated Gmail inbox, while the extension heartbeat's active tab is example.com titled 'Failed to open page'.
  - evidence: GET /browser/status and GET /observe at 2026-08-07T18:37Z
- **relay device state** — Relay reports mac bridge online, but no registered nRF9160 pendant; available device table is Safari and home-macbook-bridge online plus cloudflare-contract-test offline.
  - evidence: discover devices and GET /ops/status payload
- **capture store exposure** — GET /capture currently returns two captures, including a secret bike-lock code; perception consumers must enforce sensitivity filtering and never surface secret values in routine briefs.
  - evidence: GET /capture response at 2026-08-07T18:37Z

## Capabilities it proposed

### "Before you act, tell me whether you can really reach what you intend—screen, browser tab, Mac, relay, or pendant—and if not, give me the exact smallest fix instead of pretending it worked."
- **useful because:** Today the Mac agent's UI actions can report success while doing nothing because Accessibility is false, and there is no registered pendant. A perception-first reachability verdict would prevent the most damaging failure: confident claims about actions that never reached the world.
- **path:** faculty-perception → mac-planner → mac-vision → browser-extension → relay-realtime → faculty-judgement → faculty-action
- **model tier:** background for periodic health snapshots; realtime only when attached to an owner request
- **latency:** Under 500 ms for cached state; under 3 s when refreshing Mac/browser/relay evidence
- **cost:** <$0.01 per request when using structured route data; model cost near zero if verdict is rule-based, with occasional cheap summarization
- **security:** Expose only capability/state facts, never page contents or captured secrets. Require fresh timestamps and distinguish observed reachability from configured permissions. UI actions must be marked untrusted when inputReachability is failed.
- **missing:** A typed cross-surface reachability snapshot/verdict with freshness and action-specific prerequisites; A planner gate that consumes the verdict before selecting UI actions; Owner must grant Accessibility/Screen Recording to enable actual GUI reachability

### "When I say ‘do it’, first check whether I am looking at the right thing; if Safari is on a dead/error tab or the browser session is stale, recover or ask me before touching anything."
- **useful because:** The live extension is online but its active tab is example.com with ‘Failed to open page’, while an authenticated Gmail tab exists in another durable session. This would stop actions from being applied to a visually misleading or stale tab and use the browser's private session deliberately.
- **path:** faculty-perception → browser-extension → mac-planner → faculty-judgement → faculty-action → relay-realtime
- **model tier:** cheap structured checks plus a small background model only for semantic tab/task matching
- **latency:** 1–2 seconds before an action; no polling faster than the extension heartbeat
- **cost:** <$0.01 per check; browser extraction dominates, not model tokens
- **security:** Never reveal authenticated URLs/content in relay speech unless requested. Bind every verdict to sessionId/tabId and URL, detect navigation races, and require confirmation before switching from a requested private tab to another account/page.
- **missing:** A pre-action tab-intent matcher that compares the owner's request with tab title/URL/content; A dead-page classifier and safe recovery policy (retry, reopen same URL, or ask); A browser command barrier that refuses execution when tab identity changed after planning

### "What changed since I last asked? Give me only newly observed changes in my Mac, browser, relay, and (when connected) pendant, with timestamps and what those changes make possible or impossible."
- **useful because:** The system can observe many surfaces but currently makes each agent rediscover state independently. A signed, diff-based perception stream would let the hive notice meaningful transitions—browser tab failure, foreground-app change, permission loss, relay disconnect, or pendant arrival—without spending the owner's attention on unchanged status.
- **path:** faculty-perception → mac-planner → browser-extension → relay-realtime → faculty-judgement → faculty-action → unified
- **model tier:** rule-based diffing and TTL evaluation; cheap model only to compress multiple changes into speech
- **latency:** Record transitions within one heartbeat; spoken summary under 2 seconds on request
- **cost:** Negligible storage/compute for hashes and typed events; <$0.005 for optional natural-language compression
- **security:** Store hashes and metadata by default, not page text/audio. Redact secret captures and private URLs from cross-surface events. Each event needs source, observedAt, expiry, and confidence so stale state cannot masquerade as current.
- **missing:** Durable cross-surface observation ledger with monotonic sequence and event acknowledgements; Diff engine for /observe, /browser/status, relay device registry, and pipeline/pendant telemetry; A consumer API that returns only changes since a cursor and supports privacy redaction

### "When you are ready to send, buy, delete, or submit something, show me the exact final change and let me approve that specific change with one press of the pendant—not a vague approval that could be replayed later."
- **useful because:** Today approval is conversational and can become detached from the exact browser or Mac state after a tab changes. A physical, one-shot pendant confirmation bound to a hash of the final payload gives the owner a fast, unambiguous approval channel that the remote relay and browser alone cannot provide.
- **path:** relay-realtime → pendant → faculty-judgement → faculty-action → browser-extension → mac-planner
- **model tier:** realtime for presenting the final diff; deterministic cryptographic verification for the button approval
- **latency:** Final diff within 3 seconds; button-to-execution acknowledgment under 1 second
- **cost:** <$0.01 per transaction; cryptographic checks and relay storage dominate, not model inference
- **security:** The pendant must sign a nonce plus exact action hash, expire approvals quickly, prevent replay, and visibly distinguish approve/cancel. Never treat a generic button press as consent. Private payloads should be hashed on-device or locally and not spoken to the relay unnecessarily.
- **missing:** Signed pendant approval protocol with nonce, action hash, expiry, and cancel semantics; Relay transaction-intent store that binds approval to browser tab/session or Mac job; Browser/Mac execution gate that refuses any payload differing from the approved hash; A pendant firmware event path and confirmation LED/haptic pattern

### "Give me a physical privacy switch: when I press it, stop sending microphone, browser-page text, and screen data off the Mac, prove that each surface is muted, and keep working locally until I release it."
- **useful because:** The owner cannot today establish a single, trustworthy privacy boundary across the pendant, audio bridge, Mac agent, browser extension, and relay. A hardware-triggered mode would make privacy immediate even if the conversational model is confused or the network remains connected.
- **path:** pendant → audio bridge → mac-planner → browser-extension → relay-realtime → faculty-perception
- **model tier:** firmware and deterministic relay policy for the switch; no expensive model needed, with optional realtime confirmation after the state change
- **latency:** Mute/stop outbound capture within 100 ms locally; all-surface acknowledgment within 1 second
- **cost:** Negligible per-use API cost; engineering requires firmware, bridge, relay, and browser hooks. Battery impact is negligible if implemented as a hardware interrupt.
- **security:** The pendant must fail closed on boot, link loss, and ambiguous switch state. Relay must reject audio/page/screen uploads while the signed privacy epoch is active, and the Mac/browser must stop queued commands and redact pending payloads. Do not claim privacy until each surface returns an independently observed acknowledgment.
- **missing:** A hardware interrupt and signed privacy-epoch event in pendant firmware; Audio bridge local mute and queue purge; Relay ingress policy that enforces the privacy epoch rather than trusting model intent; Mac and browser hooks that halt capture/extraction and report acknowledgments; A visible/haptic indication that local privacy mode is active


## Changes it proposed to its own stack

### `integration` — Add a Mac USB commissioning bridge that watches /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, fingerprints nRF9160 and ESP32 firmware, runs a non-destructive health/audio-loop test, and publishes an explicitly local-only device presence plus test receipts to the relay. Keep it separate from LTE registration so ‘USB attached’, ‘relay registered’, and ‘audio verified’ are three independent states.
- **owner gets:** The owner can test the worn hardware on the Mac today instead of being told the pendant is unavailable merely because it has not registered over LTE. They get a truthful answer—connected, firmware identified, microphone/playback tested, or exact failure—before trusting a wearable interaction.
- effort: Medium-high: serial protocol adapter, firmware test commands, local daemon, relay schema, and a dashboard/status view; validate against both chips and unplug/replug races.  ·  risk: A bad probe could interfere with firmware or audio; use read-only identification first, bounded test commands, explicit device-path allowlist, and no flashing. Recover by stopping the bridge and leaving LTE registration untouched.
- cost: No per-call model cost; roughly 1–3 MB local daemon footprint and negligible idle CPU. Hardware already present; no new component required.  ·  latency: Presence within 1 s of USB attach; health/audio test 5–15 s.
- security: Serial data and test telemetry leave the Mac only as redacted typed status; never upload raw microphone/audio or modem identifiers without opt-in. Pair the local bridge separately from the relay API key.
- depends on: A serial protocol/diagnostic contract in firmware/nrf9160 and firmware/esp32-airpods-bridge; A relay endpoint for local-device telemetry distinct from LTE device registration; A visible status UI distinguishing USB-local from remotely registered

### `model-routing` — Introduce an evidence gate for perception-derived claims: before faculty-judgement or relay-realtime can say ‘I opened’, ‘I sent’, ‘the pendant heard’, or ‘the screen shows’, require a matching recent observation/action receipt with source, timestamp, target identity, and success semantics. If only intent/configuration exists, rewrite the claim as ‘I attempted’ or ‘I cannot verify’.
- **owner gets:** The owner stops hearing polished falsehoods when an action receipt says success but macOS rejected synthetic input, a browser tab changed, or a pendant is absent. Every spoken status becomes honest about what was observed versus merely requested.
- effort: Medium: typed claim taxonomy, evidence matcher, realtime output hook, and tests for stale/conflicting observations.  ·  risk: Over-blocking could make conversation awkward or delay harmless answers; limit the gate to world-state/action claims, use short uncertainty language, and permit clearly labeled plans. Recovery is fallback speech that names the missing observation.
- cost: Minimal structured evaluation; perhaps <$0.002 per response for a cheap verifier, no extra expensive realtime turn.  ·  latency: ~50–150 ms if evidence is cached; avoid network refresh in the speech critical path.
- security: Evidence references must be opaque IDs and redacted snippets; never put private page text, secrets, or raw audio into the model prompt unless the task explicitly requires it.
- depends on: A shared typed observation/receipt schema; Action receipts carrying actual-vs-reported execution status; Relay and Mac agent output hooks before speech synthesis

### `relay` — Add a privacy-preserving owner-presence attestation shared by the pendant, Mac bridge, and browser extension: the pendant emits a rotating short-lived proximity token over its local link, the Mac bridge relays only the blinded token, and the browser/action service accepts sensitive operations only when the token, active browser session, and current action nonce all match. Record presence proof metadata, never location or raw radio identifiers.
- **owner gets:** The owner gets protection against a stale relay session, unattended Mac, or copied browser command carrying out a sensitive action after they have walked away. It also lets them say ‘only do this while I am wearing the pendant’ without exposing their movements.
- effort: High: firmware cryptography and rotation, local USB/BLE transport, relay verification, browser/Mac enforcement, clock-skew and disconnect handling, and recovery UX.  ·  risk: False negatives could block a wanted action when the pendant is shielded or disconnected; provide an explicit conversational fallback requiring the stronger physical approval path, never silently bypass it. Compromise of one node must not forge the three-way proof.
- cost: No recurring model cost; modest firmware and relay CPU/storage, with a small battery cost for periodic token rotation. May require a BLE/proximity-capable transport or a secure local serial pairing protocol.  ·  latency: Under 300 ms for a cached presence proof; re-pairing may take seconds.
- security: Improves authorization and replay resistance while minimizing data. Rotating tokens must be unlinkable, and the relay must not learn continuous location or a long-lived device identifier.
- depends on: Pendant identity/key provisioning and secure storage; A Mac bridge local-link protocol (USB today, BLE later); Relay transaction nonce verification; Browser and Mac action gates that can require presence attestation


## What it asked for

_Nothing._
## Its own summary

Established fresh live truth: the Mac bridge and Safari extension are online, but GUI reachability is false (Accessibility and Screen Recording denied; inputReachability failed), the extension's active tab is a failed example.com page while a separate authenticated Gmail session exists, and no nRF9160 pendant is registered. Recorded these facts with timestamps and secret-capture warning, and proposed four new items: cross-surface action reachability verdict, tab-intent/dead-page barrier, cursor-based perception change stream, USB-local hardware commissioning, and evidence-gated spoken claims. The single most useful is the evidence gate preventing ‘I did it’ when the world cannot verify it.

**Biggest unknown:** The exact serial protocols and firmware commands for the physically attached nRF9160/ESP32 remain unknown, as does the authoritative relay schema for publishing USB-local presence separately from LTE registration. I also still need a shared typed observation/receipt schema and pre-speech hook to implement the evidence gate. Accessibility remains an owner-side blocker, not something this agent can grant.

