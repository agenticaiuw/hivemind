# Harness derivation — faculty-action — round 212

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "“Do this across my Mac and browser, and don't tell me it worked until you independently checked it; if the result is ambiguous, stop and give me one safe retry or cancel choice.”"
- **useful because:** This is the system's highest-value promise: a spoken intent becomes one operation spanning the relay, the logged-in browser and Mac, with idempotency and an independent postcondition check. It prevents the worst failure mode—claiming an email/payment/file change happened when the executor only reported an attempt—and turns unknown outcomes into a recoverable decision rather than a duplicate action.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action → dashboard
- **model tier:** Realtime only for intent capture and the short status reply; a cheaper background model plans the multi-step operation. faculty-perception performs deterministic checks, not a language-model guess.
- **latency:** Initial acknowledgement under 500 ms; execution may take seconds. Verification must finish before success is spoken. Unknown results should surface within 2 s, with retry/cancel held until explicit owner choice.
- **cost:** Usually one realtime turn plus one small planner turn; roughly $0.01–$0.05 depending on the operation. Deterministic Mac/browser receipts and verification dominate latency, not tokens.
- **security:** Never send page secrets or form contents to the pendant or relay. Bind every step to an operation ID, action digest, expiry and idempotency key. Require the existing physical transaction approval latch for irreversible actions. On unknown, never auto-retry a non-idempotent step; expose the exact safe recovery. Private evidence should be hash-only by default.
- **missing:** A live, resolvable read-only verifier (the granted verify_operation_step schema is currently unresolved) that can check app/file/browser postconditions with provenance.; A shared operation ledger linking executor receipts, verifier evidence, retry decisions and the pendant's approval nonce.; Idempotency-key support and safe retry policies per action class in POST /execute and browser execution.

### "“Bookmark this moment.”"
- **useful because:** A bookmark should preserve what the owner meant, not merely a timestamp or an audio file. The pendant captures the moment locally; the Mac contributes the foreground app and open work; the browser contributes the active tab and page title; the relay joins them into a privacy-scoped, searchable capsule. Later “what was I looking at when I said that?” becomes answerable even if the link dropped at the moment of capture.
- **path:** pendant → ESP32 audio bridge → relay → mac-planner → browser-extension → faculty-perception → dashboard
- **model tier:** Realtime is unnecessary after the button event. A small background model may summarize the owner's spoken bookmark after delivery; raw capture and joining are deterministic.
- **latency:** The pendant must acknowledge locally in under 100 ms and persist the event without waiting for LTE. Host/browser snapshots can arrive within 2 s; delayed components are attached later without rewriting the original event.
- **cost:** Near-zero when no summary is requested; one small background inference (well under $0.01) only for an optional title or tags. Storage is a few KB per bookmark plus any failure-path audio already permitted by the existing spool.
- **security:** The capsule must default to private. Store URL/title hashes or origin-only metadata unless the owner asks for full context; never copy page bodies, passwords, clipboard contents or microphone audio into the relay by default. Each component carries its own timestamp and freshness, so a stale browser snapshot cannot masquerade as contemporaneous evidence. Retain and delete on the existing owner-controlled policy.
- **missing:** A typed context-capsule/join route that accepts independently timestamped pendant, host and browser observations and preserves partial arrival.; A browser snapshot contract exposing active tab identity/title with sensitivity labels and freshness, without page secrets.; A user-facing retrieval/search surface for asking about bookmarks and inspecting or deleting their component data.

