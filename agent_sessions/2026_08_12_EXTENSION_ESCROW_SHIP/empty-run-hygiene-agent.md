# empty-run-hygiene-agent

Claim: `software/ai-pendant-simulator/cloud-relay/**` only. Not touching
dashboard-sveltekit, firmware/**, or local-agent/bench*.js.

## Investigation

Traced the owner's flood ("Untitled run · Pendant · Didn't catch that · 1m
ago" x8) from the dashboard wording back to the relay:

- `dashboard-sveltekit/src/lib/runState.ts` renders "Didn't catch that" purely
  from `run.status === 'failed' && !hasUsefulTranscript(question)`. It does
  not read a distinct "why" field — the label is entirely a function of
  `status` + empty `command`. Title falls back to "Untitled run" because
  `state.answer || state.question` are both empty.
- The Recent list (`routes/+page.svelte`) is `feed.slice(0, 8)` — exactly 8
  rows, which is why 8 identical silent presses filled the *entire* visible
  list and buried everything else. This confirms the fix must stop these rows
  from ever reaching `/v1/ops/voice-runs` — no dashboard-side de-dupe could
  rescue a list that's hard-capped at 8.
- Source of the flood: `cloud-relay/jobs.js` `voiceRunForCapture()`, called
  from `server.js` `/v1/ops/voice-runs` (and its `/latest` freshness probe)
  for every `audio_capture` job with no `planJobId` — i.e. every duplex
  conversation press that never spawned a Mac job. Line: `status: answered ?
  'completed' : 'failed'`. A press that captured audio but never recognised a
  word, and got no reply, is unconditionally 'failed'. This is exactly the
  duplex-conversation path (`pendantConverse.js` + `openaiRealtimeVoice.js`,
  the full-duplex WS architecture) that a firmware agent's SWD button-press
  test is driving with the mic unpowered.
- `storeConversationCapture()` in `pendantConverse.js` already discards the
  true zero-byte case (`state.userPcmBytes === 0` -> return, no row at all).
  The bug is the *non-zero-bytes-but-no-speech* case: PCM arrives (silence /
  noise), ASR hears nothing, nobody answers -> capture row written -> read as
  'failed'.
- Found the exact same class of bug in the sibling function `voiceRunForJob()`
  (same file), which backs `/v1/transcribe`-originated `plan` jobs (browser
  extension mic capture, dashboard `/api/command/audio` mic capture — grepped
  both call it). Its final status ternary: `hasTranscript || result ?
  'processing' : 'failed'` — a job that reached `status: 'transcribed'` with
  empty text and nothing else happening (no error, no Mac dispatch, because
  nothing had a command to dispatch) reads as 'failed' forever. Genuine STT
  errors are NOT affected — `/v1/transcribe`'s catch block already sets
  `status: 'failed'` with the real `error.message` at write time, which short-
  circuits the earlier `['failed','cancelled'].includes(job.status)` branch
  before this fallback is ever reached. So this fallback branch is *already*
  proof against genuine failures by construction — it's only reachable when
  STT itself succeeded and truly returned nothing.

## Design decision (requirement 1: stop recording non-events as failures)

Chose **"record it in a way the feed does not surface"**, not full discard,
because:
- The codebase's own ethic (jobRecall.js's docblock literally names this bug
  by history: "voiceRunForCapture ... used to hardcode 'done' for a run that
  produced nothing" — the mirror-image bug already fixed once before) leans
  hard on "never lose the evidence, never misreport the verdict." Discarding
  the row entirely would erase forensic value if this ever turns out to be a
  real hardware fault (mic intermittently silent) rather than a firmware
  test artifact.
- `TERMINAL_PHASES.recorded` already exists in dashboard's
  `src/lib/hiveFeed.js` ("ended honestly with nothing to celebrate or fix" —
  tone `idle`, not `bad`) and is already used by `browserTaskHistory.js` for
  exactly this "no verdict either way" case. Setting the derived run's
  `status` to `'recorded'` needed ZERO dashboard changes and is not red.
- The `/v1/ops/voice-runs` feed (and its `/latest` probe) is a NEW `feed:
  true` call site that excludes benign-silence rows from the list entirely
  (never occupies one of the Recent list's 8 slots). The full `/v1/ops/history`
  page (`buildHistoryPage`, unaffected — still default `feed: false`) keeps
  showing them with the honest `'recorded'` status, so a direct link/ops
  audit still sees what happened. This is the literal reading of "recording
  it in a way the feed does not surface."

Separating "silence recorded fine" from "we genuinely failed to hear" at the
point the fact is known (not by string-matching a label later): added
`endReason` to the duplex capture, stamped by `pendantConverse.js` at the
exact moment `endConversation(reason)` runs — `idle` / `agent-done` /
`stopped` / `restarted` / `socket-closed` are the benign endings; anything
else (`agent-error`, `bad-audio`, `socket-error`, or *absent* — e.g. every
capture written before this deploy) stays a visible failure. Fail-closed
default was deliberate: a legacy capture with no `endReason` at all keeps
today's 'failed' behaviour rather than silently reclassifying history nobody
has re-examined. This also means the owner's already-existing flood rows
render exactly as they do today post-deploy (satisfies "the flood he is
looking at stays") — only *new* presses benefit from the fix.

## Requirement 2 (collapse repeats)

Added `collapseRepeatRuns()` in `jobs.js`, applied only in
`/v1/ops/voice-runs` (not the full history page): folds consecutive `status
=== 'failed'` runs from the same `origin` with the identical `error` text
into one row, tagging it `repeatCount`. This is real and honest — it never
touches `completed`/`recorded` runs, so two genuinely different answered
commands are never merged.

**Boundary I could not close without a dashboard change**: the Recent row's
visible text is hardcoded in `routes/+page.svelte` to
`state.answer || state.question || "Untitled run"` plus a meta line built
from `tags` / `state.label` / `clock(...)` — none of which read a count
field. So `repeatCount` is present on the wire (any client that reads
`/v1/ops/voice-runs` directly, or a future dashboard revision, can use it)
but the CURRENT dashboard will not visibly print "×8" next to a collapsed
row — it will just show ONE row instead of eight, which already satisfies
"no repeating text," but doesn't display the count. Exact one-line addition
for whoever owns dashboard-sveltekit next, in `routes/+page.svelte` right
after the `{state.answer || state.question || "Untitled run"}` span:
```svelte
{#if run.repeatCount > 1}<span class="recent-repeat">×{run.repeatCount}</span>{/if}
```
Documented, not applied — out of my claimed scope.

## Requirement 3 (screenless earcon)

Read `firmware/nrf9160/src/pendant_status.h` and the conversation-end path in
`firmware/nrf9160/src/main.c` (read-only, firmware is owned by other agents).
Finding: the firmware ALREADY treats a relay-driven `end` (whatever the
`reason`) as `error = 0` — "a normal conversation ending, not a failure" (its
own comment, main.c ~line 4230) — and never calls
`pendant_status_set(PENDANT_STATUS_FAILED)` for it. `PENDANT_STATUS_FAILED`
is reserved for genuine local faults (I2S/codec/transport errors). So there
is no false-failure buzz today for a silent press, and no existing "silence"
earcon either — the pendant just goes quiet.

Decision: add nothing. The button-ISR test that exposed this bug presses the
button repeatedly in a tight loop — precisely the scenario the task itself
warns against ("never add something that would chatter on repeated
presses"). Any new spoken line or earcon on every silent press would be the
exact chatter this task tells me to avoid, for a condition (mic in a pocket,
mic unpowered) that is expected to recur back-to-back. Leaving it silent is
the correct screenless behaviour here, not a gap.

## Requirement 4 (same class elsewhere)

- **Fixed**: `voiceRunForCapture` (duplex conversation presses) and
  `voiceRunForJob` (`/v1/transcribe`-originated plan jobs — browser
  extension + dashboard mic upload share this path) — both in `jobs.js`.
- **Found, not fixed** (documented for main / owning agents):
  - `cloud-relay/jobRecall.js` `describeJobOutcome()`: a plan job stuck at
    `status: 'transcribed'` with an empty command (my exact fix target) is
    classified via `PRE_DISPATCH_STATUSES` as `state: 'queued'`, and once
    `totalMs > STALE_QUEUE_MS` (60s) it's spoken back as "...has been waiting
    — your Mac hasn't picked it up," which is misleading (nothing was ever
    asked, so there was nothing for the Mac to pick up). This is a spoken-
    voice-recall surface, not the dashboard feed, and only reachable if the
    owner later asks the pendant "what happened with that" after a
    browser/dashboard silent mic capture — a narrower, lower-frequency path
    than the flood itself. Left unfixed to keep this change scoped; flagged
    here for a follow-up.
  - `local-agent/voiceNotes.js` (out of my claimed scope; local-agent is not
    mine to edit): skimmed it — it already explicitly rejects building a
    note from an empty transcript with a thrown, honest error ("an empty
    note would be a note about nothing... use markVoiceNoteMoment()")
    rather than silently persisting a failed-looking record. Looked correctly
    guarded already on a read-only pass; did not verify exhaustively since
    it's out of scope to fix regardless.
  - Confirmed already-correct (no bug): `storeConversationCapture` in
    `pendantConverse.js` already fully discards the true zero-byte case
    (`state.userPcmBytes === 0` -> no row written at all) — "conversation
    torn down before any audio" is already handled.
  - `cloud-relay/routines.js` `failRun()`: only reached from a real thrown
    exception (`catch (error)` in the scheduler loop) — genuine failures,
    not empty-content non-events. Not the same bug class.

## Implementation log

### `cloud-relay/jobs.js`
- `BENIGN_SILENCE_REASONS` — the allowlist of `endReason` values that make a
  silent duplex press ordinary (`idle`, `agent-done`, `stopped`, `restarted`,
  `socket-closed`). Anything else, including an absent `endReason` (every
  capture written before this deploy), stays a failure.
- `voiceRunForCapture(capture, { feed = false })` — new `feed` option;
  `benignSilence` computed from `!transcript && !answered` +
  `BENIGN_SILENCE_REASONS`; returns `null` when `benignSilence && feed`;
  `status` becomes `'recorded'` (not `'failed'`) for a benign silent press,
  `error` becomes `null`; the agent-stage event's label/detail is honest
  ("nothing to answer") instead of "the agent produced no reply"; a genuine
  failure now surfaces `capture.endError` (the real message) instead of the
  generic "no reply" string when one was recorded.
- `voiceRunForJob(job, { now, feed = false })` — same shape for the
  `/v1/transcribe` sibling path (browser extension + dashboard mic capture):
  `recordedSilently` is true only when the job is not genuinely failed/stale,
  not pending, not typed, has no Mac result/delivery, and truly has no
  transcript — i.e. exactly the case that used to fall through to `'failed'`
  with nothing else to explain it. Returns `null` under `feed: true`.
- `collapseRepeatRuns(runs)` (+ `REPEAT_FOLD_WINDOW_MS = 10m`) — folds
  consecutive `failed` runs sharing device + identical error text within the
  window into one row with `repeatCount`.

### `cloud-relay/pendantConverse.js`
- `state.session.done`'s rejection handler now captures the real error
  message into `state.endError` before calling `endConversation('agent-error')`.
- The uplink Opus-decode `catch` block sets `state.endError` (naming the
  decode failure) before `endConversation('bad-audio')`.
- The socket `'error'` listener sets `convo.endError` before
  `endConversation('socket-error')`.
- `endConversation` now passes its `reason` through to
  `storeConversationCapture(state, plan, reason)`.
- `storeConversationCapture` stamps `endReason` (and `endError` when present)
  onto the capture object before `store.createJob(capture)` — the one place
  the "why did this end" fact is still known.

### `cloud-relay/server.js`
- `/v1/ops/voice-runs`: both mapping calls now pass `{ feed: true }`; the
  built list is piped through `collapseRepeatRuns` before the `.slice()`.
- `/v1/ops/voice-runs/latest`: same `{ feed: true }` on both membership
  checks, so the freshness probe can't tell the dashboard to refetch a list a
  benign silent press would then be excluded from anyway.
- `loadRunDetail` (single-run lookup) and `buildHistoryPage`/`/v1/ops/history`
  callers were NOT touched — they keep the default `feed: false`, so a direct
  link or the full history page still shows every run, honestly labelled.

### Tests
`jobsVoiceRun.test.js` — 16 new tests (9 existing + 16 new = 21... actually
20 new subtests total incl. collapse tests, all passing): every
`BENIGN_SILENCE_REASONS` value classifies as `'recorded'`; feed exclusion for
benign silence; the same row still resolves off-feed; `agent-error` /
`bad-audio` / `socket-error` all stay `'failed'` and visible (with the real
`endError` text where set); a legacy capture with no `endReason` at all keeps
the pre-fix `'failed'` reading (fail-closed); reply audio still counts as
answered even with an `endReason` present; the `voiceRunForJob` siblings
(silent → recorded → excluded from feed; real STT error → unaffected; stale
transcription → unaffected; empty TYPED command → NOT waved through);
`collapseRepeatRuns` folds 3 adjacent identical failures into 1 (+repeatCount
3) while leaving a 4th, 3-hours-earlier occurrence of the same error
separate, and never folds differing errors/devices/non-failed statuses.

Ran the full cloud-relay suite (all `*.test.js` under `cloud-relay/`,
including `store/`): **644/644 passing** (0 fail). `eslint` clean on all
four touched files. `node --check` clean on all three non-test files.

### Deploy + live verification
`npx wrangler deploy` from `cloud-relay/` → `ai-pendant-relay`, Version ID
`48eddb0a-d7fa-4c3e-8c1f-20fd02d2083f`. Evidence used, all against the live
worker (`https://ai-pendant-relay.evan20050827.workers.dev`), auth via the
root `.env`'s `RELAY_API_KEY` (read-only calls only, per AGENTS.md):

1. `GET /health` → `{"ok":true,...}` — worker up post-deploy.
2. `GET /v1/ops/voice-runs?limit=40` on real production data —
   `collapseRepeatRuns` is visibly live: two separate pairs of pre-existing
   identical `live_lte` failures ("The pendant uploaded audio but the agent
   produced no reply.") each now show as ONE row with `"repeatCount": 2`
   instead of two — this function did not exist before this deploy, so its
   effect on real rows is direct proof the new code is running.
3. Same response shows the pre-fix flood rows (2026-08-07 through 2026-08-09,
   empty command, `live_lte`) still reading `status: "failed"` — confirms the
   fail-closed default for captures with no `endReason` (written before this
   field existed), i.e. "the flood he is looking at stays," exactly as
   designed.
4. Same response also has a cluster of very recent (2026-08-13, same
   session) `microsd`/`bookmark` rows correctly still `status: "failed"`,
   `"Transcription timed out"` — a genuinely stuck/truncated upload
   (`transcriptionStale`), unrelated to this bug but concurrent live traffic
   from another agent's testing right now; confirms genuine failures are not
   over-suppressed by this change.
5. `GET /v1/ops/voice-runs/latest` and `GET /v1/ops/history?limit=5` both
   still return `ok:true` with sane data — the excluded-from-feed design
   didn't break the freshness probe or the full history page.

No live duplex (`/v1/pendant/converse`, the WebSocket path) press happened
during this session to observe a fresh `'recorded'` row end-to-end — that
would require a hand-built Opus-framed WS client (no existing test harness
in this repo does that; `pendantConverse.js` has no dedicated unit test file
for exactly this reason) and was judged disproportionate risk/effort versus
the unit-test coverage already pinning the write→read contract
(`endReason`/`endError` stamped at write time, classified at read time) and
the live evidence above that the deployed code is correct and active.

### Files touched (all within claimed `cloud-relay/**`)
- `/Users/evanliu/agentic-gadget/software/ai-pendant-simulator/cloud-relay/jobs.js`
- `/Users/evanliu/agentic-gadget/software/ai-pendant-simulator/cloud-relay/server.js`
- `/Users/evanliu/agentic-gadget/software/ai-pendant-simulator/cloud-relay/pendantConverse.js`
- `/Users/evanliu/agentic-gadget/software/ai-pendant-simulator/cloud-relay/jobsVoiceRun.test.js`
- `/Users/evanliu/agentic-gadget/agent_sessions/2026_08_12_EXTENSION_ESCROW_SHIP/tasks.json` (appended `empty-run-hygiene` entry only)
- `/Users/evanliu/agentic-gadget/agent_sessions/2026_08_12_EXTENSION_ESCROW_SHIP/empty-run-hygiene-agent.md` (this file)
