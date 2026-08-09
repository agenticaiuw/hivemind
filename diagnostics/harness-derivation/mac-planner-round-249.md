# Harness derivation — mac-planner — round 249

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I plug the pendant into my Mac, run a complete pendant/audio health check and tell me plainly whether today's wearable is trustworthy."
- **useful because:** The owner currently has to know which bench scripts to run and interpret UART counters. This turns the live USB-connected hardware into a one-command confidence check: capture the diagnostic fixture, verify both audio directions and packet/CPU thresholds, save the raw evidence, and speak only the result. It catches exactly the class of regressions that have repeatedly broken conversations.
- **path:** pendant → relay → mac-planner
- **model tier:** background: deterministic scripts and a cheap summarizer; reserve realtime only if the owner asks follow-up questions during the test.
- **latency:** Start within 2 seconds of the device appearing; 30-90 seconds for the fixture and log collection; a concise result immediately after parsing.
- **cost:** Usually <$0.01 per run; almost all time is local fixture execution and log parsing, not model tokens.
- **security:** UART logs may contain timestamps, identifiers, or accidental application text. Keep raw logs in ~/AI-Pendant-Workspace, redact them before relay upload, and never upload microphone samples (the diagnostic fixture is synthetic). Do not flash firmware or alter files outside the workspace without an explicit owner policy entry.
- **missing:** A Mac USB-device attach trigger or a scheduled polling routine.; A bounded allowlisted runner for the existing diagnostic fixture and a parser that emits the acceptance metrics (alias rejection, decode/encode time, mic drops, tx_starved, clipping, fixture completion).; A relay result type that can deliver a pass/fail card to the existing pendant inbox.

### "I’m looking at something on my Mac and want a one-sentence spoken explanation in my ear; use the active browser tab if there is one, otherwise tell me what app is in front."
- **useful because:** This is the fastest bridge between screen context and the wearable: no dictation, no screenshot upload, and no need to move focus. A short press or spoken request can turn the current tab's title/URL and readable page into a concise explanation, useful while standing away from the keyboard. It works today with the active Safari session and can degrade to app identity when page text is unavailable.
- **path:** pendant → mac-planner → browser-extension → relay-realtime
- **model tier:** realtime only for the final one-sentence spoken answer; use a cheap background model for page extraction/truncation and deterministic redaction.
- **latency:** Under 3 seconds for tab metadata; under 8 seconds for a readable-page summary; immediate fallback if the browser is unavailable.
- **cost:** <$0.01 for metadata-only requests; $0.01-$0.04 when page text needs summarization. The dominant cost is sending page text, so cap and deduplicate it.
- **security:** The active tab may contain secrets or private work. Default to title/domain plus a 2,000-character redacted excerpt, never passwords/forms/cookies; do not send page content until the owner has enabled browser reading. Log only domain and a hash of the excerpt. A destructive or state-changing page must never be clicked as part of this feature.
- **missing:** A pendant button/event route that requests a foreground-context snapshot without opening the microphone.; A stable semantic context read returning active app plus active tab readable text/selection; current browser inspection can identify the active URL but does not provide selected text or document semantics.; A relay request/response envelope that binds the snapshot to the exact button press and expires it after one answer.

