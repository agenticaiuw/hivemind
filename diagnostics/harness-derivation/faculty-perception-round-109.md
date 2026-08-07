# Harness derivation — faculty-perception — round 109

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live device fleet** — As of 2026-08-07T15:05:36Z, home-macbook-bridge is online and cloudflare-contract-test mobile is offline; no pendant device is registered.
  - evidence: discover(devices) returned exactly Safari on MacIntel, home-macbook-bridge online, cloudflare-contract-test offline; prior granted live pendant observability says no nRF9160 has ever registered.
- **Mac UI reachability** — At 2026-08-07T15:05:51Z, AI Pendant Agent has Accessibility trusted=false and Screen Recording granted=false; synthesized UI input will not reach the screen, so UI action receipts are untrustworthy.
  - evidence: GET /observe response: accessibility.trusted=false, eventsPost=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false; GET /ops/status permissions.ready=false.
- **browser bridge** — Safari browser bridge is online with zero pending commands as of 2026-08-07T15:05:44Z; its connected tab is the bridge UI itself with blank URL, not an owner-private content tab.
  - evidence: GET /browser/status and GET /ops/status report online=true, pendingCommands=0, tabTitle='AI Pendant Browser Bridge', tabUrl=''.
- **relay** — Cloud relay is configured and reachable; mac bridge is online. Relay reports pendantPipelineTelemetry, pendantSpeech, persistentAgentState, and durableAudio capabilities.
  - evidence: GET /ops/status relay.payload: reachable=true, macBridgeOnline=true, capabilities all true.
- **machine timezone** — Mac machine-context currently reports timezone America/New_York; this is machine configuration, not yet independently established as owner's authoritative timezone.
  - evidence: GET /machine-context returned machine.timezone='America/New_York'.

## Capabilities it proposed

### "“Did that actually happen?” — reconcile a spoken request across my pendant, relay, Mac, and logged-in browser, and tell me what is proven, what was only attempted, and what is still unknown, with the exact evidence chain."
- **useful because:** Today a spoken request can produce a relay record, a Mac job, a browser command, or even rendered audio without proving that the real-world/browser outcome occurred. The owner needs one trustworthy answer that distinguishes intent, execution, delivery, and observed outcome instead of treating a success receipt as reality.
- **path:** pendant → relay → mac-planner → browser-extension → unified
- **model tier:** Use the cheaper background/text model to assemble and reconcile receipts; reserve realtime only for the short spoken answer or an immediate follow-up. Do not spend the low-latency tier on polling or evidence normalization.
- **latency:** Under 5 seconds when all records are present; if a device or browser acknowledgment is missing, return a partial result immediately and continue reconciliation asynchronously.
- **cost:** Low per invocation: mostly authenticated reads and deterministic correlation; one short text-model call for contradiction explanation, with realtime/TTS cost only when spoken back. Dominant cost is retained evidence/context, not inference.
- **security:** Private browser URLs, page snippets, job arguments, and voice transcripts must remain scoped to the owner and be minimized in the spoken response. Never infer completion from an attempted click or queued audio. Any retry, correction, or external side effect requires a separate confirmation; this capability is read-only.
- **missing:** A durable cross-surface evidence schema linking one request through pendant capture, relay delivery, Mac job/action receipt, browser request/result, and final observation; Authoritative pendant connection and delivery acknowledgments (currently no pendant is registered); Browser-side post-action acknowledgment containing URL/tab identity, timestamp, and observed before/after state—not merely command acceptance; A reconciliation endpoint that can correlate /pipeline events, /jobs/:jobId/receipts, browser command/result records, and device delivery state with freshness and confidence; An owner-visible evidence timeline that clearly labels attempted, accepted, delivered, observed, contradicted, and unknown states

