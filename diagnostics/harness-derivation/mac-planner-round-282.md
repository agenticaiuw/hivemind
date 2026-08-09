# Harness derivation — mac-planner — round 282

Model: `gpt-5.6-luna`  ·  probes against `http://localhost:8000`

## What it established

_Nothing recorded._

## Capabilities it proposed

### "When I say “protect my focus,” make my Mac, browser, and pendant enforce one interruption policy: during a calendar meeting or a focus block, suppress ordinary notifications and browser distractions, but deliver urgent messages to the pendant; when the block ends, give me one ranked catch-up list and restore what you changed."
- **useful because:** Today each surface has partial awareness but no shared policy. This would make the wearable the exception channel, the Mac the enforcement point, and the relay the durable coordinator—without losing ordinary alerts or leaving the browser in a mysteriously altered state.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Background/scheduled classification on a cheap model; realtime only for a spoken “protect my focus” or “release focus” command. Deterministic policy evaluation should handle the common path.
- **latency:** Start enforcement within 2 seconds of the command or calendar transition; release and catch-up within 5 seconds.
- **cost:** Low: roughly one cheap classification call per transition and no model call for deterministic calendar/browser rules. Dominant cost is the initial policy setup, not each notification.
- **security:** Calendar titles, mail subjects, and active URLs leave the Mac only as redacted metadata. Do not transmit page bodies or message bodies by default. The policy must log every suppressed/delivered item and every Mac/browser mutation, and restore only resources it changed. An empty owner policy must mean no unattended suppression until configured.
- **missing:** A shared focus-policy state machine in the relay with leases, expiry, and crash-safe restoration records.; A Mac action adapter for Focus/notification settings and a browser adapter for pausing or closing only policy-tagged tabs.; A pendant alert-inbox priority/expiry field and a compact urgent-vs-bulk delivery decision.

### "Do the thing we just agreed on across my Mac and browser, then tell me exactly what changed and leave me a resume point if anything fails."
- **useful because:** This is the central promise of a wearable computer: a spoken agreement becomes a bounded, observable result rather than a vague queued job. The server decides intent, the Mac planner translates it into desktop/browser operations, and the owner gets a concise receipt plus a safe continuation point after a crash or link loss.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Realtime model only extracts the owner's intent and ambiguity. Use a cheaper background planner for multi-step decomposition; deterministic preflight, transaction staging, and receipt generation should not consume the realtime tier.
- **latency:** Acknowledge in under 1 second; show a plan preview in under 4 seconds; execute simple tasks in under 15 seconds, with long work becoming a resumable job.
- **cost:** One realtime turn plus one cheap planning call for complex tasks. API cost is dominated by the initial intent turn and any page/document summarization; receipts and retries are near-zero model cost.
- **security:** The current FULL_CONTROL path has no approval gate, so this must be explicitly opt-in per routine/command class and must refuse when the owner policy is empty. Redact secrets from receipts; never echo passwords, private page text, or file contents into the pendant. Record touched resources, hashes, and reversibility, and make retries idempotent.
- **missing:** A relay-level intent-to-job coordinator that preserves the same job identity across pendant disconnects and Mac/browser retries.; A browser transaction adapter with resource hashes and compensating actions for navigation/form edits.; A user-configurable policy registry for unattended command and URL classes, plus a spoken cancellation window.