### "When I ask 'what did I leave unfinished?', combine my pendant bookmarks, interrupted Mac jobs, and open browser work into three concrete next actions, and speak them to me."
- **useful because:** A bookmark captures the moment but not the unfinished state; a browser tab shows state but not intent; a Mac job receipt shows execution but not what the owner cared about. Joining the three gives the owner a useful answer after a commute, crash, or context switch instead of a pile of disconnected history.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** background model for clustering and ranking; realtime only to answer the final short query on the pendant.
- **latency:** Collect local state in under 2 seconds and speak a three-item answer within 6 seconds. If one surface is offline, answer from the other two and say which evidence is missing.
- **cost:** <$0.02 per query; most cost is one compact ranking call after deterministic collection. Keep raw tab URLs and bookmark payloads local unless needed for the answer.
- **security:** This is a high-context private activity history. Use a 15-minute freshness window by default, redact URL query strings and document contents, and never infer or announce a sensitive project name in a shared room without an explicit private-audio setting. Do not automatically close tabs, send mail, or mutate files; return suggestions only.
- **missing:** A relay-side correlation record joining the bookmark event ID, Mac job/receipt IDs, and browser tab snapshot with timestamps.; A read-only Mac query for interrupted/in-progress local-agent jobs and their touched resources; current inspection can report apps and tabs but not a unified unfinished-work view.; A pendant request trigger and compact response envelope that carries three ranked actions without turning them into commands.

### "Before I act on something important, ask the Mac, my authenticated browser sessions, and my recent mail/calendar whether the facts agree; tell me only the contradiction that could change my decision, with links or message dates."
- **useful because:** Today each surface can be inspected separately, but the owner has no way to detect that a calendar time, portal status, and emailed instruction disagree. A contradiction-first answer prevents missed changes and stale assumptions without dumping a research brief into the owner's ear.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Use a cheap background model for extraction and entity/time normalization; use realtime only to deliver the final contradiction when the owner asks from the pendant.
- **latency:** 8 seconds for normal mail/calendar/browser reads; if an authenticated page is slow, return the known-source comparison and identify the missing source rather than waiting indefinitely.
- **cost:** $0.02-$0.08 per check, dominated by authenticated-page extraction and model comparison; cache source fingerprints and send only changed snippets.
- **security:** This crosses the most sensitive surfaces. Keep raw mail and portal text on the Mac/relay, send the model only minimal conflicting fields, redact account numbers and message bodies, and require an owner-selected list of browser domains. Never infer that a contradiction authorizes an action.
- **missing:** A cross-source fact-normalization and contradiction engine keyed by event, person, deadline, and status.; A browser-session read API that returns a bounded, redacted authenticated-page excerpt rather than only tab metadata.; A pendant request mode that can ask a question without opening or retaining microphone audio, plus source/date citations in the spoken response.

### "When I hear an answer worth relying on, let me press the bookmark button once; later, say 'show me why' and receive the exact sources, timestamps, and wording that supported that answer."
- **useful because:** The existing bookmark records a moment, but it cannot preserve what claim the owner was relying on or reconstruct its evidence after a browser page changes. This creates an auditable personal trail for decisions made hands-free, without recording the whole conversation or forcing the owner to take notes.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Realtime attaches a compact claim identifier at answer time; a cheap background process snapshots and normalizes citations. No expensive model is needed when replaying stored evidence.
- **latency:** Bookmark acknowledgement under 300 ms locally; citation sealing within 10 seconds; replay should begin within 3 seconds and degrade honestly if a source has expired.
- **cost:** <$0.01 per captured answer plus small encrypted storage; costs are dominated by bounded source snapshots, not inference.
- **security:** Evidence can contain private mail or authenticated pages. Encrypt the claim bundle, retain only the minimum quoted spans and source hashes, expire snapshots by owner policy, and never expose a citation URL with credentials. The spoken replay must say when a source is no longer available rather than silently substituting current content.
- **missing:** An answer envelope carrying claim IDs and source spans through relay to the pendant.; A durable, encrypted provenance store with retention and deletion semantics; the current moment-bookmark ledger has no claim/evidence schema.; Browser and Mac readers must return stable source identifiers, retrieval timestamps, and content hashes, not just current text.

