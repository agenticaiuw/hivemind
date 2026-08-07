# Harness derivation — relay-realtime — round 110

Model: `gpt-realtime-2.1`  ·  probes against `https://ai-pendant-relay.evan20050827.workers.dev`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "If that task needs live web access, use a safe server browser when my Mac is offline, and tell me what you did and what you found."
- **useful because:** The owner is often away and the Mac may be asleep. This lets the system continue public web tasks without waiting for the Mac, while still reporting results through the pendant.
- **path:** relay → browser → pendant → mac-bridge
- **model tier:** Realtime for intent capture; background model for browsing/extraction; relay for summarization.
- **latency:** Quick acknowledgment on the pendant; browsing takes as long as needed; summary when done.
- **cost:** Moderate; dominated by browser runtime and extraction steps.
- **security:** Keep it to public pages unless authenticated context is explicitly available. Avoid storing raw page content unnecessarily; store extracted facts with provenance.
- **missing:** Implementation of server_browser_actions; A durable job runner for long-running browse tasks; Receipt format for extracted data and actions

### "“What changed across my Mac and my authenticated browser since I last talked to you? Give me only changes that affect me, say where each came from, and let me act on one by voice.”"
- **useful because:** Today the owner must interrogate each surface separately and cannot get a trustworthy, interruption-safe delta while away from the Mac. A single causal digest would merge Mac receipts, browser-session observations, and relay events, suppress duplicates, cite the source and time, and turn a selected item into an actionable handoff without making the owner remember which machine saw it.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use a cheap background summarizer for event clustering and deduplication; use relay-realtime only to understand the spoken query and present the final short answer; use mac-planner/mac-vision only when the owner selects an item requiring Mac inspection or action.
- **latency:** Initial spoken answer under 2 seconds from an already-built digest; an on-demand source check may take up to 8 seconds, with the pendant receiving a brief progress acknowledgement.
- **cost:** Usually well below one realtime turn: roughly $0.001–$0.01 per digest depending on event volume, plus a normal realtime turn only for the voice exchange. Mac/browser checks dominate latency, not model tokens.
- **security:** The digest crosses authenticated browser and Mac activity and could reveal sensitive titles or page contents over audio. Store only hashes, timestamps, source labels, and minimal redacted snippets by default; fetch full content only for the selected item, encrypt retained projections, and never read unrelated tabs. Any mutation still produces an existing receipt and remains subject to the owner's no-gate maximum-access policy.
- **missing:** A relay-owned append-only cross-surface event journal with per-surface cursors and deduplication keys; A durable 'last heard/last acknowledged' cursor tied to the pendant session; Mac and browser adapters that emit normalized change events with source citations rather than only final action results; A background digest worker and a typed voice query/action protocol; A spoken-item selector that can survive a dropped LTE link and resume from the same digest item

### "“Handle this privately—use my Mac or its logged-in browser, never send the page or my dictated text to a cloud browser; tell me if you cannot do it that way.”"
- **useful because:** Today routing is primarily capability-based, so an owner cannot express a data-residency constraint and know it was honored. This would let the worn front door safely handle confidential work while away from the Mac: the relay classifies the request, routes sensitive reads/actions to the local Mac/browser session, refuses cloud fallback when offline, and gives a concise spoken explanation instead of silently leaking content.
- **path:** pendant → relay → mac-planner → mac-vision → browser-extension → dashboard
- **model tier:** Use relay-realtime for intent and sensitivity classification only; use a cheaper local or background classifier for redaction/audit metadata. The Mac planner and browser extension perform the actual private operation; no cloud model receives page text or raw dictation after routing.
- **latency:** Routing decision and spoken acknowledgement under 500 ms. Local execution can take the normal Mac/browser action latency, with a short offline/unavailable response rather than waiting indefinitely.
- **cost:** Near-zero incremental API cost for routing metadata; local Mac/browser execution dominates. Optional audit summarization costs under $0.005 per event when enabled.
- **security:** The relay must not log raw sensitive utterances or page content, and must cryptographically attest which execution surface handled each step. Prevent fallback to server_browser_actions after local failure unless the owner explicitly changes the constraint. Keep only redacted action type, destination surface, and receipt hash in the dashboard; clearly disclose that the Mac itself and its browser extensions remain trusted endpoints.
- **missing:** A first-class per-request data-residency/privacy constraint in the intent contract; A relay router that can inspect live surface availability before choosing a target and enforce no-fallback semantics; Local Mac/browser receipts containing an attested execution surface and redaction status; A pendant-visible privacy mode with a one-button or spoken way to end it; Dashboard controls to review and revoke cloud-routing defaults without exposing content


## Changes it proposed to its own stack

### `relay` — Publish a relay-native capability inventory route and event feed (e.g., GET /relay/capabilities and GET /relay/events) that reflects the worker’s own routes, tool schemas, granted contexts/permissions, and recent intent-routing decisions. Provide stable identifiers and versions so other surfaces can reason about what the relay can do without scraping prompts.
- **owner gets:** It reduces misrouted requests and “I thought you could do that” failures. The owner gets more consistent behavior: the pendant can correctly route, explain limits, and avoid re-asking for already-granted tools.
- effort: Medium: add route registration and a compact serializer, plus a small audit log for routing decisions.  ·  risk: Exposure of internals if the endpoint leaks sensitive config. Mitigate by returning only non-secret metadata and requiring existing authentication.
- cost: Low per call; responses are small metadata. Biggest cost is initial engineering and tests.  ·  latency: Low; avoids extra discovery calls and failed attempts.
- security: Improves security posture through explicit, authenticated introspection rather than ad-hoc probing.
- depends on: Authentication already in place for relay routes; A minimal audit log or ring buffer for routing decisions

### `relay` — Add a request-scoped residency envelope to the live voice pipeline: {allowedSurfaces:[local_mac,local_browser], forbidCloud:true, retention:none}. The relay must carry it through /pipeline/audio, /pipeline/events, /plan, and /execute, reject any downstream result lacking an attested surface receipt, and return a spoken failure rather than silently falling back. Persist only a salted receipt hash and the envelope, not transcript or page data.
- **owner gets:** The owner can say “private” once and reliably know confidential dictation and authenticated-page work stayed on their own devices, even when the Mac is unavailable; today the available routes do not provide that guarantee.
- effort: Medium: envelope schema, propagation through relay and Mac/browser bridges, attestation field in receipts, failure-path tests, and a pendant-visible mode indicator.  ·  risk: A missing propagation edge could create a false privacy guarantee; default to fail-closed for requests marked private, and expose an audit warning if an adapter cannot attest its surface. Non-private requests remain unchanged.
- cost: Negligible storage and token overhead; no new model call. Engineering cost is in adapter and integration tests.  ·  latency: Less than 100 ms for envelope validation; local execution latency unchanged. Failure may be faster because cloud fallback is prohibited.
- security: Improves confidentiality by preventing accidental cloud routing and transcript retention, but depends on honest local adapter attestation and secure relay-to-Mac authentication.
- depends on: A shared typed envelope understood by the relay, mac-planner, browser-extension, and receipt service; Surface attestation in existing action receipts; A clear spoken/button toggle for private mode on the pendant


## What it asked for

_Nothing._
## Its own summary

Recorded a new cross-surface capability: a spoken, source-cited “what changed since I last talked” digest, plus a privacy-constrained routing capability and the relay change needed to enforce local-only handling with fail-closed behavior and attested receipts. No further discovery performed this round.

**Biggest unknown:** Whether the relay already has an undocumented event journal/cursor or surface-attestation primitive; implementing the proposals requires confirming those internals rather than assuming the listed routes provide them.

