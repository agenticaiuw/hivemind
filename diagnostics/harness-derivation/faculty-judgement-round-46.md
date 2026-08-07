# Harness derivation — faculty-judgement — round 46

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

- **cross-surface reliability** — Mac reports online but Accessibility and Screen Recording are untrusted; browser extension home-chrome is offline with three pending commands. Therefore UI execution cannot be treated as successful until permissions and browser heartbeat recover.
  - evidence: faculty-perception Round 42 live checks: Accessibility trusted=false, Screen Recording=false, /observe says UI actions may report success while doing nothing, browser offline with 3 pending commands.

## Capabilities it proposed

### "“Take care of this end to end, and don't tell me it's done until you can verify the outcome.”"
- **useful because:** Today assistants stop at a click or API acknowledgement. This closes the loop across the private browser, Mac, relay, and pendant: it verifies a receipt, changed status, confirmation message, or other owner-defined outcome, and tells the owner exactly what remains if verification fails.
- **path:** pendant captures the request, desired outcome, deadline, and any ambiguity → relay persists the intent and runs retries while the owner is away or the Mac is offline → browser extension performs authenticated form work and captures before/after evidence; irreversible submit pauses for confirmation → Mac agent checks local mail, calendar, downloads, or files for independent confirmation and can create a reminder → relay reconciles evidence and sends a short spoken receipt or a blocked/escalation alert through the pendant
- **model tier:** Cheap background model for extraction, matching receipts, and retry planning; realtime only for clarifying ambiguity and approval at the commit step.
- **latency:** Immediate acknowledgement under 2 seconds; execution can continue asynchronously. Verification usually within minutes, with deadline-aware polling and quiet hours.
- **cost:** Low to moderate per task: mostly browser/Mac operations and compact metadata; one cheap model call for outcome matching, with realtime used only if owner clarification is needed.
- **security:** Authenticated pages, mail, and local files are sensitive. Keep raw artifacts on the Mac/browser where possible, send hashes/structured fields to relay, redact secrets, and require explicit confirmation immediately before sends, purchases, deletes, or submissions. Never infer success from a UI click alone.
- **missing:** unified cross-surface evidence ledger with stable intent IDs; outcome contracts (what counts as verified, by when, and acceptable evidence); durable retry/quiet-hours policy with escalation rules; independent verification adapters for browser, local mail/files, and calendar

### "“Build me an evidence packet for this dispute or appeal, but do not submit anything.”"
- **useful because:** When a delivery, charge, appointment, or account decision goes wrong, the owner should not have to hunt through browser history, email, local files, and spoken recollections. The system would assemble a chronological, source-linked case, identify contradictions and missing proof, and leave a reviewable packet and draft next step.
- **path:** pendant records the owner's concise account, disputed outcome, and desired remedy while they are away from the Mac → relay creates a durable case with scope, retention, and a checklist of evidence still needed → browser extension reads only the owner-selected authenticated pages and captures receipts, status history, and cited snippets without submitting forms → Mac agent searches owner-approved local folders/mail/calendar, normalizes timestamps, copies source files into a case folder, and generates a redacted PDF/Markdown packet → relay reconciles sources, flags uncertainty and conflicting dates, then sends a short pendant briefing and leaves the packet on the Mac for approval or editing
- **model tier:** Cheap background model for extraction, chronology, deduplication, and redaction; realtime only for clarifying the dispute and reading the final summary aloud.
- **latency:** Acknowledge in under 2 seconds; produce an initial packet within 5 minutes for ordinary local/browser evidence, with incremental updates as additional sources become available.
- **cost:** Low to moderate per case: browser and local reads dominate execution, with one or two background-model passes over compact extracted facts. Full document OCR or long correspondence is the main variable cost.
- **security:** Cases may contain financial, medical, or account data. Require explicit source selection and a retention deadline; keep originals on the Mac/browser, put only citations and redacted excerpts in relay storage, encrypt the packet, and never send or submit without a separate confirmation. Do not include secrets, unrelated correspondence, or hidden browser tabs.
- **missing:** case/evidence schema with source citations, chronology, contradiction and missing-proof fields; owner-controlled local-file and mail search scope with redaction and retention controls; document bundling/export with stable provenance links and tamper-evident hashes; a review UI that lets the owner remove evidence and edit the draft before any external action


