# Harness derivation — mac-planner — round 65

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **mac-planner live readiness** — Mac bridge is online but not ready for UI automation: Accessibility trusted=false and Screen Recording granted=false. Browser bridge home-chrome is offline with 3 pending commands, so browser actions cannot safely run or be replayed blindly.
  - evidence: GET /ops/status at 2026-08-07T11:04Z reports macBridgeOnline=true, accessibility.trusted=false, screenRecording.granted=false, browser.online=false, pendingCommands=3; GET /browser/status confirms same.

## Capabilities it proposed

### "“When I ask ‘why is this here?’ or ‘what changed?’, give me one evidence-backed answer across my Mac, private browser tabs, Calendar/Mail, and the pendant’s action history—with the exact source, timestamp, and what I can undo or review next.”"
- **useful because:** Today each surface can report its own facts, but the owner cannot audit a cross-device decision without manually hunting through tabs, mail, files, and receipts. A single spoken answer with a compact evidence chain makes the system trustworthy and lets the owner catch stale or incorrect automation before it matters.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use the cheaper background model to assemble and normalize deltas/evidence; use gpt-realtime-2.1 only to answer the live spoken question and compress the cited result for audio. mac-planner reads Calendar/Mail and action receipts; browser-extension reads only already-open authenticated tabs; relay joins the evidence and serves a signed answer; dashboard exposes clickable source snippets and undo/review links.
- **latency:** Precompute a compact evidence index after each completed job and on a low-frequency schedule (seconds to a few minutes, no live-model spend). A spoken audit query should return an initial answer in under 2 seconds, with deeper source hydration within 5 seconds. Never block on an offline browser: label its evidence unavailable and continue with explicit freshness.
- **cost:** Roughly $0.005–$0.03 per background delta/index cycle depending on source volume, dominated by model normalization; live audit queries ~$0.01–$0.04, dominated by realtime response and any browser extraction. Hashing unchanged snippets locally avoids resending full pages and reduces context cost.
- **security:** Private mail, calendar, authenticated-page snippets, and action receipts leave the Mac only as a minimized, redacted evidence capsule; raw bodies stay local by default. Each citation needs source URL/app, timestamp, snippet hash, and sensitivity label. Never expose secrets or hidden tab content; require explicit user intent for a named private source. Undo links must map to existing receipts and state honestly when an action is irreversible. If a source is stale/offline, say so rather than infer.
- **missing:** A cross-surface evidence ledger with content hashes, timestamps, provenance, sensitivity, and retention/erase controls; A joiner that links Mac read capsules, browser extraction results, pendant utterance/job IDs, and action receipts into one evidence graph; A small relay endpoint for cited audit queries and signed, expiring source capsules; Dashboard and pendant response format for ‘why/what changed’ with source drill-down and undo/review affordances; A background scheduler that indexes only changed content and a freshness contract for offline browser tabs

### "“Use my private information for this one task, but don’t remember it afterward—and show me exactly what was accessed, where it went, and that the temporary copies were deleted.”"
- **useful because:** The owner must currently choose between giving the system broad ongoing access or withholding data and losing useful automation. A purpose-bound, verifiable privacy mode would make sensitive one-off tasks practical: the owner gets the result without silently expanding long-term memory or leaving browser, relay, Mac, or audio remnants behind.
- **path:** pendant → relay-realtime → mac-planner → browser-extension → dashboard
- **model tier:** Use a cheaper background model for local redaction, access accounting, and deletion verification; reserve gpt-realtime-2.1 for the owner’s live request and a short spoken confirmation. The relay issues a signed, expiring purpose token; Mac and browser enforce it at read/export boundaries; the dashboard shows the resulting audit receipt.
- **latency:** Token issuance and local policy checks under 200 ms. A normal one-off task should add less than 1 second. Deletion verification can continue asynchronously, with the pendant announcing completion or any residue within 10 seconds.
- **cost:** Approximately $0.002–$0.02 per invocation, mostly cheap redaction/classification and receipt generation; no additional model call is needed when data is already structured. Storage and hashing are local and small.
- **security:** The policy must be enforced by components, not merely promised by the model. Sensitive values should be redacted before relay transmission where possible; relay payloads need envelope encryption, short TTLs, and no inclusion in general memory/context projection. Mac/browser temporary files, screenshots, clipboard contents, model traces, caches, and generated audio need an erase manifest. If deletion cannot be verified, the system must say so plainly and identify the residue. The owner must explicitly choose the purpose and retention scope, but not approve every routine read within that scope.
- **missing:** A purpose-token and capability-scope protocol shared by relay, Mac, and browser; Enforced ephemeral storage namespaces with TTL and cryptographic erase receipts on Mac, relay, and browser bridge; A memory/context firewall that rejects purpose-scoped capsules from durable memory and future prompt projections; Redaction and egress accounting at every surface boundary, including screenshots and generated audio; A dashboard/pendant privacy receipt that lists accessed sources, transformations, destinations, expiry, and deletion status


