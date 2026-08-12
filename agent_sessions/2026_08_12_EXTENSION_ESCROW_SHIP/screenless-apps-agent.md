# screenless-apps-agent — Phase 1 of the screenless app framework

Owner of `software/ai-pendant-simulator/cloud-relay`. Implemented
`docs/Screenless_App_Grammar.md` (written by a previous attempt that died on a
rate limit before writing any code) and corrected it where it was wrong or
where the measurements disagreed with it.

## What shipped

**The app ring** — `cloud-relay/menuRing.js`, a pure reducer over the
firmware's `{"type":"menu",delta:±1}` / `{"type":"menu_select"}` /
`{"type":"menu_back"}` frames. Ring: Time, Timer, Reminders, Calendar, Audio
devices, Back. State is relay-side, per converse session, closed at the start
of every conversation. Effects (earcon / name / app / timer / audio-select /
audio-sink / closed) are returned, never performed, so navigation is testable
without a socket.

**Earcons** — `cloud-relay/pendantEarcon.js`. Position-pitched blips (pitch
rises through a ring; inner rings sit a fifth up), a two-tone enter, a falling
escape, and the timer's rising three-note chime. Rendered locally as 24 kHz
s16le so a detent costs microseconds instead of a TTS round trip; only the
SETTLED position is spoken, debounced 200 ms.

**Timers** — `cloud-relay/timerStore.js`, on the existing `getState`/`saveState`
rows approvals use. No new store methods, no Durable Object. Claim-before-speak
so a reconnect racing a stale socket cannot double-chime; a chime that fails to
stream goes back on the queue and speaks at the next press with "that was N
ago" attached.

**Apps** — `cloud-relay/pendantApps.js`. Time answers from the pendant's own
LTE clock (Mac timezone as fallback, "UTC" said out loud when guessing).
Reminders and Calendar ride `run_applescript` with read-only bodies on the
existing relay→Mac job path.

**Voice parity** — `set_timer` in `cloud-relay/openaiRealtimeVoice.js`, backed
by the SAME store through `createTimerControl`. Knob-set and voice-set timers
are one system by construction, not by agreement.

**Coordinator's mid-task additions** — Audio devices app (`bt_list` /
`bt_select` / `audio_sink`), the `approval_readback` haptic sender, and
`X-Pendant-Mode` labelling on the command route.

## What the measurements changed

Everything below is a fact from the owner's actual Mac on 2026-08-12, not a
guess, and each one changed the code.

| Measured | Consequence |
| --- | --- |
| Reminders per-item AppleScript loop: **never returned** (killed at 40 s); the live pendant job sat in `processing` forever | Rewritten as one bulk property read + a LOCAL loop → **~16 s** |
| Calendar with the app quit: instant `-600 Application isn't running`; in-script `launch` is classified as an app launch and needs approval | Calendar's plan runs hands-free `open_app` first |
| Calendar with the app running: **>90 s** and still going | Honest limitation, documented. Entering Calendar usually reaches the wait window and speaks the sleeping-Mac line. The fix is a typed EventKit read on the Mac side. |
| `compose_briefing` / `list_reminders`: `not on the hands-free allowlist` | Neither used. `run_applescript` bodies classify `{safe:true}` / tier `read`, so no approval is parked in front of a spoken question. `pendantApps.test.js` imports the real `actionRisk.js` rather than asserting a belief about it. |
| 16 s of silence after entering an app | "Checking your reminders." on entry; `APP_BRIEF_WAIT_MS` 20 s → 26 s |

Two bugs the tests caught before production: `Number(null) === 0` making every
`minutes`-only timer throw "positive duration", and `10 minutes timer started`
(English drops the plural on an attributive measure — hence two duration
formatters).

## Live verification (production, not local)

`wrangler deploy` → version `36422c99`, `/health` ok.

- **Knob**: detent → 5 frames (blip + "Time."), detent → 5 more, push → enter
  earcon, push on the 1-minute preset → 26 frames + `timer … started by knob:
  60000ms` in the worker log, Time app → 19 frames, `menu_back` → 2 frames and
  **no words**, exactly as the grammar specifies.
- **Timer queue-to-next-press**: a fresh conversation opened after expiry, with
  no interaction at all, produced 18 frames / 5618 bytes — the chime and the
  sentence, queued and delivered at the press.
- **Audio devices**: entering put `{"type":"bt_list"}` on the wire; answering
  as the firmware would built the ring and spoke it; pushing the second entry
  sent `{"type":"bt_select","index":1}` **and**
  `{"type":"audio_sink","sink":"bluetooth"}`.
- **Reminders**: enqueued `actionCount=1`, the Mac claimed it — and this is how
  the 16 s/40 s measurements above were found.

The first knob run returned zero bytes and it was worth chasing rather than
reporting: a clean zero here is a harness or propagation artifact, and the
second run (against the settled deployment) showed the full path.

## Tests

`cloud-relay` + `shared`: **658 → 743, all green.** New: `menuRing.test.js`
(27), `timerStore.test.js` (19), `pendantApps.test.js` (22),
`pendantEarcon.test.js` (11), plus 6 `set_timer` tests driven through the
Realtime socket seam into the real memory store.

## Firmware TODOs (not mine to write)

1. **Encoder long-hold → `{"type":"menu_back"}`.** `encoder_push_isr` in
   `firmware/nrf9160/src/main.c` debounces the falling edge and sets
   `menu_select_req` with no duration measurement, so a hold is
   indistinguishable from a press. The relay handles `menu_back` today; until
   firmware emits it, the `Back` ring entry is the escape.
2. **`X-Pendant-Mode: ptt` on the blue-button command upload.** The relay
   accepts and stores it now (allowlist `ptt|duplex|memo`, converse tags
   `duplex`, ring jobs tag `knob`). Deliberately NOT inferred from the
   transport — which transport a button uses is a build detail.
3. **Phase 2: mirror timer expiry to the device** so a pendant out of coverage
   still beeps. The relay store stays the source of truth.

## Mac-side TODO (mac-agent's territory)

A typed EventKit `list_reminders` / calendar read **plus its hands-free
allowlist entry in the same change** — the allowlist half is what makes it
usable, and it is the only thing that makes the Calendar app fast enough to be
worth entering.