### "Every night while the pendant and audio bridge are plugged into my Mac, run a silent hardware health check; tell me in the morning only if the radio, storage, clock, or 24 kHz audio path regressed, with the exact test and last-known-good comparison."
- **useful because:** The hardware is physically present today but failures currently surface only during a conversation. A nightly bench check turns the attached pendant into a dependable instrument: the relay can spot trends, the Mac can collect USB test output, and the owner hears one actionable warning instead of debugging a dead wearable in public.
- **path:** pendant → relay → mac-bridge → dashboard
- **model tier:** No realtime model for measurement. Run deterministic fixtures and threshold checks overnight; use a cheap background model only to summarize a failed diff into a short spoken alert.
- **latency:** Run within a 10-minute overnight window, with the morning result available in under 2 seconds. A failed fixture should stop promptly on a safety threshold.
- **cost:** Negligible model cost on healthy nights; one short background summarization call only on failure. Device cost is zero because both chips are already USB-attached.
- **security:** The fixture must never capture or persist microphone content, and logs must redact serial identifiers and any owner audio. Keep raw logs local with bounded retention; upload only counters, hashes, and failure excerpts. A failed test must not flash firmware, alter settings, or silently erase the SD ring.
- **missing:** A bounded, read-only Mac USB bench runner that can enumerate the two approved serial devices, invoke the existing firmware diagnostic trigger, collect framed logs, and return exit status plus timestamps—without becoming a product serial transport.; A relay trend store for fixture metrics and a last-known-good baseline, with alert deduplication.; A scheduled routine that knows the pendant is attached and skips cleanly when either device is absent.

### "I have 12 minutes before my next meeting—use my calendar, unread mail, and the work I already have open in the browser to choose the highest-value reversible task, do it on my Mac, and stop automatically when the time budget is up."
- **useful because:** The owner currently has to decide what fits a short gap, gather context from several surfaces, and execute it manually. This turns an otherwise lost interval into bounded progress while respecting the next commitment; it is not a briefing or a generic task runner because selection is driven by the live time window and the currently open work.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Use a cheap background model to rank candidate tasks and estimate duration; use the realtime tier only to clarify an ambiguous request. Deterministic deadline and cancellation enforcement must live outside the model.
- **latency:** Return a ranked plan in 5 seconds, begin the first action within 8 seconds, and hard-stop at the owner’s stated deadline with a receipt in under 3 seconds.
- **cost:** One small ranking call per invocation; cost is dominated by redacted mail/browser context, not execution. No model call is needed for the deadline watchdog or receipt.
- **security:** Only snippets, titles, URLs, and calendar time ranges should leave the Mac by default; do not upload full mail or page bodies. Candidate actions must be classified as reversible before selection, and the owner must configure which apps, domains, and mutation classes are allowed. The deadline watchdog must cancel queued actions and never leave a half-submitted form or unsaved document without reporting it.
- **missing:** A time-budgeted planner that estimates each candidate action, reserves a hard stop, and re-plans when an action overruns.; A cross-surface candidate extractor that joins mac_read_sources, active browser tabs, and Mac foreground state without dumping raw content to the relay.; An interruptible Mac/browser executor with checkpoint boundaries and an explicit partial-completion receipt.

### "Before I commit to a date, deadline, or meeting in an email or browser form, check it against my calendar and existing commitments and warn me about overlaps or impossible travel time—without sending or editing anything."
- **useful because:** The owner can currently read each source, but no surface checks a proposed commitment against the others at the moment it is about to become real. A short, private pre-commitment check prevents double-booking and overpromising while leaving the final decision and submission to the owner.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Cheap structured extraction for dates, locations, and commitment strength; deterministic calendar interval and travel-buffer checks. Realtime is useful only when the owner asks for a spoken explanation.
- **latency:** Warn within 1 second after the owner invokes the check, or within 3 seconds for a page/form containing several candidate dates.
- **cost:** Low: one small extraction call for unstructured text, then local deterministic checks. No cost when no check is requested.
- **security:** Default to selected text or a redacted snippet, never whole inboxes or page bodies. Do not submit, alter, or draft a reply automatically. Location and calendar details must stay local unless the owner explicitly asks for a shared explanation; keep a short audit record that can be deleted.
- **missing:** A browser pre-submit hook that can provide the selected date/time/location and pause before a form submission without stealing the session.; A normalized commitment representation shared by Calendar, Mail, browser forms, and pendant bookmarks, including travel buffers and confidence.; A Mac-local checker that can answer from redacted context without sending private page content to the relay.

