# Knob typing — feasibility study (Project Hivemind pendant)

Owner of this file + knob-options.json + knob-sim/: research-knob-typing agent.

## Working log
- 2026-09-29 — Started. Created knob-sim/ with a venv (numpy, wordfreq). Spawned a background sub-agent (sonnet) to price angle sensors / encoders / haptic-detent option into knob-options.json.
- Plan: simulator (knob layouts × user noise × segmentation errors) -> Bayesian lexicon decoder with insert/delete alignment -> accuracy vs σ for 20 apps / ~200 commands+numbers / 5k / 20k; T9 baseline; WPM timing model; portable C decoder measured natively; literature σ estimates.
- 2026-09-29 — sim.py written (layouts uniform/freq/hints; per-user bias+scale; drop 3 %, spurious pause 3 %, close-letter merge 25 %; doubles = one long-dwell pause, flag detected 90 %). Full sweep running (results_all.txt).
- 2026-09-29 — Portable C decoder knob_decode.c + export_lex.py: front-coded 6-bit lexicon, prefix-shared Viterbi. Agrees 100 % with the Python decoder on 300 cases x 3 lexicons. Cross-compiled for Cortex-M33 (Zephyr SDK gcc, -O2, FPv5): kd_decode = 1016 B code; DP inner loop = 16 instructions/cell.
- 2026-09-29 — Sub-agent returned knob-options.json (27 rows). Spot-verified TMAG5273 (TI page: 2.3 mA active, 5 nA sleep, 1 uA wake-and-sleep, SOT-23, 1.7-3.6 V) and MT6701 (LCSC C3003196: $1.43/1, $0.89/100, 10 mA).
- 2026-09-29 — Confusion analysis (commands, sigma 0.3): residual 1 % errors are prefix/drop confusions (timer->time, eighty->eight, hours->hour, task->ask), not position noise. Grammar context and read-back fix these.
- 2026-09-29 — Full sweep done (434 s, results_all.txt / results_all.json). WPM model run (wpm_results.txt). Report written below.

---

# Report

## TL;DR
- **Closed sets are close to perfect.** For about 20 app names, the right app is the top-1 guess 99.5–100 % of the time at every σ up to 2 letter-widths. Top-3 is 100 %.
- **Numbers and units ("fifty minutes") work very well** when decoded with a grammar: top-1 is 97–99.7 % at σ ≤ 1 and top-3 is 100 %.
- **About 200 command words work well:** top-1 is 95–99 % at σ ≤ 1.
- **General text is usable but clearly worse than T9.** With 20k words, personalized, at a realistic σ of about 0.75–1.0, top-1 is 81–88 % and top-3 is 92–96 % (token-weighted). T9 with perfect key presses gets 95 % top-1 on the same lexicon.
- **Speed:** the model ceiling for an expert is about 18–22 WPM; a novice gets about 13 WPM. Voice is about 100+ WPM, so general text is a fallback, not a primary input.
- **It runs locally with room to spare.** A 20k-word lexicon packs into 83 KB of flash. The decoder uses about 6.7 KB of RAM and about 1 KB of code, and should take about 40 ms per word on a 128 MHz M33 (estimate, not measured on the chip). With 5k words it is 21 KB and about 10 ms; with 200 words it is 1 KB and under 0.1 ms. A 256 KB-RAM part is more than enough.
- **Recommended hardware:** a TMAG5273 3D-Hall angle sensor (bare, SOT-23, $1.94 each or $1.30 at 100) with a 6×2.5 mm diametric magnet, in a knob of about 10–14 mm diameter with hard end-stops at A and Z. The hint detents come from LRA ticks, not mechanical detents. The sensor wakes itself: in wake-and-sleep mode (about 1 µA) a magnetic-threshold interrupt fires on rotation.

