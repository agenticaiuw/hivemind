# Harness derivation — faculty-perception — round 255

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **live Mac control observability** — At 2026-08-09T03:56Z the live Mac agent reports Accessibility trusted, Screen Recording granted, automation grants present, and permissions.ready=true for com.aipendant.agent; browser extension Safari is online on a YouTube tab, relay reachable, and relay reports macBridgeOnline=true. The local agent's /v1/devices/status is not a route, so its 404 cannot establish relay registry state.
  - evidence: read_continuity_snapshot(include=['relay','pipeline']) invoked GET /ops/snapshot and returned status.permissions.ready=true, accessibility.trusted=true, screenRecording.granted=true, browser.online=true, relay.reachable=true; probe_http GET /v1/devices/status returned Mac-agent 404 explicitly saying no such route.

## Capabilities it proposed

### "“What is actually on my screen right now, and is the browser showing the same thing?”"
- **useful because:** The owner gets a timestamped, source-labelled answer instead of a model guessing from stale tab metadata: a Mac screenshot/AX observation is compared with the authenticated browser DOM, and disagreement is surfaced explicitly. The pendant supplies the question and hears the answer; the Mac supplies pixels and accessibility state; the browser supplies logged-in page facts; the relay keeps the request alive if the Mac response is delayed.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime for the short spoken request and final answer; a cheaper background classifier can compare screenshot/OCR against browser text and only invoke the realtime model for ambiguity.
- **latency:** 2–5 seconds, dominated by screenshot/browser snapshot transfer and one comparison pass; speak immediately with “checking” if either source is slow.
- **cost:** Roughly $0.01–$0.05 per invocation depending on image tokens; browser and accessibility reads dominate latency, not the relay.
- **security:** Screen pixels and logged-in page text leave the Mac only for this request and must be redacted before relay/model upload; never expose passwords or payment fields. Require confirmation before any resulting action. Attach capturedAt, source, URL, and content hash to the response so the owner knows its age.
- **missing:** A single Mac route that returns screenshot plus accessibility tree with field-level secret redaction; A browser snapshot contract that returns DOM/text and screenshot timestamps under one correlation ID; A relay correlation record joining pendant utterance, Mac observation, browser observation, and final answer

### "“Tell me when the computer, browser, relay, and pendant disagree about what just happened.”"
- **useful because:** Today each surface can report a locally plausible success while the owner experiences a failure. A contradiction monitor would distinguish ‘Mac executed’, ‘browser confirmed’, ‘relay accepted’, and ‘pendant heard’ and alert only when those claims diverge, such as a browser mutation with no Mac receipt or a relay completion while the device is absent. It is a reality fence, not another activity feed.
- **path:** pendant → relay → mac → browser
- **model tier:** Background rules first (cheap, deterministic joins and freshness thresholds); use the realtime model only to phrase a concise spoken alert when a contradiction crosses a user-visible threshold.
- **latency:** Under 10 seconds for browser/Mac contradictions and under one relay heartbeat for delivery contradictions; no continuous model calls.
- **cost:** Near-zero model cost for normal operation; occasional alert phrasing under $0.01. Storage is a bounded event index, not full page/audio retention.
- **security:** Do not copy page bodies into the monitor; retain IDs, hashes, URLs stripped of query secrets, timestamps, and state transitions. Alerts may reveal private activity through the pendant, so apply quiet hours and require an explicit owner policy for sensitive domains.
- **missing:** A durable correlation ID shared by browser command, Mac action ledger, relay job, and pendant utterance; A rule engine that consumes state transitions rather than polling truncated snapshots; A device-originated receipt for actual playback; current ‘delivered’ only means bytes reached a socket; An owner-configurable severity policy for contradictions

### "“Mark exactly what I’m looking at so I can come back to this later.”"
- **useful because:** A spoken bookmark would preserve the authenticated browser page or visible Mac state as verifiable evidence, not a vague note: the owner can later reopen the same tab, see the captured title/URL/region, and know whether the content changed. The pendant makes capture hands-free; the browser contributes session-bound context; the Mac mints the existing content-addressed capsule; the relay can deliver a short confirmation even if the owner walks away.
- **path:** pendant → relay → mac → browser
- **model tier:** Realtime only for intent detection and a short confirmation; deterministic Mac/browser code performs capture, hashing, redaction, and capsule storage. A cheaper background process can retire expired bodies and detect page changes.
- **latency:** Capture acknowledgement within 2 seconds; capsule persistence within 5 seconds. Never block the spoken confirmation on an optional relay upload.
- **cost:** Usually below $0.01, with model cost limited to the voice turn; local hashing/storage and browser capture dominate.
- **security:** The capsule must redact secrets before persistence, preserve the existing 24-hour body TTL and 7-day tombstone grace, and never speak or upload page contents. Require a confirmation phrase for sensitive pages and make the bookmark visibly revocable from the Mac.
- **missing:** A mounted call path from the browser extension’s current session to the existing evidenceCapsules and browserProvenance stores for a voice-triggered capture; A stable browser-side locator/region capture when the owner says ‘this’; A relay acknowledgement that references capsuleId without retaining the page body

