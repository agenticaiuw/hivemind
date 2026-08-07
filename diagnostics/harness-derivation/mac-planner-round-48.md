# Harness derivation — mac-planner — round 48

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner readiness** — The newly granted mac_readonly_inspect tool is present but unimplemented: all three inspection operations returned that error. Live ops snapshot still reports browser offline with 3 pending commands, Accessibility untrusted, Screen Recording missing, while Mac bridge and relay are online.
  - evidence: GET /ops/snapshot HTTP 200 and three mac_readonly_inspect calls returned 'This tool was granted a schema but has no implementation yet.'

## Capabilities it proposed

### "“If I ask you to do something while my browser or Mac is unavailable, remember it safely, tell me what is waiting, and finish it when the right device comes back—without acting on stale information.”"
- **useful because:** Today the relay and Mac are reachable, but Chrome is offline with three pending commands and Mac automation is not ready. The owner needs an honest degraded mode: capture intent once, avoid silent replay, and get a concise pendant status plus a completion receipt when connectivity and permissions recover.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** background for queue classification, freshness checks, and reconciliation; realtime only for the one-sentence spoken acknowledgement and interruption handling
- **latency:** Immediate acknowledgement under 1 second; reconnect reconciliation within 10 seconds; no expensive model call if a deterministic state/freshness check resolves it
- **cost:** Usually one short background call (~2–4k input tokens) per queued intent and one deterministic reconnect pass; realtime cost only when the owner is actively speaking
- **security:** Persist only the intent, required device/origin scope, sensitivity, and expiry—not page contents or secrets. Never replay browser mutations after an epoch change or stale deadline. Speak that an item is queued without exposing private details; require the existing owner confirmation policy for sending, deletion, purchases, or submissions.
- **missing:** A shared intent ledger/state machine spanning relay, Mac jobs, and browser commands; A pendant-visible queue/status and cancel operation that works offline; Connectivity/permission change events from Mac and browser, plus deterministic stale-intent and timezone validation before resume; A reconciliation receipt linking the original voice request to each attempted device action

### "“For this request, keep my data local—or let it use the browser and relay—and prove afterward exactly where the data went.”"
- **useful because:** The owner cannot currently express a per-request privacy boundary that is enforced across the pendant, Cloudflare relay, Mac, and authenticated browser. This would let them use the hive for sensitive work without guessing which surface received page text, audio, files, or credentials, while still allowing broader routing for ordinary tasks.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Deterministic policy compiler and audit verifier for routing and receipts; background model only to translate natural-language privacy instructions into a typed policy. Realtime is unnecessary except for a brief spoken acknowledgement.
- **latency:** Compile and attach the policy in under 100 ms; enforce it on every hop without an extra model round trip. Produce a human-readable receipt within 2 seconds of completion.
- **cost:** Negligible per-hop policy checks and receipt storage; one background call (~1–2k input tokens) only when the spoken boundary is ambiguous. Storage is bounded by retaining hashes and metadata rather than payloads.
- **security:** The policy must fail closed: a relay or browser route lacking the required residency label cannot receive the request. Receipts should contain destination, data class, timestamps, hashes, and retention/deletion status—not secrets or page contents. The pendant needs an offline-visible policy state and a physical cancel/clear gesture. Compromised software cannot honestly attest itself, so Mac/browser builds need signed capability and deletion attestations.
- **missing:** A typed per-request data-residency policy and propagation protocol understood by pendant, relay, Mac, and browser; Signed capability declarations from each surface (what it may receive, store, and delete) and fail-closed enforcement at ingress; A tamper-evident cross-surface audit receipt with payload hashes, retention deadlines, and deletion acknowledgements; Pendant UI/LED/audio feedback for the active privacy boundary and an offline emergency cancel/clear control; Dashboard views and tests for policy violations, rejected routes, and incomplete deletion attestations


## Changes it proposed to its own stack

### `context` — Add a deterministic cross-surface temporal authority and stale-action guard. Every scheduled or delayed intent carries the owner's profile zone (currently America/Chicago), the Mac-reported zone (currently America/New_York), the browser locale/zone when available, creation time, expiry, and a human-readable local-time rendering. On creation, the relay resolves relative times against the owner's zone; if device zones disagree, it marks the intent timezone_conflict and asks once. On reconnect or execution, Mac and browser must revalidate the zone, permissions, session/connection epoch, and freshness before acting; otherwise the item remains queued and the pendant speaks a short explanation. Dashboard shows both zones and the exact next-run instant.
- **owner gets:** Prevents a silent two-hour scheduling error and prevents stale browser or Mac actions after the current offline/permission state changes. The owner gets one clear question instead of discovering a wrong reminder or action later.
- effort: Medium: typed temporal metadata in relay/job schemas, deterministic resolver and reconnect preflight, Mac/browser status events, pendant status/cancel utterances, dashboard rendering, and tests across DST transitions.  ·  risk: Existing routines could be delayed or ask an extra question when the profile zone is intentionally different. Recover by allowing a per-intent explicit zone (“9 AM New York”), and by preserving the original intent for edit/cancel rather than dropping it. No action should execute on unresolved conflict.
- cost: Negligible storage and deterministic CPU; occasional background model call only to phrase an unusual conflict. No realtime call required for normal scheduling.  ·  latency: Normal requests unchanged; conflict detection is sub-100 ms. Reconnect adds one status/preflight round trip, typically under 1 second.
- security: Improves safety by preventing stale authenticated actions. Zone and device metadata are low sensitivity; never persist page contents or credentials in the ledger.
- depends on: Shared intent ledger/state machine across relay, Mac jobs, and browser commands; Connectivity and permission change events; Browser command epoch leases and re-auth resume


## What it asked for

_Nothing._
## Its own summary

I discovered and recorded two new gaps beyond the backlog: (1) a cross-surface offline intent ledger so voice requests survive browser/Mac outages without stale replay, with pendant status/cancel and receipts; (2) a deterministic timezone/staleness guard because the owner profile is America/Chicago while the Mac reports America/New_York. Current live state: relay and Mac bridge online, Chrome offline with 3 pending commands, Accessibility and Screen Recording unavailable. I also verified the newly granted mac_readonly_inspect schema has no implementation yet.

**Biggest unknown:** Whether the owner wants the profile timezone (Chicago) to be authoritative for all delayed actions, or whether some calendars/browser accounts should override it per intent.