### "Warn me through the pendant before I paste a secret, private document, or customer data into the wrong website or app, and show me exactly what kind of data was detected without repeating the secret."
- **useful because:** Logged-in browser sessions and Mac apps can reach places the relay cannot inspect, so a server-only privacy rule is too late. A local guard at the paste/upload boundary would prevent accidental disclosure while preserving the owner’s ability to proceed deliberately.
- **path:** pendant → relay → mac-bridge → browser → dashboard
- **model tier:** Run lightweight local detectors first (credential patterns, high-entropy tokens, document labels, destination domain policy). Use a cheap background model only for ambiguous classification, never the realtime model for raw secret content.
- **latency:** Decision before paste or upload completes, ideally under 100 ms for known patterns and under 1 second for an ambiguous local classification. The pendant warning must arrive within 2 seconds.
- **cost:** Near-zero API cost for pattern and destination checks; occasional low-cost local/background classification for ambiguous text. The privacy boundary should not require sending content to a server.
- **security:** Raw clipboard and file contents remain on the Mac. Store only a category, destination, hash, and allow/deny decision; never log the secret or transmit it to the relay. The owner must configure domains/apps that are trusted, and an explicit override must be visible and time-limited rather than silently weakening the rule.
- **missing:** A browser extension and Mac paste/upload interception layer that can inspect locally and pause the operation before transmission.; A local policy engine mapping data categories to destination domains/apps, with one-shot owner overrides.; A pendant warning protocol carrying only category and destination, plus a durable audit receipt that excludes payload content.


## Changes it proposed to its own stack

### `integration` — Add a read-only USB bench adapter on the Mac that recognizes only /dev/cu.usbmodem00096003658* and /dev/cu.usbserial-0287A9CA, runs the already-accepted audio_path_diagnostic_fixture through the existing serial diagnostic hooks, parses framed counters, and emits a signed metric receipt to the relay. It must be a bounded one-shot command with timeout, device identity, firmware hash, and no arbitrary serial writes; this is bench instrumentation, not a normal pendant transport.
- **owner gets:** The owner can know before wearing it whether the actual pendant and bridge are healthy, and can hand a failure report to the builder instead of reproducing an intermittent audio problem during a real call.
- effort: Medium: a small Mac helper plus firmware diagnostic framing and relay receipt schema; 1–2 days for a first fixture report, longer for trend baselines.  ·  risk: Wrong-port matching or a hung firmware test could block the Mac. Use an explicit allowlisted device regex, hard timeout, process kill, and local-only raw logs. If parsing fails, report unknown rather than healthy.
- cost: Negligible compute and storage; no API call on healthy runs, one cheap summarization call only for a failed receipt.  ·  latency: A full fixture takes seconds to a few minutes depending on packet count; it runs off-call and never delays live audio.
- security: No microphone payload leaves the Mac; upload only counters, firmware/device hashes, and redacted failure excerpts. Do not add a persistent USB control channel.
- depends on: The accepted audio_path_diagnostic_fixture must expose a stable framed serial output.; A relay endpoint for metric receipts and last-known-good comparison.; Owner-configured nightly routine policy; do not assume unattended execution is authorized merely because FULL_CONTROL_MODE is enabled.


## What it asked for

_Nothing._
## Its own summary

Discovered the live granted surface, devices, and route inventory. Added three owner-facing capabilities: a cross-surface focus firewall, transactional spoken Mac/browser execution with resumable receipts, and overnight attached-hardware health reporting. Added a concrete integration change for a bounded, read-only USB diagnostic runner. The strongest genuinely new gap is not another inbox or bookmark: it is a shared policy/transaction layer between pendant intent, relay jobs, browser state, and Mac mutations.

**Biggest unknown:** Whether the owner wants unattended execution for any command/URL classes remains unset. I still need an explicit owner policy registry (including suppression, browser mutation, and scheduled USB diagnostics). The USB runner also needs a real bounded serial-diagnostic implementation; current approved tooling can inspect Mac state and execute actions, but there is no dedicated live USB fixture adapter. Accessibility/Screen Recording remain manually blocked, so semantic UI automation is still less reliable than AppleScript/browser routes.

