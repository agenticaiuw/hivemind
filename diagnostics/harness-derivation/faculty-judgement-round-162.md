# Harness derivation — faculty-judgement — round 162

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **USB device inventory route** — The live Mac agent has no GET /devices route; discovery's device summaries are not an HTTP surface. A USB tethered mode needs a new device-status adapter, not just wiring an existing route.
  - evidence: GET /devices returned HTTP 404: No such route on this agent.

## Capabilities it proposed

### "When I say “use the pendant over USB,” make the Mac treat the tethered nRF9160 and audio bridge as a local wearable: route the conversation and staged briefs to it, show whether the microphone/audio path is live, and queue safely if I unplug it."
- **useful because:** The pendant is physically attached now but LTE registration is false. This gives the owner a useful wearable today instead of pretending the cloud path exists, and makes unplugging/replugging unsurprising.
- **path:** pendant → mac → relay
- **model tier:** background for connection/status classification; realtime only for the live spoken turn
- **latency:** Connection state under 1 s; live audio path should add under 150 ms; reconnect status can be eventual within 5 s.
- **cost:** Negligible model cost for status; transport engineering dominates. Audio bandwidth is already provisioned by the verified 24 kHz path.
- **security:** USB serial is a local trust boundary: bind to the known device identities, authenticate the session, never expose raw serial commands to the relay, and require the existing physical approval latch for mutations. Unplug must stop capture rather than spill queued PCM.
- **missing:** USB serial transport adapter for /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA; device-session authentication and capability advertisement; Mac routing that prefers USB when LTE is unregistered; health/status route for the local audio and microphone legs

### "Only tell me that my briefing was delivered when the pendant actually downloaded and played it; if playback was interrupted or audio failed, keep the item available and give me a short recovery choice instead of silently losing it."
- **useful because:** A generated answer is not the same as an answer heard. This closes the most important gap in a wearable: the owner can trust that “done” means heard, and can recover after unplugging, checksum errors, or a dropped link.
- **path:** relay → pendant → mac
- **model tier:** Deterministic event reconciliation; use the expensive realtime model only to phrase a recovery choice when several items compete.
- **latency:** ACK ingestion under 1 s; delivery state visible within 2 s; recovery speech under 3 s after a failure event.
- **cost:** Near-zero model cost; storage and idempotent event handling dominate.
- **security:** Accept only authenticated device-session events, deduplicate by eventId and enforce monotonic sequence checks. Speak only opaque item titles or redacted summaries on recovery; provenance must explain why an item was requeued. Never treat download as playback.
- **missing:** A durable join from artifactId to briefing item and relay job; server-side state machine consuming pendant ACKs and reconciling offline replay; a policy for interrupted-item retry/expiry and a compact fallback; USB transport support so ACKs can arrive while LTE is unregistered

### "Before my morning brief, tell me which sources were genuinely readable and current; if calendar or reminders returned an empty result because permission is missing, say that plainly and do not claim my day is clear."
- **useful because:** The current system can confidently say “nothing waiting” or “calendar is clear” when EventKit is unauthorized. The owner needs a truthful brief more than a cheerful one, especially when duplicate scheduled briefings already exist.
- **path:** mac → relay → pendant
- **model tier:** Deterministic reconciliation and provenance first; background model summarizes only verified findings.
- **latency:** Under 5 s for the preflight; no additional spoken turn if all sources are healthy; one short caveat when a source is unreadable.
- **cost:** Low: existing local readers and reconciliation; model cost only for final wording.
- **security:** Return source health and permission provenance, not event contents, unless the briefing policy permits them. Keep unreadable distinct from empty and block downstream urgency suppression when freshness/authorization is unknown.
- **missing:** A single scheduled preflight hook before routine briefings; EventKit-specific calendar/reminders authorization probes (not Automation-TCC probes); routine deduplication and an idempotent briefing-run key; a spoken delivery path that consumes the verified result

### "Let me ask, “What did you not check, and what did you not do?” and get a bounded negative-space report: sources unavailable, actions skipped, items never delivered, and assumptions that were not verified."
- **useful because:** Receipts tell the owner what succeeded, but not what the system silently failed to inspect or chose not to do. This is the difference between a trustworthy assistant and one that merely sounds complete.
- **path:** relay → mac → browser → pendant
- **model tier:** Deterministic set comparison and provenance first; use the expensive model only to compress the report into one spoken sentence.
- **latency:** Under 4 seconds for a recent job or briefing; deeper day-scale audits may take 15 seconds and should be queued.
- **cost:** Low model cost; the work is joining job plans, preflight results, source health, action receipts, and pendant delivery events.
- **security:** The report must distinguish “not attempted,” “attempted but unavailable,” and “attempted and empty.” Do not infer absence from a missing receipt. Sensitive source names should be redacted in spoken output unless explicitly requested.
- **missing:** A durable planned-step ledger that records skipped and blocked steps, not just executed actions; a query joining relay jobs to Mac/browser actions and delivery ACKs; typed negative evidence with expiry and provenance; an owner-facing route for an omission report

### "Give me a temporary, named boundary for this situation—such as “during this trip, never use work sources and never speak names”—show me exactly what it changes, and automatically forget it at the time I choose."
- **useful because:** Permanent global preferences are too blunt for travel, guests, confidential work, or a day spent offline. The owner needs a reversible situation-specific boundary that every body obeys, including when the pendant is disconnected.
- **path:** pendant → relay → mac → browser
- **model tier:** Deterministic policy compilation and enforcement; realtime is only for confirming the owner’s spoken boundary and summarizing conflicts.
- **latency:** Boundary activation within 2 seconds; every action preflight adds under 100 ms; expiry is enforced locally even if the relay is unreachable.
- **cost:** Low recurring model cost; the hard work is signed propagation, local caching, and tests proving fail-closed expiry.
- **security:** The pendant must receive only a signed compact policy, not source contents. A stale or unverifiable policy must fail closed. Activation, override, and expiry need provenance, and irreversible actions still require physical consent.
- **missing:** A scoped policy object with start/end, source classes, destinations, and speech rules; signed propagation and monotonic-version handling across relay, Mac, browser, and pendant; policy-aware gates in speech, memory projection, browser extraction, and autonomy evaluation; a voice or dashboard editor with simulation before activation

### "When I ask “why is my day going wrong?”, show me the smallest causal chain across calendar, mail, browser, Mac jobs, routines, and pendant delivery—not a list of symptoms—and let me choose which link to inspect or correct."
- **useful because:** Today the owner gets separate statuses and receipts but no explanation of how one blocked permission, stale browser session, failed routine, or unheard briefing caused the next problem. A causal answer is more useful than another dashboard.
- **path:** relay → mac → browser → pendant
- **model tier:** Background causal graph construction over typed evidence; realtime only for the final concise explanation and selected corrective action.
- **latency:** Recent-window explanation under 8 seconds; historical analysis can run in the background and notify only when a high-confidence causal chain is found.
- **cost:** Moderate storage and graph-maintenance cost; model usage can stay low by ranking deterministic edges before synthesis.
- **security:** Every causal edge needs source references, confidence, timestamps, and an explicit distinction between correlation and causation. Never mutate anything from an explanation without an autonomy-policy evaluation and, where required, physical approval.
- **missing:** Cross-surface foreign keys between relay, Mac, browser, routine, and artifact IDs; a typed causal-edge store with confidence and expiry; deterministic edge rules for permission failures, stale leases, skipped jobs, and undelivered audio; an owner-facing explanation route connected to corrective previews


## What it asked for

_Nothing._
