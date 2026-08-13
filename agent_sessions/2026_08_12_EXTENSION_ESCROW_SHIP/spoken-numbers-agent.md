# spoken-numbers-agent — local number speech for the numeric-entry knob

Session: 2026_08_12_EXTENSION_ESCROW_SHIP
Owned files (only these two, nothing else touched):

- `software/ai-pendant-simulator/cloud-relay/spokenNumbers.js` (745 lines)
- `software/ai-pendant-simulator/cloud-relay/spokenNumbers.test.js` (405 lines)

## The problem

Numeric entry is a knob and an ear: one detent is +1, and ~200 ms after the
knob stops the owner must hear the bare number. TTS (`cloud-relay/speak.js` →
OpenAI `/audio/speech`) is 500-1500 ms of round trip, which is one to three
detents of lag — by the time the number arrives it is describing a value that
no longer exists. So the number is synthesized on the relay: no network, no
audio assets, no model.

## What was built

A Klatt-lite source-filter synthesizer, following `pendantEarcon.js` for format
and style: 24 kHz mono s16le, the pendant's own reply format, so the buffers
ride the existing `streamAnnouncementPcm` path with no resampling.

- Glottal pulse train (differentiated Rosenberg) or shaped noise
- Four cascaded resonators, F1-F3 moving per phoneme, F4 fixed at 3650 Hz
- A separate frication bandpass (parallel branch, downstream of the cascade)
- Aspiration injected INTO the cascade, so /h/ wears the next vowel's formants
- Per-sample linear interpolation of all parameters between control points, so
  words are one continuous gesture rather than a row of steady states
- Diphthongs as two targets and the glide between them
- Stops as explicit closure + burst + aspirated release
- F0 declination 128 → 98 Hz across the utterance, and final lengthening ×1.3
- Deterministic: two seeded mulberry32 noise streams, never `Math.random()`

### Export surface

| export | what |
| --- | --- |
| `renderNumberPcm(n, { sampleRate = 24000 })` | Buffer, 24 kHz mono s16le |
| `numberWords(n)` | `23 → ['twenty','three']`, pure |
| `phonemesFor(word)` | `'one' → ['w','ah','n']`, returns a copy |
| `phonemeTimeline(n, { sampleRate })` | `[{word, phoneme, type, startMs, endMs}]` |
| `PHONEMES` | the formant/duration table |
| `SPOKEN_WORDS` | the 29 closed-set words |
| `MAX_SPOKEN_NUMBER` | 999 |

`phonemeTimeline` exists so the tests can window a specific vowel's steady
state from the audio without re-deriving the renderer's own arithmetic (which
would agree with a broken renderer just as happily as with a good one).

Range: 0..999 (spec asked for 0..199; the hundreds composition was free).
Out of range / non-integer throws `RangeError` rather than mispronouncing.

## Measurements

### Latency (this Mac, node 22.19, JIT warmed with 10 full passes, per-number
median of 9 timed runs)

| range | mean | median | p95 | worst |
| --- | --- | --- | --- | --- |
| 0..199 | **1.27 ms** | 1.18 ms | 1.97 ms | **2.14 ms** (n=177) |
| 0..59 (clock fields) | **0.74 ms** | — | — | **1.11 ms** |
| 1..180 (timer minutes) | 1.22 ms | — | — | 2.14 ms |

Rendered audio duration for comparison: mean 1214 ms over 0..199, 706 ms over
0..59. Synthesis costs **0.10% of the audio it produces** (~950x realtime).
Shortest utterance "eight" 253 ms (0.27 ms to render); longest "one hundred
seventy seven" 2026 ms (2.14 ms to render).

Against 500-1500 ms for the same words through `speak.js`: 400-2000x faster.

### Two bugs found and fixed by measurement, not by reading