### "“Keep this private while you work.” Detect when my Mac or logged-in browser is showing sensitive material, then make the spoken pendant response safe—use a neutral notification, headphones-only/local playback, or wait for my explicit unlock—while preserving the task state."
- **useful because:** A wearable voice assistant can leak account, health, work, or message content aloud at exactly the wrong moment. Today the relay, Mac, and browser know pieces of the situation but do not share a perception-backed privacy boundary. This gives the owner confidence that asking for help will not broadcast private page contents or job results.
- **path:** pendant → browser-extension → mac-vision → mac-planner → relay-realtime → unified
- **model tier:** Use deterministic local policy and lightweight classification for most decisions; use a cheap background model only to classify ambiguous page/app sensitivity. Realtime should speak only a short safe acknowledgment after the policy decision.
- **latency:** Under 150 ms for known sensitive apps/tabs and under 1 second for ambiguous classification; fail closed to a neutral acknowledgment when state cannot be established.
- **cost:** Near-zero for known app/domain rules; occasional small text-model cost for ambiguous page classification. The main cost is implementation and local encrypted state, not inference.
- **security:** Sensitivity classification should happen on the Mac whenever possible; page text and account identifiers must not leave the device merely to decide whether to speak. No raw private content should be sent to the relay or stored in ordinary logs. The owner needs an explicit local override and an auditable record of why speech was suppressed. Because Screen Recording/Accessibility are currently unavailable, visual sensitivity detection must be marked unknown rather than guessed.
- **missing:** A local privacy-policy engine shared by relay, Mac, and browser with deny-by-default handling for unknown foreground/tab state; Browser extension metadata for logged-in origin, page sensitivity class, and whether the current tab is visibly foreground, without uploading page contents; Pendant playback routing and acknowledgment controls that can select headphones/local playback, suppress speech, or emit a neutral tone; A reliable local presence/proximity signal tying the pendant wearer to the Mac session; currently no pendant is registered; A privacy-safe event contract so suppressed content is recoverable after explicit unlock without placing it in relay logs


## Changes it proposed to its own stack

### `context` — Add a monotonic observation ledger and freshness gate shared by every surface. Each observation is append-only and typed as live, historical, inferred, or unavailable, with observedAt, source identity, scope, confidence, and expiry. Consumers must request a current observation lease before presenting a fact as present-tense or using it to authorize a side effect; stale pipeline events cannot satisfy a live-device check. Contradictory observations remain visible as a conflict instead of being overwritten.
- **owner gets:** The owner gets honest answers about what is true now. A historical pendant event will no longer be mistaken for a connected pendant, and an old browser tab or receipt will not be presented as current reality. When the system cannot know, it can say so clearly rather than sounding confident.
- effort: Medium-high: define the event schema and state transitions, add writers around relay/device/browser/Mac observations, implement TTL and conflict handling, then update planner and speech projections to consume leases. Start read-only in diagnostics before enforcing gates.  ·  risk: Incorrect TTLs could make useful facts appear unavailable, and clock skew could create false conflicts. Recover with source-local monotonic sequence numbers, server receipt time, configurable TTLs, and a shadow mode that reports would-be refusals before enforcement. Never delete raw evidence when compacting the ledger.
- cost: Small storage and compute increase for indexed observation records; negligible model/API cost because freshness and conflict resolution are deterministic. Retention needs bounded compaction with pointers to durable audit objects.  ·  latency: Single local indexed lookup (target under 20 ms); conflict explanation may add a cheap background model call, but normal speech should not wait for it.
- security: Observation payloads can contain sensitive tab/app/device metadata. Encrypt at rest, minimize content fields, enforce per-surface scopes, and keep private page text out of the relay unless explicitly required. The ledger must not become a new cross-account data lake.
- depends on: A durable cross-surface identifier for a user request and device/session identity; Explicit source clocks or sequence numbers for relay, Mac bridge, browser extension, and pendant once one exists; A policy for which observations are allowed to authorize actions versus merely inform the owner


## What it asked for

_Nothing._