### "Before I submit or send something from my Mac, warn me through the pendant if the attachment, recipient, or browser destination conflicts with my private-data rules, and name the exact field that is risky without revealing its contents aloud."
- **useful because:** Today the Mac can perform a send and the browser can hold authenticated sessions, but the wearable has no last-second privacy check that spans both. A compact warning catches accidental disclosure while preserving the secret itself, especially when the owner is moving quickly or using a portal with unfamiliar fields.
- **path:** pendant → relay → mac-planner → browser-extension
- **model tier:** Deterministic local classifiers for recipients, domains, file labels, and configured rules; a small background model only for ambiguous document classification. Realtime is reserved for the warning's short spoken phrase.
- **latency:** Under 500 ms for known domains/files; under 3 seconds for ambiguous content. If classification is unavailable, report uncertainty rather than silently approving.
- **cost:** Near-zero for metadata and hashes; $0.01-$0.05 only for an ambiguous local document classification. Keep document bytes on the Mac whenever possible.
- **security:** The checker itself must not exfiltrate the secrets it protects. Process attachments locally, hash rather than upload them, redact recipient addresses in relay logs, and let the owner define rules such as external-domain, confidential-label, or personal-identifier. It must warn, not block, until explicit policy is configured; sending remains subject to the owner's existing destructive-action preference.
- **missing:** A pre-submit interception point shared by Mac actions and authenticated browser forms, with field/attachment metadata and a cancel/hold response.; A local policy editor for private-data classes and destinations, plus an explainable classifier that identifies the risky field without quoting it.; A low-latency pendant alert/acknowledgement channel bound to the exact pending submission and expiring after one decision.


## Changes it proposed to its own stack

### `firmware` — Extend the accepted audio_path_diagnostic_fixture UART output with a versioned, single-line CBOR/JSON summary record containing fixture_id, firmware_git, sample_rate, frame_ms, encode/decode p95, alias_rejection_db, mic_drops, tx_starved, clipping_peak, and pass/fail per criterion, emitted only after all counters are finalized. Keep the existing human-readable log and synthetic-only behavior.
- **owner gets:** The owner gets a trustworthy wearable health result instead of a vague 'test completed'; the Mac can detect regressions and explain exactly which audio property failed without an expensive model reading raw logs.
- effort: Small-to-medium firmware change plus a Mac parser and golden-vector tests; bench validation on the currently USB-attached nRF9160.  ·  risk: A malformed or stale summary could create false confidence. Include schema version, firmware hash, monotonic run ID, and require all mandatory fields before declaring pass; retain raw logs for diagnosis. Recovery is to fall back to the existing human-readable parser.
- cost: Negligible flash/RAM and no model cost for parsing; roughly 1-2 KB of additional firmware/log code.  ·  latency: No meaningful call-path impact; adds at most a few milliseconds at diagnostic completion.
- security: No microphone payload or secrets; firmware hash and counters are safe to store locally. Redact any future free-text fields.
- depends on: audio_path_diagnostic_fixture must be implemented on the pendant; A Mac-side bounded parser/runner for the USB UART fixture; The owner selecting an unattended diagnostic policy for device attach or schedule


## What it asked for

_Nothing._
## Its own summary

This round produced three owner-facing capabilities and one concrete firmware change. (1) USB attach health check: run the synthetic bidirectional audio fixture on the live pendant, parse objective thresholds, save evidence, and speak pass/fail. (2) Screen-to-ear glance: summarize the active Safari tab or fall back to foreground app, with strict redaction and no focus stealing. (3) Unfinished-work radar: join offline moment bookmarks, interrupted Mac jobs/receipts, and open browser work into three next actions. I also specified a versioned machine-readable diagnostic summary record so the health check cannot depend on fragile log prose. The recorder noted that these are connective work over existing pieces, which is useful: the missing value is orchestration and policy, not another isolated primitive.

**Biggest unknown:** The live system still lacks the glue and owner policy for unattended USB attach diagnostics, a pendant-triggered context request, and cross-surface correlation. Specifically needed are a device-attach trigger, bounded UART runner/parser, relay envelopes joining IDs and timestamps, and explicit redaction/freshness rules. I did not ask for Accessibility or serial-session access; the current design works around those limits with existing browser inspection, foreground metadata, and bounded bench execution.

