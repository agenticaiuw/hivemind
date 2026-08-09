# Harness derivation — unified — round 163

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **owner timezone ambiguity** — The owner projection says America/Chicago, while the authoritative Mac timezone context says America/New_York. Treat Mac-resolved schedules as America/New_York and do not infer the owner's personal timezone until explicitly resolved.
  - evidence: discover(owner) remembered.timezone=America/Chicago; granted authoritative timezone context says Mac system zone America/New_York and owner timezone remains open.

## Capabilities it proposed

### "When I press the bookmark button during a conversation, save exactly what this turn was about and let me retrieve it later."
- **useful because:** The owner can mark a useful answer or decision without recording room audio, then later hear or inspect a concise, source-linked note tied to the exact conversation turn rather than an unexplained timestamp.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use realtime only to assign the active turn ID and speak acknowledgement; use a background model to summarize the already-transcribed turn and extract links/entities.
- **latency:** Immediate LED/short spoken acknowledgement under 300 ms; note materialization within 10 s after link availability; offline bookmark must be durable immediately.
- **cost:** Low: one short realtime acknowledgement plus background summarization of one turn; storage is a small metadata record, not PCM.
- **security:** Never store pre-press or ambient audio. Persist transcript-derived text and provenance only, with explicit retention/deletion policy still needed; browser sources must remain bound to the tab/session that supplied them.
- **missing:** Extend existing offline_moment_bookmark payload with signed monotonic event counter, active turn/job nonce, and source references; Relay endpoint that resolves bookmark to the completed turn transcript and receipts; Mac note creation path that can attach the summarized artifact without copying secrets from unrelated tabs; Owner retention/deletion policy

### "With the pendant plugged into my Mac, run a private audio check and tell me whether the microphone, link, and speaker are healthy before I start a call."
- **useful because:** The owner gets a one-button, local proof that the whole wearable audio chain works now, instead of discovering a dead mic or bridge only after an important conversation begins.
- **path:** pendant → mac-planner → relay-realtime
- **model tier:** Deterministic test orchestration and a cheap background model only to phrase the result; no realtime model is needed unless the owner asks a spoken follow-up.
- **latency:** 30–60 s for a full duplex fixture; a clear result within 2 s for a cached recent pass, with timestamp and age spoken.
- **cost:** Negligible model cost; local USB serial, bridge playback confirmation, and bounded fixture artifacts dominate.
- **security:** Use synthetic audio only and do not upload raw microphone content. Require deliberate physical start; retain counters and hashes, not recordings. A failed test must not auto-change the live codec profile.
- **missing:** Expose the existing audio_path_diagnostic_fixture as a user-triggered USB command with typed result; Correlate ESP32 bridge playback acknowledgement with pendant sequence numbers; Add a freshness-aware HEALTHY/DEGRADED/FAILED summary over the raw fixture counters; A Mac-side route that invokes the fixture and returns a signed receipt

### "If my Mac cable or LTE link drops while I am talking, keep this turn intact, finish it on whichever transport is still available, and tell me where the handoff occurred."
- **useful because:** A dropped USB cable or transient modem outage would stop being a confusing half-answer or duplicated reply. The owner gets one coherent turn, with an honest boundary if continuity was impossible.
- **path:** pendant → relay-realtime → mac-planner
- **model tier:** Deterministic transport/session controller owns sequencing and deduplication; realtime is used only for the live conversation audio, not for handoff decisions.
- **latency:** Detect loss within 250 ms, pause at the next 60 ms audio frame boundary, and resume within 1 s when the alternate path is ready; never replay already acknowledged frames.
- **cost:** Negligible extra model cost; bounded sequence metadata and a small relay session record dominate.
- **security:** The relay must not accept late frames from an old transport or mix sessions. Use a signed session epoch, monotonic turn/frame numbers, and explicit owner-visible handoff receipts; do not buffer ambient audio outside an active turn.
- **missing:** A relay transport-session state machine with epoch/fence tokens and exactly-once turn close; Bridge and pendant handoff messages that acknowledge the last consumed frame, not merely bytes sent; A Mac route that reports USB detach/reattach without requiring Accessibility; A compact spoken/LED handoff receipt and tests for simultaneous uplink/downlink loss

