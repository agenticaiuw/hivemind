# Harness derivation — faculty-perception — round 46

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **Mac UI input reachability** — As of 2026-08-07T11:22:48Z, AI Pendant Agent cannot reach the Mac UI: Accessibility trusted=false, Screen Recording=false, inputReachability.status=failed, uiActionsWillReachTheScreen=false. Synthesized events are rejected as permission is granted to a different binary.
  - evidence: GET /observe response at 2026-08-07T11:22:48.540Z
- **Mac agent readiness** — As of 2026-08-07T11:22:48Z, Mac agent permissions.ready=false despite requiredMissing=[]; automation grants are cached but Accessibility and Screen Recording remain unavailable.
  - evidence: GET /ops/status response at 2026-08-07T11:22:48Z
- **Cross-surface status** — Relay is reachable and mac bridge online (last seen 2026-08-07T11:22:35Z), while browser extension home-chrome is offline with 4 pending commands; no browser tabs are currently reachable through the extension.
  - evidence: GET /ops/status response at 2026-08-07T11:22:48Z
- **Mac-reported timezone** — The Mac machine-context currently reports timezone America/New_York. This is a machine-reported value, not independently established as the owner's authoritative timezone.
  - evidence: GET /machine-context response at 2026-08-07T11:22Z

## Capabilities it proposed

### "“Before you do anything, tell me exactly what you can see and what you cannot reach right now.”"
- **useful because:** Today an online Mac bridge and successful-looking UI receipts can coexist with no real screen/input access. The owner needs an immediate, evidence-backed truth report so they are never misled about whether the pendant, relay, Mac screen, private browser tabs, or account sessions are actually observable. It turns silent permission/offline failures into an actionable explanation and a safe fallback.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for assembling the report; realtime only to speak the short result when asked
- **latency:** Under 2 seconds for cached health, under 5 seconds when fresh probes are required; never block on an unavailable surface
- **cost:** Usually <$0.01 per report if generated from typed probe results; dominant cost is optional realtime speech, not reasoning
- **security:** Report only capability metadata and redacted evidence (app name, session IDs, timestamps), never page contents or tokens. Private-tab/account reachability must be stated without exposing URLs unless requested. Do not run UI actions as a probe; require confirmation before any test that changes focus or posts input.
- **missing:** A unified typed observation contract across relay, Mac, browser extension, and pendant with per-surface status, timestamp, evidence source, and confidence; A read-only relay endpoint that fan-outs fresh probes and returns a signed/cited reachability report; A pendant/dashboard rendering for degraded states and explicit 'unknown' rather than optimistic online; Permission repair for the exact com.aipendant.agent binary (currently Accessibility and Screen Recording are still false)

### "“What changed since I left my computer?”"
- **useful because:** A dropped pendant link or sleeping Mac currently erases the owner's sense of continuity. A privacy-preserving change report would distinguish observed transitions—foreground app, browser-session availability, relay/bridge connectivity, pending work—from guesses, so the owner can resume safely without rereading everything or trusting stale state.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background summarizer over structured events; realtime only when the owner asks by voice
- **latency:** Return cached transitions in under 1 second; refresh reachable probes within 5 seconds, and clearly label unobserved intervals
- **cost:** <$0.005 per query using event deltas; storage and periodic probes dominate, not model tokens
- **security:** Store hashes and metadata by default, not screen pixels or page text. Browser events should say session/tab availability and change category, with URLs/content redacted unless explicitly requested. Sign event timestamps and mark clock uncertainty. Never infer user activity from an app merely being foregrounded.
- **missing:** A durable cross-surface observation ledger with monotonic sequence numbers, gap markers, source identity, and retention controls; Mac/browser emitters for state transitions (including explicit offline/permission failures), plus relay fan-in and deduplication; A pendant command to request the last-known delta and a dashboard timeline with 'not observed' gaps

### "“I’m holding this—bring up everything I need for it.” (or “Tap this object to connect it to my work.”)"
- **useful because:** The owner’s physical day and digital work are disconnected. A pendant tap on an NFC/BLE-tagged notebook, medication case, package, instrument, or room marker could identify the object locally, let the relay retrieve its durable association, have the Mac open the relevant local project, and have the browser surface the matching private page—without making the owner explain what they are looking at.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap background classifier/router for the object ID and stored association; realtime only for the brief spoken confirmation
- **latency:** Local recognition under 300 ms; digital handoff under 3 seconds; if any surface is unavailable, keep the physical association and say exactly which handoff was skipped
- **cost:** <$0.01 per handoff; dominant ongoing cost is optional NFC/BLE hardware and durable association storage, not model inference
- **security:** Object IDs must be opaque and local by default. Private browser URLs/content stay on the owner’s devices; relay stores only encrypted associations and event metadata. Require confirmation before opening sensitive accounts or exposing an object’s association aloud in public. Provide an immediate unpair/delete control.
- **missing:** Pendant NFC reader or reliable BLE tag scanning support, with local pairing and offline object-ID cache; A relay object-association registry with encrypted owner-scoped records, revocation, and event provenance; Mac and browser handlers that accept an object ID and open only approved local projects/private tabs, with a preview before sensitive navigation; A dashboard and pendant interaction for creating, renaming, testing, and deleting physical-to-digital links


## Changes it proposed to its own stack

### `hardware` — Add a low-power NFC reader, with BLE-tag fallback, to the pendant and expose a signed local objectId event to the relay. Keep a small encrypted association cache on-device so a tap still identifies the object while offline and syncs the handoff when connectivity returns.
- **owner gets:** The owner can connect a real object to the right digital context with one tap instead of searching, remembering names, or dictating a long explanation—especially useful for medication, instruments, notebooks, deliveries, and recurring projects.
- effort: Medium hardware revision plus firmware driver, pairing UX, relay registry, and Mac/browser object-context handlers.  ·  risk: Accidental scans, tag cloning, and unwanted context opening; mitigate with explicit pairing, rotating identifiers where possible, signed events, proximity/time checks, and preview/confirmation for sensitive contexts. If the reader fails, ordinary pendant voice behavior remains unaffected.
- cost: Roughly a few dollars in component/BOM cost and sub-milliwatt average draw with duty-cycled scanning; modest storage and API cost for encrypted association metadata.  ·  latency: Local tag detection adds under 300 ms; digital context handoff remains network-dependent and should degrade gracefully to a spoken association.
- security: Adds a physical identity surface, so object IDs must be opaque, owner-scoped, revocable, and never treated as authentication. Do not allow a tag alone to authorize purchases, messages, or account access.
- depends on: Pendant PCB space and firmware support for NFC/BLE scanning; Relay object-association registry and revocation; Mac/browser handlers for object-context handoff


## What it asked for

_Nothing._
## Its own summary

Fresh probes established that the grant did not take effect: at 11:22:48Z the exact AI Pendant Agent binary still has Accessibility=false, Screen Recording=false, inputReachability=failed, and ops ready=false. UI actions and screenshots therefore cannot be trusted. Relay and Mac bridge are online, but Chrome extension is offline with 4 pending commands. I recorded these facts and proposed two new perception capabilities: an evidence-backed reachability report and a privacy-preserving 'what changed since I left?' event delta. What is still needed is permission repair for the exact running binary plus browser-extension reconnection; until then mac-vision cannot provide a trustworthy UI hierarchy.

**Biggest unknown:** Whether macOS permissions were granted to a different/stale AI Pendant Agent binary and how to repair TCC for com.aipendant.agent without relying on false-success UI receipts.

