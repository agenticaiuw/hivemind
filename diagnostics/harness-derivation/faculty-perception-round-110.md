# Harness derivation — faculty-perception — round 110

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **browser_bridge_live_state** — At 2026-08-07T15:08:39Z, Safari browser bridge is online (extension v1.2.0), with 3 tabs and zero pending commands. Its reported active tab URL is https://example.com and title is 'Failed to open page'; the durable session snapshot labels the same tab 'Inbox (14,987) - evan20050827@gmail.com - Gmail'. This discrepancy is unresolved and should not be treated as proof of page contents.
  - evidence: GET /browser/status and GET /observe returned HTTP 200 with these values.
- **mac_agent_input_reachability** — The Mac agent is online and browser bridge is online, but Accessibility and Screen Recording are not granted to the running AI Pendant Agent binary. /observe reports inputReachability.status='failed', eventsPost=false, uiActionsWillReachTheScreen=false; UI action receipts are therefore untrusted even though automation permissions are cached as granted for many apps.
  - evidence: GET /ops/status and GET /observe at 2026-08-07T15:08:42Z.
- **timezone_conflict** — Owner memory states authoritative timezone America/Chicago, while live GET /machine-context reports machine timezone America/New_York. This conflict is unresolved; time-based actions should not infer timezone from machine context alone.
  - evidence: Owner projection from discover(owner) and live GET /machine-context HTTP 200.

## Capabilities it proposed

### "Before you act on my browser or schedule anything, tell me if the live page identity and clock context are trustworthy."
- **useful because:** Today the bridge can report a URL/title pair that disagrees with its durable session snapshot, and the owner's remembered timezone disagrees with the machine timezone. A perception gate would prevent the system from confidently reading the wrong tab or scheduling at the wrong local time.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** deterministic checks first; background model only to explain a persistent discrepancy; realtime only when the owner is waiting
- **latency:** under 300 ms for URL/title/session and timezone checks; no model call for the common consistent case
- **cost:** near-zero API cost in the consistent case; occasional small background explanation call when discrepancies persist
- **security:** Do not expose page contents merely to reconcile identity. Return metadata and confidence only; require confirmation before using a low-confidence tab or timezone for destructive or time-sensitive actions.
- **missing:** A durable cross-surface perception snapshot endpoint that atomically captures browser heartbeat/status, session metadata, and machine/owner timezone sources; A policy in faculty-judgement that refuses page reads or scheduled execution when identity/timezone confidence is low; A browser heartbeat/session contract that includes a monotonic snapshot id and canonical URL/title pair

### "Read the page I mean, and prove to me which tab you read before you summarize it."
- **useful because:** The live bridge currently exposes a contradictory identity: the active tab reports https://example.com/'Failed to open page' while the durable session labels that tab as a Gmail inbox. The owner cannot safely distinguish a stale session record from the page actually being read, so browser answers can be confidently wrong.
- **path:** browser-extension → mac-planner → relay-realtime → faculty-perception → faculty-judgement
- **model tier:** Deterministic browser metadata and challenge verification; use the cheaper background tier to summarize only after the proof passes; realtime is reserved for the spoken response.
- **latency:** Under 1 second for a fresh heartbeat plus tab proof; summarization may take the normal background latency.
- **cost:** Negligible API cost for proof metadata; one background summarization call only after verification, with page length dominating tokens.
- **security:** Return origin, tab/window id, heartbeat sequence, title, URL, and a short DOM/content digest—not passwords, cookies, or full page text in the proof. Never treat a session label as authoritative. If identity is stale or conflicting, refuse the summary and ask the owner to focus/reload the tab.
- **missing:** Browser-extension protocol for an atomic tab-attestation response containing tabId, windowId, frame URL/origin, title, heartbeat sequence, and content digest; Relay persistence for the attestation and its expiry, bound to the requesting session; Judgement rule requiring a fresh attestation before page reads and including the attestation in the spoken/cited receipt