### "Use my browser session to complete this task, but keep the page contents and credentials on my Mac; send the relay only the minimum typed result needed to coordinate the job."
- **useful because:** The owner could use logged-in browser sessions without turning the relay into a copy of private pages, mail, orders, or credentials. The pendant remains useful while sensitive computation stays on the machine that already has access.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** A local Mac planner performs page interpretation and browser actions; the relay uses a cheaper deterministic coordinator over typed intents, hashes, and redacted receipts. Realtime is unnecessary except for the owner's short spoken request and confirmation.
- **latency:** Under 2 seconds for policy acknowledgement, then normal browser-task latency. A blocked redaction or schema mismatch must fail closed rather than wait indefinitely.
- **cost:** Lower relay token usage because page text and screenshots stay local; modest Mac compute and a small typed receipt per step dominate.
- **security:** The browser extension must enforce an explicit data-flow policy before each job, prevent screenshots/DOM/text from crossing the boundary, redact error messages and URLs where necessary, and record hashes rather than secrets. Destructive actions still require the existing physical approval mechanism.
- **missing:** A typed, least-privilege browser result schema with field-level sensitivity labels; A Mac-local planner mode that can solve browser tasks without sending page observations to the relay; Relay enforcement that rejects untyped or sensitivity-violating payloads rather than trusting the client; A per-job owner-visible receipt showing exactly which fields crossed the boundary

### "Before you give me a consequential answer, check the independent sources available on my Mac and in my browser, tell me where they disagree, and do not collapse uncertainty into one confident sentence."
- **useful because:** The owner would get an honest conflict report for decisions involving current news, purchases, schedules, or account data instead of a fluent answer that hides stale or contradictory sources.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Use a cheap background/planner model for retrieval, normalization, and contradiction detection; reserve realtime for the final short spoken answer only.
- **latency:** A quick answer in 3–8 seconds for already-open tabs and local files; up to 30 seconds for fresh retrieval. If sources cannot be independently checked, say so rather than fabricate confidence.
- **cost:** Moderate background tokens proportional to the number of source excerpts; relay receives normalized claims and citations rather than full private pages.
- **security:** Respect browser tab bindings and local-file permissions. Do not expose unrelated tab contents to the relay. Every claim needs source identity, retrieval time, and an explicit confidence/disagreement status.
- **missing:** A cross-surface claim extraction and contradiction engine with typed claim IDs; A source-isolation policy that prevents one page from being counted as multiple independent sources; A compact spoken uncertainty format and a detailed Mac receipt with the compared excerpts; Owner policy for which domains or sources are trusted for which categories

### "Forget this conversation everywhere you can reach, then tell me exactly what was deleted, what was only made inaccessible, and what could not be reached."
- **useful because:** The owner gets a real, bounded deletion operation instead of an ambiguous privacy promise. It would cover relay artifacts, Mac work products, browser-side temporary state, and pendant/bridge queues while clearly distinguishing verified deletion from expiry or link loss.
- **path:** pendant → relay-realtime → mac-planner → browser-extension
- **model tier:** Deterministic deletion planner and receipt verifier; no generative model is needed except to phrase the final short spoken report.
- **latency:** A local stop acknowledgment within 300 ms; complete reachable-surface verification within 10 s, with an asynchronous receipt if a surface is offline.
- **cost:** Low model cost; storage scans, authenticated deletion calls, and cryptographic receipts dominate.
- **security:** Deletion must be scoped to an explicit conversation/session ID, never inferred from vague time ranges. Require physical confirmation for irreversible deletion, use idempotent tombstones, prevent browser credentials or page contents from entering receipts, and report unreachable surfaces honestly.
- **missing:** A conversation-wide deletion manifest linking relay jobs, pipeline artifacts, Mac notes/drafts, browser command results, and pendant inbox/outbox entries; Idempotent delete/tombstone endpoints on each surface with authenticated receipts; A physical confirmation flow bound to the deletion manifest; An owner-defined retention policy for what may be deleted immediately versus retained for audit


## What it asked for

_Nothing._