## 1. Simulator (knob-sim/sim.py)
- The travel is 26 letter-widths long. Three layouts:
  - **uniform:** letters evenly spaced, alphabetical.
  - **freq:** each letter's width is proportional to the square root of its English frequency.
  - **hints:** uniform spacing plus tactile hints at A/F/K/P/U/Z and the end-stops. Error is modelled as growing with distance from the nearest hint: 0.35σ on a hint, up to 1.0σ two letters away. **This is an assumption.**
- User noise model: `o = 13 + s·(μ−13) + b + N(0, σ)`.
  - Per-user bias b ~ N(0, 0.6 letters). The literature reports a systematic overshoot of 13–38° (see §4).
  - Per-user scale s ~ N(1, 0.06).
- Segmentation errors:
  - A pause is dropped 3 % of the time.
  - A spurious hesitation pause is inserted 3 % of the time.
  - Two adjacent letters less than 1 letter apart merge into one long pause 25 % of the time.
- **Double letters ("ll") follow a convention:** one pause, held longer (about 1.8× dwell). The long-dwell flag is detected 90 % of the time, with 5 % false positives. The decoder models these flags probabilistically, so a merged pause and a real double compete fairly.
- **Decoder:** for each lexicon word, a Viterbi edit-distance alignment (match, delete a letter, insert a spurious pause). The score adds the Gaussian log-likelihood, the flag likelihood and log P(word), taken from wordfreq unigrams, or a uniform prior for the closed sets.
  - **generic:** a population-calibrated σ with zero bias.
  - **personalized:** bias, scale and σ are least-squares fitted from 20 accepted words, which the device learns from confirmations.
- **Vocabularies:**
  - apps: 20 words.
  - commands: 206 words (commands, 0–100 number words, units, apps).
  - numbers+units: a grammar over 808 phrases; each word is typed separately with a press between words.
  - 5k and 20k: wordfreq top-n.
- Test words are sampled by frequency (token-weighted), which is what real text looks like. The 20k set is also reported with uniform sampling over word types. There are 12 simulated users per condition; n is shown in results_all.txt (1,200–2,400 trials per cell).

## 2–3. Accuracy (personalized decoder, top-1 / top-3)

| Vocabulary | σ=0.3 | 0.5 | 0.75 | 1.0 | 1.5 | 2.0 | T9 (perfect keys) |
|---|---|---|---|---|---|---|---|
| 20 apps (uniform) | 1.000/1.000 | 1.000/1.000 | .998/1.000 | .999/1.000 | .987/.999 | .982/.999 | 1.000/1.000 |
| 20 apps (hints) | 1.000/1.000 | 1.000/1.000 | .999/1.000 | .998/1.000 | .995/1.000 | .991/1.000 | |
| 206 commands (uniform) | .991/1.000 | .986/.998 | .963/.998 | .952/.993 | .902/.978 | .818/.944 | .995/1.000 |
| 206 commands (hints) | .996/1.000 | .987/.998 | .980/.999 | .966/.997 | .931/.992 | .887/.975 | |
| number+unit phrases (hints, grammar) | .997/1.000 | .992/1.000 | .997/1.000 | .973/1.000 | .958/.997 | .947/.997 | |
| 5k general (uniform) | .935/.988 | .909/.976 | .876/.966 | .807/.939 | .742/.896 | .630/.822 | .958/.999 |
| 5k general (hints) | .946/.992 | .918/.977 | .886/.971 | .854/.958 | .783/.931 | .715/.885 | |
| 20k general (uniform) | .932/.980 | .881/.961 | .854/.950 | .805/.917 | .709/.861 | .599/.781 | .950/.997 |
| 20k general (hints) | .932/.982 | .913/.973 | .879/.963 | .846/.952 | .773/.908 | .699/.866 | |
| 20k, uniform over word types (hints) | .907/.973 | .863/.950 | .799/.912 | .738/.860 | – | – | .880/.974 |

