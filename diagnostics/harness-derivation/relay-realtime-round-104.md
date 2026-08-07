# Harness derivation — relay-realtime — round 104

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“When you tell me something you learned or changed across my Mac and authenticated browser, let me tap the pendant to hear exactly which source, timestamp, and action receipt supports each sentence—and tap again to compare the current state with the state you saw.”"
- **useful because:** Voice summaries are otherwise hard to audit while the owner is away from a screen. This gives the owner fast, spoken provenance and change detection without dumping a long transcript, making cross-surface automation trustworthy enough for daily use while preserving the owner's no-gates policy.
- **path:** pendant → relay → mac-planner → browser-extension → dashboard
- **model tier:** Realtime only speaks the short answer and navigates provenance by button/tap. A cheaper background model aligns answer claims to source excerpts, Mac/browser observations, timestamps, and action receipts; deterministic hashes detect whether a source changed.
- **latency:** Initial answer remains conversational (under 700 ms when cached). A provenance request should begin playback within 1 second; fresh comparison evidence may take up to 5 seconds.
- **cost:** About $0.002–$0.03 per summarized result, mostly for claim-to-evidence alignment; hashes, receipts, and cached excerpts are inexpensive storage.
- **security:** Evidence may include private browser pages and local files. Store encrypted, least-content excerpts rather than credentials or cookies; apply per-surface access checks at playback time; expire sensitive evidence; clearly label stale or unavailable sources. This is observability, not an approval gate, and must never silently expose another person's data in a spoken environment.
- **missing:** A claim/evidence graph tying each spoken response to typed observations and action receipts; A pendant interaction state machine for next-claim, replay, compare, and stop using its single button/LED/audio channel; Stable source snapshots or content hashes with freshness and redaction metadata across Mac and browser; A relay endpoint that streams short provenance cards rather than full raw transcripts; Dashboard view for inspecting and deleting provenance records


## Changes it proposed to its own stack

### `relay` — Add a relay-native capability inventory endpoint and registration flow (e.g., GET /relay/capabilities) that exposes the relay’s own routes, granted tools, and versioned contract. Back it with a typed schema shared with orchestrator and other agents, and include a minimal health/metrics view for voice sessions.
- **owner gets:** Faster, more reliable voice behavior: the pendant agent can discover what it can actually do, avoid dead-end calls, and give accurate spoken feedback instead of guessing or re-probing. That reduces latency, errors, and confusion during everyday use.
- effort: Medium. Requires defining a schema, wiring route exposure in the Worker, and aligning orchestrator/grants with the same contract.  ·  risk: Low to medium. Risk is exposing internal details; mitigate by limiting output to non-sensitive capability descriptors and redacting tokens or secrets. Recovery is straightforward: disable the endpoint or roll back schema.
- cost: Low API cost. Mainly developer time. Minimal runtime overhead for a cached capability payload.  ·  latency: Positive: fewer wasted probes and failed tool attempts; faster routing decisions.
- security: Must ensure no secrets, bearer tokens, or owner data leak; output should be public-safe metadata only.
- depends on: Shared typed capability schema between orchestrator and relay


## What it asked for

_Nothing._