## Changes it proposed to its own stack

### `integration` — Add a fleet readiness and recovery coordinator spanning relay, Mac bridge, browser extension, and pendant. Each node publishes a short-lived capability lease (online, permissions, foreground/session identity, queue depth, last-seen). Before dispatch, the relay classifies a job as runnable, deferred, or unsafe-to-replay; on reconnect it reconciles command IDs and leases, drops expired browser commands by default, and sends the pendant a concise recovery prompt. The Mac side should expose a guided one-click repair path for missing Accessibility/Screen Recording and the browser side an explicit extension-heartbeat repair page, without replaying stale mutations.
- **owner gets:** The owner currently gets opaque failures after a 45-second wait, and three browser commands are stranded while the bridge is offline. This would turn “it didn’t work” into an immediate, truthful “browser is offline; nothing was replayed; tap to recover,” then resume only the still-valid work when the Mac and browser return.
- effort: Medium-high: shared lease schema, durable reconciliation state machine, relay endpoints, Mac/browser health probes, pendant notification UX, and tests for crash/reconnect races.  ·  risk: A bad lease or clock could defer valid work or incorrectly mark a node healthy. Mitigate with monotonic server timestamps, short leases, idempotency keys, explicit expired-command states, and a dashboard repair/retry action. Recovery is safe because stale irreversible browser mutations are never auto-replayed.
- cost: Small persistent D1/local JSON growth for leases and command states; negligible model cost. One background health update per node per 15–60 seconds. Engineering cost is chiefly reconnect and race-condition testing.  ·  latency: Adds tens of milliseconds to dispatch when leases are fresh; avoids the current tens-of-seconds timeout on an offline browser. Reconnect reconciliation runs asynchronously.
- security: Capability leases must contain no page contents or secrets. Bind leases to paired device IDs and signed request IDs; expose only coarse permission states to relay. Repair URLs/actions must be local and authenticated.
- depends on: A durable browser command queue with request IDs and tab/session affinity; A receipt/undo ledger that records failed, expired, and completed commands; A relay-to-Mac/browser heartbeat endpoint and a small pendant notification/status protocol


## What it asked for

_Nothing._
## Its own summary

Discovered the current fleet state and added two new items beyond the repeated backlog: (1) an evidence-backed cross-surface audit capability for “why is this here?/what changed?”, joining Calendar/Mail, authenticated tabs, Mac receipts, and pendant history with source hashes, freshness, and undo/review links; (2) a fleet readiness/recovery coordinator that leases node capabilities, prevents stale browser replay, and gives immediate pendant recovery status. Live evidence: Mac bridge is online but Accessibility and Screen Recording are not granted; browser bridge is offline with three pending commands. I recorded this finding.

**Biggest unknown:** The newly granted mac_readonly_inspect tool has a schema but no implementation, so I cannot verify running apps, foreground app, or UI state directly. I also still lack the evidence-ledger, readiness-lease, and browser-reconciliation endpoints needed to implement the proposals; browser availability and permission repair remain the immediate operational blockers.