Other findings:
- **Personalization matters most at low σ.** At σ=0.3, the generic decoder gets 84 % top-1 on 5k and the personalized one gets 94 %, because the user's systematic bias dominates. At σ ≥ 1.5, personalization adds only a few points.
- **Hint detents are the best layout.** They add about 4–7 points at σ ≥ 1 for general text, and 3–7 points for commands at σ ≥ 1.5. The frequency-weighted layout is about the same as uniform (within ±2 points) and costs alphabetical intuitiveness, so it is not worth it.
- **There is an error floor at low σ** (about 1 % for commands and about 6 % for general text). It comes from dropped or merged pauses, not position noise. Examples: timer→time, eighty→eight, hours→hour, task→ask, news→next. The fixes are grammar/context, spoken read-back, and turn-back-to-cycle.
- **T9 is the fair baseline.** With perfect key presses, T9 beats the knob on general text at any realistic σ. On closed sets both are essentially perfect. The knob's advantage is not accuracy: it is one small control, eyes-free, with no key grid to find.

## Words per minute (knob-sim/wpm.py, wpm_results.txt)
- **Per-pause timing model:** dwell + 0.10 s + 0.10 s/bit × log2(D/We+1). We = 4.133σ, because the decoder tolerates error. Add 0.3 s per regrip, 0.3 s to accept a word, and the expected correction cost.
- **Pinch knob** (twisted between thumb and index): about 19.5 WPM at a 250 ms dwell, from 17.7 WPM (300 ms) to 22.8 WPM (150 ms). A novice with about 0.4 s planning time per letter gets **about 13 WPM**. For reference, COMPASS, a visual rotary-bezel keyboard, measured 10 WPM on first use and 12.5 WPM after 90 minutes.
- **Radius:** for a pinch knob the error is angular, so radius mainly sets the footprint. Smaller is fine down to about 8–10 mm diameter, as long as it is grippable.
- **Thumb-rolled edge wheel:** the error is fingertip displacement (assumed 1.5 mm), so a small radius hurts.

  | Wheel radius | Letter arc | σ (letters) | Top-1, 5k | WPM |
  |---|---|---|---|---|
  | 2.5 mm (the existing "5 mm scroll encoder") | 0.5 mm | 3.0 | 63 % | 24 |
  | 6 mm | – | 1.4 | 76 % | 22 |
  | 12 mm | – | 0.86 | 84 % | 18 |

  **"Smaller = faster" is true, but only by about 15–25 %, and accuracy collapses below about 6 mm radius.** The existing 5 mm edge encoder is fine for scrolling an n-best list but too small for letter targeting.

## 4. Realistic σ from literature
- **Eyes-free haptic rotation of a 40 mm knob** (Bielefeld studies summarized in arXiv 2411.12765):
  - variable error (SD) is about 10–15° for a 90° twist;
  - systematic overshoot is 13–38°, which personalization removes;
  - distance and direction had no significant effect on either error.
- **Converting to letters:** with 300° of travel, one letter-width is 11.5°, so the SD is **about 0.9–1.3 letter-widths without landmarks**. End-stops and hint ticks shrink this near the landmarks. Counting ticks from a hint is reliable: WristDial got 94 % accuracy for 1-of-10 eyes-free selection using tactile counting, and 95 % with speech feedback.
- **My working estimate:**
  - novice, no hints: σ ≈ 1.0–1.5;
  - practiced, with hard end-stops plus LRA hint ticks: σ ≈ 0.6–0.9.
- **Design point: σ ≈ 0.75 with hints**, which gives apps 99.9 %, commands 98 %, number+unit 99.7 %, and 20k text 88 % top-1 / 96 % top-3. **These σ values are estimates; they need a user study with the prototype.**
- The swipe-keyboard analogy holds. SHARK2 (Kristensson & Zhai, UIST 2004) decodes 10–20k-word vocabularies from imprecise gestures using location plus a language model, which is the same principle in 2D. The knob has only 1D input, so it is inherently more ambiguous (e.g. "news"/"next").