### "Schedule this for 9 AM my time, and tell me exactly which timezone and calendar zone you used."
- **useful because:** The owner's remembered timezone is America/Chicago while live machine context says America/New_York. Today a routine or reminder can silently use the wrong zone, especially across relay, Mac, and calendar. The owner needs a visible, deterministic temporal interpretation rather than a plausible-looking confirmation.
- **path:** relay-realtime → faculty-perception → faculty-judgement → mac-planner → mac-terminal
- **model tier:** Deterministic timezone/DST resolution and calendar API operations; background model only for ambiguous natural-language time phrases; no realtime escalation beyond the owner's conversational turn.
- **latency:** Under 500 ms to resolve timezone and present the interpretation; calendar write within 2 seconds after confirmation.
- **cost:** Near-zero model cost for explicit times; small background call only for phrases such as 'after lunch'.
- **security:** Never silently choose between conflicting timezone sources. Show local time, IANA zone, UTC instant, DST offset, and target calendar zone; require confirmation when sources disagree or the event crosses a date boundary. Do not transmit calendar contents to the relay beyond the minimum event metadata.
- **missing:** A signed owner-authoritative timezone preference available to relay and Mac planner (not merely a memory projection); Calendar write/read contract that returns the calendar's actual IANA timezone and event instant; Judgement policy for conflict, DST gaps/overlaps, and stale timezone preferences


## Changes it proposed to its own stack

### `integration` — Add a read-only /perception/snapshot aggregator in the Mac agent that captures browser status, durable browser sessions, /observe input reachability, machine timezone, and owner timezone projection under one snapshotId and timestamp. Compute explicit fields: browserIdentity=consistent|conflict|unknown, inputTrust=trusted|untrusted, timezone=owner|machine|conflict. Never return page content. Make faculty-judgement consume this snapshot before browser reads or time-based execution.
- **owner gets:** The assistant will stop claiming it is looking at the right page or using the right local time when the system's own observations disagree, and can explain exactly what needs fixing.
- effort: Moderate: one aggregator, schema tests for stale heartbeats and mismatched tab metadata, and a judgement policy hook.  ·  risk: A stale or partially unavailable source could over-block. Recover by marking fields unknown rather than failing open; permit harmless read-only inspection with an explicit low-confidence warning.
- cost: No recurring model/API cost; one local authenticated GET and small JSON payload per gated action.  ·  latency: Approximately 10–50 ms locally, plus relay round-trip only if requested through voice.
- security: Improves safety by reducing confused-deputy actions; metadata-only output avoids leaking page content. Owner timezone is sensitive context and should remain scoped to judgement.
- depends on: An owner-timezone projection API or signed context value (currently only discover(owner) exposes it); Judgement integration point that can enforce confidence gates

### `browser-harness` — Replace the bridge's split tab reporting with one atomic TabAttestation message: read tabId/windowId, URL, title, frame origin, document readiness, and a bounded content digest in the same extension turn; attach heartbeat sequence, extension instance id, and monotonic timestamp. Reject cached session metadata when its sequence or tab identity differs, and expire attestations after 10 seconds.
- **owner gets:** When the assistant says what is on a page, the owner gets an honest, recent proof of which tab was read instead of a summary that may come from a stale or mismatched tab record.
- effort: Moderate browser-extension and relay protocol change, plus simulated Safari tests for navigation races, duplicate tabs, and failed loads.  ·  risk: Pages that navigate during attestation may cause more refusals. Recover by retrying once, then asking the owner to keep the tab focused; never silently fall back to stale metadata.
- cost: No model cost; a few hundred bytes of metadata per read and modest relay storage.  ·  latency: Adds roughly one extension round trip, typically under 300 ms; avoids expensive wrong summaries.
- security: Digest only; no cookies or page secrets. Origin and URL can be sensitive, so retain briefly and scope to the requesting session.
- depends on: Browser extension support for atomic attestation; Relay storage and expiry for attestation sequence; Judgement refusing page summaries without a fresh matching attestation


## What it asked for

_Nothing._
## Its own summary

Fresh live observations recorded: Safari bridge is online with 3 tabs and zero pending commands, but its active URL/title conflicts with the durable session snapshot; Mac UI input is untrusted because Accessibility and Screen Recording remain false; owner timezone (America/Chicago) conflicts with machine timezone (America/New_York). I proposed and recorded a metadata-only perception snapshot aggregator and confidence gate connecting browser status, sessions, observe, machine context, and judgement. No pendant is connected, so pendant/audio behavior remains unverifiable.

**Biggest unknown:** Which browser identity is authoritative (live tab URL/title versus durable session metadata), and which timezone should govern scheduled actions. I still need an owner-authoritative timezone/context source and an atomic browser snapshot identity contract; Accessibility remains an owner-side prerequisite for trustworthy UI actions.