### "“Keep an eye on this page and tell me when the thing I care about changes—don't buy or submit anything.”"
- **useful because:** The pendant is ideal for a durable watch that starts from the owner's authenticated browser without making the owner keep a tab open or remember a reminder. The relay schedules checks while the Mac sleeps; when the logged-in browser is needed, it asks the browser extension for a narrow field observation, then alerts the pendant with the before/after evidence. This turns the hive into an agent that notices change without silently acting.
- **path:** pendant → browser-extension → mac-planner → relay → faculty-perception → faculty-action
- **model tier:** Use a cheap background/scheduled model only to interpret the owner's watch condition and normalize page observations. Use realtime only when the pendant delivers the alert or the owner asks a follow-up. Prefer deterministic selectors and hashes over model interpretation after setup.
- **latency:** Creating a watch should take under 10 s. Poll cadence can be minutes to hours, bounded by site rate limits. Alert delivery should begin within 30 s of a detected change; if the browser is unavailable, report stale/unknown rather than claiming no change.
- **cost:** Low ongoing cost: scheduled browser observation plus small state comparisons; roughly $0.001–$0.02 per check depending on model use. Browser session and relay wakeups dominate operational cost.
- **security:** Read-only by construction: no clicks, typing, purchases or submissions. Scope each watch to one origin, selector and expiry; redact secrets and page bodies, store only a normalized value/hash and provenance. Require renewed browser permission when the session or origin changes. The pendant alert should identify the site and change, not expose private page contents aloud in public.
- **missing:** A durable scheduled-watch record with owner, origin, selector/condition, cadence, expiry, last observation and change provenance.; A browser read-only observation endpoint that can run later against the bound session and return a sensitivity-labeled field, not an arbitrary page dump.; Relay scheduling and deduplicated alert delivery to the pendant, including a clear stale/blocked state when the browser is offline.; An owner-facing list/pause/delete control for active watches.

### "“For this one task only, let you use my logged-in browser on this site; when it’s done, revoke access and show me exactly what the permission covered.”"
- **useful because:** Today, a browser session is effectively all-or-nothing: either the agent can reach a logged-in tab or it cannot. The owner should be able to grant a narrow, temporary capability—one origin, one operation class, one expiry—without exposing credentials or granting an indefinite session. The pendant confirms the scope, the browser extension enforces it, and the relay produces a revocation receipt. This is safer than asking the owner to trust an opaque browser connection and more useful than a generic approve button.
- **path:** pendant → relay → browser-extension → mac-planner → faculty-judgement → faculty-action → dashboard
- **model tier:** Realtime handles the spoken scope and concise confirmation; deterministic policy code compiles it into an allowlist. A cheaper background model may summarize the final audit record, but must not decide scope or enforcement.
- **latency:** Scope preview and physical confirmation within 1–2 s. Enforcement must be synchronous at every browser command; revocation should occur immediately on completion, expiry, cancellation or link loss.
- **cost:** Negligible inference cost after the initial voice turn; implementation cost is in browser-extension enforcement, signed leases and audit storage. Roughly <$0.01 per invocation in model usage.
- **security:** Never transmit passwords, cookies or page bodies to the relay or pendant. The lease must be signed, origin-bound, command-class-bound, monotonic and single-use where possible. Default deny on ambiguity, browser restart, origin redirect, stale lease or clock disagreement. The owner must see a human-readable scope before confirmation; every command and revocation gets an append-only audit record. Irreversible actions still require the existing physical transaction approval latch.
- **missing:** A browser-extension enforcement layer that rejects commands lacking a signed, unexpired, origin- and action-class-scoped lease.; A relay lease issuer/revoker with monotonic sequence, expiry, cancellation and crash-safe deny-by-default state.; A typed scope preview and audit UI on the dashboard/pendant that cannot include secrets.; A command envelope carrying the lease ID so browser receipts can be joined to the exact grant and revocation.