## 5. On-device feasibility (knob-sim/knob_decode.c, export_lex.py)
- **Lexicon format:** sorted, front-coded list. Each word stores a 1-byte header (shared-prefix length and suffix length), a 1-byte quantized −log P (0.1 nat steps), and its suffix letters as 6-bit symbols (letter plus double flag).

  | Lexicon | Flash | Per word |
  |---|---|---|
  | 206 words | 1.0 KB | 4.97 B |
  | 5k | 21 KB | 4.27 B |
  | 20k | 83 KB | 4.14 B |

  Plain strings would take 42 KB and 179 KB respectively. The lexicon runs in place from flash (XIP), so it needs no RAM.
- **Decoder:** Viterbi DP that reuses rows across shared prefixes. The C decoder matches the Python decoder 100 % on 300 test cases for each of the three lexicons.
- **RAM:** 1.6 KB for the DP rows (16×25 floats) plus 5.0 KB for the emission table (52×24), about 6.7 KB of stack in total. With int16 it would be half that. No heap.
- **Measured on the host (Apple silicon, -O2):**

  | Lexicon | Time per word | DP cells per word |
  |---|---|---|
  | 206 words | 4.7 µs | 3.8k |
  | 5k | 63 µs | 48k |
  | 20k | 281 µs | 194k |

- **Cortex-M33** (cross-compiled with the Zephyr SDK gcc, -mcpu=cortex-m33, FPv5-SP, -O2):
  - kd_decode is 1016 B of code.
  - The inner loop is 16 instructions per DP cell, about 20 cycles.
  - At 128 MHz, including word unpacking, that gives **about 40 ms per word for 20k, about 10 ms for 5k, and under 0.1 ms for 200 words**, run once when the word is accepted. The nRF9160 already in the project has the same M33 core at 64 MHz, so double those times there.
- **Headroom:** a 256 KB-RAM part is plenty. Beam or length pruning (words more than 3 letters longer or shorter than the observation are skipped for scoring but still used for prefix rows) could cut the time 2–4× if needed.
- **Optional:** bigram or LLM rescoring of the top-k on the phone/agent side would recover much of the 20k top-1 gap, since the pendant already talks to an agent.

## 6. Hardware (knob-options.json, 27 rows; prices seen live 2026-09-29, nulls explained in notes)
- **The mapping needs an absolute angle.** Options:
  1. **Magnetic angle sensor with a diametric magnet** (recommended).
     - **TMAG5273** (TI): I2C, SOT-23, 1.7–3.6 V, 2.3 mA active, 5 nA sleep, and a wake-and-sleep mode at about 1 µA whose threshold interrupt wakes the MCU when the knob turns. No touch IC is needed. $1.94 each or $1.30 at 100 (LCSC); Adafruit breakout $5.95.
     - **MT6701** is cheaper and more precise (14-bit, $1.43 each or $0.89 at 100), but draws 10 mA and has no sleep mode. It would need a load switch plus a wake source (IQS228B touch IC, about 6.5 µA, $0.42).
     - **AS5600** is similar: about 6.5 mA with no true off.
     - **TLE5012B, MA730 and AS5048** are $3–5, over-spec, and power-hungry.
     - The 11.5°-per-letter resolution needed is loose, so TMAG5273's accuracy is sufficient after a one-time calibration.
  2. **Incremental encoder with hard end-stops at A and Z.** It re-homes on hitting a stop, and the nRF GPIO SENSE can count edges while the chip sleeps (about 0 µA). Parts: Alps EC05E, 5 mm, $2.82; EC10E, $1.04.
     - Detented versions give 12–24 steps per revolution, i.e. 15–30° per step. That is 1.3–2.6 letters per step, which is too coarse and fights the hint layout. A non-detented, higher-PPR part would be needed.
  3. **Absolute contacting encoder or potentiometer.**
     - Bourns EAW: 128 positions, $10.50, 0 µA idle, but bulky.
     - Bourns 3382: $1.27, read by the SAADC only when awake; wear and contact noise are concerns.