### "“Privacy seal.” (or hold the pendant’s physical button) “Stop seeing, hearing, recording, and acting everywhere—now—and prove what was cut off.”"
- **useful because:** The owner gets an emergency, trustworthy privacy boundary instead of separately closing a tab, muting a microphone, and hoping queued work stops. One physical gesture would revoke new screen/browser captures, cancel unstarted Mac actions, stop relay speech/streaming, suppress announcements, and return a compact receipt listing what was interrupted and what data was already retained. This is the single most useful missing safety capability because it works when the owner cannot safely explain a situation aloud.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** No model for enforcement; deterministic firmware, relay, browser, and Mac safety handlers. Realtime may speak one short confirmation only after every surface reports its seal state.
- **latency:** Local audio/capture mute in under 100 ms; relay and Mac revocation fan-out under 2 seconds; confirmation must say which surfaces have not yet acknowledged.
- **cost:** Negligible per invocation; bounded durable audit metadata only. Hardware work is firmware/button handling, not new recurring API spend.
- **security:** The seal must be fail-closed, authenticated, idempotent, and survive a dropped link. It must never upload the owner’s final utterance as a command by default. Store only event IDs, timestamps, and retention actions; require an explicit physical gesture to lift the seal. Any already-persisted audio or evidence must be reported and separately deletable.
- **missing:** A pendant-local privacy-seal state machine and physical-button interrupt path; A relay broadcast/revocation primitive that reaches every active session and queued announcement; Mac and browser handlers that atomically refuse new capture/action commands and cancel pending work; A signed, append-only seal receipt visible on the dashboard and readable later from the pendant

### "“Show me everything this system currently knows about me, where each item came from, when it expires, and let me erase selected items.”"
- **useful because:** The owner cannot today inspect the collective’s actual memory as one accountable inventory. This would expose the difference between owner statements, machine-derived preferences, browser evidence, relay announcements, action receipts, and retained audio—then allow precise deletion without guessing which store contains a copy. It would have caught the pinned machine-authored America/Chicago preference immediately.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** A deterministic inventory and deletion engine does the work; use a cheaper text model only to organize thousands of records into a spoken summary. Realtime is reserved for the owner’s short query and confirmation of destructive deletion.
- **latency:** Inventory summary in under 10 seconds, with progressive sections; deletion receipt under 3 seconds per store. Never claim erasure until every participating store acknowledges it.
- **cost:** Low: mostly local indexed reads and bounded metadata; occasional summarization under $0.05. No page bodies or audio need enter a model.
- **security:** This is the highest-sensitivity endpoint: require physical pendant presence or an already-authenticated Mac session, redact secrets by default, separate ‘hidden from projection’ from ‘deleted’, and retain tamper-evident deletion receipts without retaining deleted content. Relay and browser stores must not silently rehydrate erased facts.
- **missing:** A cross-store data inventory schema with provenance, retention, projection, and deletion semantics; Deletion APIs for relay announcements/audio and browser/session evidence that return durable receipts; A join that maps Mac context facts and action ledgers to the relay and browser copies derived from them; A dashboard and pendant-readable export with pagination and owner confirmation

### "“Why do you believe that, and what would change your mind?”"
- **useful because:** The owner should be able to interrogate any spoken conclusion—especially a date, preference, or claim about an action—and receive the exact evidence chain, freshness, source authority, contradictions, and correction path. Today a high-confidence machine fact can be injected as if it were owner intent; this capability makes the system’s beliefs inspectable and lets the owner demote or correct the specific premise without wiping unrelated memory.
- **path:** pendant → relay → mac → browser → dashboard
- **model tier:** Deterministic provenance traversal and confidence arithmetic first; a cheaper reasoning model can translate the chain into plain language. Realtime only handles the conversational follow-up and must quote the structured evidence rather than inventing rationale.
- **latency:** First answer in 3 seconds from indexed facts; deeper evidence retrieval under 8 seconds. A stale or contradictory chain must be labelled unknown, not filled by the model.
- **cost:** Usually cents or less; graph traversal and cached hashes dominate. Model use is limited to rendering the already-computed chain.
- **security:** Evidence may include private URLs, screen regions, or message metadata; show redacted summaries by default and require an explicit reveal. Corrections must be versioned, attributable to the owner, and prevent the old machine assertion from winning projection by confidence alone.
- **missing:** A provenance graph linking memory facts to browser capsules, Mac observations, relay jobs, and device events; A first-class distinction between owner assertion, machine observation, inference, and stale copy in every projection; Owner-facing demote/correct/retract operations with conflict resolution and durable receipts; A dashboard/pendant renderer for evidence chains and counter-evidence


## What it asked for

_Nothing._
## Its own summary

Discovered a material change: the exact AI Pendant Agent now has Accessibility, Screen Recording, automation, and permissions.ready=true; Safari’s browser bridge is online on a YouTube tab and the relay is reachable. I recorded that verified state and informed faculty-judgement. I produced three new owner-facing capabilities: a source-labelled screen-vs-browser reality answer, a cross-surface contradiction monitor, and a hands-free evidence bookmark using the existing capsule/provenance stores. The live Mac agent does not expose /v1/devices/status, so its 404 is not pendant evidence; device discovery currently lists nrf9160-pendant offline, which still needs authoritative relay confirmation.

**Biggest unknown:** The system still cannot establish a single authoritative, end-to-end chain from an owner utterance to a specific browser/Mac action and then to actual pendant playback. I still need a relay-side device-status read reachable from this agent, a shared correlation ID across browser/Mac/relay records, and a device-originated playback receipt. No further macOS permission grant is needed now.

