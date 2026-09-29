"""Words-per-minute model for knob typing (text-entry WPM = (chars+space)/5 per minute).

Per pause:  t = dwell + a + b*log2(D/We + 1) + regrips*t_regrip
  D  = travel to next letter (letter widths), We = 4.133*sigma (effective width:
       the decoder tolerates error, so users aim at a sigma-wide target, Soukoreff & MacKenzie 2004)
  a = 0.10 s, b = 0.10 s/bit (typical finger/wrist Fitts constants)
Per word: + 0.30 s knob press to accept; + expected correction cost:
  top-1 miss but in top-3: +0.6 s per cycle step (turn-back to cycle, speaker reads next); else retype.

Two grip styles, which respond to radius differently:
  pinch knob (twist between thumb+index): error is ANGULAR (wrist/finger twist), sigma in letters
      ~ independent of radius; regrip every ~110 deg of twist.  Radius only sets footprint.
  thumb-rolled edge wheel: error is DISPLACEMENT at the fingertip (sigma_mm), so sigma_letters =
      sqrt(sigma_cog^2 + (sigma_mm / letter_arc_mm)^2); one stroke covers ~18 mm of surface.
"""
import math, sys
import numpy as np
import sim

A, B, T_REGRIP, T_ACCEPT, T_CYCLE = 0.10, 0.10, 0.30, 0.30, 0.6
TRAVEL_DEG = 300.0

# accuracy lookup (personalized, uniform layout, token-weighted) filled from results_all.txt by hand below
def interp_acc(table, sigma):
    xs = sorted(table); ys1 = [table[x][0] for x in xs]; ys3 = [table[x][1] for x in xs]
    return float(np.interp(sigma, xs, ys1)), float(np.interp(sigma, xs, ys3))

def word_time(word, prev_pos, centers, sigma, dwell, deg_per_stroke):
    units = sim.collapse(word)
    t, pos = 0.0, prev_pos
    we = 4.133 * sigma
    for c, dbl in units:
        mu = centers[sim.IDX[c]]
        d = abs(mu - pos)
        t += dwell * (1.8 if dbl else 1.0) + A + B * math.log2(d / we + 1)
        t += T_REGRIP * max(0, math.ceil(d * TRAVEL_DEG / 26 / deg_per_stroke) - 1)
        pos = mu
    return t + T_ACCEPT, pos

def wpm(sigma, dwell, deg_per_stroke, acc, n=4000, seed=3):
    words, prior = sim.make_lexicon("5k")
    centers, _ = sim.layout("uniform")
    rng = np.random.default_rng(seed)
    sample = rng.choice(len(words), n, p=prior)
    top1, top3 = acc
    tot_t = tot_c = 0.0; pos = 13.0
    for i in sample:
        w = words[i]
        t, pos = word_time(w, pos, centers, sigma, dwell, deg_per_stroke)
        # expected correction cost: in top-3 -> ~1.5 cycles avg, else retype once
        t += (top3 - top1) * 1.5 * T_CYCLE + (1 - top3) * t
        tot_t += t; tot_c += len(w) + 1
    return (tot_c / 5) / (tot_t / 60)

if __name__ == "__main__":
    # personalized top1/top3 from results_all.txt (5k, uniform, token-weighted); edit if rerun
    ACC_5K = {float(k): tuple(v) for k, v in eval(sys.argv[1]).items()} if len(sys.argv) > 1 else None
    if ACC_5K is None:
        raise SystemExit("pass the 5k accuracy table as a dict literal")
    print("== pinch knob (angular error; regrip every 110 deg) ==")
    for sigma in (0.5, 0.75, 1.0, 1.5):
        acc = interp_acc(ACC_5K, sigma)
        row = [f"{wpm(sigma, d, 110, acc):5.1f}" for d in (0.15, 0.25, 0.30)]
        print(f"sigma={sigma:<4} top1={acc[0]:.2f}  WPM @dwell 150/250/300 ms: {' / '.join(row)}")
    print("== thumb-rolled edge wheel (fingertip error sigma_mm=1.5 mm, sigma_cog=0.6 letter, 18 mm stroke) ==")
    for r_mm in (2.5, 4, 6, 8, 12):
        arc_letter = 2 * math.pi * r_mm * TRAVEL_DEG / 360 / 26
        sigma = math.sqrt(0.6 ** 2 + (1.5 / arc_letter) ** 2)
        deg_stroke = 18 / (2 * math.pi * r_mm) * 360
        acc = interp_acc(ACC_5K, min(sigma, 2.0))
        print(f"r={r_mm:>4} mm  letter arc {arc_letter:4.2f} mm  sigma={sigma:4.2f} letters  stroke={deg_stroke:5.0f} deg  "
              f"top1={acc[0]:.2f}  WPM@250ms {wpm(sigma, 0.25, deg_stroke, acc):5.1f}")