- **Haptic programmable detents (SmartKnob-style):** not plausible in a pendant.
  - The smallest gimbal BLDC found, the PM1105 (12×16 mm, $22.91), draws 0.59 A nominal and is rated 8–12 V.
  - The TMC6300 driver costs $6.37 bare or $17.95 as a breakout.
  - The existing DRV2605L LRA already gives programmable tick "detents" at no cost in parts.
- **Power** at 10 minutes of knob use per day:
  - TMAG5273: about 0.38 mAh/day active plus about 0.02 mAh/day in wake-and-sleep.
  - MT6701 with the IQS228B touch IC: about 1.7 mAh/day active plus about 0.16 mAh/day touch standby.
  - Both are negligible against the radio/audio budget, and TMAG5273 needs one fewer part.

## 7. Verdict
- **Where it works:**
  - Selecting from a closed set: apps, the ~200 commands and features, contacts, and numbers with units using a grammar. At a realistic σ it is **98–100 % top-1 and 100 % top-3**. With spoken read-back and press-to-accept, it is effectively error-free.
  - It is private (no voice), one-handed, eyes-free, works in a pocket, needs about one knob of footprint, and costs about $2–3 in parts.
  - It makes a good "command/number/app" channel, and **a better selector than scrolling** once there are more than about 15 items.
- **Where it struggles:**
  - General text. Top-1 is 80–88 % at 20k (worse for rare words) and top-3 is 92–96 %.
  - It runs at about 13 WPM (novice) to 20 WPM (expert), against about 100+ WPM for voice. It is below T9 with perfect keys.
  - The characteristic failure is a dropped or merged pause turning a word into its prefix (timer→time).
  - It is usable for a short private reply ("ok", "running late", "yes 5pm"), not for composing.
- **Eyes-free feedback design:**
  - An LRA tick when passing each hint letter (A/F/K/P/U/Z) and a firmer bump at the end-stops.
  - A soft tick when a pause registers; a double tick when a long dwell registers as a double letter.
  - A knob press accepts the word. The speaker (or an earbud) then reads the top candidate quietly.
  - A quick turn-back plus press cycles to the next alternative (top-3 covers 96–100 %).
  - A long press deletes or cancels.
  - Personalization runs silently from accepted words, re-fitting bias/scale/σ after about 20 words.
  - The decoder should report the posterior margin; below a threshold it should always read back rather than act. A silent pause or empty observation never counts as a confirmation.
- **How it complements voice:** voice handles content (messages, questions) and the knob handles control (which app, which contact, how long, how loud, yes/no/undo). The knob also covers quiet or public settings where voice is inappropriate, and can correct a voice misrecognition by picking from the n-best list.
- **Next step:** build a 3D-printed 12 mm knob with end-stops, a TMAG5273 breakout and the DRV2605L ticks. Log real pause positions from about 5 users to measure σ; the simulator and C decoder are ready to consume those logs.

## Sources
- COMPASS: Rotational Keyboard on Non-Touch Smartwatches (Yi et al., CHI 2017): https://pi.cs.tsinghua.edu.cn/lab/papers/COMPASS_Xin%20Yi_CHI2017.pdf
- Motion Analysis of Upper Limb and Hand in a Haptic Rotation Task (arXiv 2411.12765; related-work figures for overshoot and variable error): https://arxiv.org/pdf/2411.12765
- WristDial, eyes-free integer input (IJHCI 2021): https://www.tandfonline.com/doi/full/10.1080/10447318.2021.1898848 (abstract summary via https://scholar.nycu.edu.tw/en/publications/wristdial-an-eyes-free-integer-value-input-method-by-quantizing-t)
- SHARK2 (Kristensson & Zhai, UIST 2004): https://dl.acm.org/doi/10.1145/1029632.1029640
- SmartKnob (Scott Bezek): https://github.com/scottbez1/smartknob
- TI TMAG5273: https://www.ti.com/product/TMAG5273 ; MT6701 at LCSC: https://www.lcsc.com/product-detail/C3003196.html
- Word frequencies: wordfreq (Python package, en top-n list)