1. **Cascade normalization.** First version peak-normalized every resonator,
   which reads as the more principled choice. In a CASCADE it attenuates
   everything below each stage's resonance by 20-30 dB, so F1 arrived ~60 dB
   down: the /iy/ of "three" measured an RMS of 0.0000 while its own /th/ sat
   at 0.0755. Fixed by DC-normalizing the cascade (Klatt's own choice) and
   peak-normalizing only the isolated frication bandpass. Both `tune`
   functions are kept, with the reason written down next to them.
2. **Inner loop.** 5.6 ms/number, from a per-sample closure allocation for the
   parameter lerp and a `for..of` over the resonator array. Inlined: 1.27 ms.

### Formant verification (the real phonetic guard)

Test 12 renders the number, cuts the steady state of one vowel, and runs a
hand-written DFT over it. Two analysis choices, both forced by measurement:

- **Pre-emphasis** (0.97). Without it the source's ~6 dB/octave tilt made the
  peak-picker return the lowest frequency it was allowed to look at — F2 of
  /iy/ measured 580 Hz.
- **8 ms windows, Welch-averaged.** A long window resolves the 110 Hz PITCH
  harmonics and the picker finds those instead of formants (first attempt
  returned 240, 350, 460, 570 — a harmonic series). Windows shorter than two
  pitch periods smear harmonics into the formant envelope.

Measured against the table (all eight vowels checked during development):

| vowel | table F1/F2 | measured | error |
| --- | --- | --- | --- |
| /iy/ "three" | 300 / 2300 | 310 / 2310 | +3.3% / +0.4% |
| /uw/ "two" | 310 / 920 | 330 / 910 | +6.5% / −1.1% |
| /ay/ "nine" | 730 / 1150 | 670 / 1210 | −8.2% / +5.2% |
| /er/ "thirty" | 480 / 1350 | 470 / 1350 | −2.1% / 0.0% |
| /ah/ "one" | 660 / 1250 | 690 / 1250 | +4.5% / 0.0% |
| /eh/ "ten" | 560 / 1780 | 570 / 1810 | +1.8% / +1.7% |
| /ih/ "six" | 400 / 1950 | 370 / 1970 | −7.5% / +1.0% |
| /ao/ "four" | 580 / 880 | 570 / 970 | −1.7% / +10.2% |

Test tolerance is stated in the file as ±15%. A separate test asserts the
ORDERING from the spectrum (F2 of /iy/ > 2× F2 of /uw/; F1 of /ay/ > 1.6× F1 of
/iy/ and /uw/), which is what survives even if the peak-picker drifts.

### Mutation check — do the tests actually catch a broken synthesizer?

Run on throwaway copies, repo files untouched:

| mutation | result |
| --- | --- |
| table says /iy/ F2 = 1200 (table lies about the vowel) | ordering test fails |
| frication branch deleted | fricative test fails |
| resonators pinned to 500/1500, ignoring the table | formant + ordering tests fail |
| all durations ÷12 (degenerates to a click) | 4 tests fail |

Note the layering: pinning the resonators fails the table-vs-measurement test,
while a wrong TABLE fails the ordering test. Both are load-bearing.

### Intelligibility — objective probe, and its limits

I cannot listen. Instead: MFCC (26 mel, 12 cepstra, cepstral-mean-normalized) +
DTW template match of each synthesized word against a full 29-word reference
set spoken by macOS `say -v Alex`. Same reference voice for every candidate, so
voice mismatch is a constant and the RANKING carries the information.

Calibrated against four real, fully intelligible TTS voices scored the same way
against the same Alex references:

| candidate | top-1 | top-3 |
| --- | --- | --- |
| Flo (en_US) | 18/29 | 25/29 |
| Fred (en_US) | 17/29 | 24/29 |
| Daniel (en_GB) | 17/29 | 25/29 |
| Eddy (en_US) | 15/29 | 25/29 |
| **this synthesizer** | **17/29** | **25/29** |
| chance | 1/29 | 3/29 |

HARNESS BUG CAUGHT: an initial control run with "Samantha" scored a perfect
29/29 at distance 0.000. Samantha is not installed on this Mac and `say`
silently fell back to the default voice, which IS Alex — it was scoring the
reference against itself. Discarded and re-run with voices confirmed present in
`say -v '?'`.

Per-word, comparing my rank to the median rank of the three real voices, the
words where mine is *specifically* worse were sonorant-heavy, not
fricative-heavy: `twelve`, `one`, `fifty`, `twenty`, `seventy`, `nine`,
`eleven`. My /s/ words (`six`, `seven`, `seventeen`, `sixty`, `sixteen`) all
ranked 1. That is the opposite of the usual prior, and it prompted one
phonetically-motivated fix: /l/ given a real steady state (two targets, 80 ms —
a lateral is not pure transition), /w/ 60→70 ms, /v/ 60→70 ms and slightly
louder. That moved 16→17 top-1 and 24→25 top-3, and `eleven` from rank 2 to 1.

I STOPPED TUNING THERE. Further movement is inside the metric's own noise (a
real voice scored rank 13 on "thirty" and rank 9 on "two"), and chasing it
would be overfitting to MFCC/DTW rather than to an ear.