### "“Work with this private page, but keep the page contents on my Mac; send the relay only the minimum result needed to answer me.”"
- **useful because:** The owner currently has to choose between useful browser automation and trusting a remote service with page contents. A confidential mode would keep DOM text, files and form values inside the Mac/browser boundary while the relay receives only a typed intent, redacted progress, and a narrow result. This makes sensitive tasks—medical portals, finances, private messages—practical without turning the pendant or relay into a copy of the owner's accounts.
- **path:** pendant → relay → mac-planner → browser-extension → faculty-perception → faculty-action → dashboard
- **model tier:** Use a local Mac model or deterministic extractors for DOM/file interpretation; realtime is only for the owner's command and final response. The relay must not call a general model on raw page content in this mode.
- **latency:** Command acknowledgement under 500 ms; local page processing within a few seconds. If a step needs information that cannot be safely reduced to the declared output schema, pause and ask the owner rather than uploading it.
- **cost:** Remote model cost can be near zero for the sensitive path; local compute and browser execution dominate. Optional local inference may use the Mac's resources without per-call API cost.
- **security:** Enforce the boundary technically, not by prompt: browser extension and Mac agent must reject telemetry containing raw DOM, screenshots, clipboard, cookies, or typed secrets. Declare an output schema before execution, redact logs, encrypt local scratch state, and show the owner what fields may leave the Mac. Physical approval remains required for irreversible submission. A compromised Mac is inside the trust boundary and must be disclosed.
- **missing:** A local-only execution mode with an enforceable egress firewall between browser/Mac and relay.; Typed result schemas and taint tracking so page-derived secrets cannot enter receipts, prompts, logs or pendant speech accidentally.; Local audit and deletion controls showing exactly what stayed on-device and what minimal fields crossed the boundary.; A browser-extension capability to perform DOM operations and return schema-conforming values without screenshots or raw page serialization.


## Changes it proposed to its own stack

### `hardware` — Add a small secure-element coprocessor (for example, an I2C Ed25519/HMAC device) to the pendant's production jewellery board, with a device-unique non-exportable key, monotonic counter support, and a firmware API that signs approval, lease, bookmark, and delivery receipts. Provision each unit at manufacture and reject unsigned firmware/configuration that attempts to read the private key.
- **owner gets:** The owner gets a pendant whose physical confirmations and private browser-access grants are cryptographically tied to that particular piece of jewellery. A stolen relay token, copied firmware image, or replayed approval cannot impersonate the pendant or silently authorize an action.
- effort: Production-board redesign, secure-element driver and provisioning ceremony; moderate hardware/firmware effort plus factory key-management work. Prototype first on the current nRF9160 DK with an external breakout before committing the enclosure.  ·  risk: Provisioning mistakes could permanently brick identity or make recovery impossible. Use a signed manufacturing certificate, an explicit key-rotation/replacement path, and keep a non-secret recovery identifier. Firmware should fail closed for high-risk approvals but remain usable for ordinary recording if the secure element is unavailable.
- cost: Approximately $0.50–$2 per production unit plus PCB/layout and provisioning tooling; a few mA only during signing, negligible standby impact.  ·  latency: Typically tens of milliseconds per signature, acceptable before a deliberate approval is acknowledged; do not put signing in the audio callback.
- security: Substantially strengthens physical_transaction_approval_latch and scoped browser leases by preventing key extraction and replay. It introduces manufacturing-key custody and supply-chain trust, which must be audited.
- depends on: Define the production pendant board/enclosure rather than treating the DK as the product.; Specify the canonical signed envelope and rotation/revocation protocol for approval and lease receipts.; Bring the current i2c2 bus up carefully; the secure element must not interfere with the existing audio path.


## What it asked for

_Nothing._
## Its own summary

Recorded three capabilities this round: (1) cross-surface operation execution that refuses to claim success until an independent postcondition verifier checks it, and safely handles unknown outcomes; (2) a privacy-scoped “Bookmark this moment” capsule joining pendant audio/time with Mac and browser context; and (3) a read-only durable browser watch that alerts the pendant when a watched field changes without submitting anything. The live inventory confirms Safari and the Mac bridge are online, but no pendant is registered.

**Biggest unknown:** The granted verify_operation_step tool is still unresolved: it does not reach faculty-perception and falls back to unrelated routes. I still need a live typed verifier with provenance, plus a shared operation ledger/idempotency layer. For physical end-to-end testing I still need a registered pendant/LTE path; USB remains bench-only.

