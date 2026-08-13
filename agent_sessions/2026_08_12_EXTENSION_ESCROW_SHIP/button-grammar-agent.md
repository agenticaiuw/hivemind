# button-grammar — buttons select, context decides which verb

Resumed from a killed run. Owner ruling, 2026-08-13, verbatim:

> "remember we can use the fucking buttons bro, right now it seems like you're
> using stopping the turning as confirmation for selecting but we should just
> use a button. only when no [app] is selected those buttons are reserved for
> the llm talk and the memo."

Dwell-to-select is dead as a COMMIT gesture. The 200 ms settle survives — it was
never about selection, it is about when the ring is allowed to speak.

## Claimed files
- software/ai-pendant-simulator/cloud-relay/menuRing.js + menuRing.test.js
- software/ai-pendant-simulator/cloud-relay/controlVocabulary.js + .test.js (new)
- software/ai-pendant-simulator/cloud-relay/spokenNumbers.js + .test.js (new)
- software/ai-pendant-simulator/cloud-relay/pendantConverse.js
- software/ai-pendant-simulator/cloud-relay/timerStore.js
- firmware/esp32-airpods-bridge/src/main.cpp
- docs/Screenless_App_Grammar.md

NOT touched: firmware/nrf9160/** (two agents are flashing that board),
CONTROLS_WIRING.md, hardware/BREADBOARD_WIRING.md.

## The bench this must speak to
yellow + blue buttons, encoder TURN only (no push), red mic-mute switch, pot for
volume, haptic. **Green button is dead. The RGB LED is not wired.** No spoken
line may reference a light, a colour-as-status, or a knob press.

## Design decisions taken

**Context, not remapping.** Two buttons and no encoder switch means a confirm
gesture can only come from a button, and both buttons already carry a global
verb. The only free variable left is CONTEXT: what the buttons mean depends on
whether the ring is open. Relay owns that bit and tells the device.

**Numeric entry.** One detent = one unit at any speed. Field announced once
("Setting minutes."), every settle speaks the bare number, yellow commits and
repeats the value with units. Numbers are synthesized LOCALLY so the settle is
immediate — a TTS round trip per detent is the thing that made a spinner
impossible before.

**Boundaries differ by kind, on purpose.** Durations stop at their ends (a wrap
turns a bumped 3-hour timer into a 1-minute one); clock fields wrap (a clock is
a circle). Both announce the edge audibly.

## Log

### ESP32 (finished the killed run, then audited it)
The inherited diff was complete and coherent. A read-only audit of the FULL
file (not just the diff — its comments are confident and could have been wrong)
against the ESP32-A2DP library source found one real hole and several stale
strings. All fixed:

- **Zero-address hole.** `addressFastPathReady()` did not check the cached
  BD_ADDR was non-zero. `set_auto_reconnect(zeros, 12)` makes the library
  decide it has no last connection, fall back to its OWN NVS namespace
  (`connected_bda`) and page whatever peer IT last saw — the exact second
  opinion this change deletes. Reachable via an inbound A2DP connection during
  the ~10 s the stack is still connectable. Now rejected at both ends.
- **Malformed `connect` blanked a live target**, permanently disabling retry
  for a device still wanted. Parsed into a temporary, committed on success.
- `discoveryOnly` was write-only dead state; deleted.
- "scanning will resume" was false with auto-reconnect off (our 30 s page is
  the only recovery); "streaming at 50%" contradicted `set_volume(80)`;
  "AirPods A2DP link" named a device class in a file that owns no preference.

Build: RAM 23.7%, Flash 86.1%. **Not flashed**, per brief.

### Relay
- `controlVocabulary.js` — the control table + composers. Every spoken hint is
  built from it; nothing is hardcoded.
- `menuRing.js` — dwell removed as commit; yellow selects, blue backs, context
  effect emitted by a wrapper so no branch can forget it. Alarm app, numeric
  entry, audio ring ordering.
- `menuSettle.js` — the debounce, extracted with an injectable clock so
  "40 detents = 1 spoken number" is a test rather than a claim.
- `spokenNumbers.js` — local formant synthesis (delegated). **1.2 ms mean /
  2.2 ms worst** per number against 450-1200 ms of audio produced.
- `timerStore.js` — alarms ride the same store; only the SPEECH differs.

### Bug this work caught (would have shipped)
Cursor preservation in `menuWithAudioDevices` fired on the ring's FIRST fill.
Before any device answers, the placeholder ring is `[Pendant speaker, Back]`,
so index 0 read as "Pendant speaker" — and the arriving list "restored" the
owner onto the speaker, scrolling straight past the headphones at index 0.
That is the owner's original complaint arriving through the back door.
Regression-tested.

### Results
- `node --test 'cloud-relay/*.test.js' 'shared/*.test.js'` → **753/753**
  (703 baseline + 50: menuRing 31→38, controlVocabulary 13, menuSettle 10,
  spokenNumbers 15, timerStore 19→25).
- eslint clean on every touched relay file.
- Deployed (`npx wrangler deploy`, version 3f9fa2a1); `/health` → 200,
  `macBridgeOnline: true`.
</content>