## Changes it proposed to its own stack

### `integration` — Create a unified cross-surface evidence ledger: every owner request gets a stable intent ID, and pendant transcript/bookmark, relay job events, Mac action receipts, browser tab/session evidence, and final outcome are linked into one append-only timeline. Each claim carries source, timestamp, freshness, confidence, and an evidence hash; the judge must distinguish observed completion, queued, blocked, and merely acknowledged. Generate a concise spoken receipt and a drill-down bundle on the Mac, with automatic expiry/redaction for sensitive page content.
- **owner gets:** The owner will stop having to wonder whether “done” means actually completed, queued while offline, or silently did nothing. They can ask “what happened to that?” and get a trustworthy answer with the exact proof, even when the browser or Mac reconnects later.
- effort: Medium-high: shared intent/evidence schema, adapters for pendant/relay/Mac/browser, durable storage and redacted receipt UI, plus failure-injection tests for offline and false-success cases.  ·  risk: Evidence may contain private page text or spoken content; default to hashes, snippets, and short retention, with explicit opt-in for full artifacts. Clock skew, duplicate events, and retries could create misleading timelines; use monotonic sequence numbers, source timestamps, and conflict markers rather than silently merging.
- cost: Low ongoing API cost (mostly storage and compact metadata); occasional summarization can use a cheap background model. Engineering/storage cost is the main impact.  ·  latency: No material impact on first response; receipt finalization is asynchronous and may arrive after reconnect.
- security: Improves auditability but creates a sensitive metadata index. Encrypt at rest, scope by owner/session, redact secrets and page bodies, and provide deletion by intent ID.
- depends on: durable cross-surface job/event persistence; action receipt and browser provenance primitives; typed context projection with freshness/confidence

### `hardware` — Finish the 24 kHz superwideband path on the capture side instead of only decoding 24 kHz playback: choose a production microphone/codec and clock tree that natively samples 24 kHz (or 48 kHz with a verified decimator), expose a timestamped 24 kHz PCM/Opus contract through the bridge and relay, and reserve DSP headroom so encode+decode cannot starve the voice loop. Keep the nRF9160 DK implementation explicitly marked as a compatibility/downsample mode.
- **owner gets:** The owner's voice will sound natural in both directions instead of receiving wideband audio while their spoken input is still narrowed and resampled. It also avoids subtle pitch, latency, and clock-drift defects that make conversation tiring over a full day.
- effort: High: production audio front-end selection, clock/PLL and PCB work, fixed-point resampling/Opus profiling, bridge/relay contract updates, and acoustic regression testing in real enclosure conditions.  ·  risk: A new clock or codec can introduce drift, radio-burst underruns, battery drain, or worse microphone noise. Keep the current 15.625/16 kHz mode as a negotiated fallback, gate rollout by measured packet loss/CPU/latency, and provide a firmware rollback.
- cost: Prototype hardware roughly $10–$30 in codec/mic/clock and board changes per unit; modest added power for higher-rate capture and DSP. Ongoing API cost is negligible; audio bytes may rise if bitrate increases.  ·  latency: Potentially +5–15 ms from higher-rate buffering/resampling; must enforce a bounded 60 ms frame and underrun fallback.
- security: No new data category; higher-fidelity speech increases sensitivity. Apply existing short retention, encryption, and deletion policies to raw audio.
- depends on: end-to-end 24 kHz negotiated media contract; audio acceptance criteria and clock-drift test fixtures; CPU/power budget measurement on the intended production hardware


## What it asked for

_Nothing._
## Its own summary

Round 46 produced three new increments: a unified cross-surface evidence ledger, an owner-facing end-to-end outcome-verification capability, and a production hardware change to make 24 kHz capture genuinely end to end. I also sent mac-vision explicit safety gates and recorded the live false-success risk from missing Mac permissions/browser heartbeat.

**Biggest unknown:** Whether the orchestrator has actually provisioned the previously requested persistence, recovery, audio-acceptance, and permission capabilities; discover:granted still reports empty, so implementation readiness cannot yet be verified.