## Bench listen — the only real check

None of the above proves a human understands it. Generate WAVs with:

```
node - <<'EOF'
import fs from 'node:fs'
import { renderNumberPcm, numberWords } from './software/ai-pendant-simulator/cloud-relay/spokenNumbers.js'
const wav = (p, r = 24000) => { const h = Buffer.alloc(44)
  h.write('RIFF',0); h.writeUInt32LE(36+p.length,4); h.write('WAVE',8); h.write('fmt ',12)
  h.writeUInt32LE(16,16); h.writeUInt16LE(1,20); h.writeUInt16LE(1,22); h.writeUInt32LE(r,24)
  h.writeUInt32LE(r*2,28); h.writeUInt16LE(2,32); h.writeUInt16LE(16,34); h.write('data',36)
  h.writeUInt32LE(p.length,40); return Buffer.concat([h,p]) }
const all = []
for (const n of [0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,17,19,20,23,30,45,59,90,99,118,180]) {
  all.push(renderNumberPcm(n), Buffer.alloc(16800))
}
fs.writeFileSync('/tmp/numbers.wav', wav(Buffer.concat(all)))
EOF
afplay /tmp/numbers.wav
```

Listen for: `twelve`, `five`, `nine`, `thirty`, `twenty` — the ones the probe
ranks weakest. If any are wrong, the fix is a formant/duration edit in
`PHONEMES`, which is one table in one file.

## Verification

```
cd software/ai-pendant-simulator && node --test 'cloud-relay/spokenNumbers.test.js'
# 15 pass, 0 fail, 937 ms
npx eslint cloud-relay/spokenNumbers.js cloud-relay/spokenNumbers.test.js   # clean
```

15 tests: word decomposition (incl. teens and round tens), closed-set closure,
range refusal, transcriptions, copy-not-reference, all 0..199 render as valid
even-length buffers, byte-identical determinism, duration sanity, rail +
click-free edges, timeline/buffer agreement, sample-rate independence, formant
measurement, spectral ordering, fricative banding, stop closure-then-burst.

## Hard limits hit

- **I cannot hear it.** Everything above is instrumentation. A bench listen is
  the only real check and nothing here substitutes for it.
- The MFCC/DTW probe measures voice mismatch as much as intelligibility; it can
  rule out "acoustically generic mush" (which would score near 1/29) but it
  cannot certify a word is understandable.
- `/th/` vs `/f/` are barely distinguished — both are diffuse noise with no
  strong pole, which is true of the real sounds too. They are kept deliberately
  quiet: a loud /th/ turns "three" into "see".
- Nothing here was wired into `pendantConverse.js` or the numeric-entry mode —
  other agents own those files. This is a pure module plus its tests.
